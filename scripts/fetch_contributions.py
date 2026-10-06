import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "idann1idann-create"
OUTPUT = Path("data/contributions.json")


def extract_count(text: str) -> int:
    if not text:
        return 0

    if text.lower().startswith("no contributions"):
        return 0

    match = re.search(r"([\d,]+)\s+contribution", text, re.IGNORECASE)

    if match:
        return int(match.group(1).replace(",", ""))

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

    for cell in soup.select(".ContributionCalendar-day"):
        date = cell.get("data-date")

        if not date:
            continue

        count = 0

        cell_id = cell.get("id")

        # GitHub now stores the readable contribution count
        # in a tooltip associated with the calendar cell.
        if cell_id:
            tooltip = soup.find("tool-tip", attrs={"for": cell_id})

            if tooltip:
                count = extract_count(
                    tooltip.get_text(" ", strip=True)
                )

        # Fallback for older GitHub markup
        if count == 0:
            aria = cell.get("aria-label", "")

            if aria:
                count = extract_count(aria)

        days.append({
            "date": date,
            "count": count
        })

    if not days:
        raise RuntimeError(
            "No contribution cells found. GitHub may have changed its HTML."
        )

    days.sort(key=lambda x: x["date"])

    total = sum(day["count"] for day in days)

    best_day = max(
        days,
        key=lambda x: x["count"]
    )

    longest_streak = 0
    run = 0

    for day in days:
        if day["count"] > 0:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 0

    current_streak = 0

    for day in reversed(days):
        if day["count"] > 0:
            current_streak += 1
        else:
            break

    monthly = {}

    for day in days:
        month = day["date"][:7]
        monthly[month] = monthly.get(month, 0) + day["count"]

    data = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
        "days": days
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print(f"Saved contribution data to {OUTPUT}")
    print(f"Total public contributions: {total}")
    print(f"Current streak: {current_streak}")
    print(f"Longest streak: {longest_streak}")
    print(f"Best day: {best_day}")


if __name__ == "__main__":
    main()
