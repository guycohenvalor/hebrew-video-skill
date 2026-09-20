# -*- coding: utf-8 -*-
"""
Studio Record 60 FPS - High-Conversion Screen Studio Automation Engine
Part of the hebrew-video skill.
Renders web applications inside a Mac/Chrome studio shell with smooth cubic Bezier
virtual mouse cursor, click ripple animations, keystroke HUD badges, and dynamic camera
breathing cadence at TRUE broadcast-grade 60.0 FPS (0 duplicate frames, 0 ghosting)
via Headless Chrome Compositor Stepping (HeadlessExperimental.beginFrame) into FFmpeg image2pipe.
"""

import os
import sys
import time
import json
import base64
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
        self.interval_us = 1000000.0 / fps
        self.base_ticks = 1000000.0
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.client = None

    def start(self, app_url="about:blank", tab_title="הדגמת מערכת חיה", host="http://localhost:3000", path="/"):
        """Launches headless Chromium with begin-frame control and initializes CDP session."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--enable-begin-frame-control',
                '--run-all-compositor-stages-before-draw',
                '--disable-new-content-rendering-timeout',
                '--no-sandbox'
            ]
        )
        self.context = self.browser.new_context(
            viewport={'width': self.width, 'height': self.height}
        )
        self.page = self.context.new_page()
        self.client = self.context.new_cdp_session(self.page)
        self.client.send('HeadlessExperimental.enable')

        # Load studio template
        print(f"[StudioRecorder] Loading template: {self.template_path.as_uri()}...")
        self.page.goto(self.template_path.as_uri())
        self.page.wait_for_load_state('networkidle')

        # Configure tab title, address bar host, and iframe target URL if helper exists
        self.page.evaluate("""
            config => {
                if (window.studioConfigure) window.studioConfigure(config);
            }
        """, {
            "title": tab_title,
            "host": host,
            "path": path,
            "url": app_url
        })
        time.sleep(0.5)
        return self

    def render_timeline(self, duration_sec, output_mp4):
        """
        Renders exact duration_sec * fps frames deterministically via window.studioSeek(t)
        and HeadlessExperimental.beginFrame, piping JPEG bytes directly to FFmpeg.
        Guarantees 0 duplicate frames during motion and 0 ghosting.
        """
        out_path = pathlib.Path(output_mp4).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_frames = int(duration_sec * self.fps)

        cmd = [
            'ffmpeg', '-y',
            '-f', 'image2pipe',
            '-vcodec', 'mjpeg',
            '-r', str(int(self.fps)),
            '-i', '-',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', str(self.crf),
            '-pix_fmt', 'yuv420p',
            str(out_path)
        ]
        print(f"[StudioRecorder] Starting True 60 FPS Compositor Pipe ({total_frames} frames, {duration_sec:.1f}s)...")
        ffmpeg_proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        t0 = time.time()
        for frame_idx in range(total_frames):
            t_sec = frame_idx / self.fps
            ticks = self.base_ticks + frame_idx * self.interval_us

            # Advance virtual time in JS
            self.page.evaluate(f"window.studioSeek({t_sec:.5f})")

            # Capture direct compositor paint
            res = self.client.send('HeadlessExperimental.beginFrame', {
                'frameTimeTicks': ticks,
                'interval': self.interval_us,
                'screenshot': {'format': 'jpeg', 'quality': 88}
            })

            img_bytes = base64.b64decode(res['screenshotData'])
            ffmpeg_proc.stdin.write(img_bytes)

            if (frame_idx + 1) % 300 == 0 or frame_idx == total_frames - 1:
                elapsed = time.time() - t0
                speed = (frame_idx + 1) / elapsed if elapsed > 0 else 0
                pct = (frame_idx + 1) / total_frames * 100
                print(f"  [{frame_idx+1:4d}/{total_frames}] ({t_sec:4.1f}s) - {pct:5.1f}% - Elapsed: {elapsed:5.1f}s ({speed:4.1f} fps)")

        print("[StudioRecorder] Closing FFmpeg pipe and finalizing master MP4...")
        ffmpeg_proc.stdin.close()
        ffmpeg_proc.wait()

        self.context.close()
        self.browser.close()
        self.playwright.stop()

        file_size_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"[StudioRecorder] Master 60 FPS recording complete: {out_path} ({file_size_mb:.2f} MB)")
        return str(out_path)


def run_scenario(scenario_file, output_mp4, duration=60.0):
    """Executes scenario or timeline recording at 60 FPS."""
    recorder = StudioRecorder(fps=60, crf=17)
    if os.path.exists(scenario_file):
        with open(scenario_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        recorder.start(
            app_url=data.get("app_url", "about:blank"),
            tab_title=data.get("tab_title", "Studio Demo"),
            host=data.get("host", "http://localhost:3000"),
            path=data.get("path", "/")
        )
        dur = data.get("duration", duration)
    else:
        recorder.start()
        dur = duration
    return recorder.render_timeline(dur, output_mp4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record True 60 FPS Screen Studio Browser Demo")
    parser.add_argument("--scenario", default="", help="Path to scenario JSON file")
    parser.add_argument("--output", default="out/studio_demo.mp4", help="Output MP4 file path")
    parser.add_argument("--duration", type=float, default=60.0, help="Duration in seconds (default: 60.0)")
    parser.add_argument("--fps", type=int, default=60, help="Output framerate (default: 60)")
    args = parser.parse_args()

    run_scenario(args.scenario, args.output, duration=args.duration)
