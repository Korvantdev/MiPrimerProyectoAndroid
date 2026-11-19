#!/usr/bin/env python3
"""Compose the documentation previews from the Robolectric screenshots.

The actual screenshots are produced by:
    ./gradlew testDebugUnitTest --tests '*renderDocumentationScreenshots*'

Run this script afterwards:
    python tools/render_docs.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "app" / "build" / "screenshots"
OUT = ROOT / "docs" / "screenshots"

FONT_BOLD = Path("C:/Windows/Fonts/seguisb.ttf")
FONT_REGULAR = Path("C:/Windows/Fonts/segoeui.ttf")
FALLBACK_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FALLBACK_REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

INK = (17, 32, 58)
MUTED = (86, 104, 132)
ACCENT = (11, 125, 255)
CARD = (255, 255, 255)
BG_TOP = (247, 251, 255)
BG_BOTTOM = (229, 241, 255)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    options = (FONT_BOLD, FALLBACK_BOLD) if bold else (FONT_REGULAR, FALLBACK_REGULAR)
    for path in options:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def fit(img: Image.Image, width: int) -> Image.Image:
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.Resampling.LANCZOS)


def framed(img: Image.Image, width: int, border: int = 7, radius: int = 26) -> Image.Image:
    screen = fit(img.convert("RGB"), width)
    radius = min(radius, screen.width // 8, screen.height // 8)
    mask = Image.new("L", screen.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, screen.width - 1, screen.height - 1),
                                           radius=radius, fill=255)
    frame = Image.new("RGBA", (screen.width + border * 2, screen.height + border * 2),
                      (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((0, 0, frame.width - 1, frame.height - 1),
                           radius=radius + border, fill=(24, 28, 37, 255))
    frame.paste(screen, (border, border), mask)
    return frame


def with_shadow(frame: Image.Image, blur: int = 18, spread: int = 4) -> Image.Image:
    pad = blur * 2 + spread
    canvas = Image.new("RGBA", (frame.width + pad * 2, frame.height + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = frame.split()[-1]
    shadow_mask = Image.new("L", canvas.size, 0)
    shadow_mask.paste(mask, (pad, pad + spread))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(blur))
    shadow.putalpha(shadow_mask.point(lambda v: int(v * 0.28)))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(frame, (pad, pad))
    return canvas


def background(size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(size[1]):
        t = y / max(size[1] - 1, 1)
        color = tuple(round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(size[0]):
            px[x, y] = color
    return img


def label(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, subtitle: str,
          width: int, align_center: bool = True) -> None:
    title_font = font(25, bold=True)
    subtitle_font = font(17)
    if align_center:
        tw = draw.textlength(title, font=title_font)
        sw = draw.textlength(subtitle, font=subtitle_font)
        draw.text((x + (width - tw) / 2, y), title, font=title_font, fill=INK)
        draw.text((x + (width - sw) / 2, y + 32), subtitle, font=subtitle_font, fill=MUTED)
    else:
        draw.text((x, y), title, font=title_font, fill=INK)
        draw.text((x, y + 32), subtitle, font=subtitle_font, fill=MUTED)


def preview_languages() -> None:
    width, height = 1600, 770
    canvas = background((width, height))
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 44), "Cuatro idiomas, una sola pantalla", font=font(38, bold=True), fill=INK)
    draw.text((72, 94), "Español (predeterminado) · English · Français · Deutsch",
              font=font(21), fill=MUTED)

    entries = [
        ("ES", "Español", "Bienvenido", "phone-portrait-es.png"),
        ("EN", "English", "Welcome", "phone-portrait-en.png"),
        ("FR", "Français", "Bienvenue", "phone-portrait-fr.png"),
        ("DE", "Deutsch", "Willkommen", "phone-portrait-de.png"),
    ]
    phone_w = 300
    slot_w = phone_w + 14
    gap = 32
    total = len(entries) * slot_w + (len(entries) - 1) * gap
    x = (width - total) // 2
    top = 140
    for code, language, greeting, filename in entries:
        source = Image.open(SRC / filename)
        phone = with_shadow(framed(source, phone_w))
        canvas.paste(phone, (x, top - 36), phone)
        label(draw, x, top + 545, f"{code} · {language}", greeting, slot_w)
        x += slot_w + gap

    canvas.save(ROOT / "docs" / "preview-languages.png", optimize=True)


def preview_screens() -> None:
    width, height = 1780, 1240
    canvas = background((width, height))
    draw = ImageDraw.Draw(canvas)
    draw.text((68, 40), "Una interfaz que se adapta", font=font(38, bold=True), fill=INK)
    draw.text((70, 90), "Teléfono y tableta · vertical y horizontal · sin distorsión del fondo",
              font=font(21), fill=MUTED)

    cards = [
        ("Teléfono · vertical", "360 × 640 dp", "phone-portrait-es.png", 0, 0, 830, 540),
        ("Teléfono · horizontal", "640 × 360 dp", "phone-landscape-es.png", 1, 0, 830, 540),
        ("Tableta · vertical", "600 × 960 dp", "tablet-portrait-es.png", 0, 1, 830, 540),
        ("Tableta · horizontal", "960 × 600 dp", "tablet-landscape-es.png", 1, 1, 830, 540),
    ]
    margin = 60
    gap = 30
    card_w = (width - margin * 2 - gap) // 2
    card_h = (height - 150 - margin - gap) // 2
    for title, subtitle, filename, col, row, max_w, max_h in cards:
        x = margin + col * (card_w + gap)
        y = 150 + row * (card_h + gap)
        card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, card_w - 1, card_h - 1), radius=26, fill=CARD + (255,))
        shadow = Image.new("RGBA", (card_w + 60, card_h + 60), (0, 0, 0, 0))
        sm = Image.new("L", shadow.size, 0)
        ImageDraw.Draw(sm).rounded_rectangle((30, 34, 30 + card_w, 30 + card_h),
                                             radius=26, fill=140)
        shadow.putalpha(sm.filter(ImageFilter.GaussianBlur(18)))
        canvas.paste(shadow, (x - 30, y - 28), shadow)
        canvas.paste(card, (x, y), card)

        d = ImageDraw.Draw(canvas)
        d.text((x + 26, y + 20), title, font=font(24, bold=True), fill=INK)
        d.text((x + 26, y + 52), subtitle, font=font(16), fill=MUTED)

        source = Image.open(SRC / filename)
        # Fit into the lower part of the actual card (the card may be narrower than the
        # nominal max_w/max_h values used to describe the layout).
        available_w = card_w - 70
        available_h = card_h - 105
        image = framed(source, min(available_w, round(available_h * source.width / source.height)))
        if image.height > available_h:
            image = image.resize((round(image.width * available_h / image.height), available_h),
                                 Image.Resampling.LANCZOS)
        canvas.paste(image, (x + (card_w - image.width) // 2,
                             y + 88 + (available_h - image.height) // 2), image)

    canvas.save(ROOT / "docs" / "preview-screens.png", optimize=True)


def copy_individual() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    targets = {
        "phone-portrait-es.png": 720,
        "phone-portrait-en.png": 720,
        "phone-portrait-fr.png": 720,
        "phone-portrait-de.png": 720,
        "phone-landscape-es.png": 1280,
        "tablet-portrait-es.png": 800,
        "tablet-landscape-es.png": 1280,
    }
    for name, width in targets.items():
        source = Image.open(SRC / name).convert("RGB")
        resized = fit(source, width)
        resized.save(OUT / name, optimize=True)


def main() -> None:
    missing = [name for name in (
        "phone-portrait-es.png", "phone-portrait-en.png", "phone-portrait-fr.png",
        "phone-portrait-de.png", "phone-landscape-es.png", "tablet-portrait-es.png",
        "tablet-landscape-es.png") if not (SRC / name).exists()]
    if missing:
        raise SystemExit("Missing screenshots. Run the Robolectric screenshot test first: " + ", ".join(missing))
    copy_individual()
    preview_languages()
    preview_screens()
    print("Wrote docs/screenshots and docs/preview-*.png")


if __name__ == "__main__":
    main()
