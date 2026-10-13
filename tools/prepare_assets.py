"""Builds the web assets in static/img from the raw files in media/.

Run once (the generated files are committed), or again if you change the media:

    py tools/prepare_assets.py

Outputs:
  logo_pk.png, logo_pk_it.png  logos recoloured to phosphor green, transparent background
  fish.webp                    small mascot for the landing page
  sonar_scan.png               the level 4 image with the flag hidden in it
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
OUT = ROOT / "static" / "img"
PRIVATE = ROOT / "private"  # NOT served by /static; app.py hands it out only to players who earned it
OUT.mkdir(parents=True, exist_ok=True)
PRIVATE.mkdir(exist_ok=True)

PHOSPHOR = (80, 255, 120)
FLAG4 = "SPOOF{nereus_unmasked}"

# Hidden-text parameters. The server never needs them, but the scanner JS uses the same
# black point (BLACK_POINT) to stretch the contrast.
BLACK_POINT = 6  # every dark pixel gets at least this green level
TEXT_LEVEL = 9   # the hidden text is only 3 levels above the background


def recolor_logo(src: Path, dst: Path, size: int = 256) -> None:
    """Dark pixels of the logo become phosphor green, white becomes transparent."""
    img = Image.open(src).convert("RGB")
    img.thumbnail((size, size), Image.LANCZOS)
    gray = img.convert("L")
    alpha = gray.point(lambda v: 255 - v)
    # Stretch alpha so light logo colours do not look washed out.
    lo, hi = alpha.getextrema()
    if hi > lo:
        alpha = alpha.point(lambda v: min(255, int((v - lo) * 255 / (hi - lo))))
    out = Image.new("RGBA", img.size, PHOSPHOR + (0,))
    out.putalpha(alpha)
    out.save(dst, optimize=True)


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "cour.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_fish() -> None:
    img = Image.open(MEDIA / "fish.webp").convert("RGB")

    # Small mascot for the landing page.
    mascot = img.copy()
    mascot.thumbnail((720, 720), Image.LANCZOS)
    mascot.save(OUT / "fish.webp", quality=80, method=6)

    # Steganography image: the fish plus an extra black strip with the hidden flag.
    width = 1200
    fish_h = round(img.height * width / img.width)
    height = fish_h + 110
    scan = Image.new("RGB", (width, height), (0, 0, 0))
    scan.paste(img.resize((width, fish_h), Image.LANCZOS), (0, 0))
    px = scan.load()

    # Raise the black level a little so that the text can sit just above it.
    mask = Image.new("L", scan.size, 0)
    draw = ImageDraw.Draw(mask)
    font = find_font(54)
    draw.text((30, fish_h + 20), FLAG4, fill=255, font=font)
    mpx = mask.load()

    for y in range(height):
        for x in range(width):
            r, g, b = px[x, y]
            dark = max(r, g, b) < 40
            if dark:
                level = TEXT_LEVEL if mpx[x, y] > 128 else BLACK_POINT
                px[x, y] = (0, level, 0)

    info = PngInfo()
    info.add_text("Comment", FLAG4)
    info.add_text("Software", "NEREUS sonar scanner v0.9 (do not trust)")
    scan.save(PRIVATE / "sonar_scan.png", pnginfo=info, optimize=True)


def main() -> None:
    recolor_logo(MEDIA / "PK_logo.webp", OUT / "logo_pk.png")
    recolor_logo(MEDIA / "PK_IT_Logo.webp", OUT / "logo_pk_it.png")
    build_fish()
    for p in sorted(OUT.iterdir()):
        print(f"{p.name:20} {p.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    main()
