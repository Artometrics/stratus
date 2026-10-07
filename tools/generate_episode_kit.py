#!/usr/bin/env python3
"""
Rainfall Health — Stratus Multi-Channel Episode Kit Engine
Powered by Google Gemini 3
Generates complete YouTube, LinkedIn, Transistor, Quarto Blog, Subtitle,
and Thumbnail scene briefs from a single episode transcript or topic brief.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
ARTICLES_DIR = BASE_DIR / "articles"

SYSTEM_PROMPT = """You are the Senior Executive Content Strategist and Editorial Director for Rainfall Health and its Stratus CMS intelligence platform.
Rainfall Health delivers data intelligence and clinical adherence networks for the CMS Transforming Episode Accountability Model (TEAM) and bundled payments.
Your tone is authoritative, analytical, healthcare-insider, concise, and compelling. Never use generic corporate jargon or fluffy marketing filler.
You write for hospital CFOs, Chief Medical Officers, orthopedic department chairs, and health system strategy executives."""

def generate_kit(title: str, guest: str = "", guest_role: str = "", content_or_transcript: str = "") -> dict:
    """Generates structured content across all 5 distribution channels in one Gemini call."""
    client = genai.Client()

    prompt = f"""Generate a comprehensive multi-channel publishing kit for the following episode/article.

Episode Title/Topic: {title}
Guest Name: {guest or "Not specified / Editorial"}
Guest Role & Organization: {guest_role or "Healthcare Leader"}
Core Content / Transcript / Key Points:
{content_or_transcript or title}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "slug": "url-friendly-kebab-case-slug",
  "youtube": {{
    "titles": [
      "High CTR Title 1",
      "High CTR Title 2",
      "High CTR Title 3"
    ],
    "description": "Full YouTube video description formatted with chapters, summary, guest bio, and links",
    "chapters": [
      {{"time": "0:00", "title": "Introduction & Overview"}},
      {{"time": "02:15", "title": "Core Mechanism"}},
      {{"time": "06:40", "title": "Strategic Playbook"}}
    ],
    "tags": ["CMS TEAM", "Healthcare Policy", "Bundled Payments", "Hospital Finance"]
  }},
  "linkedin": {{
    "post": "Full formatted LinkedIn post with hook, 3-5 bold bullet takeaways, discussion prompt, and hashtags"
  }},
  "transistor": {{
    "show_notes_html": "<p>Rich HTML formatted show notes with headers, bullet points, and guest bio ready to paste into Transistor.fm</p>"
  }},
  "thumbnail_scenes": {{
    "editorial": "One-sentence flat vector scene for editorial banner adhering to Rainfall style guide",
    "interview": "One-sentence flat vector scene of two friendly figures across desk with UI cards",
    "data": "One-sentence flat vector scene featuring stacked analytic metrics and floating bars",
    "care": "One-sentence flat vector scene featuring home care transition and patient recovery"
  }},
  "blog_qmd": "Complete Quarto markdown (.qmd) article including YAML frontmatter with title, description, categories, and full 2-column body content"
}}
"""

    print(f"🚀 Generating Multi-Channel Episode Kit with Gemini...")
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )

    try:
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Error parsing JSON response: {e}")
        print("Raw output:", response.text)
        raise


def save_blog_post(slug: str, qmd_content: str) -> Path:
    """Saves the generated Quarto blog post to the articles/ directory."""
    dest = ARTICLES_DIR / f"{slug}.qmd"
    with open(dest, "w", encoding="utf-8") as f:
        f.write(qmd_content)
    print(f"📝 Blog article saved to {dest}")
    return dest


def main():
    parser = argparse.ArgumentParser(description="Generate complete Stratus Episode Kit")
    parser.add_argument("--title", type=str, required=True, help="Episode title or topic")
    parser.add_argument("--guest", type=str, default="", help="Guest name")
    parser.add_argument("--role", type=str, default="", help="Guest role / organization")
    parser.add_argument("--transcript-file", type=str, help="Path to transcript text file")
    parser.add_argument("--notes", type=str, default="", help="Episode notes or brief")
    parser.add_argument("--save-article", action="store_true", help="Save the .qmd directly into articles/")
    parser.add_argument("--output-json", type=str, help="Path to save output JSON")
    args = parser.parse_args()

    content = args.notes
    if args.transcript_file and os.path.exists(args.transcript_file):
        with open(args.transcript_file, "r", encoding="utf-8") as f:
            content = f.read()

    kit = generate_kit(args.title, args.guest, args.role, content)

    if args.save_article:
        save_blog_post(kit.get("slug", "new-episode"), kit.get("blog_qmd", ""))

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(kit, f, indent=2)
        print(f"💾 Kit saved to {args.output_json}")
    else:
        print(json.dumps(kit, indent=2))


if __name__ == "__main__":
    main()
