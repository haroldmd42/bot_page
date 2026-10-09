"""
uploader_youtube.py
-------------------
Handles uploading vertical videos to YouTube Shorts via YouTube Data API v3.
Features:
- Authentication via OAuth2 Refresh Token (zero user interaction required in CI/CD).
- Resumable upload with exponential backoff for high resilience.
- Shorts-optimized metadata (auto #Shorts tag in title/description).
- Dry-run fallback mode when credentials are missing or during testing.
"""

import os
import time
import random
import logging
from typing import Dict, Any, Optional

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    Credentials = None
    build = None
    MediaFileUpload = None
    HttpError = Exception
    GOOGLE_API_AVAILABLE = False

logger = logging.getLogger("YouTubeUploader")


class YouTubeUploader:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        dry_run: bool = False
    ):
        self.client_id = client_id or os.getenv("YT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("YT_CLIENT_SECRET")
        self.refresh_token = refresh_token or os.getenv("YT_REFRESH_TOKEN")
        self.dry_run = dry_run or os.getenv("DRY_RUN", "false").lower() == "true"
        self.privacy_status = os.getenv("YT_PRIVACY_STATUS", "public")

    def _get_authenticated_service(self):
        """Constructs an authorized YouTube Data API service client."""
        if not (self.client_id and self.client_secret and self.refresh_token):
            raise ValueError(
                "Missing YouTube credentials. Please set YT_CLIENT_ID, YT_CLIENT_SECRET, and YT_REFRESH_TOKEN."
            )

        credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
        )
        return build("youtube", "v3", credentials=credentials)

    def upload_short(
        self,
        file_path: str,
        title: str,
        description: str,
        tags: list = None
    ) -> Dict[str, Any]:
        """
        Uploads a vertical video as a YouTube Short.
        Returns: { 'video_id': str, 'url': str, 'status': str }
        """
        logger.info(f"Preparing YouTube Shorts upload for '{title}'...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found at: {file_path}")

        # Ensure #Shorts is present in title and description for YouTube algorithm indexing
        if "#Shorts" not in title and "#shorts" not in title:
            title = f"{title[:88]} #Shorts"
        if "#Shorts" not in description:
            description = f"{description}\n\n#Shorts #Viral #Tech #Trends"

        if tags is None:
            tags = ["Shorts", "Viral", "Trending", "Reels"]
        elif "Shorts" not in tags:
            tags.append("Shorts")

        # Dry-run / mock mode for testing without exhausting API quotas
        if self.dry_run or not (self.client_id and self.client_secret and self.refresh_token):
            logger.warning("[DRY-RUN] Simulating YouTube upload. Real API credentials not provided or dry-run active.")
            simulated_id = f"yt_{int(time.time())}"
            return {
                "video_id": simulated_id,
                "url": f"https://youtube.com/shorts/{simulated_id}",
                "status": "simulated_success",
                "title": title
            }

        youtube = self._get_authenticated_service()

        body = {
            "snippet": {
                "title": title[:100],  # YouTube title limit is 100 characters
                "description": description[:5000],
                "tags": tags,
                "categoryId": "28"  # 28 = Science & Technology
            },
            "status": {
                "privacyStatus": self.privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        # Media upload with 2MB chunksize for reliable resumable upload
        media = MediaFileUpload(
            file_path,
            mimetype="video/mp4",
            chunksize=2 * 1024 * 1024,
            resumable=True
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        logger.info(f"Initiating resumable chunk upload to YouTube...")
        response = None
        retry_count = 0
        max_retries = 5

        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    pct = int(status.progress() * 100)
                    logger.info(f"Upload progress: {pct}%")
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    retry_count += 1
                    if retry_count > max_retries:
                        raise e
                    sleep_time = (2 ** retry_count) + random.uniform(0, 1)
                    logger.warning(f"Server error {e.resp.status}. Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"YouTube HTTP Error: {e}")
                    raise e
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    raise e
                sleep_time = (2 ** retry_count) + random.uniform(0, 1)
                logger.warning(f"Connection error: {e}. Retrying in {sleep_time:.1f}s...")
                time.sleep(sleep_time)

        video_id = response.get("id")
        short_url = f"https://youtube.com/shorts/{video_id}"
        logger.info(f"YouTube Short published successfully! URL: {short_url}")

        return {
            "video_id": video_id,
            "url": short_url,
            "status": "published",
            "title": title
        }
