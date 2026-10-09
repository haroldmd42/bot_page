"""
funny_clip_manager.py
---------------------
Manages sourcing, downloading, and tracking funny video clips for Shorts/Reels.
Features:
- Connects to Pexels Video API (if PEXELS_API_KEY is present) for endless fresh funny clips.
- Includes a curated fallback library of royalty-free funny animal and fail clips.
- Avoids repeating clips by persisting used IDs in data/used_clips.json.
- Formats clips to vertical 9:16 (1080x1920) ready for comedic overlays.
"""

import os
import json
import random
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("FunnyClipManager")


class FunnyClipManager:
    def __init__(self, used_clips_file: str = "data/used_clips.json", temp_dir: str = "output/clips"):
        self.used_clips_file = used_clips_file
        self.temp_dir = temp_dir
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        self.used_clips = self._load_used_clips()
        os.makedirs(self.temp_dir, exist_ok=True)

        # Curated collection of royalty-free open comedic clips (funny animals, fails, funny reactions)
        self.curated_funny_clips = [
            {
                "id": "clip_cat_derp_01",
                "category": "funny_animals",
                "title": "Gato Calculando Mal el Salto",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-cat-looking-at-the-camera-42777-large.mp4",
                "fallback_duration": 12.0
            },
            {
                "id": "clip_dog_zoomies_02",
                "category": "funny_animals",
                "title": "Perro con Zoomies Incontrolables",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-funny-playful-dog-on-the-grass-44243-large.mp4",
                "fallback_duration": 14.0
            },
            {
                "id": "clip_cat_box_03",
                "category": "funny_animals",
                "title": "Gato Atrapado en Caja Ridículamente Pequeña",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-cat-curiously-inspecting-a-room-42867-large.mp4",
                "fallback_duration": 10.0
            },
            {
                "id": "clip_funny_duck_04",
                "category": "funny_animals",
                "title": "Pato Corriendo en Modo Pánico",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-little-ducks-walking-in-a-yard-43224-large.mp4",
                "fallback_duration": 11.0
            },
            {
                "id": "clip_clumsy_puppy_05",
                "category": "relatable_fails",
                "title": "Cachorro Tropezando con su Propia Sombra",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-dog-running-excitedly-in-the-yard-44238-large.mp4",
                "fallback_duration": 13.0
            },
            {
                "id": "clip_silly_monkey_06",
                "category": "unexpected_comedy",
                "title": "Reacción Inesperada Absurda",
                "url": "https://assets.mixkit.co/videos/preview/mixkit-funny-monkey-eating-fruit-in-a-tree-44445-large.mp4",
                "fallback_duration": 12.0
            }
        ]

    def _load_used_clips(self) -> List[str]:
        if os.path.exists(self.used_clips_file):
            try:
                with open(self.used_clips_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_used_clip(self, clip_id: str):
        if clip_id not in self.used_clips:
            self.used_clips.append(clip_id)
            os.makedirs(os.path.dirname(self.used_clips_file), exist_ok=True)
            with open(self.used_clips_file, "w", encoding="utf-8") as f:
                json.dump(self.used_clips, f, indent=2)

    def fetch_pexels_video(self, query: str = "funny animal") -> Optional[Dict[str, Any]]:
        """Searches Pexels API for vertical funny portrait clips if API key is provided."""
        if not self.pexels_api_key:
            return None

        try:
            url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=15"
            headers = {"Authorization": self.pexels_api_key}
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                videos = data.get("videos", [])
                for vid in videos:
                    vid_id = f"pexels_{vid.get('id')}"
                    if vid_id in self.used_clips:
                        continue
                    # Pick an HD or SD mp4 file
                    video_files = vid.get("video_files", [])
                    mp4_files = [vf for vf in video_files if vf.get("file_type") == "video/mp4" and vf.get("link")]
                    if mp4_files:
                        best = sorted(mp4_files, key=lambda x: x.get("width", 0), reverse=True)[0]
                        return {
                            "id": vid_id,
                            "category": "pexels_dynamic",
                            "title": query.title(),
                            "url": best["link"],
                            "duration": vid.get("duration", 15)
                        }
        except Exception as e:
            logger.warning(f"Error querying Pexels: {e}")
    def fetch_pixabay_video(self, query: str = "funny cat") -> Optional[Dict[str, Any]]:
        """Searches Pixabay API for funny clips if PIXABAY_API_KEY is configured."""
        if not self.pixabay_api_key:
            return None

        try:
            url = f"https://pixabay.com/api/videos/?key={self.pixabay_api_key}&q={requests.utils.quote(query)}&per_page=20"
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                data = res.json()
                hits = data.get("hits", [])
                for hit in hits:
                    vid_id = f"pixabay_{hit.get('id')}"
                    if vid_id in self.used_clips:
                        continue
                    vids = hit.get("videos", {})
                    # Select best available video stream (medium, large or small)
                    selected = vids.get("medium") or vids.get("large") or vids.get("small")
                    if selected and selected.get("url"):
                        return {
                            "id": vid_id,
                            "category": "pixabay_dynamic",
                            "title": hit.get("tags", query).split(",")[0].strip().title(),
                            "url": selected["url"],
                            "duration": hit.get("duration", 15)
                        }
        except Exception as e:
            logger.warning(f"Error querying Pixabay: {e}")
        return None

    def get_next_funny_clip(self, preferred_category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves a funny clip that hasn't been used yet.
        1. Checks if the user dropped any custom funny video files into assets/clips/.
        2. Queries Pixabay API if PIXABAY_API_KEY is configured.
        3. Queries Pexels API if PEXELS_API_KEY is configured.
        4. Returns None if no external clip is found, allowing procedural comedic scene rendering.
        """
        # 1. Check local assets/clips folder
        local_dir = "assets/clips"
        if os.path.exists(local_dir):
            local_files = [
                os.path.join(local_dir, f)
                for f in os.listdir(local_dir)
                if f.lower().endswith((".mp4", ".mov", ".mkv"))
            ]
            unused_local = [f for f in local_files if f not in self.used_clips]
            if unused_local:
                chosen = random.choice(unused_local)
                self._save_used_clip(chosen)
                return {
                    "id": os.path.basename(chosen),
                    "category": "local_custom",
                    "title": os.path.splitext(os.path.basename(chosen))[0].replace("_", " ").title(),
                    "local_path": chosen
                }

        search_terms = ["funny cat", "funny dog", "funny fails", "clumsy animal", "funny pets", "cute cat funny"]
        query = random.choice(search_terms)

        # 2. Try Pixabay (Instant free API)
        if self.pixabay_api_key:
            pixabay_clip = self.fetch_pixabay_video(query)
            if pixabay_clip:
                self._save_used_clip(pixabay_clip["id"])
                return pixabay_clip

        # 3. Try Pexels search if API key exists
        if self.pexels_api_key:
            pexels_clip = self.fetch_pexels_video(query)
            if pexels_clip:
                self._save_used_clip(pexels_clip["id"])
                return pexels_clip

        # 4. No external clip file available -> fallback to procedural comedy scenes
        return None

    def download_clip(self, clip_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Downloads or retrieves the local clip video path."""
        if not clip_data:
            return None

        # If it's already a local file in assets/clips/
        if clip_data.get("local_path") and os.path.exists(clip_data["local_path"]):
            return clip_data["local_path"]

        clip_id = clip_data.get("id", "temp_clip")
        target_path = os.path.join(self.temp_dir, f"{clip_id}.mp4")

        if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
            return target_path

        url = clip_data.get("url")
        if not url:
            return None

        logger.info(f"Downloading funny video clip ({clip_data.get('title')})...")
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get(url, headers=headers, stream=True, timeout=30)
            if res.status_code == 200:
                with open(target_path, "wb") as f:
                    for chunk in res.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                logger.info(f"Clip saved to: {target_path} ({os.path.getsize(target_path) / (1024*1024):.2f} MB)")
                return target_path
            else:
                logger.warning(f"Failed to download clip, status {res.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Clip download error: {e}")
            return None
