#!/usr/bin/env python3
"""Generate the nine-patch background and launcher icons from the assignment art.

The Android mascot is intentionally left in a "fixed" patch:
  * horizontal stretch: only the far-left and far-right sky columns
  * vertical stretch: only the upper sky
  * fixed: the mascot, its shadow and the cloud band at the bottom

Run from the repository root:
    python tools/prepare_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/seguisb.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
)
FONT_REGULAR_CANDIDATES = (
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)
SOURCE = ROOT / "design" / "background-source.png"
NINEPATCH = ROOT / "app" / "src" / "main" / "res" / "drawable-xxhdpi" / "background.9.png"
GUIDE = ROOT / "docs" / "ninepatch-guide.png"
STRETCH_DEMO = ROOT / "docs" / "ninepatch-stretch-demo.png"

# Source image is 1024 x 853. The mascot occupies x=440..615, y=498..691.
H_STRETCH = ((0, 128), (896, 1024))
V_STRETCH = (0, 320)

# Nine-patch marker colours must be fully opaque black.
BLACK = (0, 0, 0, 255)


def make_ninepatch(source: Image.Image) -> Image.Image:
    """Wrap the bitmap in a one-pixel transparent border with stretch markers."""
    width, height = source.size
    out = Image.new("RGBA", (width + 2, height + 2), (0, 0, 0, 0))
    out.paste(source.convert("RGBA"), (1, 1))

    pixels = out.load()
    for start, end in H_STRETCH:
        for x in range(start, end):
            pixels[x + 1, 0] = BLACK
    for y in range(*V_STRETCH):
        pixels[0, y + 1] = BLACK

    return out


def stretch_ninepatch(source: Image.Image, width: int, height: int) -> Image.Image:
    """Pure-Python approximation of Android's nine-patch scaling (for docs)."""
    src_w, src_h = source.size
    fixed_x = [H_STRETCH[0][1], H_STRETCH[1][0]]
    fixed_y = V_STRETCH[1]

    # Horizontal destination boundaries: the two edge stretches absorb extra width.
    extra_x = max(width - src_w, 0)
    left_extra = extra_x // 2
    right_extra = extra_x - left_extra
    xs = [0, H_STRETCH[0][1] + left_extra, H_STRETCH[1][0] + left_extra, width]
    src_xs = [0, H_STRETCH[0][1], H_STRETCH[1][0], src_w]

    extra_y = max(height - src_h, 0)
    ys = [0, fixed_y + extra_y, height]
    src_ys = [0, fixed_y, src_h]

    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for row in range(2):
        sy0, sy1 = src_ys[row], src_ys[row + 1]
        dy0, dy1 = ys[row], ys[row + 1]
        for col in range(3):
            sx0, sx1 = src_xs[col], src_xs[col + 1]
            dx0, dx1 = xs[col], xs[col + 1]
            if dx1 <= dx0 or dy1 <= dy0:
                continue
            tile = source.crop((sx0, sy0, sx1, sy1)).resize(
                (dx1 - dx0, dy1 - dy0), Image.Resampling.LANCZOS
            )
            out.paste(tile, (dx0, dy0))
    return out


def draw_marker_ticks(draw: ImageDraw.ImageDraw, origin: tuple[int, int], size: tuple[int, int]) -> None:
    ox, oy = origin
    width, height = size
    for start, end in H_STRETCH:
        draw.rectangle((ox + start, oy - 8, ox + end - 1, oy - 1), fill=(20, 20, 20))
    for y in range(*V_STRETCH):
        draw.rectangle((ox - 8, oy + y, ox - 1, oy + y), fill=(20, 20, 20))


def make_guide(source: Image.Image) -> Image.Image:
    """Visual explanation of the three protected patches and two stretch zones."""
    width, height = source.size
    margin = 72
    canvas = Image.new("RGB", (width + margin * 2, height + margin * 2), (246, 249, 255))
    canvas.paste(source.convert("RGB"), (margin, margin))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    ox, oy = margin, margin

    colors = {
        "h": (124, 92, 190, 150),
        "v": (52, 160, 120, 150),
        "fixed": (29, 158, 105, 70),
    }
    # Edge columns that are scaled horizontally.
    for start, end in H_STRETCH:
        draw.rectangle((ox + start, oy, ox + end - 1, oy + height - 1), fill=colors["h"])
    # Upper band that is scaled vertically.
    draw.rectangle((ox, oy, ox + width - 1, oy + V_STRETCH[1] - 1), fill=colors["v"])
    # Fixed mascot + clouds.
    draw.rectangle(
        (ox + H_STRETCH[0][1], oy + V_STRETCH[1], ox + H_STRETCH[1][0] - 1, oy + height - 1),
        fill=colors["fixed"],
    )

    # Grid lines.
    for x in (H_STRETCH[0][1], H_STRETCH[1][0]):
        draw.line((ox + x, oy, ox + x, oy + height), fill=(255, 255, 255, 220), width=3)
    draw.line((ox, oy + V_STRETCH[1], ox + width, oy + V_STRETCH[1]), fill=(255, 255, 255, 220), width=3)
    draw_marker_ticks(draw, (ox, oy), (width, height))

    # Mascot protection box.
    draw.rectangle((ox + 440, oy + 498, ox + 615, oy + 691), outline=(255, 255, 255, 255), width=4)
    draw.rectangle((ox + 436, oy + 494, ox + 619, oy + 695), outline=(255, 196, 0, 255), width=2)

    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    font = load_font(24, bold=True)
    small = load_font(18)
    draw.text((margin, 16), "Nine-patch: zonas de estiramiento y zona fija", fill=(16, 38, 74), font=font)
    draw.text(
        (margin, height + margin + 16),
        "Morado: estira en horizontal (solo cielo)   ·   Verde: estira en vertical (solo cielo)   ·   "
        "Zona central: mascota + nubes fijas",
        fill=(36, 55, 82),
        font=small,
    )
    draw.text(
        (margin, height + margin + 44),
        "Marcas negras superiores: 0-128 px y 896-1023 px   ·   Marca izquierda: 0-319 px",
        fill=(70, 84, 104),
        font=small,
    )
    return canvas


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_CANDIDATES if bold else FONT_REGULAR_CANDIDATES
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def make_stretch_demo(source: Image.Image) -> Image.Image:
    wide = stretch_ninepatch(source, 1536, 960)
    portrait = stretch_ninepatch(source, 900, 1280)
    margin = 36
    label_h = 52
    canvas = Image.new(
        "RGB",
        (margin * 3 + wide.width + portrait.width, margin * 2 + label_h + max(wide.height, portrait.height)),
        (246, 249, 255),
    )
    draw = ImageDraw.Draw(canvas)
    font = load_font(24, bold=True)
    draw.text((margin, 14), "9-patch escalado a 1536 x 960 (horizontal)", fill=(16, 38, 74), font=font)
    draw.text((margin * 2 + wide.width, 14), "9-patch escalado a 900 x 1280 (vertical)", fill=(16, 38, 74), font=font)
    canvas.paste(wide.convert("RGB"), (margin, margin + label_h))
    canvas.paste(portrait.convert("RGB"), (margin * 2 + wide.width, margin + label_h))
    return canvas


def round_rect(draw: ImageDraw.ImageDraw, box, radius, fill) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def make_icon(size: int, circular: bool = False) -> Image.Image:
    """Draw a crisp legacy launcher icon at high resolution, then downsample."""
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()

    # Vertical blue gradient.
    top = (8, 136, 255)
    bottom = (126, 212, 255)
    for y in range(s):
        t = y / max(s - 1, 1)
        color = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(s):
            px[x, y] = color

    draw = ImageDraw.Draw(img)
    # Soft cloud band.
    for cx, cy, r, alpha in [
        (0.10, 0.93, 0.23, 215),
        (0.30, 0.96, 0.25, 235),
        (0.52, 0.94, 0.24, 240),
        (0.74, 0.96, 0.24, 235),
        (0.94, 0.92, 0.22, 215),
    ]:
        box = (cx * s - r * s, cy * s - r * s, cx * s + r * s, cy * s + r * s)
        draw.ellipse(box, fill=(255, 255, 255, alpha))

    black = (16, 16, 18, 255)
    cyan = (79, 216, 255, 255)
    cx = s / 2
    robot_w = 0.46 * s
    head_w = 0.34 * s
    head_top = 0.36 * s
    head_h = 0.20 * s
    head_bottom = head_top + head_h

    # Antennae.
    draw.line((cx - head_w * 0.34, head_top + 2, cx - head_w * 0.50, head_top - 0.09 * s), fill=black, width=max(2, round(0.012 * s)))
    draw.line((cx + head_w * 0.34, head_top + 2, cx + head_w * 0.50, head_top - 0.09 * s), fill=black, width=max(2, round(0.012 * s)))
    # Head (bottom corners hidden by body).
    round_rect(draw, (cx - head_w / 2, head_top, cx + head_w / 2, head_bottom + 0.02 * s), 0.10 * s, black)
    # Eyes.
    eye_r = 0.018 * s
    for dx in (-0.075 * s, 0.075 * s):
        draw.ellipse((cx + dx - eye_r, head_top + 0.085 * s - eye_r, cx + dx + eye_r, head_top + 0.085 * s + eye_r), fill=cyan)
    # Body.
    body_top = head_bottom - 0.01 * s
    body_bottom = body_top + 0.23 * s
    round_rect(draw, (cx - robot_w * 0.42, body_top, cx + robot_w * 0.42, body_bottom), 0.035 * s, black)
    # Arms.
    arm_w = 0.045 * s
    arm_top = body_top + 0.02 * s
    arm_bottom = body_bottom - 0.055 * s
    round_rect(draw, (cx - robot_w * 0.56, arm_top, cx - robot_w * 0.56 + arm_w, arm_bottom), arm_w / 2, black)
    round_rect(draw, (cx + robot_w * 0.56 - arm_w, arm_top, cx + robot_w * 0.56, arm_bottom), arm_w / 2, black)
    # Legs.
    leg_w = 0.055 * s
    for dx in (-0.105 * s, 0.105 * s):
        round_rect(draw, (cx + dx - leg_w / 2, body_bottom - 2, cx + dx + leg_w / 2, body_bottom + 0.095 * s), leg_w / 2, black)

    if circular:
        mask = Image.new("L", (s, s), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
        img.putalpha(mask)
    else:
        radius = int(0.20 * s)
        mask = Image.new("L", (s, s), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, s - 1, s - 1), radius=radius, fill=255)
        img.putalpha(mask)

    return img.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source image: {SOURCE}")

    source = Image.open(SOURCE).convert("RGB")
    if source.size != (1024, 853):
        raise SystemExit(f"Unexpected source size {source.size}; expected 1024x853")

    NINEPATCH.parent.mkdir(parents=True, exist_ok=True)
    ninepatch = make_ninepatch(source)
    ninepatch.save(NINEPATCH, optimize=True)
    print(f"Wrote {NINEPATCH} ({ninepatch.width}x{ninepatch.height})")

    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    make_guide(source).save(GUIDE, optimize=True)
    print(f"Wrote {GUIDE}")
    make_stretch_demo(source).save(STRETCH_DEMO, optimize=True)
    print(f"Wrote {STRETCH_DEMO}")

    densities = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    res = ROOT / "app" / "src" / "main" / "res"
    for density, size in densities.items():
        folder = res / f"mipmap-{density}"
        folder.mkdir(parents=True, exist_ok=True)
        make_icon(size).save(folder / "ic_launcher.png", optimize=True)
        make_icon(size, circular=True).save(folder / "ic_launcher_round.png", optimize=True)
    print(f"Wrote launcher icons for {', '.join(densities)}")


if __name__ == "__main__":
    main()
