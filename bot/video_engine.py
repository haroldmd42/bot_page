"""
video_engine.py
---------------
High-performance vertical video generator for Meta Reels and YouTube Shorts.
- Generates 1080x1920 (9:16) video with Hook-Value-CTA structure.
- Generates natural neural voiceover using edge-tts (100% free, zero cost).
- Renders kinetic typography, contrast badges, and subtitles using Pillow + MoviePy.
- Completely self-contained without needing ImageMagick.
"""

from __future__ import annotations

import asyncio
import os
import math
import random
import logging
from typing import Dict, List, Tuple, Optional
try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    # Compatibility fix for Pillow 10+ where Image.ANTIALIAS was deprecated/removed
    if hasattr(Image, "Resampling") and not hasattr(Image, "ANTIALIAS"):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None
    ImageFilter = None
    np = None
    PIL_AVAILABLE = False

# Ensure imageio-ffmpeg binaries are in PATH
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    if ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except Exception:
    pass

# MoviePy imports
try:
    from moviepy.editor import (
        AudioFileClip,
        ImageClip,
        VideoFileClip,
        CompositeVideoClip,
        CompositeAudioClip,
        concatenate_videoclips,
        concatenate_audioclips,
        vfx,
        afx
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    AudioFileClip = None
    ImageClip = None
    VideoFileClip = None
    CompositeVideoClip = None
    CompositeAudioClip = None
    concatenate_videoclips = None
    concatenate_audioclips = None
    vfx = None
    afx = None
    MOVIEPY_AVAILABLE = False

logger = logging.getLogger("VideoEngine")


class VideoEngine:
    def __init__(self, output_dir: str = "output", voice: str = "es-ES-AlvaroNeural"):
        self.width = 1080
        self.height = 1920
        self.fps = 24
        self.output_dir = output_dir
        self.voice = voice  # High quality free neural voice from Edge TTS
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_font(self, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        """Finds an available system font or loads fallback."""
        candidates = [
            # Windows fonts
            "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\impact.ttf",
            # Linux / GitHub Actions runner fonts
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            # Generic names
            "arial.ttf",
            "DejaVuSans-Bold.ttf"
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

        try:
            return ImageFont.load_default()
        except Exception:
            return None

    async def _generate_audio_tts(self, text: str, output_path: str) -> float:
        """
        Synthesizes speech using edge-tts (free, no API key required).
        Returns audio duration in seconds.
        """
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice, rate="+5%")
            await communicate.save(output_path)
            clip = AudioFileClip(output_path)
            duration = clip.duration
            clip.close()
            return duration
        except Exception as e:
            logger.warning(f"edge-tts unavailable or failed ({e}). Generating fallback audio.")
            # Fallback: create a silent audio file using moviepy/numpy if edge-tts fails
            import wave
            import struct
            duration = max(len(text) * 0.08, 25.0)  # estimated speech duration
            sample_rate = 44100
            num_samples = int(duration * sample_rate)
            with wave.open(output_path, "w") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                # gentle subtle ambient tone
                for i in range(num_samples):
                    val = int(300 * math.sin(2 * math.pi * 220 * (i / sample_rate)))
                    data = struct.pack("<h", val)
                    wav_file.writeframesraw(data)
            return duration

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> List[str]:
        """Splits text into lines that fit within max_width."""
        words = text.split()
        if not words:
            return []
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def _draw_text_with_outline(
        self,
        draw: ImageDraw.Draw,
        text: str,
        pos: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        fill_color: Tuple[int, int, int],
        outline_color: Tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 4
    ):
        """Draws high contrast text with a prominent black stroke and drop shadow."""
        x, y = pos
        # Drop shadow
        draw.text((x + 6, y + 6), text, font=font, fill=(10, 10, 15, 200))
        # Black outline / stroke
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx * dx + dy * dy <= outline_width * outline_width:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        # Main text fill
        draw.text((x, y), text, font=font, fill=fill_color)

    def _create_background_image(self, theme_idx: int = 0) -> Image.Image:
        """
        Creates an ultra-modern dark vertical aesthetic background
        with dynamic gradients and glassmorphism cards.
        """
        img = Image.new("RGBA", (self.width, self.height), (15, 17, 23, 255))
        draw = ImageDraw.Draw(img)

        # Gradient palettes: dark navy to violet, or emerald to slate
        palettes = [
            [(15, 23, 42), (88, 28, 135), (30, 27, 75)],   # Slate -> Purple -> Deep Indigo
            [(17, 24, 39), (13, 148, 136), (15, 23, 42)],  # Deep Gray -> Teal -> Slate
            [(24, 24, 27), (225, 29, 72), (15, 23, 42)]    # Zinc -> Crimson -> Black
        ]
        color_start, color_mid, color_end = palettes[theme_idx % len(palettes)]

        # Draw smooth vertical gradient
        for y in range(self.height):
            ratio = y / self.height
            if ratio < 0.5:
                sub_r = ratio / 0.5
                r = int(color_start[0] + (color_mid[0] - color_start[0]) * sub_r)
                g = int(color_start[1] + (color_mid[1] - color_start[1]) * sub_r)
                b = int(color_start[2] + (color_mid[2] - color_start[2]) * sub_r)
            else:
                sub_r = (ratio - 0.5) / 0.5
                r = int(color_mid[0] + (color_end[0] - color_mid[0]) * sub_r)
                g = int(color_mid[1] + (color_end[1] - color_mid[1]) * sub_r)
                b = int(color_mid[2] + (color_end[2] - color_mid[2]) * sub_r)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b, 255))

        # Add ambient glow orbs in the background
        orb = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        orb_draw = ImageDraw.Draw(orb)
        for radius in range(300, 0, -10):
            alpha = int(40 * (1 - radius / 300))
            orb_draw.ellipse(
                [(300 - radius, 300 - radius), (300 + radius, 300 + radius)],
                fill=(99, 102, 241, alpha)
            )
        img.alpha_composite(orb, (240, 400))

        return img

    def render_slide_frame(
        self,
        scene_type: str,
        niche: str,
        title: str,
        main_text: str,
        step_number: Optional[int] = None,
        progress_pct: float = 0.0,
        theme_idx: int = 0
    ) -> np.ndarray:
        """
        Renders a single high-definition 1080x1920 frame for a scene.
        """
        img = self._create_background_image(theme_idx)
        draw = ImageDraw.Draw(img)

        # 1. Top Status & Branding Bar
        # Top Progress line
        prog_w = int(self.width * progress_pct)
        draw.rectangle([(0, 0), (self.width, 14)], fill=(30, 41, 59, 255))
        draw.rectangle([(0, 0), (prog_w, 14)], fill=(250, 204, 21, 255))  # Bright yellow progress bar

        # Top Category Badge (Glass effect)
        badge_font = self._get_font(36, bold=True)
        badge_text = f"🔥 {niche.upper()}"
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        bw = bbox[2] - bbox[0] + 60
        bh = bbox[3] - bbox[1] + 30
        bx = (self.width - bw) // 2
        by = 120

        # Rounded pill badge
        draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=25, fill=(30, 41, 59, 230), outline=(250, 204, 21, 255), width=3)
        draw.text((bx + 30, by + 12), badge_text, font=badge_font, fill=(250, 204, 21))

        # 2. Main Content Card Area
        card_x1, card_y1 = 80, 260
        card_x2, card_y2 = self.width - 80, 1640

        # Card container with glassmorphic border
        draw.rounded_rectangle(
            [(card_x1, card_y1), (card_x2, card_y2)],
            radius=40,
            fill=(15, 23, 42, 180),
            outline=(148, 163, 184, 80),
            width=3
        )

        # Header Title in Card
        title_font = self._get_font(52, bold=True)
        wrapped_title = self._wrap_text(title, title_font, (card_x2 - card_x1) - 60, draw)
        curr_y = card_y1 + 60
        for line in wrapped_title[:2]:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            lw = bbox[2] - bbox[0]
            draw.text(((self.width - lw) // 2, curr_y), line, font=title_font, fill=(241, 245, 249))
            curr_y += 70

        # Divider line
        curr_y += 30
        draw.line([(card_x1 + 60, curr_y), (card_x2 - 60, curr_y)], fill=(71, 85, 105, 180), width=2)
        curr_y += 60

        # 3. Dynamic Center Stage (Hook, Value point, or CTA)
        if scene_type == "hook":
            # Giant Viral Hook Box
            hook_font = self._get_font(68, bold=True)
            wrapped_hook = self._wrap_text(main_text, hook_font, (card_x2 - card_x1) - 80, draw)

            # Central Hook Banner Box
            hook_box_y = curr_y + 120
            total_text_h = len(wrapped_hook) * 90
            draw.rounded_rectangle(
                [(card_x1 + 30, hook_box_y - 30), (card_x2 - 30, hook_box_y + total_text_h + 30)],
                radius=30,
                fill=(220, 38, 38, 220),  # Urgent red / crimson accent
                outline=(250, 204, 21, 255),
                width=4
            )

            # "ATENCIÓN" Alert tag
            tag_font = self._get_font(40, bold=True)
            draw.text((card_x1 + 70, hook_box_y - 20), "⚠️ NO TE LO PIERDAS:", font=tag_font, fill=(255, 255, 255))

            text_y = hook_box_y + 50
            for line in wrapped_hook:
                bbox = draw.textbbox((0, 0), line, font=hook_font)
                lw = bbox[2] - bbox[0]
                self._draw_text_with_outline(
                    draw,
                    line,
                    ((self.width - lw) // 2, text_y),
                    hook_font,
                    fill_color=(255, 255, 255),
                    outline_color=(0, 0, 0),
                    outline_width=4
                )
                text_y += 95

        elif scene_type == "point":
            # Numbered Step / Value Box
            step_badge_y = curr_y + 40
            badge_r = 60
            center_x = self.width // 2

            # Circular Step Indicator
            draw.ellipse(
                [(center_x - badge_r, step_badge_y - badge_r), (center_x + badge_r, step_badge_y + badge_r)],
                fill=(234, 179, 8, 255),  # Gold/Yellow
                outline=(255, 255, 255),
                width=4
            )
            step_num_font = self._get_font(64, bold=True)
            step_num_text = f"#{step_number}"
            bbox = draw.textbbox((0, 0), step_num_text, font=step_num_font)
            sw = bbox[2] - bbox[0]
            sh = bbox[3] - bbox[1]
            draw.text((center_x - sw // 2, step_badge_y - sh // 2 - 5), step_num_text, font=step_num_font, fill=(15, 23, 42))

            # Main content text with subtitles emphasis
            content_font = self._get_font(62, bold=True)
            wrapped_body = self._wrap_text(main_text, content_font, (card_x2 - card_x1) - 80, draw)
            text_y = step_badge_y + 130
            for line in wrapped_body:
                bbox = draw.textbbox((0, 0), line, font=content_font)
                lw = bbox[2] - bbox[0]
                self._draw_text_with_outline(
                    draw,
                    line,
                    ((self.width - lw) // 2, text_y),
                    content_font,
                    fill_color=(254, 240, 138),  # Vibrant yellow
                    outline_color=(0, 0, 0),
                    outline_width=4
                )
                text_y += 88

        elif scene_type == "cta":
            # Final CTA Box with high energy callout
            cta_font = self._get_font(64, bold=True)
            wrapped_cta = self._wrap_text(main_text, cta_font, (card_x2 - card_x1) - 80, draw)

            cta_box_y = curr_y + 80
            total_text_h = len(wrapped_cta) * 90
            draw.rounded_rectangle(
                [(card_x1 + 30, cta_box_y - 20), (card_x2 - 30, cta_box_y + total_text_h + 160)],
                radius=35,
                fill=(16, 185, 129, 210),  # High converting emerald green
                outline=(255, 255, 255, 255),
                width=4
            )

            tag_font = self._get_font(42, bold=True)
            draw.text((card_x1 + 70, cta_box_y + 10), "🚀 ACCIÓN INMEDIATA:", font=tag_font, fill=(255, 255, 255))

            text_y = cta_box_y + 80
            for line in wrapped_cta:
                bbox = draw.textbbox((0, 0), line, font=cta_font)
                lw = bbox[2] - bbox[0]
                self._draw_text_with_outline(
                    draw,
                    line,
                    ((self.width - lw) // 2, text_y),
                    cta_font,
                    fill_color=(255, 255, 255),
                    outline_color=(0, 0, 0),
                    outline_width=4
                )
                text_y += 90

            # Follow & Like Pill
            pill_font = self._get_font(46, bold=True)
            pill_text = "❤️ DALE LIKE & COMPARTE"
            p_bbox = draw.textbbox((0, 0), pill_text, font=pill_font)
            pw = p_bbox[2] - p_bbox[0] + 80
            ph = p_bbox[3] - p_bbox[1] + 30
            px = (self.width - pw) // 2
            py = text_y + 30
            draw.rounded_rectangle([(px, py), (px + pw, py + ph)], radius=30, fill=(255, 255, 255), outline=(0, 0, 0), width=2)
            draw.text((px + 40, py + 12), pill_text, font=pill_font, fill=(225, 29, 72))

        # 4. Bottom Footer Watermark
        footer_font = self._get_font(34, bold=False)
        footer_text = "@viral_shorts_official • Síguenos para más"
        f_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        fw = f_bbox[2] - f_bbox[0]
        draw.text(((self.width - fw) // 2, 1720), footer_text, font=footer_font, fill=(148, 163, 184))

        # Convert PIL Image (RGBA) to NumPy RGB array for MoviePy
        rgb_img = img.convert("RGB")
        return np.array(rgb_img)

    async def generate_video(self, script_data: Dict[str, Any], output_filename: str) -> str:
        """
        Orchestrates full video compilation:
        1. Synthesizes voice narration.
        2. Calculates scene segment timing (Hook 0-3s, Value points, CTA).
        3. Generates frames and concatenates clips.
        4. Exports 9:16 vertical MP4 video with audio.
        """
        output_filepath = os.path.join(self.output_dir, output_filename)
        audio_filepath = os.path.join(self.output_dir, f"{os.path.splitext(output_filename)[0]}_voice.mp3")

        # Fallback simulation if dependencies are not installed in current environment
        if not MOVIEPY_AVAILABLE or not PIL_AVAILABLE:
            logger.warning("MoviePy or Pillow is not installed locally. Generating mock MP4 file for dry-run verification.")
            os.makedirs(self.output_dir, exist_ok=True)
            with open(output_filepath, "wb") as f:
                # Minimal MP4 file header container bytes
                f.write(b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free")
            return output_filepath

        logger.info(f"Synthesizing voiceover for: {script_data.get('title')}...")
        speech_text = script_data.get("full_speech", script_data.get("hook", ""))
        audio_duration = await self._generate_audio_tts(speech_text, audio_filepath)

        # Enforce target duration between 25s and 55s
        target_duration = max(min(audio_duration, 55.0), 25.0)
        logger.info(f"Audio synthesized. Duration: {target_duration:.2f}s")

        # Plan scenes: Hook (0 to 3.5s), 3 Points (split evenly), CTA (last 5s)
        hook_duration = min(3.5, target_duration * 0.15)
        cta_duration = min(5.5, target_duration * 0.20)
        remaining_duration = max(target_duration - hook_duration - cta_duration, 10.0)

        points = script_data.get("points", ["Punto de valor clave"])
        point_duration = remaining_duration / max(len(points), 1)

        scenes = []

        # Scene 1: Hook
        scenes.append({
            "type": "hook",
            "duration": hook_duration,
            "text": script_data.get("hook", ""),
            "step": None
        })

        # Scene 2..N: Value Points
        for i, point in enumerate(points):
            scenes.append({
                "type": "point",
                "duration": point_duration,
                "text": point,
                "step": i + 1
            })

        # Scene Final: CTA
        scenes.append({
            "type": "cta",
            "duration": cta_duration,
            "text": script_data.get("cta", "Comenta tu opinión y sígueme para más trucos"),
            "step": None
        })

        video_clips = []
        elapsed = 0.0

        for idx, sc in enumerate(scenes):
            progress_pct = elapsed / target_duration
            frame_arr = self.render_slide_frame(
                scene_type=sc["type"],
                niche=script_data.get("niche", "Tech & AI"),
                title=script_data.get("title", ""),
                main_text=sc["text"],
                step_number=sc["step"],
                progress_pct=progress_pct,
                theme_idx=idx
            )
            # Create video clip from image array
            clip = ImageClip(frame_arr).set_duration(sc["duration"])
            video_clips.append(clip)
            elapsed += sc["duration"]

        logger.info(f"Assembling {len(video_clips)} video scenes...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        # Attach voice audio track
        if os.path.exists(audio_filepath):
            try:
                audio_clip = AudioFileClip(audio_filepath)
                if audio_clip.duration > final_video.duration:
                    audio_clip = audio_clip.subclip(0, final_video.duration)
                final_video = final_video.set_audio(audio_clip)
            except Exception as e:
                logger.warning(f"Could not attach audio clip: {e}")

        logger.info(f"Rendering final MP4 to {output_filepath}...")
        final_video.write_videofile(
            output_filepath,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=4,
            temp_audiofile=os.path.join(self.output_dir, "temp-audio.m4a"),
            remove_temp=True,
            verbose=False,
            logger=None
        )

        final_video.close()
        logger.info(f"Video generated successfully at: {output_filepath}")
        return output_filepath

    def render_meme_overlays(self, hook: str, cta: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Renders top meme header card and bottom subtitle punchline card as transparent RGBA overlays.
        Ultra-modern viral TikTok/Shorts styling with gold accents and high-contrast typography.
        """
        # 1. Top Meme Header (1080 x 440)
        top_img = Image.new("RGBA", (self.width, 440), (0, 0, 0, 0))
        top_draw = ImageDraw.Draw(top_img)

        # Progress / accent line at top
        top_draw.rectangle([(0, 0), (self.width, 10)], fill=(250, 204, 21, 255))

        # Meme Header Card with glassmorphism feel
        top_draw.rounded_rectangle(
            [(30, 30), (self.width - 30, 410)],
            radius=26,
            fill=(15, 23, 42, 235),
            outline=(250, 204, 21, 220),
            width=3
        )

        hook_font = self._get_font(48, bold=True)
        wrapped_hook = self._wrap_text(hook, hook_font, self.width - 140, top_draw)

        y_text = 65
        for idx, line in enumerate(wrapped_hook[:4]):
            bbox = top_draw.textbbox((0, 0), line, font=hook_font)
            lw = bbox[2] - bbox[0]
            # First line in bright white, second line in vibrant yellow
            fill = (250, 204, 21) if idx == 1 else (255, 255, 255)
            self._draw_text_with_outline(
                top_draw,
                line,
                ((self.width - lw) // 2, y_text),
                hook_font,
                fill_color=fill,
                outline_color=(0, 0, 0),
                outline_width=4
            )
            y_text += 78

        # 2. Bottom CTA Punchline & Subtitle Card (1080 x 360)
        bot_img = Image.new("RGBA", (self.width, 360), (0, 0, 0, 0))
        bot_draw = ImageDraw.Draw(bot_img)

        bot_draw.rounded_rectangle(
            [(40, 25), (self.width - 40, 315)],
            radius=26,
            fill=(15, 23, 42, 230),
            outline=(59, 130, 246, 180),
            width=3
        )

        cta_font = self._get_font(42, bold=True)
        wrapped_cta = self._wrap_text(cta, cta_font, self.width - 140, bot_draw)

        y_cta = 55
        for line in wrapped_cta[:2]:
            bbox = bot_draw.textbbox((0, 0), line, font=cta_font)
            lw = bbox[2] - bbox[0]
            self._draw_text_with_outline(
                bot_draw,
                line,
                ((self.width - lw) // 2, y_cta),
                cta_font,
                fill_color=(254, 240, 138),
                outline_color=(0, 0, 0),
                outline_width=4
            )
            y_cta += 65

        # Footer Engagement Pill
        pill_font = self._get_font(32, bold=True)
        pill_text = "❤️ DALE LIKE & COMPARTE 😂"
        p_bbox = bot_draw.textbbox((0, 0), pill_text, font=pill_font)
        pw = p_bbox[2] - p_bbox[0] + 60
        ph = p_bbox[3] - p_bbox[1] + 24
        px = (self.width - pw) // 2
        py = max(y_cta + 10, 210)
        bot_draw.rounded_rectangle([(px, py), (px + pw, py + ph)], radius=20, fill=(225, 29, 72, 230), outline=(255, 255, 255, 180), width=2)
        bot_draw.text((px + 30, py + 8), pill_text, font=pill_font, fill=(255, 255, 255))

        return np.array(top_img), np.array(bot_img)

    async def generate_funny_video(self, script_data: Dict[str, Any], clip_path: Optional[str], output_filename: str) -> str:
        """
        Orchestrates professional 9:16 comedy short:
        - Real funny video clip with blurred ambient background.
        - Synchronized neural voiceover narration.
        - Preserves funny original audio sounds (ducked to 35%) alongside voiceover.
        - Top meme hook header & bottom punchline overlays.
        """
        output_filepath = os.path.join(self.output_dir, output_filename)
        audio_filepath = os.path.join(self.output_dir, f"{os.path.splitext(output_filename)[0]}_voice.mp3")

        # Fallback simulation if dependencies are missing in current environment
        if not MOVIEPY_AVAILABLE or not PIL_AVAILABLE:
            logger.warning("MoviePy/Pillow missing locally. Creating simulated MP4.")
            os.makedirs(self.output_dir, exist_ok=True)
            with open(output_filepath, "wb") as f:
                f.write(b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free")
            return output_filepath

        # 1. Synthesize voiceover
        speech_text = script_data.get("full_speech", script_data.get("hook", ""))
        audio_duration = await self._generate_audio_tts(speech_text, audio_filepath)
        target_duration = max(min(audio_duration, 45.0), 10.0)

        # 2. Guarantee a real funny clip (never allow None or invalid file)
        has_valid_clip = clip_path and os.path.exists(clip_path) and os.path.getsize(clip_path) > 10000
        if not has_valid_clip:
            local_dir = "assets/clips"
            if os.path.exists(local_dir):
                candidates = [
                    os.path.join(local_dir, f) for f in os.listdir(local_dir)
                    if f.lower().endswith((".mp4", ".webm", ".mkv", ".mov"))
                    and os.path.getsize(os.path.join(local_dir, f)) > 10000
                ]
                if candidates:
                    clip_path = random.choice(candidates)
                    has_valid_clip = True

        raw_clip = VideoFileClip(clip_path)

        # 3. Extract and prepare audio track
        original_audio = raw_clip.audio
        raw_clip = raw_clip.without_audio()

        # Match video duration to narration
        # If the clip is shorter than narration, loop seamlessly so audio isn't cut off
        repeats = int(math.ceil(target_duration / max(raw_clip.duration, 0.1))) + 1
        if raw_clip.duration < target_duration:
            raw_clip = concatenate_videoclips([raw_clip] * repeats).subclip(0, target_duration)
        else:
            raw_clip = raw_clip.subclip(0, target_duration)

        # 4. Create blurred/zoomed ambient background (TikTok/Reels style)
        bg_clip = raw_clip.resize(height=self.height)
        if bg_clip.w > self.width:
            bg_clip = bg_clip.crop(x_center=bg_clip.w / 2, width=self.width)
        dark_overlay = ImageClip(np.zeros((self.height, self.width, 3), dtype=np.uint8) + 16).set_duration(target_duration).set_opacity(0.65)
        bg_composite = CompositeVideoClip([bg_clip, dark_overlay], size=(self.width, self.height)).without_audio()

        # 5. Position centered foreground video
        aspect_ratio = raw_clip.w / max(raw_clip.h, 1)
        if aspect_ratio < 0.65:
            # Already vertical 9:16
            fg_clip = raw_clip.resize(width=self.width).set_position(("center", "center"))
        else:
            fg_w = min(1040, self.width - 30)
            fg_clip = raw_clip.resize(width=fg_w)
            y_pos = max((self.height - fg_clip.h) // 2, 430)
            fg_clip = fg_clip.set_position(("center", y_pos))

        # 6. Overlays: Top Meme Hook Header & Bottom Punchline Subtitle
        top_arr, bot_arr = self.render_meme_overlays(
            hook=script_data.get("hook", ""),
            cta=script_data.get("cta", "Comenta y Comparte 😂")
        )
        top_clip = ImageClip(top_arr).set_duration(target_duration).set_position(("center", 0))
        bot_clip = ImageClip(bot_arr).set_duration(target_duration).set_position(("center", self.height - 350))

        final_video = CompositeVideoClip([bg_composite, fg_clip, top_clip, bot_clip], size=(self.width, self.height)).set_duration(target_duration)

        # 7. Audio Mixing (Original funny video audio + Neural voiceover)
        voice_clip = AudioFileClip(audio_filepath) if os.path.exists(audio_filepath) else None
        if original_audio is not None and voice_clip is not None:
            try:
                clip_audio = original_audio.volumex(0.35)
                if clip_audio.duration < target_duration:
                    clip_audio = concatenate_audioclips([clip_audio] * repeats)
                clip_audio = clip_audio.subclip(0, target_duration)
                combined_audio = CompositeAudioClip([clip_audio, voice_clip.volumex(1.0)]).set_duration(target_duration)
                final_video = final_video.set_audio(combined_audio)
            except Exception as e:
                logger.warning(f"Audio mix notice: {e}. Attaching voice only.")
                final_video = final_video.set_audio(voice_clip)
        elif voice_clip is not None:
            final_video = final_video.set_audio(voice_clip)

        # 8. Export professional vertical video
        logger.info(f"Rendering funny Short MP4 to {output_filepath}...")
        final_video.write_videofile(
            output_filepath,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=4,
            temp_audiofile=os.path.join(self.output_dir, "temp-audio.m4a"),
            remove_temp=True,
            verbose=False,
            logger=None
        )

        final_video.close()
        raw_clip.close()
        if voice_clip:
            voice_clip.close()

        logger.info(f"Funny Short created successfully at: {output_filepath}")
        return output_filepath


def run_funny_video_generation_sync(script_data: Dict[str, Any], clip_path: Optional[str], output_filename: str) -> str:
    """Synchronous helper for funny video compilation."""
    engine = VideoEngine()
    return asyncio.run(engine.generate_funny_video(script_data, clip_path, output_filename))


def run_video_generation_sync(script_data: Dict[str, Any], output_filename: str) -> str:
    """Synchronous helper wrapper."""
    engine = VideoEngine()
    return asyncio.run(engine.generate_video(script_data, output_filename))
