from pathlib import Path
from PIL import Image

INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

COLS = 100
RAMP = " .`:-=+*cs#%@"

CHAR_W = 7.2
CHAR_H = 11.5
FONT_SIZE = 11
LEFT_PAD = 8
TOP_PAD = 14


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

    width = int(COLS * CHAR_W + LEFT_PAD * 2)
    height = int(rows * CHAR_H + TOP_PAD * 2)

    row_duration = 0.55
    row_stagger = 0.045

    svg_parts = []

    svg_parts.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg"
             width="{width}"
             height="{height}"
             viewBox="0 0 {width} {height}">'''
    )

    svg_parts.append(
        """
        <rect width="100%" height="100%" fill="#0d1117"/>
        """
    )

    svg_parts.append("<defs>")

    for i in range(rows):
        clip_width = COLS * CHAR_W

        svg_parts.append(
            f'''
            <clipPath id="clip-{i}">
                <rect
                    x="{LEFT_PAD}"
                    y="{TOP_PAD + i * CHAR_H - CHAR_H}"
                    width="0"
                    height="{CHAR_H + 3}">
                    <animate
                        attributeName="width"
                        from="0"
                        to="{clip_width}"
                        dur="{row_duration}s"
                        begin="{i * row_stagger}s"
                        fill="freeze"/>
                </rect>
            </clipPath>
            '''
        )

    svg_parts.append("</defs>")

    svg_parts.append(
        f'''
        <g
            font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
            font-size="{FONT_SIZE}"
            fill="#c9d1d9"
            xml:space="preserve">
        '''
    )

    for i, row in enumerate(ascii_rows):
        y = TOP_PAD + i * CHAR_H

        svg_parts.append(
            f'''
            <text
                x="{LEFT_PAD}"
                y="{y}"
                clip-path="url(#clip-{i})">
                {escape_xml(row)}
            </text>
            '''
        )

        cursor_x = LEFT_PAD + COLS * CHAR_W

        svg_parts.append(
            f'''
            <rect
                x="{LEFT_PAD}"
                y="{y - FONT_SIZE + 1}"
                width="6"
                height="{FONT_SIZE + 1}"
                fill="#c9d1d9"
                opacity="0">
                <animate
                    attributeName="x"
                    from="{LEFT_PAD}"
                    to="{cursor_x}"
                    dur="{row_duration}s"
                    begin="{i * row_stagger}s"
                    fill="freeze"/>
                <animate
                    attributeName="opacity"
                    values="0;1;1;0"
                    keyTimes="0;0.02;0.92;1"
                    dur="{row_duration}s"
                    begin="{i * row_stagger}s"
                    fill="freeze"/>
            </rect>
            '''
        )

    svg_parts.append("</g>")
    svg_parts.append("</svg>")

    OUTPUT.write_text("\n".join(svg_parts), encoding="utf-8")

    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
