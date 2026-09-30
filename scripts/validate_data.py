#!/usr/bin/env python3
"""Validate the published intelligence dataset without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


REQUIRED_ITEM_FIELDS = {
    "id": str,
    "title": str,
    "summary": str,
    "pm_takeaway": str,
    "action": str,
    "published_at": str,
    "brand": str,
    "market": str,
    "category": str,
    "signal_type": str,
    "impact": str,
    "score": (int, float),
    "confidence": int,
    "source": str,
    "source_tier": str,
    "source_url": str,
    "tags": list,
}
VALID_CATEGORIES = {
    "品牌与扩张",
    "产品与包装",
    "营销与内容",
    "渠道与电商",
    "物流与履约",
    "支付与金融",
    "政策与合规",
    "市场与消费",
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"Cannot parse {path}: {error}"]

    if payload.get("version") != 1:
        errors.append("version must be 1")
    if not isinstance(payload.get("meta"), dict):
        errors.append("meta must be an object")
    items = payload.get("items")
    if not isinstance(items, list):
        return errors + ["items must be an array"]
    if not items:
        errors.append("items must not be empty")

    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        prefix = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field, expected_type in REQUIRED_ITEM_FIELDS.items():
            if field not in item:
                errors.append(f"{prefix}.{field} is missing")
            elif not isinstance(item[field], expected_type):
                errors.append(f"{prefix}.{field} has the wrong type")

        item_id = item.get("id")
        if isinstance(item_id, str):
            if item_id in seen_ids:
                errors.append(f"{prefix}.id is duplicated: {item_id}")
            seen_ids.add(item_id)

        if item.get("category") not in VALID_CATEGORIES:
            errors.append(f"{prefix}.category is invalid: {item.get('category')}")
        if item.get("impact") not in {"opportunity", "risk", "mixed"}:
            errors.append(f"{prefix}.impact is invalid: {item.get('impact')}")
        if item.get("source_tier") not in {"A", "B", "C", "D"}:
            errors.append(f"{prefix}.source_tier is invalid")

        score = item.get("score")
        if isinstance(score, (int, float)) and not 0 <= score <= 10:
            errors.append(f"{prefix}.score must be between 0 and 10")
        confidence = item.get("confidence")
        if isinstance(confidence, int) and not 0 <= confidence <= 100:
            errors.append(f"{prefix}.confidence must be between 0 and 100")

        source_url = item.get("source_url")
        if isinstance(source_url, str):
            parsed = urlsplit(source_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                errors.append(f"{prefix}.source_url must be an absolute HTTP(S) URL")

        published_at = item.get("published_at")
        if isinstance(published_at, str):
            try:
                datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{prefix}.published_at is not ISO-8601")

        for field in ("title", "summary", "pm_takeaway", "action"):
            value = item.get(field)
            if isinstance(value, str):
                if not value.strip():
                    errors.append(f"{prefix}.{field} must not be empty")
                if re.search(r"<[^>]+>", value):
                    errors.append(f"{prefix}.{field} contains HTML")

    meta = payload.get("meta", {})
    if isinstance(meta, dict):
        for field in ("generated_at", "window_start", "window_end", "review_mode", "next_run_at"):
            if not isinstance(meta.get(field), str) or not meta.get(field):
                errors.append(f"meta.{field} must be a non-empty string")
        health = meta.get("source_health")
        if not isinstance(health, dict):
            errors.append("meta.source_health must be an object")
        elif health.get("healthy", 0) + health.get("delayed", 0) != health.get("total"):
            errors.append("meta.source_health counts do not add up")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/intel.json"))
    args = parser.parse_args()
    errors = validate(args.data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validated {args.data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
