#!/usr/bin/env python3
"""
Rainfall Health — Stratus Studio Thumbnail Generator
Powered by Gemini 3 Pro Image (Nano Banana Pro)
Generates 16:9 editorial banners adhering strictly to the Rainfall Health Style Brief
with automated bottom-right logo signet watermarking.
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
MEDIA_DIR = ASSETS_DIR / "media"
ICONMARK_PATH = ASSETS_DIR / "rainfall-iconmark-primary.png"

# Official Rainfall Health Style Guide Prompt Template
STYLE_PROMPT = """Flat vector editorial illustration for a blog header. Bold, uniform black outlines. Flat color fills only, no gradients on characters, no texture, no realistic shading. Limited palette: Bright Sky Blue (#2B72E6), Clear Sky Blue (#8FBAFF), Ice Blue (#EAF1FC), Violet (#8B69FF), Black (#1D1C1A), White (#FFFFFF). Warm brown (#AD7E5E) and peach (#F2D6C2) skin tones. Characters are simplified and friendly, with eyes drawn as closed curved lines and minimal facial features. Background uses large soft cloud shapes cropped at the edges and clean geometric panels. UI elements are rounded cards or buttons with a hard, offset Black drop shadow (no blur). Abstract "text" is shown only as horizontal black bars paired with shorter colored bars. Clean, spacious composition, 16:9, with the bottom-right corner left empty."""

AVOID_PROMPT = """Real text or words, letters, logos, 3D, photo-realism, gradients on people, detailed faces, open eyes, colors outside the palette, busy backgrounds, blurred drop shadows."""

# Curated Scene Presets for the 4 Core Studio Styles
STYLE_PRESETS = {
    "editorial": "A modern healthcare research desk with floating rounded data cards, abstract cloud forms in the background, and a simplified building outline on the left edge.",
    "interview": "A healthcare leader and clinician seated across a sleek minimalist desk in thoughtful discussion, with a floating clipboard and comparison panel above them.",
    "data": "Large stacked analytic metric cards with horizontal colored indicator bars, surrounded by soft sky blue cloud cutouts and clean geometric grid lines.",
    "care": "A compassionate care coordinator visiting a senior patient at home, with simplified medicine and adherence schedule cards floating gently beside them."
}


def apply_watermark(base_image_path: Path, output_path: Path = None, padding: int = 36, logo_height: int = 70):
    """Overlays the official Rainfall Health iconmark signet onto the bottom-right corner."""
    if output_path is None:
        output_path = base_image_path

    if not ICONMARK_PATH.exists():
        print(f"Warning: Watermark logo not found at {ICONMARK_PATH}. Saving without watermark.")
        return output_path

    base = Image.open(base_image_path).convert("RGBA")
    logo = Image.open(ICONMARK_PATH).convert("RGBA")

    # Calculate proportional scale
    aspect = logo.width / logo.height
    new_w = int(logo_height * aspect)
    logo_resized = logo.resize((new_w, logo_height), Image.Resampling.LANCZOS)

    # Position at bottom-right with padding
    x = base.width - new_w - padding
    y = base.height - logo_height - padding

    # Composite
    base.paste(logo_resized, (x, y), logo_resized)
    base.save(output_path, "PNG")
    return output_path


def generate_single_banner(scene: str, output_path: Path, add_watermark: bool = True) -> Path:
    """Calls gemini-3-pro-image to generate a single 16:9 banner adhering to the brand brief."""
    client = genai.Client()

    full_prompt = (
        f"{STYLE_PROMPT}\n\n"
        f"Scene: {scene}\n\n"
        f"Avoid: {AVOID_PROMPT}"
    )

    print(f"🎨 Generating Nano Banana Pro banner...")
    print(f"   Scene: {scene[:80]}...")

    response = client.models.generate_content(
        model="gemini-3-pro-image",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9"),
        ),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    saved = False
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                saved = True
                break
        if saved:
            break

    if not saved:
        raise RuntimeError("No image data received from Gemini API.")

    if add_watermark:
        apply_watermark(output_path)

    print(f"✅ Banner saved to {output_path}")
    return output_path


def generate_variations_batch(episode_slug: str, scene_description: str, out_dir: Path = None) -> list[Path]:
    """Generates 4 variations (banner-a through banner-d) for an episode."""
    if out_dir is None:
        out_dir = MEDIA_DIR / f"{episode_slug}-options"
    out_dir.mkdir(parents=True, exist_ok=True)

    variations = [
        ("banner-a.png", f"{scene_description}, wide composition with soft geometric clouds and clean panels"),
        ("banner-b.png", f"{scene_description}, focused mid-shot with floating rounded UI cards and drop shadows"),
        ("banner-c.png", f"{scene_description}, conceptual perspective with split panel layout and ice blue background"),
        ("banner-d.png", f"{scene_description}, clean minimalist layout with dominant sky blue accents and warm tones")
    ]

    results = []
    for filename, variation_scene in variations:
        dest = out_dir / filename
        try:
            generate_single_banner(variation_scene, dest, add_watermark=True)
            results.append(dest)
        except Exception as e:
            print(f"❌ Error generating {filename}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Generate Rainfall Health thumbnails using Nano Banana Pro")
    parser.add_argument("--scene", type=str, help="1-sentence scene description")
    parser.add_argument("--style", choices=list(STYLE_PRESETS.keys()), default="editorial", help="Preset style")
    parser.add_argument("--slug", type=str, default="custom-episode", help="Slug for output naming")
    parser.add_argument("--batch", action="store_true", help="Generate 4 variations (banner-a..d)")
    parser.add_argument("--output", type=str, help="Specific output file path")
    parser.add_argument("--no-watermark", action="store_true", help="Skip logo watermark overlay")
    args = parser.parse_args()

    scene = args.scene or STYLE_PRESETS.get(args.style)

    if args.batch:
        generate_variations_batch(args.slug, scene)
    else:
        out_path = Path(args.output) if args.output else (MEDIA_DIR / f"{args.slug}-banner.png")
        generate_single_banner(scene, out_path, add_watermark=not args.no_watermark)


if __name__ == "__main__":
    main()
