"""
analytics_collector.py
-----------------------
Extracts performance analytics from YouTube Data API v3 and Meta Graph API.
Updates `data/history.json` and compiles time-series metrics into `data/metrics.json`.
Provides data for the React Dashboard and feeds the growth optimizer feedback loop.
"""

import json
import os
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    Credentials = None
    build = None
    GOOGLE_API_AVAILABLE = False

logger = logging.getLogger("AnalyticsCollector")


class AnalyticsCollector:
    def __init__(
        self,
        history_path: str = "data/history.json",
        metrics_path: str = "data/metrics.json"
    ):
        self.history_path = history_path
        self.metrics_path = metrics_path
        self.yt_client_id = os.getenv("YT_CLIENT_ID")
        self.yt_client_secret = os.getenv("YT_CLIENT_SECRET")
        self.yt_refresh_token = os.getenv("YT_REFRESH_TOKEN")
        self.fb_access_token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        self.dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    def _load_history(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.history_path):
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_history(self, data: List[Dict[str, Any]]):
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_metrics(self) -> Dict[str, Any]:
        if os.path.exists(self.metrics_path):
            with open(self.metrics_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_metrics(self, data: Dict[str, Any]):
        os.makedirs(os.path.dirname(self.metrics_path), exist_ok=True)
        with open(self.metrics_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def fetch_youtube_metrics(self, video_id: str) -> Dict[str, int]:
        """Queries YouTube Data API v3 for real view, like, and comment counts."""
        if not video_id or video_id.startswith("yt_sample") or video_id.startswith("yt_"):
            return {"views": 0, "likes": 0, "comments": 0}

        if not (self.yt_client_id and self.yt_client_secret and self.yt_refresh_token):
            return {"views": 0, "likes": 0, "comments": 0}

        try:
            creds = Credentials(
                token=None,
                refresh_token=self.yt_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.yt_client_id,
                client_secret=self.yt_client_secret
            )
            youtube = build("youtube", "v3", credentials=creds)
            response = youtube.videos().list(part="statistics", id=video_id).execute()

            items = response.get("items", [])
            if not items:
                logger.warning(f"No YouTube stats found for real video ID {video_id}")
                return {"views": 0, "likes": 0, "comments": 0}

            stats = items[0].get("statistics", {})
            return {
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0))
            }
        except Exception as e:
            logger.error(f"Error fetching real YouTube metrics for {video_id}: {e}")
            return {"views": 0, "likes": 0, "comments": 0}

    def fetch_facebook_metrics(self, video_id: str) -> Dict[str, int]:
        """Queries Meta Graph API for real views, reactions, and comments."""
        if not video_id or video_id.startswith("fb_sample") or video_id.startswith("fb_") or not self.fb_access_token or self.fb_access_token == "mock_pending":
            return {"views": 0, "likes": 0, "comments": 0, "shares": 0}

        try:
            url = f"https://graph.facebook.com/v19.0/{video_id}"
            params = {
                "fields": "views,likes.summary(true),comments.summary(true),sharedposts.summary(true)",
                "access_token": self.fb_access_token
            }
            res = requests.get(url, params=params, timeout=20)
            if res.status_code != 200:
                logger.warning(f"Meta Graph API notice for {video_id}: {res.status_code}")
                return {"views": 0, "likes": 0, "comments": 0, "shares": 0}

            data = res.json()
            views = data.get("views", 0)
            likes = data.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = data.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares = data.get("sharedposts", {}).get("summary", {}).get("total_count", 0)

            return {
                "views": int(views),
                "likes": int(likes),
                "comments": int(comments),
                "shares": int(shares)
            }
        except Exception as e:
            logger.error(f"Error fetching real Facebook metrics for {video_id}: {e}")
            return {"views": 0, "likes": 0, "comments": 0, "shares": 0}

    def sync_youtube_channel_videos(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans the authenticated YouTube channel for all uploaded videos via YouTube Data API v3.
        Synchronizes live views, likes, and comments, and imports any videos missing from history.
        """
        if not (self.yt_client_id and self.yt_client_secret and self.yt_refresh_token):
            logger.info("YouTube credentials not provided in environment. Skipping channel video discovery.")
            return history

        try:
            creds = Credentials(
                token=None,
                refresh_token=self.yt_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.yt_client_id,
                client_secret=self.yt_client_secret
            )
            youtube = build("youtube", "v3", credentials=creds)

            # 1. Fetch channel's uploads playlist
            channel_res = youtube.channels().list(mine=True, part="contentDetails,snippet").execute()
            items = channel_res.get("items", [])
            if not items:
                logger.warning("No YouTube channel found for current credentials.")
                return history

            channel = items[0]
            uploads_playlist_id = channel.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
            channel_title = channel.get("snippet", {}).get("title", "Mi Canal")
            logger.info(f"Conectado a canal de YouTube: '{channel_title}' (Uploads: {uploads_playlist_id})")

            if not uploads_playlist_id:
                return history

            # 2. Retrieve uploads from channel (up to 50 videos)
            playlist_res = youtube.playlistItems().list(
                playlistId=uploads_playlist_id,
                part="snippet,contentDetails",
                maxResults=50
            ).execute()

            yt_items = playlist_res.get("items", [])
            logger.info(f"Encontrados {len(yt_items)} videos en el canal de YouTube.")

            video_ids = [item["contentDetails"]["videoId"] for item in yt_items if item.get("contentDetails", {}).get("videoId")]
            if not video_ids:
                return history

            # 3. Retrieve live statistics for all channel videos in batch
            stats_res = youtube.videos().list(
                id=",".join(video_ids),
                part="snippet,statistics"
            ).execute()

            video_data_map = {}
            for v in stats_res.get("items", []):
                vid = v.get("id")
                stats = v.get("statistics", {})
                snippet = v.get("snippet", {})
                video_data_map[vid] = {
                    "video_id": vid,
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "published_at": snippet.get("publishedAt", datetime.now().isoformat() + "Z"),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "tags": snippet.get("tags", ["Shorts"])
                }

            # 4. Merge into history
            existing_ids = {
                item.get("youtube", {}).get("video_id")
                for item in history
                if item.get("youtube", {}).get("video_id")
            }

            for vid, vdata in video_data_map.items():
                if vid in existing_ids:
                    # Update live stats
                    for item in history:
                        if item.get("youtube", {}).get("video_id") == vid:
                            item["title"] = vdata["title"]
                            item["youtube"]["views"] = vdata["views"]
                            item["youtube"]["likes"] = vdata["likes"]
                            item["youtube"]["comments"] = vdata["comments"]
                            item["youtube"]["status"] = "published"
                            item["status"] = "published"
                else:
                    # New video found on channel -> Add to history
                    logger.info(f"Importando video detectado en canal de YouTube: '{vdata['title']}' ({vid})")
                    niche = "Humor & Comedia"
                    tl = vdata["title"].lower()
                    if any(w in tl for w in ["ia", "ai", "tech", "algoritmo"]):
                        niche = "Tech & AI"
                    elif any(w in tl for w in ["gato", "perro", "mascota"]):
                        niche = "Animales & Mascotas"

                    new_record = {
                        "id": f"vid_yt_{vid}",
                        "title": vdata["title"],
                        "hook": vdata["title"],
                        "niche": niche,
                        "created_at": vdata["published_at"],
                        "duration": 25.0,
                        "status": "published",
                        "tags": vdata["tags"],
                        "youtube": {
                            "video_id": vid,
                            "url": f"https://youtube.com/shorts/{vid}",
                            "status": "published",
                            "views": vdata["views"],
                            "likes": vdata["likes"],
                            "comments": vdata["comments"]
                        },
                        "facebook": {
                            "video_id": None,
                            "url": None,
                            "status": "pending_setup",
                            "views": 0,
                            "likes": 0,
                            "comments": 0,
                            "shares": 0
                        },
                        "metrics_summary": {
                            "total_views": vdata["views"],
                            "total_likes": vdata["likes"],
                            "total_comments": vdata["comments"],
                            "total_shares": 0,
                            "engagement_rate": round(((vdata["likes"] + vdata["comments"]) / max(vdata["views"], 1)) * 100.0, 2)
                        }
                    }
                    history.insert(0, new_record)

            return history
        except Exception as e:
            logger.error(f"Error sincronizando videos del canal de YouTube: {e}")
            return history

    def sync_facebook_page_videos(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Discovers all videos/reels currently published on the Facebook Page via Meta Graph API.
        """
        if not self.fb_access_token or self.fb_access_token == "mock_pending":
            return history

        page_id = os.getenv("FB_PAGE_ID", "me")
        try:
            url = f"https://graph.facebook.com/v19.0/{page_id}/videos"
            params = {
                "fields": "id,title,description,created_time,views,likes.summary(true),comments.summary(true),sharedposts.summary(true)",
                "access_token": self.fb_access_token,
                "limit": 30
            }
            res = requests.get(url, params=params, timeout=20)
            if res.status_code != 200:
                logger.warning(f"Facebook Graph API notice: {res.status_code}")
                return history

            data = res.json()
            fb_videos = data.get("data", [])
            logger.info(f"Encontrados {len(fb_videos)} videos en la página de Facebook.")

            existing_fb_ids = {
                item.get("facebook", {}).get("video_id")
                for item in history
                if item.get("facebook", {}).get("video_id")
            }

            for fb_v in fb_videos:
                fid = fb_v.get("id")
                views = int(fb_v.get("views", 0))
                likes = int(fb_v.get("likes", {}).get("summary", {}).get("total_count", 0))
                comments = int(fb_v.get("comments", {}).get("summary", {}).get("total_count", 0))
                shares = int(fb_v.get("sharedposts", {}).get("summary", {}).get("total_count", 0))
                title = fb_v.get("title") or fb_v.get("description", "Facebook Reel")[:50]

                if fid in existing_fb_ids:
                    for item in history:
                        if item.get("facebook", {}).get("video_id") == fid:
                            item["facebook"]["views"] = views
                            item["facebook"]["likes"] = likes
                            item["facebook"]["comments"] = comments
                            item["facebook"]["shares"] = shares
                            item["facebook"]["status"] = "published"
                else:
                    # Match by title or insert
                    matched = False
                    for item in history:
                        if item.get("title", "").strip().lower() in title.strip().lower() or title.strip().lower() in item.get("title", "").strip().lower():
                            item["facebook"]["video_id"] = fid
                            item["facebook"]["url"] = f"https://www.facebook.com/reel/{fid}"
                            item["facebook"]["status"] = "published"
                            item["facebook"]["views"] = views
                            item["facebook"]["likes"] = likes
                            item["facebook"]["comments"] = comments
                            item["facebook"]["shares"] = shares
                            matched = True
                            break

                    if not matched:
                        history.insert(0, {
                            "id": f"vid_fb_{fid}",
                            "title": title,
                            "hook": title,
                            "niche": "Facebook Reels",
                            "created_at": fb_v.get("created_time", datetime.now().isoformat() + "Z"),
                            "duration": 20.0,
                            "status": "published",
                            "tags": ["Reels", "Viral"],
                            "youtube": { "video_id": None, "url": None, "status": "pending_setup", "views": 0, "likes": 0, "comments": 0 },
                            "facebook": {
                                "video_id": fid,
                                "url": f"https://www.facebook.com/reel/{fid}",
                                "status": "published",
                                "views": views,
                                "likes": likes,
                                "comments": comments,
                                "shares": shares
                            },
                            "metrics_summary": {
                                "total_views": views,
                                "total_likes": likes,
                                "total_comments": comments,
                                "total_shares": shares,
                                "engagement_rate": round(((likes + comments + shares) / max(views, 1)) * 100.0, 2)
                            }
                        })
            return history
        except Exception as e:
            logger.error(f"Error sincronizando videos de Facebook: {e}")
            return history

    def collect_and_sync(self) -> Dict[str, Any]:
        """
        Gathers metrics across all videos, syncs channel uploads,
        updates history, and regenerates aggregated metrics dataset.
        """
        logger.info("Starting analytics collection and channel sync routine...")
        history = self._load_history()
        existing_metrics = self._load_metrics()

        # 1. Sync live videos directly from YouTube channel and Facebook Page
        history = self.sync_youtube_channel_videos(history)
        history = self.sync_facebook_page_videos(history)

        tot_views = 0

        tot_likes = 0
        tot_comments = 0
        tot_shares = 0
        yt_total_views = 0
        fb_total_views = 0

        # Update each video record
        for item in history:
            # YouTube stats
            yt_id = item.get("youtube", {}).get("video_id")
            if yt_id:
                yt_stats = self.fetch_youtube_metrics(yt_id)
                # Keep maximum observed count so numbers never decline
                current_yt_views = max(item.get("youtube", {}).get("views", 0), yt_stats.get("views", 0))
                current_yt_likes = max(item.get("youtube", {}).get("likes", 0), yt_stats.get("likes", 0))
                current_yt_comments = max(item.get("youtube", {}).get("comments", 0), yt_stats.get("comments", 0))
                item["youtube"]["views"] = current_yt_views
                item["youtube"]["likes"] = current_yt_likes
                item["youtube"]["comments"] = current_yt_comments

            # Facebook stats
            fb_id = item.get("facebook", {}).get("video_id")
            if fb_id:
                fb_stats = self.fetch_facebook_metrics(fb_id)
                current_fb_views = max(item.get("facebook", {}).get("views", 0), fb_stats.get("views", 0))
                current_fb_likes = max(item.get("facebook", {}).get("likes", 0), fb_stats.get("likes", 0))
                current_fb_comments = max(item.get("facebook", {}).get("comments", 0), fb_stats.get("comments", 0))
                current_fb_shares = max(item.get("facebook", {}).get("shares", 0), fb_stats.get("shares", 0))
                item["facebook"]["views"] = current_fb_views
                item["facebook"]["likes"] = current_fb_likes
                item["facebook"]["comments"] = current_fb_comments
                item["facebook"]["shares"] = current_fb_shares

            # Combined summary
            v_views = item.get("youtube", {}).get("views", 0) + item.get("facebook", {}).get("views", 0)
            v_likes = item.get("youtube", {}).get("likes", 0) + item.get("facebook", {}).get("likes", 0)
            v_comments = item.get("youtube", {}).get("comments", 0) + item.get("facebook", {}).get("comments", 0)
            v_shares = item.get("facebook", {}).get("shares", 0)

            eng_rate = ((v_likes + v_comments + v_shares) / max(v_views, 1)) * 100.0

            item["metrics_summary"] = {
                "total_views": v_views,
                "total_likes": v_likes,
                "total_comments": v_comments,
                "total_shares": v_shares,
                "engagement_rate": round(eng_rate, 2)
            }

            tot_views += v_views
            tot_likes += v_likes
            tot_comments += v_comments
            tot_shares += v_shares
            yt_total_views += item.get("youtube", {}).get("views", 0)
            fb_total_views += item.get("facebook", {}).get("views", 0)

        self._save_history(history)
        logger.info(f"Updated metrics for {len(history)} videos in {self.history_path}")

        # Recompute time-series growth trends
        today_str = datetime.now().strftime("%Y-%m-%d")
        growth_trends = existing_metrics.get("growth_trends", [])

        # Check if today's snapshot exists
        existing_today = next((item for item in growth_trends if item.get("date") == today_str), None)
        avg_eng = ((tot_likes + tot_comments + tot_shares) / max(tot_views, 1)) * 100.0

        if existing_today:
            existing_today["views"] = tot_views
            existing_today["likes"] = tot_likes
            existing_today["comments"] = tot_comments
            existing_today["shares"] = tot_shares
            existing_today["cumulative_views"] = tot_views
            existing_today["engagement_rate"] = round(avg_eng, 2)
        else:
            growth_trends.append({
                "date": today_str,
                "views": tot_views,
                "likes": tot_likes,
                "comments": tot_comments,
                "shares": tot_shares,
                "engagement_rate": round(avg_eng, 2),
                "cumulative_views": tot_views
            })

        # Monetization calculations
        yt_target = 10_000_000  # 10M views for YouTube Partner Program Shorts
        fb_target = 500_000     # 500K views Meta Performance bonus milestone

        metrics_payload = {
            "last_updated": datetime.now().isoformat() + "Z",
            "overview": {
                "total_videos": len(history),
                "total_views": tot_views,
                "total_likes": tot_likes,
                "total_comments": tot_comments,
                "total_shares": tot_shares,
                "average_engagement_rate": round(avg_eng, 2),
                "top_performing_niche": "Tech & AI",
                "youtube_shorts_monetization": {
                    "target_views": yt_target,
                    "current_views": yt_total_views,
                    "percentage": round((yt_total_views / yt_target) * 100.0, 2),
                    "estimated_cpm_usd": 0.08,
                    "estimated_earnings_usd": round((yt_total_views / 1000) * 0.08, 2)
                },
                "facebook_reels_monetization": {
                    "target_views": fb_target,
                    "current_views": fb_total_views,
                    "percentage": round(min((fb_total_views / fb_target) * 100.0, 100.0), 2),
                    "estimated_cpm_usd": 0.15,
                    "estimated_earnings_usd": round((fb_total_views / 1000) * 0.15, 2)
                }
            },
            "growth_trends": growth_trends[-14:],  # Keep last 14 days
            "platform_breakdown": {
                "youtube": {
                    "views": yt_total_views,
                    "share_pct": round((yt_total_views / max(tot_views, 1)) * 100.0, 1)
                },
                "facebook": {
                    "views": fb_total_views,
                    "share_pct": round((fb_total_views / max(tot_views, 1)) * 100.0, 1)
                }
            },
            "optimization_recommendations": existing_metrics.get("optimization_recommendations", [])
        }

        self._save_metrics(metrics_payload)
        logger.info(f"Saved aggregated metrics to {self.metrics_path}")
        return metrics_payload
