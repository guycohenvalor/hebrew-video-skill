# -*- coding: utf-8 -*-
"""
Studio Record 60 FPS - High-Conversion Screen Studio Automation Engine
Part of the hebrew-video skill.
Records web applications inside a Mac/Chrome studio shell with smooth cubic Bezier
virtual mouse cursor, click ripple animations, keystroke HUD badges, and dynamic camera
zoom/pan at broadcast-grade 60 FPS.
"""

import os
import sys
import time
import json
import shutil
import argparse
import subprocess
import pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent.resolve()
SKILL_ROOT = HERE.parent
DEFAULT_TEMPLATE = SKILL_ROOT / "templates" / "studio_recorder.html"

class StudioRecorder:
    def __init__(self, template_path=None, viewport=(1920, 1200), fps=60, crf=17):
        self.template_path = pathlib.Path(template_path or DEFAULT_TEMPLATE).resolve()
        self.width, self.height = viewport
        self.fps = fps
        self.crf = crf
        self.temp_dir = HERE / "temp_rec"
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self, app_url="about:blank", tab_title="הדגמת מערכת חיה", host="http://localhost:3000", path="/"):
        """Launches headless Chromium and initializes the studio template."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=['--enable-features=VaapiVideoDecoder', '--disable-gpu-vsync', '--no-sandbox']
        )
        self.context = self.browser.new_context(
            record_video_dir=str(self.temp_dir),
            viewport={'width': self.width, 'height': self.height},
            record_video_size={'width': self.width, 'height': self.height}
        )
        self.page = self.context.new_page()

        # Load studio template
        self.page.goto(self.template_path.as_uri())
        self.page.wait_for_load_state('networkidle')

        # Configure tab title, address bar host, and iframe target URL
        self.page.evaluate("""
            config => window.studioConfigure(config)
        """, {
            "title": tab_title,
            "host": host,
            "path": path,
            "url": app_url
        })
        time.sleep(1.0)
        return self

    @property
    def frame(self):
        """Returns the frame locator for the embedded web application."""
        return self.page.frame_locator('#app-frame')

    def move_cursor(self, x, y, duration_ms=800):
        """Smoothly glides the virtual cursor using ease-out cubic animation."""
        self.page.evaluate(f"window.studioMoveCursor({x}, {y}, {duration_ms})")
        self.page.wait_for_timeout(duration_ms + 80)

    def click(self, x=None, y=None, trigger_ripple=True, settle_ms=250):
        """Moves cursor if coords given, triggers tactile ripple, and holds briefly."""
        if x is not None and y is not None:
            self.move_cursor(x, y)
        if trigger_ripple:
            self.page.evaluate("window.studioClick()")
        self.page.wait_for_timeout(settle_ms)

    def show_hud(self, text, duration_ms=1200):
        """Displays a Mac-style floating keystroke HUD pill."""
        self.page.evaluate(f"window.studioShowHud({json.dumps(text)}, {duration_ms})")
        self.page.wait_for_timeout(300)

    def set_camera(self, scale, origin_x=960, origin_y=600, duration_ms=1200):
        """Dynamically zooms and pans the camera stage (1.0x to 1.5x)."""
        self.page.evaluate(f"window.studioSetCamera({scale}, {origin_x}, {origin_y}, {duration_ms})")
        self.page.wait_for_timeout(duration_ms + 100)

    def reset_camera(self, duration_ms=1200):
        """Smoothly resets camera to 1.0x full desktop overview."""
        self.page.evaluate(f"window.studioResetCamera({duration_ms})")
        self.page.wait_for_timeout(duration_ms + 100)

    def scroll_app(self, delta_y):
        """Smoothly scrolls the inner application window."""
        self.page.evaluate(f"window.scrollIframe({delta_y})")
        self.page.wait_for_timeout(400)

    def type_text(self, selector, text, delay_ms=65):
        """Types text with natural human keystroke cadences."""
        locator = self.frame.locator(selector)
        locator.click()
        locator.press_sequentially(text, delay=delay_ms)
        self.page.wait_for_timeout(600)

    def hold(self, seconds):
        """Holds current state steady."""
        self.page.wait_for_timeout(int(seconds * 1000))

    def stop_and_encode(self, output_mp4):
        """Closes Playwright and transcodes captured WebM to 60 FPS master MP4."""
        self.context.close()
        self.browser.close()
        self.playwright.stop()

        webm_files = list(self.temp_dir.glob("*.webm"))
        if not webm_files:
            raise RuntimeError("No WebM screencast file was produced by Playwright!")

        raw_webm = str(webm_files[0])
        out_path = pathlib.Path(output_mp4).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            'ffmpeg', '-y',
            '-i', raw_webm,
            '-filter:v', f'framerate=fps={self.fps}:interp_start=0:interp_end=255',
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', str(self.crf),
            '-pix_fmt', 'yuv420p',
            str(out_path)
        ]
        print(f"[StudioRecorder] Transcoding to 60 FPS MP4 ({out_path.name})...")
        subprocess.check_call(cmd)

        # Cleanup temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        print(f"[StudioRecorder] Finished master recording: {out_path}")
        return str(out_path)


def run_scenario(scenario_file, output_mp4):
    """Executes a JSON scenario defining steps for automated 60 FPS recording."""
    with open(scenario_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    recorder = StudioRecorder(
        fps=data.get("fps", 60),
        crf=data.get("crf", 17)
    )

    recorder.start(
        app_url=data.get("app_url", "about:blank"),
        tab_title=data.get("tab_title", "Studio Demo"),
        host=data.get("host", "http://localhost:3000"),
        path=data.get("path", "/")
    )

    for step in data.get("steps", []):
        action = step.get("action")
        if action == "hold":
            recorder.hold(step.get("seconds", 1.0))
        elif action == "camera":
            recorder.set_camera(step.get("scale", 1.0), step.get("x", 960), step.get("y", 600), step.get("duration_ms", 1200))
        elif action == "reset_camera":
            recorder.reset_camera(step.get("duration_ms", 1200))
        elif action == "move_cursor":
            recorder.move_cursor(step.get("x", 960), step.get("y", 600), step.get("duration_ms", 800))
        elif action == "click":
            recorder.click(step.get("x"), step.get("y"), step.get("ripple", True), step.get("settle_ms", 250))
        elif action == "hud":
            recorder.show_hud(step.get("text", ""), step.get("duration_ms", 1200))
        elif action == "type":
            recorder.type_text(step.get("selector"), step.get("text"), step.get("delay_ms", 65))
        elif action == "scroll":
            recorder.scroll_app(step.get("delta_y", 300))

    return recorder.stop_and_encode(output_mp4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record 60 FPS Screen Studio Browser Demo")
    parser.add_argument("--scenario", help="Path to scenario JSON file")
    parser.add_argument("--output", default="out/studio_demo.mp4", help="Output MP4 file path")
    parser.add_argument("--fps", type=int, default=60, help="Output framerate (default: 60)")
    args = parser.parse_args()

    if args.scenario:
        run_scenario(args.scenario, args.output)
    else:
        print("Studio Recorder ready. Use --scenario <file.json> or import StudioRecorder in Python.")
