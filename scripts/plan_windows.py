#!/usr/bin/env python3
"""Plan deterministic Shanghai-time collection windows."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Shanghai")
RUN_AT = time(11, 0)
MAX_CATCH_UP_DAYS = 62


def due_anchor(now: datetime | None = None) -> date:
    """Return the latest local date whose 11:00 run is due."""
    local_now = (now or datetime.now(TIMEZONE)).astimezone(TIMEZONE)
    if local_now.timetz().replace(tzinfo=None) < RUN_AT:
        return local_now.date() - timedelta(days=1)
    return local_now.date()


def windows_for(anchor: date, mode: str = "auto") -> list[dict[str, str]]:
    """Return inclusive date windows for one planned local anchor."""
    windows: list[dict[str, str]] = []

    if mode in {"auto", "daily"}:
        windows.append(
            {
                "start": (anchor - timedelta(days=2)).isoformat(),
                "end": anchor.isoformat(),
                "reason": "daily_3d",
                "anchor": anchor.isoformat(),
            }
        )

    if mode == "weekly" or (mode == "auto" and anchor.weekday() == 6):
        windows.append(
            {
                "start": anchor.replace(day=1).isoformat(),
                "end": anchor.isoformat(),
                "reason": "weekly_month_to_date",
                "anchor": anchor.isoformat(),
            }
        )

    if mode == "monthly" or (mode == "auto" and anchor.day == 1):
        previous_end = anchor - timedelta(days=1)
        windows.append(
            {
                "start": previous_end.replace(day=1).isoformat(),
                "end": previous_end.isoformat(),
                "reason": "monthly_previous_month",
                "anchor": anchor.isoformat(),
            }
        )

    if mode not in {"auto", "daily", "weekly", "monthly"}:
        raise ValueError(f"Unsupported mode: {mode}")

    return windows


def _read_last_completed(state_path: Path) -> date | None:
    if not state_path.exists():
        return None
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        value = payload.get("last_completed_anchor")
        return date.fromisoformat(value) if value else None
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def build_plan(
    *,
    anchor: date,
    mode: str,
    state_path: Path,
    generated_at: datetime | None = None,
) -> dict[str, object]:
    if mode == "auto":
        last_completed = _read_last_completed(state_path)
        if last_completed and last_completed < anchor:
            gap = (anchor - last_completed).days
            if gap > MAX_CATCH_UP_DAYS:
                raise ValueError(
                    f"Catch-up window is {gap} days; maximum is {MAX_CATCH_UP_DAYS}. "
                    "Use a manual range after reviewing the source load."
                )
            anchors = [last_completed + timedelta(days=offset) for offset in range(1, gap + 1)]
        else:
            anchors = [anchor]
    else:
        anchors = [anchor]

    windows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for planned_anchor in anchors:
        for window in windows_for(planned_anchor, mode):
            signature = (window["start"], window["end"], window["reason"])
            if signature not in seen:
                seen.add(signature)
                windows.append(window)

    starts = [date.fromisoformat(window["start"]) for window in windows]
    ends = [date.fromisoformat(window["end"]) for window in windows]
    now = (generated_at or datetime.now(TIMEZONE)).astimezone(TIMEZONE)

    return {
        "version": 1,
        "timezone": "Asia/Shanghai",
        "schedule_time": "11:00",
        "generated_at": now.isoformat(timespec="seconds"),
        "due_anchor": anchor.isoformat(),
        "mode": mode,
        "anchors": [item.isoformat() for item in anchors],
        "windows": windows,
        "coverage_start": min(starts).isoformat(),
        "coverage_end": max(ends).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anchor", help="Shanghai date in YYYY-MM-DD; defaults to latest due run")
    parser.add_argument(
        "--mode",
        choices=("auto", "daily", "weekly", "monthly"),
        default="auto",
    )
    parser.add_argument("--state", type=Path, default=Path("data/state/schedule.json"))
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    anchor = date.fromisoformat(args.anchor) if args.anchor else due_anchor()
    plan = build_plan(anchor=anchor, mode=args.mode, state_path=args.state)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Planned {len(plan['windows'])} window(s) for {len(plan['anchors'])} anchor(s): "
        f"{plan['coverage_start']} → {plan['coverage_end']}"
    )


if __name__ == "__main__":
    main()
