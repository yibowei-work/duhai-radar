import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts.plan_windows import build_plan, due_anchor, windows_for


SHANGHAI = ZoneInfo("Asia/Shanghai")


class PlanningTests(unittest.TestCase):
    def test_due_anchor_before_and_after_run(self):
        self.assertEqual(
            due_anchor(datetime(2026, 9, 30, 10, 59, tzinfo=SHANGHAI)),
            date(2026, 9, 29),
        )
        self.assertEqual(
            due_anchor(datetime(2026, 9, 30, 11, 0, tzinfo=SHANGHAI)),
            date(2026, 9, 30),
        )

    def test_sunday_includes_month_to_date(self):
        windows = windows_for(date(2026, 9, 27), "auto")
        self.assertEqual([window["reason"] for window in windows], ["daily_3d", "weekly_month_to_date"])
        self.assertEqual(windows[1]["start"], "2026-09-01")

    def test_first_day_includes_previous_month(self):
        windows = windows_for(date(2026, 10, 1), "auto")
        monthly = next(window for window in windows if window["reason"] == "monthly_previous_month")
        self.assertEqual(monthly["start"], "2026-09-01")
        self.assertEqual(monthly["end"], "2026-09-30")

    def test_missed_sunday_is_replayed_on_monday(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state = Path(temp_dir) / "schedule.json"
            state.write_text(json.dumps({"last_completed_anchor": "2026-09-26"}), encoding="utf-8")
            plan = build_plan(anchor=date(2026, 9, 28), mode="auto", state_path=state)
        self.assertEqual(plan["anchors"], ["2026-09-27", "2026-09-28"])
        self.assertIn("weekly_month_to_date", [window["reason"] for window in plan["windows"]])


if __name__ == "__main__":
    unittest.main()
