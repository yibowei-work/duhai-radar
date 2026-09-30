#!/usr/bin/env python3
"""Collect public cross-border intelligence into a deterministic JSON dataset."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, time as dt_time, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("Asia/Shanghai")
TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "spm",
    "source",
}
BRANDS = {
    "shein": "希音",
    "temu": "拼多多跨境平台",
    "miniso": "名创优品",
    "pop mart": "泡泡玛特",
    "泡泡玛特": "泡泡玛特",
    "anker": "安克创新",
    "安克": "安克创新",
    "ecoflow": "正浩创新",
    "roborock": "石头科技",
    "石头科技": "石头科技",
    "byd": "比亚迪",
    "比亚迪": "比亚迪",
    "chagee": "霸王茶姬",
    "霸王茶姬": "霸王茶姬",
    "luckin": "瑞幸咖啡",
    "瑞幸": "瑞幸咖啡",
    "aliexpress": "全球速卖通",
    "tiktok shop": "抖音海外电商平台",
    "菜鸟": "菜鸟",
    "ant international": "蚂蚁国际",
    "蚂蚁国际": "蚂蚁国际",
}
CATEGORY_KEYWORDS = {
    "政策与合规": [
        "regulation",
        "tariff",
        "customs",
        "compliance",
        "recall",
        "sanction",
        "safety",
        "vat",
        "关税",
        "海关",
        "合规",
        "召回",
        "监管",
        "法规",
        "处罚",
    ],
    "物流与履约": [
        "logistics",
        "fulfillment",
        "warehouse",
        "delivery",
        "shipping",
        "port",
        "物流",
        "履约",
        "仓储",
        "海外仓",
        "配送",
        "航线",
    ],
    "支付与金融": [
        "payment",
        "checkout",
        "fintech",
        "wallet",
        "fraud",
        "settlement",
        "支付",
        "收款",
        "结算",
        "钱包",
        "金融",
        "汇率",
    ],
    "营销与内容": [
        "campaign",
        "creator",
        "influencer",
        "livestream",
        "advertising",
        "marketing",
        "联名",
        "营销",
        "达人",
        "直播",
        "广告",
        "内容",
    ],
    "产品与包装": [
        "product launch",
        "packaging",
        "materials",
        "category expansion",
        "新品",
        "包装",
        "材料",
        "品类",
        "产品",
    ],
    "渠道与电商": [
        "e-commerce",
        "ecommerce",
        "marketplace",
        "seller",
        "shopify",
        "amazon",
        "platform",
        "电商",
        "平台",
        "卖家",
        "渠道",
        "独立站",
    ],
    "市场与消费": [
        "earnings",
        "revenue",
        "consumer",
        "gmv",
        "sales",
        "财报",
        "收入",
        "消费",
        "销售",
        "趋势",
    ],
    "品牌与扩张": [
        "expansion",
        "store",
        "overseas",
        "global",
        "international",
        "market entry",
        "出海",
        "海外",
        "全球",
        "开店",
        "扩张",
        "进入",
    ],
}
RISK_KEYWORDS = [
    "recall",
    "ban",
    "penalty",
    "investigation",
    "lawsuit",
    "decline",
    "tariff",
    "sanction",
    "warning",
    "召回",
    "禁令",
    "处罚",
    "调查",
    "诉讼",
    "下滑",
    "关税",
    "风险",
]
OPPORTUNITY_KEYWORDS = [
    "launch",
    "growth",
    "expand",
    "partnership",
    "milestone",
    "opens",
    "new market",
    "增长",
    "上线",
    "发布",
    "合作",
    "开业",
    "新市场",
    "里程碑",
]
MARKETS = {
    "united states": "美国",
    "u.s.": "美国",
    " us ": "美国",
    "美国": "美国",
    "european union": "欧盟",
    "eu ": "欧盟",
    "欧盟": "欧盟",
    "europe": "欧洲",
    "欧洲": "欧洲",
    "singapore": "新加坡",
    "新加坡": "新加坡",
    "spain": "西班牙",
    "西班牙": "西班牙",
    "japan": "日本",
    "日本": "日本",
    "southeast asia": "东南亚",
    "东南亚": "东南亚",
    "middle east": "中东",
    "中东": "中东",
    "latin america": "拉美",
    "拉美": "拉美",
    "global": "全球",
    "全球": "全球",
}
PM_LENS = {
    "品牌与扩张": (
        "把扩张拆成获客、复购与本地经营三个阶段，不只看门店或商品交易总额。",
        "记录进入节奏、渠道结构与本地团队配置，建立市场进入对照表。",
    ),
    "产品与包装": (
        "判断底层能力能否跨品类复用，并把包装材料与法规证据纳入商品数据。",
        "挑一个代表性商品款，补齐材料、标签、证据与替代方案字段。",
    ),
    "营销与内容": (
        "把内容看作交易系统的一部分，联动选品、库存、达人和复购。",
        "拆解一次活动从素材到成交的完整漏斗，并记录可复用模块。",
    ),
    "渠道与电商": (
        "平台规则变化最终会落到流量、费用、履约门槛和商家毛利。",
        "更新平台政策日志，并重算一个代表性商品款的单位经济。",
    ),
    "物流与履约": (
        "只有进入商品页承诺、订单轨迹和异常补偿，物流才成为用户体验。",
        "对比三个市场的预计送达、轨迹完整度、退货入口与补偿规则。",
    ),
    "支付与金融": (
        "支付创新要同时观察转化率、授权体验、拒付与跨境结算成本。",
        "画出一次跨境支付的授权、风控、清算与争议链路。",
    ),
    "政策与合规": (
        "规则不是发布日一次性事件，要持续跟踪生效日、实施细则与执法案例。",
        "把生效日期、适用品类、证据要求和负责人写进合规日历。",
    ),
    "市场与消费": (
        "总量增长可能掩盖同店、复购、折扣与渠道库存的结构性变化。",
        "按市场和用户分组拆分增长，补看复购、退货和折扣深度。",
    ),
}


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", value, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def has_chinese_text(value: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", value))


def clip_text(value: str, limit: int = 220) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip("，。,. ;；") + "…"


def canonicalize_url(value: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(value.strip())
    except ValueError:
        return value.strip()
    query = []
    for key, item in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in TRACKING_PARAMS:
            continue
        query.append((key, item))
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, urllib.parse.urlencode(sorted(query)), "")
    )


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    try:
        parsed = parsedate_to_datetime(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=TIMEZONE)
        return parsed
    except (TypeError, ValueError, OverflowError):
        pass
    if re.fullmatch(r"\d{8}T\d{6}Z", raw):
        return datetime.strptime(raw, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=TIMEZONE)
    except ValueError:
        return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_value(node: ET.Element, names: tuple[str, ...]) -> str:
    for child in node:
        if _local_name(child.tag) in names:
            if child.text and child.text.strip():
                return child.text.strip()
            if child.attrib.get("href"):
                return child.attrib["href"].strip()
    return ""


def parse_feed(payload: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(payload)
    records: list[dict[str, str]] = []
    for node in root.iter():
        if _local_name(node.tag) not in {"item", "entry"}:
            continue
        link = _child_value(node, ("link", "guid", "id"))
        records.append(
            {
                "title": _child_value(node, ("title",)),
                "url": link,
                "summary": _child_value(node, ("description", "summary", "content")),
                "published_at": _child_value(
                    node, ("pubdate", "published", "updated", "date")
                ),
                "source": _child_value(node, ("source",)),
            }
        )
    return records


def request_bytes(url: str, user_agent: str, retries: int = 2) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": user_agent,
                    "Accept": "application/json, application/rss+xml, application/atom+xml, text/xml;q=0.9, */*;q=0.5",
                },
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt < retries:
                time.sleep((2**attempt) + random.random())
    assert last_error is not None
    raise last_error


def fetch_source(
    source: dict[str, Any], start: date, end: date, user_agent: str
) -> list[dict[str, str]]:
    kind = source["kind"]
    if kind == "rss":
        return parse_feed(request_bytes(source["url"], user_agent))

    if kind == "gdelt":
        params = {
            "query": source["query"],
            "mode": "ArtList",
            "maxrecords": str(source.get("max_records", 100)),
            "format": "json",
            "startdatetime": start.strftime("%Y%m%d000000"),
            "enddatetime": (end + timedelta(days=1)).strftime("%Y%m%d000000"),
            "sort": "DateDesc",
        }
        url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(params)
        payload = json.loads(request_bytes(url, user_agent))
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "summary": item.get("title", ""),
                "published_at": item.get("seendate", ""),
                "source": item.get("domain", source["label"]),
            }
            for item in payload.get("articles", [])
        ]

    if kind == "federal_register":
        params = {
            "per_page": "100",
            "order": "newest",
            "conditions[term]": source["query"],
            "conditions[publication_date][gte]": start.isoformat(),
            "conditions[publication_date][lte]": end.isoformat(),
        }
        url = "https://www.federalregister.gov/api/v1/documents.json?" + urllib.parse.urlencode(params)
        payload = json.loads(request_bytes(url, user_agent))
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("html_url", ""),
                "summary": item.get("abstract", "") or item.get("title", ""),
                "published_at": item.get("publication_date", ""),
                "source": source["label"],
            }
            for item in payload.get("results", [])
        ]

    raise ValueError(f"Unsupported source kind: {kind}")


def classify_category(text: str, fallback: str) -> str:
    lowered = text.lower()
    scores = {
        category: sum(1 for keyword in keywords if keyword in lowered)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else fallback


def classify_impact(text: str) -> str:
    lowered = text.lower()
    risk = sum(1 for keyword in RISK_KEYWORDS if keyword in lowered)
    opportunity = sum(1 for keyword in OPPORTUNITY_KEYWORDS if keyword in lowered)
    if risk and opportunity:
        return "mixed"
    if risk:
        return "risk"
    if opportunity:
        return "opportunity"
    return "mixed"


def detect_brand(text: str, source: dict[str, Any]) -> str:
    lowered = text.lower()
    for keyword, brand in BRANDS.items():
        if keyword in lowered:
            return brand
    if source["kind"] == "federal_register":
        return "美国监管"
    if source["id"] == "shopify-changelog":
        return "Shopify"
    return "行业基础设施"


def detect_market(text: str) -> str:
    lowered = f" {text.lower()} "
    for keyword, market in MARKETS.items():
        if keyword in lowered:
            return market
    return "多市场"


def infer_signal_type(category: str, text: str) -> str:
    lowered = text.lower()
    options = [
        ("recall", ["recall", "召回"]),
        ("tariff_change", ["tariff", "关税"]),
        ("regulation_effective", ["regulation", "rule", "法规", "监管"]),
        ("warehouse_open", ["warehouse", "fulfillment center", "海外仓"]),
        ("store_open", ["store", "门店", "开店"]),
        ("product_launch", ["launch", "新品", "发布"]),
        ("campaign_launch", ["campaign", "营销", "活动"]),
        ("payment_method", ["payment", "wallet", "支付", "钱包"]),
        ("earnings", ["earnings", "revenue", "gmv", "财报", "收入"]),
        ("platform_rule", ["platform", "seller", "平台", "卖家"]),
    ]
    for signal_type, keywords in options:
        if any(keyword in lowered for keyword in keywords):
            return signal_type
    return {
        "品牌与扩张": "market_entry",
        "产品与包装": "category_expansion",
        "营销与内容": "campaign_launch",
        "渠道与电商": "platform_rule",
        "物流与履约": "logistics_route",
        "支付与金融": "checkout_change",
        "政策与合规": "regulation_proposed",
        "市场与消费": "consumer_trend",
    }[category]


def normalize_title(value: str) -> str:
    return re.sub(r"[^0-9a-z\u3400-\u9fff]+", "", value.lower())


def source_confidence(tier: str) -> int:
    return {"A": 93, "B": 84, "C": 70, "D": 52}.get(tier, 60)


def to_item(
    raw: dict[str, str],
    source: dict[str, Any],
    relevance_keywords: list[str],
    start: date,
    end: date,
) -> dict[str, Any] | None:
    title = clean_text(raw.get("title"))
    url = canonicalize_url(raw.get("url", ""))
    summary = clean_text(raw.get("summary"))
    published = parse_datetime(raw.get("published_at"))
    if not title or not url or not published or not url.startswith(("http://", "https://")):
        return None
    if not has_chinese_text(title):
        return None
    if summary and not has_chinese_text(summary):
        summary = ""
    local_date = published.astimezone(TIMEZONE).date()
    if local_date < start or local_date > end:
        return None

    combined = f"{title} {summary}"
    lowered = combined.lower()
    if not source.get("always_relevant") and not any(
        keyword.lower() in lowered for keyword in relevance_keywords
    ):
        return None

    category = classify_category(combined, source["default_category"])
    impact = classify_impact(combined)
    brand = detect_brand(combined, source)
    market = detect_market(combined)
    tier = source["tier"]
    takeaway, action = PM_LENS[category]

    score = 6.4 + {"A": 1.4, "B": 0.8, "C": 0.3, "D": 0}.get(tier, 0)
    if not source.get("discovery_only"):
        score += 0.3
    if brand != "行业基础设施":
        score += 0.3
    if (end - local_date).days <= 2:
        score += 0.4
    if impact in {"opportunity", "risk"}:
        score += 0.2
    score = round(min(score, 9.4), 1)

    clean_summary = clip_text(summary or "该来源发布了与中国品牌出海相关的新变化，详情请查看原始来源。")
    item_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:18]
    source_name = clean_text(raw.get("source")) or source["label"]

    tags = []
    for value in (category, market, brand):
        if value not in tags and value not in {"多市场", "行业基础设施"}:
            tags.append(value)

    return {
        "id": f"intel-{item_id}",
        "title": clip_text(title, 160),
        "summary": clean_summary,
        "pm_takeaway": takeaway,
        "action": action,
        "published_at": published.isoformat(timespec="seconds"),
        "brand": brand,
        "market": market,
        "category": category,
        "signal_type": infer_signal_type(category, combined),
        "impact": impact,
        "stage": "reported",
        "score": score,
        "confidence": source_confidence(tier),
        "source": clip_text(source_name, 80),
        "source_tier": tier,
        "source_url": url,
        "tags": tags,
    }


def merge_items(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in existing}
    title_index = {normalize_title(item["title"]): item["id"] for item in existing}
    tier_rank = {"A": 4, "B": 3, "C": 2, "D": 1}

    for item in incoming:
        title_key = normalize_title(item["title"])
        duplicate_id = title_index.get(title_key)
        if duplicate_id and duplicate_id != item["id"]:
            current = by_id[duplicate_id]
            if tier_rank.get(item["source_tier"], 0) > tier_rank.get(current["source_tier"], 0):
                item["id"] = duplicate_id
                by_id[duplicate_id] = item
            continue
        by_id[item["id"]] = item
        title_index[title_key] = item["id"]

    return sorted(
        by_id.values(),
        key=lambda item: (item["published_at"], item["score"], item["id"]),
        reverse=True,
    )[:300]


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=Path("data/intel.json"))
    parser.add_argument("--state", type=Path, default=Path("data/state/schedule.json"))
    parser.add_argument("--report", type=Path, default=Path("work/collector-report.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    config = json.loads(args.sources.read_text(encoding="utf-8"))
    existing = json.loads(args.data.read_text(encoding="utf-8")) if args.data.exists() else {"version": 1, "items": []}
    start = date.fromisoformat(plan["coverage_start"])
    end = date.fromisoformat(plan["coverage_end"])
    sources = [source for source in config["sources"] if source.get("enabled", True)]

    incoming: list[dict[str, Any]] = []
    successes: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for source in sources:
        try:
            records = fetch_source(source, start, end, config["user_agent"])
            accepted = 0
            for raw in records:
                item = to_item(raw, source, config["relevance_keywords"], start, end)
                if item:
                    incoming.append(item)
                    accepted += 1
            successes.append(
                {"id": source["id"], "fetched": len(records), "accepted": accepted}
            )
            print(f"✓ {source['label']}: {accepted}/{len(records)} accepted")
        except Exception as error:  # isolate third-party source failures
            failures.append(
                {"id": source["id"], "error": f"{type(error).__name__}: {str(error)[:240]}"}
            )
            print(f"! {source['label']}: {type(error).__name__}: {error}", file=sys.stderr)

    report = {
        "generated_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
        "coverage_start": start.isoformat(),
        "coverage_end": end.isoformat(),
        "successes": successes,
        "failures": failures,
        "incoming_items": len(incoming),
    }
    atomic_json(args.report, report)

    if not successes:
        print("All sources failed; preserving the last successful dataset.", file=sys.stderr)
        return 10

    merged = merge_items(existing.get("items", []), incoming)
    reasons = [window["reason"] for window in plan["windows"]]
    review_mode = (
        "monthly_previous_month"
        if "monthly_previous_month" in reasons
        else "weekly_month_to_date"
        if "weekly_month_to_date" in reasons
        else "daily_3d"
    )
    due = date.fromisoformat(plan["due_anchor"])
    next_run = datetime.combine(due + timedelta(days=1), dt_time(11, 0), TIMEZONE)
    now = datetime.now(TIMEZONE)
    output = {
        "version": 1,
        "meta": {
            "generated_at": now.isoformat(timespec="seconds"),
            "window_start": start.isoformat(),
            "window_end": end.isoformat(),
            "review_mode": review_mode,
            "next_run_at": next_run.isoformat(timespec="seconds"),
            "source_health": {
                "healthy": len(successes),
                "delayed": len(failures),
                "total": len(sources),
            },
        },
        "items": merged,
    }
    atomic_json(args.data, output)
    atomic_json(
        args.state,
        {
            "version": 1,
            "last_completed_anchor": plan["due_anchor"],
            "last_success_at": now.isoformat(timespec="seconds"),
            "last_review_mode": review_mode,
            "source_failures": failures,
        },
    )
    print(f"Published {len(merged)} total items ({len(incoming)} accepted this run).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
