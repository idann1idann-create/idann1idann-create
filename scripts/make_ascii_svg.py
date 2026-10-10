from pathlib import Path
from PIL import Image, ImageChops

INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

COLS = 104
RAMP = " .`:-=+*cs#%@"

CHAR_W = 7.2
CHAR_H = 11.5
FONT_SIZE = 11
LEFT_PAD = 10
TOP_PAD = 10


def pixel_to_char(value: int) -> str:
    """
    255 = white -> sparse / blank
    0   = black -> dense
    """
    normalized = 1.0 - (value / 255.0)
    idx = round(normalized * (len(RAMP) - 1))
    return RAMP[idx]


def escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"{INPUT} was not found. "
            "Run scripts/prep_photo.py first."
        )

    img = Image.open(INPUT).convert("L")

    # Remove the large white margins left by the source photo before
    # sampling it. Keep a little headroom so the portrait does not touch
    # the panel edges.
    bounds = ImageChops.difference(
        img,
        Image.new("L", img.size, 255),
    ).point(lambda value: 255 if value > 5 else 0).getbbox()
    if bounds:
        content_height = bounds[3] - bounds[1]
        top_padding = max(12, round(content_height * 0.025))
        img = img.crop((
            bounds[0],
            max(0, bounds[1] - top_padding),
            bounds[2],
            bounds[3],
        ))

    # Terminal characters are taller than they are wide,
    # so compensate for that when resizing.
    aspect = img.height / img.width
    rows = max(1, int(COLS * aspect * 0.52))

    img = img.resize((COLS, rows))

    ascii_rows = []

    for y in range(rows):
        chars = []
        for x in range(COLS):
            value = img.getpixel((x, y))
            chars.append(pixel_to_char(value))
        ascii_rows.append("".join(chars).rstrip())

    OUTPUT.write_text(render_svg(ascii_rows), encoding="utf-8")
    print(f"Created {OUTPUT}")


def render_svg(ascii_rows):
    """Frame the sampled portrait without adding whitespace to the ASCII rows."""
    width = int(COLS * CHAR_W + LEFT_PAD * 2)
    height = int(len(ascii_rows) * CHAR_H + TOP_PAD * 2)
    scale = min(382 / width, 290 / height)
    left = (430 - width * scale) / 2
    top = 55 + (290 - height * scale) / 2
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="430" height="370"
        viewBox="0 0 430 370" role="img" aria-labelledby="portrait-title">
      <title id="portrait-title">ASCII portrait of Idan</title>
      <rect x="0.5" y="0.5" width="429" height="369" rx="14" fill="#0d1117" stroke="#30363d"/>
      <text x="24" y="30" font-family="ui-monospace, monospace" font-size="12" fill="#919ba5">idan / portrait</text>
      <path d="M24 44H406" stroke="#30363d"/>
      <style>
        @media (prefers-reduced-motion: no-preference) {{
          .ascii-row {{ animation: reveal .45s ease-out backwards; }}
        }}
        @keyframes reveal {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      </style>
      <g transform="translate({left:.3f} {top:.3f}) scale({scale:.5f})"
         font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
         font-size="{FONT_SIZE}" fill="#c9d1d9" xml:space="preserve" style="white-space:pre">''']
    for i, row in enumerate(ascii_rows):
        # Position visible glyphs explicitly: SVG engines differ in how they
        # collapse leading spaces, even with xml:space and white-space:pre.
        positions = " ".join(f"{LEFT_PAD + j * CHAR_W:.2f}"
                             for j, char in enumerate(row) if char != " ")
        visible = row.replace(" ", "")
        if visible:
            parts.append(
                f'<text class="ascii-row" x="{positions}" y="{TOP_PAD + i * CHAR_H}" '
                f'style="animation-delay:{i * .025:.3f}s">{escape_xml(visible)}</text>'
            )
    parts.extend(["</g>", "</svg>"])
    return "\n".join(parts)


if __name__ == "__main__":
    main()
