#!/usr/bin/env python3
"""
Rainfall Health — Stratus Studio Local API & Server
Serves the local Studio Web Dashboard and powers live Gemini 3 Pro Image (Nano Banana Pro)
and multi-channel content generation endpoints.
"""

import os
import sys
import json
import base64
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools.generate_thumbnail import generate_single_banner, generate_variations_batch, STYLE_PRESETS
from tools.generate_episode_kit import generate_kit, save_blog_post

PORT = 8080


class StudioRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if parsed.path == "/api/generate-kit":
            self.handle_generate_kit(payload)
        elif parsed.path == "/api/generate-thumbnail":
            self.handle_generate_thumbnail(payload)
        elif parsed.path == "/api/generate-batch":
            self.handle_generate_batch(payload)
        elif parsed.path == "/api/save-article":
            self.handle_save_article(payload)
        else:
            self.send_error(404, "Endpoint Not Found")

    def send_json(self, data, status=200):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def handle_generate_kit(self, payload):
        title = payload.get("title", "New CMS TEAM Analysis")
        guest = payload.get("guest", "")
        role = payload.get("role", "")
        notes = payload.get("notes", "")

        try:
            kit = generate_kit(title, guest, role, notes)
            self.send_json({"status": "success", "kit": kit})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_generate_thumbnail(self, payload):
        scene = payload.get("scene", "")
        slug = payload.get("slug", "studio-banner")
        style = payload.get("style", "editorial")
        watermark = payload.get("watermark", True)

        if not scene:
            scene = STYLE_PRESETS.get(style, STYLE_PRESETS["editorial"])

        dest = BASE_DIR / "assets" / "media" / f"{slug}.png"
        try:
            generate_single_banner(scene, dest, add_watermark=watermark)
            rel_url = f"assets/media/{slug}.png"
            self.send_json({"status": "success", "url": rel_url, "path": str(dest)})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_generate_batch(self, payload):
        slug = payload.get("slug", "episode-batch")
        scene = payload.get("scene", STYLE_PRESETS["editorial"])

        try:
            files = generate_variations_batch(slug, scene)
            urls = [f"assets/media/{slug}-options/{f.name}" for f in files]
            self.send_json({"status": "success", "urls": urls})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)

    def handle_save_article(self, payload):
        slug = payload.get("slug", "new-article")
        content = payload.get("content", "")

        try:
            saved_path = save_blog_post(slug, content)
            self.send_json({"status": "success", "path": str(saved_path)})
        except Exception as e:
            self.send_json({"status": "error", "message": str(e)}, status=500)


def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, StudioRequestHandler)
    print(f"\n========================================================")
    print(f"⚡ Stratus Studio Local Engine is running at:")
    print(f"👉 http://localhost:{PORT}/studio.html")
    print(f"========================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Stratus Studio...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
