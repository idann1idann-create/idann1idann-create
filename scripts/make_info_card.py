import os
from pathlib import Path

OUTPUT = Path("info-card.svg")

WIDTH = 490
HEIGHT = 310

BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#39d353"
CYAN = "#58a6ff"
YELLOW = "#d29922"
PURPLE = "#bc8cff"

STATIC = os.getenv("STATIC") == "1"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


rows = [
    ("Now", "Building Osto / Atlas", GREEN),
    ("Prev", "Financial Planner", CYAN),
    ("Stack", "Python · React · AI", PURPLE),
    ("Highlights", "Finance · Automation · Agents", YELLOW),
]

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">'''
)

svg.append(
    f'''
    <rect
        x="1"
        y="1"
        width="{WIDTH - 2}"
        height="{HEIGHT - 2}"
        rx="14"
        fill="{BG}"
        stroke="{BORDER}"
        stroke-width="2"/>
    '''
)

svg.append(
    f'''
    <text
        x="28"
        y="42"
        font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
        font-size="18"
        font-weight="700"
        fill="{TEXT}">
        idan@github
    </text>

    <text
        x="28"
        y="68"
        font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
        font-size="13"
        fill="{MUTED}">
        ------------------------------
    </text>
    '''
)

start_y = 105
gap = 42

for i, (key, value, color) in enumerate(rows):
    y = start_y + i * gap

    if STATIC:
        animation = ""
        opacity = "1"
        transform = ""
    else:
        delay = 0.18 * i

        animation = f'''
        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.35s"
            begin="{delay}s"
            fill="freeze"/>

        <animateTransform
            attributeName="transform"
            type="translate"
            from="0 8"
            to="0 0"
            dur="0.35s"
            begin="{delay}s"
            fill="freeze"/>
        '''

        opacity = "0"
        transform = ""

    svg.append(
        f'''
        <g opacity="{opacity}" {transform}>
            {animation}

            <text
                x="28"
                y="{y}"
                font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
                font-size="14"
                font-weight="700"
                fill="{color}">
                {esc(key)}
            </text>

            <text
                x="145"
                y="{y}"
                font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
                font-size="14"
                fill="{TEXT}">
                {esc(value)}
            </text>
        </g>
        '''
    )

svg.append(
    f'''
    <text
        x="28"
        y="285"
        font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
        font-size="12"
        fill="{MUTED}">
        github.com/idann1idann-create
    </text>
    '''
)

svg.append("</svg>")

OUTPUT.write_text("\n".join(svg), encoding="utf-8")

print(f"Created {OUTPUT}")
