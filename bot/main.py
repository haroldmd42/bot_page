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
from bot.funny_clip_manager import FunnyClipManager
from bot.video_engine import run_funny_video_generation_sync, run_video_generation_sync
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
    """Syncs data/history.json and data/metrics.json to dashboard/public/data/ and dashboard/dist/data/."""
    src_data_dir = os.path.abspath("data")
    dest_public_dir = os.path.abspath("dashboard/public/data")
    dest_dist_dir = os.path.abspath("dashboard/dist/data")
    os.makedirs(dest_public_dir, exist_ok=True)
    os.makedirs(dest_dist_dir, exist_ok=True)

    for filename in ["history.json", "metrics.json"]:
        src_file = os.path.join(src_data_dir, filename)
        if os.path.exists(src_file):
            shutil.copy2(src_file, os.path.join(dest_public_dir, filename))
            shutil.copy2(src_file, os.path.join(dest_dist_dir, filename))
            logger.info(f"Synced {filename} to dashboard public and dist directories.")



def run_publish_flow(dry_run: bool = False, topic: str = None, count: int = 3) -> list:
    """
    Executes content creation and distribution for distinct funny videos (default 3 per run).
    Each video uses a different funny clip, unique comedic hook, and distinct voiceover.
    """
    logger.info("==================================================")
    logger.info(f"🚀 INICIANDO PIPELINE DE COMEDIA: {count} VIDEOS VIRALES")
    logger.info("==================================================")

    clip_manager = FunnyClipManager()
    optimizer = GrowthOptimizer()
    scripts = optimizer.generate_batch_scripts(count=count, custom_topic=topic)

    history_file = "data/history.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    published_records = []

    for idx, script in enumerate(scripts):
        logger.info(f"\n🎬 ──────────────────────────────────────────────")
        logger.info(f"PROCESANDO VIDEO {idx + 1}/{count}: {script['title']}")
        logger.info(f"Hook: \"{script['hook']}\"")
        logger.info(f"Categoría: {script['niche']}")
        logger.info(f"────────────────────────────────────────────────")

        # Step 1: Obtain a fresh, non-repeated funny clip
        clip_data = clip_manager.get_next_funny_clip()
        clip_title = clip_data.get('title', 'Clip')
        clip_id = clip_data.get('id', 'clip')
        logger.info(f"1/4: Clip de comedia asignado: '{clip_title}' (ID: {clip_id}, Fuente: {clip_data.get('source', 'auto')})")
        clip_path = clip_manager.download_clip(clip_data)

        # Step 2: Render funny 9:16 vertical video with meme overlays and voiceover
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"funny_{timestamp_str}_{idx + 1}.mp4"
        logger.info(f"2/4: Renderizando Short cómico 9:16 con clip real ({video_filename})...")
        video_path = run_funny_video_generation_sync(script, clip_path, video_filename)

        # Step 3: Distribute to YouTube Shorts
        logger.info("3/4: Publicando en YouTube Shorts...")
        try:
            yt_uploader = YouTubeUploader(dry_run=dry_run)
            yt_result = yt_uploader.upload_short(
                file_path=video_path,
                title=script["title"],
                description=f"{script['hook']}\n\n{script['voiceover']}\n\n#Shorts #Humor #Comedia #Risas #Memes #Viral",
                tags=script.get("tags", ["Shorts", "Humor", "Comedia", "Risas"])
            )
        except Exception as e:
            logger.error(f"Error inesperado al subir a YouTube: {e}")
            yt_result = {"status": "error", "error": str(e), "url": None, "video_id": None}

        # Step 4: Distribute to Facebook Reels
        logger.info("4/4: Publicando en Facebook Reels...")
        try:
            fb_uploader = FacebookReelsUploader(dry_run=dry_run)
            fb_result = fb_uploader.upload_reel(
                file_path=video_path,
                title=script["title"],
                description=f"{script['hook']}\n\n{script['cta']}"
            )
        except Exception as e:
            logger.error(f"Error inesperado al subir a Facebook Reels: {e}")
            fb_result = {"status": "error", "error": str(e), "url": None, "video_id": None}

        yt_ok = yt_result.get("status") in ["published", "simulated"]
        fb_ok = fb_result.get("status") in ["published", "simulated"]
        record_status = "published" if (yt_ok or fb_ok) else "limit_reached"

        new_video_record = {
            "id": f"vid_funny_{timestamp_str}_{idx + 1}",
            "title": script["title"],
            "hook": script["hook"],
            "niche": script["niche"],
            "created_at": datetime.now().isoformat() + "Z",
            "duration": 20.0,
            "status": record_status,
            "tags": script.get("tags", []),
            "youtube": {
                "video_id": yt_result.get("video_id"),
                "url": yt_result.get("url"),
                "status": yt_result.get("status"),
                "error": yt_result.get("error"),
                "views": 0,
                "likes": 0,
                "comments": 0
            },
            "facebook": {
                "video_id": fb_result.get("video_id"),
                "url": fb_result.get("url"),
                "status": fb_result.get("status"),
                "error": fb_result.get("error"),
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

        if not dry_run:
            # Add to beginning of history
            history.insert(0, new_video_record)
        published_records.append(new_video_record)

        logger.info(f"✅ Video {idx + 1}/{count} procesado. YouTube: {yt_result.get('status')} | Facebook: {fb_result.get('status')}")


        # Rate-limiting pause between uploads
        if idx < count - 1 and not dry_run:
            logger.info("Pausando 15 segundos antes del siguiente video...")
            time.sleep(15)

    if not dry_run:
        # Save all newly created records
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        sync_data_to_dashboard()
    else:
        logger.info("[DRY-RUN] Historial real preservado intacto (sin mocks).")

    logger.info("==================================================")
    logger.info(f"🎉 BATCH COMPLETADO: {len(published_records)} VIDEOS VIRALES PROCESADOS")
    logger.info("==================================================")
    return published_records


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
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Cantidad de videos distintos a generar y publicar (default: 3)"
    )

    args = parser.parse_args()

    if args.mode == "publish":
        run_publish_flow(dry_run=args.dry_run, topic=args.topic, count=args.count)
    elif args.mode == "analytics":
        run_analytics_flow()
    elif args.mode == "full":
        run_publish_flow(dry_run=args.dry_run, topic=args.topic, count=args.count)
        time.sleep(2)
        run_analytics_flow()


if __name__ == "__main__":
    main()
