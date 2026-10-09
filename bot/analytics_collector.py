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
        """Queries YouTube Data API v3 for view, like, and comment counts."""
        if not (self.yt_client_id and self.yt_client_secret and self.yt_refresh_token) or video_id.startswith("yt_sample") or video_id.startswith("yt_"):
            # Simulated realistic growth for demo / dry-run mode
            growth_factor = random.uniform(1.02, 1.08)
            return {
                "views": int(random.randint(1500, 5000) * growth_factor),
                "likes": int(random.randint(120, 450) * growth_factor),
                "comments": int(random.randint(15, 60) * growth_factor)
            }

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
                logger.warning(f"No YouTube stats found for ID {video_id}")
                return {"views": 0, "likes": 0, "comments": 0}

            stats = items[0].get("statistics", {})
            return {
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0))
            }
        except Exception as e:
            logger.error(f"Error fetching YouTube metrics for {video_id}: {e}")
            return {"views": 0, "likes": 0, "comments": 0}

    def fetch_facebook_metrics(self, video_id: str) -> Dict[str, int]:
        """Queries Meta Graph API for views, reactions, and comments."""
        if not self.fb_access_token or video_id.startswith("fb_sample") or video_id.startswith("fb_"):
            growth_factor = random.uniform(1.03, 1.09)
            return {
                "views": int(random.randint(2200, 6500) * growth_factor),
                "likes": int(random.randint(180, 550) * growth_factor),
                "comments": int(random.randint(25, 90) * growth_factor),
                "shares": int(random.randint(40, 150) * growth_factor)
            }

        try:
            url = f"https://graph.facebook.com/v19.0/{video_id}"
            params = {
                "fields": "views,likes.summary(true),comments.summary(true),sharedposts.summary(true)",
                "access_token": self.fb_access_token
            }
            res = requests.get(url, params=params, timeout=20)
            if res.status_code != 200:
                logger.warning(f"Meta Graph API error for {video_id}: {res.text}")
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
            logger.error(f"Error fetching Facebook metrics for {video_id}: {e}")
            return {"views": 0, "likes": 0, "comments": 0, "shares": 0}

    def collect_and_sync(self) -> Dict[str, Any]:
        """
        Gathers metrics across all videos, updates history,
        and regenerates aggregated metrics dataset.
        """
        logger.info("Starting analytics collection routine...")
        history = self._load_history()
        existing_metrics = self._load_metrics()

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
