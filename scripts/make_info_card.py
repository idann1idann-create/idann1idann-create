import os
from html import escape
from pathlib import Path

OUTPUT = Path("info-card.svg")
FONT = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
rows = [
    ("Now", ["Building Osto / Atlas"], "#39d353"),
    ("Prev", ["Financial Planner"], "#58a6ff"),
    ("Stack", ["Python · React · AI"], "#bc8cff"),
    ("Focus", ["Finance · Automation", "Agents"], "#d29922"),
]


def render_svg(static=False):
    animation = "" if static else """
      <style>
        @media (prefers-reduced-motion: no-preference) {
          .info-row { animation: reveal .35s ease-out backwards; }
        }
        @keyframes reveal { from { opacity: 0; } to { opacity: 1; } }
      </style>"""
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="430" height="430"
      viewBox="0 0 430 430" role="img" aria-labelledby="info-title info-desc">
      <title id="info-title">Idan — developer profile</title>
      <desc id="info-desc">Building Osto / Atlas. Previously Financial Planner. Python, React and AI. Finance, automation and agents.</desc>
      <rect x="0.5" y="0.5" width="429" height="429" rx="14" fill="#0d1117" stroke="#30363d"/>
      {animation}
      <g font-family="{FONT}">
        <text x="24" y="40" font-size="20" font-weight="700" fill="#c9d1d9">idan@github</text>
        <text x="24" y="65" font-size="12" fill="#919ba5">builder / finance / automation</text>
        <path d="M24 82H406" stroke="#30363d"/>''']
    for i, (key, lines, color) in enumerate(rows):
        y = 126 + i * 54
        svg.append(f'<g class="info-row" style="animation-delay:{i * .12:.2f}s">')
        svg.append(f'<text x="24" y="{y}" font-size="15" font-weight="700" fill="{color}">{escape(key)}</text>')
        for j, value in enumerate(lines):
            svg.append(f'<text x="100" y="{y + j * 22}" font-size="15" fill="#c9d1d9">{escape(value)}</text>')
        svg.append('</g>')
    svg.extend([
        '<path d="M24 372H406" stroke="#30363d"/>',
        '<text x="24" y="398" font-size="12" fill="#919ba5">github.com/idann1idann-create</text>',
        '</g></svg>',
    ])
    return "\n".join(line.rstrip() for line in "\n".join(svg).splitlines())


if __name__ == "__main__":
    OUTPUT.write_text(render_svg(static=os.getenv("STATIC") == "1"), encoding="utf-8")
    print(f"Created {OUTPUT}")
