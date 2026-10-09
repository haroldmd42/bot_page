"""
uploader_facebook.py
--------------------
Uploads vertical video content as Facebook Page Reels via Meta Graph API v19.0+.
Implements the 3-phase Reels upload protocol:
Phase 1: Start upload session (obtain video_id and upload_url)
Phase 2: Transfer binary video bytes
Phase 3: Finish and publish Reel with caption and tags
"""

import os
import time
import random
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger("FacebookUploader")


class FacebookReelsUploader:
    def __init__(
        self,
        page_id: Optional[str] = None,
        access_token: Optional[str] = None,
        dry_run: bool = False
    ):
        self.page_id = page_id or os.getenv("FB_PAGE_ID")
        self.access_token = access_token or os.getenv("FB_PAGE_ACCESS_TOKEN")
        self.dry_run = dry_run or os.getenv("DRY_RUN", "false").lower() == "true"
        self.api_version = os.getenv("FB_GRAPH_VERSION", "v19.0")
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def upload_reel(
        self,
        file_path: str,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Executes Meta's 3-phase video reels publishing flow.
        """
        logger.info(f"Preparing Facebook Reel upload for '{title}'...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")

        file_size = os.path.getsize(file_path)

        # When credentials are not yet configured
        if self.dry_run or not (self.page_id and self.access_token) or self.access_token == "mock_pending" or self.page_id == "mock_pending":
            logger.info("Facebook credentials not yet active or marked as mock_pending. Skipping Facebook Reel.")
            return {
                "video_id": None,
                "url": None,
                "status": "pending_setup",
                "title": title
            }

        headers = {
            "Authorization": f"OAuth {self.access_token}"
        }

        # --- Phase 1: Initialize Upload Session ---
        logger.info(f"Phase 1: Initializing Reel session on Page {self.page_id}...")
        start_endpoint = f"{self.base_url}/{self.page_id}/video_reels"
        start_payload = {
            "upload_phase": "start",
            "access_token": self.access_token
        }

        response = requests.post(start_endpoint, data=start_payload, timeout=30)
        if response.status_code != 200:
            logger.error(f"Failed to start Reel upload session: {response.text}")
            response.raise_for_status()

        start_data = response.json()
        video_id = start_data.get("video_id")
        upload_url = start_data.get("upload_url")

        if not video_id or not upload_url:
            raise RuntimeError(f"Unexpected response from Meta API: {start_data}")

        logger.info(f"Session established. Video ID: {video_id}")

        # --- Phase 2: Binary Video Data Transfer ---
        logger.info(f"Phase 2: Transferring binary video stream ({file_size / (1024*1024):.2f} MB)...")
        upload_headers = {
            "Authorization": f"OAuth {self.access_token}",
            "offset": "0",
            "file_size": str(file_size)
        }

        retry_count = 0
        max_retries = 4
        success_phase2 = False

        while not success_phase2 and retry_count <= max_retries:
            try:
                with open(file_path, "rb") as video_file:
                    upload_res = requests.post(
                        upload_url,
                        headers=upload_headers,
                        data=video_file,
                        timeout=120
                    )
                if upload_res.status_code in [200, 204]:
                    success_phase2 = True
                    logger.info("Video binary upload completed successfully.")
                else:
                    logger.warning(f"Upload chunk warning: {upload_res.status_code} - {upload_res.text}")
                    retry_count += 1
                    time.sleep(2 ** retry_count)
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    raise e
                time.sleep((2 ** retry_count) + random.uniform(0, 1))

        # --- Phase 3: Finish and Publish ---
        logger.info("Phase 3: Finalizing Reel publication...")
        finish_payload = {
            "upload_phase": "finish",
            "access_token": self.access_token,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": f"{title}\n\n{description}"
        }

        finish_res = requests.post(start_endpoint, data=finish_payload, timeout=30)
        if finish_res.status_code != 200:
            logger.error(f"Failed to finalize Reel: {finish_res.text}")
            finish_res.raise_for_status()

        reel_url = f"https://facebook.com/reel/{video_id}"
        logger.info(f"Facebook Reel published successfully! URL: {reel_url}")

        return {
            "video_id": video_id,
            "url": reel_url,
            "status": "published",
            "title": title
        }
