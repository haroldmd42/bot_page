"""
main.py
-------
Master orchestrator for the Autonomous Social Video Agent.
Integrates:
- Growth Optimizer (feedback loop & viral script generator)
- Video Engine (1080x1920 9:16 vertical video & TTS synthesis)
- YouTube Shorts Uploader (OAuth2 API v3)
- Facebook Reels Uploader (Meta Graph API)
- Analytics Collector (views, likes, comments, monetization stats)
"""

import argparse
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    def load_dotenv():
        pass

# Configure UTF-8 streams on Windows to prevent UnicodeEncodeError with emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure the project root and bot package are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.growth_optimizer import GrowthOptimizer
from bot.video_engine import run_video_generation_sync
from bot.uploader_youtube import YouTubeUploader
from bot.uploader_facebook import FacebookReelsUploader
from bot.analytics_collector import AnalyticsCollector

# Configure rich colored console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AutonomousAgent")


def sync_data_to_dashboard():
    """Syncs data/history.json and data/metrics.json to dashboard/public/data/."""
    src_data_dir = os.path.abspath("data")
    dest_data_dir = os.path.abspath("dashboard/public/data")
    os.makedirs(dest_data_dir, exist_ok=True)

    for filename in ["history.json", "metrics.json"]:
        src_file = os.path.join(src_data_dir, filename)
        dest_file = os.path.join(dest_data_dir, filename)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            logger.info(f"Synced {filename} to dashboard public directory.")


def run_publish_flow(dry_run: bool = False, topic: str = None) -> dict:
    """Executes the full content creation and distribution cycle."""
    logger.info("==================================================")
    logger.info("🚀 STARTING AUTONOMOUS PUBLISHING PIPELINE")
    logger.info("==================================================")

    # Step 1: Growth feedback loop & Script formulation
    logger.info("1/5: Analyzing metrics & selecting high-converting hook...")
    optimizer = GrowthOptimizer()
    script = optimizer.generate_optimized_script(custom_topic=topic)

    logger.info(f"Selected Niche: {script.get('niche')}")
    logger.info(f"Selected Title: {script.get('title')}")
    logger.info(f"Hook: \"{script.get('hook')}\"")

    # Step 2: High definition vertical video rendering
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"short_{timestamp_str}.mp4"
    logger.info(f"2/5: Generating 9:16 vertical video ({video_filename})...")

    video_path = run_video_generation_sync(script, video_filename)
    logger.info(f"Video created at: {video_path}")

    # Step 3: Publish to YouTube Shorts
    logger.info("3/5: Distributing to YouTube Shorts...")
    yt_uploader = YouTubeUploader(dry_run=dry_run)
    yt_result = yt_uploader.upload_short(
        file_path=video_path,
        title=script["title"],
        description=f"{script['hook']}\n\n#Shorts #Viral #Growth",
        tags=script.get("tags", [])
    )

    # Step 4: Publish to Facebook Reels
    logger.info("4/5: Distributing to Facebook Reels...")
    fb_uploader = FacebookReelsUploader(dry_run=dry_run)
    fb_result = fb_uploader.upload_reel(
        file_path=video_path,
        title=script["title"],
        description=script["hook"]
    )

    # Step 5: Update history records
    logger.info("5/5: Recording video in history.json...")
    history_file = "data/history.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    new_video_record = {
        "id": f"vid_{timestamp_str}",
        "title": script["title"],
        "hook": script["hook"],
        "niche": script["niche"],
        "created_at": datetime.now().isoformat() + "Z",
        "duration": 35.0,
        "status": "published",
        "tags": script.get("tags", []),
        "youtube": {
            "video_id": yt_result.get("video_id"),
            "url": yt_result.get("url"),
            "status": yt_result.get("status"),
            "views": 0,
            "likes": 0,
            "comments": 0
        },
        "facebook": {
            "video_id": fb_result.get("video_id"),
            "url": fb_result.get("url"),
            "status": fb_result.get("status"),
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0
        },
        "metrics_summary": {
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_shares": 0,
            "engagement_rate": 0.0
        }
    }

    # Prepend new video so it appears first
    history.insert(0, new_video_record)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    sync_data_to_dashboard()

    logger.info("==================================================")
    logger.info(f"✅ VIDEO PUBLISHED SUCCESSFULLY: {script['title']}")
    logger.info(f"   YouTube: {yt_result.get('url')}")
    logger.info(f"   Facebook: {fb_result.get('url')}")
    logger.info("==================================================")

    return new_video_record


def run_analytics_flow():
    """Gathers latest social metrics and optimizes recommendations."""
    logger.info("==================================================")
    logger.info("📊 GATHERING ANALYTICS & UPDATING GROWTH ENGINE")
    logger.info("==================================================")

    collector = AnalyticsCollector()
    metrics = collector.collect_and_sync()

    # Re-run growth optimizer to generate updated recommendations
    optimizer = GrowthOptimizer()
    perf = optimizer.analyze_performance()

    metrics_file = "data/metrics.json"
    if os.path.exists(metrics_file):
        with open(metrics_file, "r", encoding="utf-8") as f:
            full_metrics = json.load(f)
        full_metrics["optimization_recommendations"] = perf.get("recommendations", [])
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(full_metrics, f, indent=2, ensure_ascii=False)

    sync_data_to_dashboard()

    logger.info(f"Total Views: {metrics['overview']['total_views']:,}")
    logger.info(f"Total Likes: {metrics['overview']['total_likes']:,}")
    logger.info(f"Avg Engagement: {metrics['overview']['average_engagement_rate']}%")
    logger.info("Analytics update complete!")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Autonomous Social Video Growth Agent")
    parser.add_argument(
        "--mode",
        choices=["publish", "analytics", "full"],
        default="publish",
        help="Pipeline execution mode: publish, analytics, or full"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate video creation and API publishing without credentials"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Custom topic or theme override for the video script"
    )

    args = parser.parse_args()

    if args.mode == "publish":
        run_publish_flow(dry_run=args.dry_run, topic=args.topic)
    elif args.mode == "analytics":
        run_analytics_flow()
    elif args.mode == "full":
        run_publish_flow(dry_run=args.dry_run, topic=args.topic)
        time.sleep(2)
        run_analytics_flow()


if __name__ == "__main__":
    main()
