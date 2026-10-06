import json
from datetime import datetime
from pathlib import Path


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]

BG = "#0d1117"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
BORDER = "#30363d"

CELL = 11
GAP = 3

LEFT = 42
TOP = 48

WEEKS = 53
DAYS = 7

GRID_W = WEEKS * (CELL + GAP)
GRID_H = DAYS * (CELL + GAP)

WIDTH = 860
HEIGHT = 210


def level_for(count: int, max_count: int) -> int:
    if count <= 0:
        return 0

    if max_count <= 1:
        return 5

    ratio = count / max_count

    if ratio <= 0.2:
        return 1
    if ratio <= 0.4:
        return 2
    if ratio <= 0.6:
        return 3
    if ratio <= 0.8:
        return 4

    return 5


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            "data/contributions.json was not found. "
            "Run fetch_contributions.py first."
        )

    data = json.loads(INPUT.read_text(encoding="utf-8"))

    days = data["days"]

    if not days:
        raise RuntimeError("No contribution data found.")

    counts = [d["count"] for d in days]
    max_count = max(counts) if counts else 0

    day_map = {
        d["date"]: d["count"]
        for d in days
    }

    parsed_dates = [
        datetime.strptime(d["date"], "%Y-%m-%d").date()
        for d in days
    ]

    first_date = min(parsed_dates)
    # Move start date back to Sunday
    start_date = first_date

    while start_date.weekday() != 6:
        from datetime import timedelta
        start_date -= timedelta(days=1)

    svg = []

    svg.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{WIDTH}"
        height="{HEIGHT}"
        viewBox="0 0 {WIDTH} {HEIGHT}"
        role="img"
        aria-labelledby="heatmap-title">'''
    )

    svg.append(
        f'''
        <title id="heatmap-title">Public GitHub contributions by day</title>
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
        <style>
            .cell {{
                opacity: 0;
                transform: translateY(-8px);
                animation:
                    reveal 0.38s ease-out forwards;
            }}

            @keyframes reveal {{
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        </style>
        '''
    )

    svg.append(
        f'''
        <text
            x="24"
            y="28"
            font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
            font-size="14"
            font-weight="700"
            fill="{TEXT}">
            contribution activity
        </text>
        '''
    )

    # Weekday labels
    weekday_labels = [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri"),
    ]

    for row, label in weekday_labels:
        y = TOP + row * (CELL + GAP) + CELL

        svg.append(
            f'''
            <text
                x="8"
                y="{y}"
                font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
                font-size="10"
                fill="{MUTED}">
                {label}
            </text>
            '''
        )

    from datetime import timedelta

    for week in range(WEEKS):
        for day in range(DAYS):
            current_date = start_date + timedelta(
                days=week * 7 + day
            )

            date_str = current_date.isoformat()

            count = day_map.get(date_str, 0)

            level = level_for(count, max_count)
            color = PALETTE[level]

            x = LEFT + week * (CELL + GAP)
            y = TOP + day * (CELL + GAP)

            delay = (week + day) * 0.012

            svg.append(
                f'''
                <rect
                    class="cell"
                    x="{x}"
                    y="{y}"
                    width="{CELL}"
                    height="{CELL}"
                    rx="2"
                    fill="{color}"
                    style="animation-delay:{delay:.3f}s">
                    <title>{date_str}: {count} contributions</title>
                </rect>
                '''
            )

    legend_y = TOP + GRID_H + 18
    legend_x = WIDTH - 205

    svg.append(
        f'''
        <text
            x="{legend_x}"
            y="{legend_y}"
            font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
            font-size="10"
            fill="{MUTED}">
            Less
        </text>
        '''
    )

    for i, color in enumerate(PALETTE):
        x = legend_x + 32 + i * 16

        svg.append(
            f'''
            <rect
                x="{x}"
                y="{legend_y - 10}"
                width="10"
                height="10"
                rx="2"
                fill="{color}"/>
            '''
        )

    svg.append(
        f'''
        <text
            x="{legend_x + 136}"
            y="{legend_y}"
            font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
            font-size="10"
            fill="{MUTED}">
            More
        </text>
        '''
    )

    total = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)

    refreshed = data.get("generated_at", "")[:10] or "unknown"
    footer = (
        f"{total:,} public contributions · updated {refreshed} UTC"
        f"  ·  current streak {current_streak}"
        f"  ·  longest {longest_streak}"
    )

    svg.append(
        f'''
        <text
            x="24"
            y="{HEIGHT - 18}"
            font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
            font-size="11"
            fill="{MUTED}">
            {esc(footer)}
        </text>
        '''
    )

    svg.append("</svg>")

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
