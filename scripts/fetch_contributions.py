import json
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "idann1idann-create"
OUTPUT = Path("data/contributions.json")


def parse_count(text: str) -> int:
    if not text:
        return 0

    text = text.replace(",", "").strip()

    parts = text.split()
    for part in parts:
        if part.isdigit():
            return int(part)

    return 0


def main():
    url = f"https://github.com/users/{USERNAME}/contributions"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    days = []

    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")

        if not date:
            continue

        count = 0

        aria = cell.get("aria-label", "")
        if aria:
            count = parse_count(aria)

        days.append({
            "date": date,
            "count": count
        })

    if not days:
        raise RuntimeError(
            "No contribution cells found. GitHub may have changed the HTML structure."
        )

    days.sort(key=lambda x: x["date"])

    counts = [d["count"] for d in days]

    total = sum(counts)

    best_day = max(
        days,
        key=lambda x: x["count"]
    )

    longest_streak = 0
    current_run = 0

    for d in days:
        if d["count"] > 0:
            current_run += 1
            longest_streak = max(longest_streak, current_run)
        else:
            current_run = 0

    current_streak = 0

    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    monthly = {}

    for d in days:
        month = d["date"][:7]
        monthly.setdefault(month, 0)
        monthly[month] += d["count"]

    data = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
        "days": days,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print(f"Saved contribution data to {OUTPUT}")
    print(f"Total contributions: {total}")
    print(f"Current streak: {current_streak}")
    print(f"Longest streak: {longest_streak}")
    print(f"Best day: {best_day}")


if __name__ == "__main__":
    main()
