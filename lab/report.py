"""Build a deterministic month-end evidence packet from normalized inputs."""
import argparse
import calendar
import json
import re
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SAMPLE = Path(__file__).resolve().parents[1] / "fixtures" / "dealer-month.json"
ENTITY = "north-store"
PERIOD = "2026-09"


class InputError(ValueError):
    """A source cannot support the requested decision."""


def require(condition, message):
    if not condition:
        raise InputError(message)


def mapping(value, name):
    require(isinstance(value, dict), f"{name} must be an object")
    return value


def ident(value, name):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", value),
            f"{name} must be a short source identifier")
    return value


def integer(record, key):
    value = record.get(key)
    require(type(value) is int and abs(value) < 10**16, f"Invalid integer for {key}")
    return value


def date_field(record, key):
    value = record.get(key)
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value),
            f"Expected ISO date for {key}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"Invalid calendar date for {key}") from exc


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON field")
        result[key] = value
    return result


def load_snapshot(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def rounded(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def build_packet(snapshot, entity, period):
    mapping(snapshot, "Snapshot")
    ident(entity, "Requested entity")
    require(isinstance(period, str) and re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", period)
            and not period.startswith("0000"), "Expected YYYY-MM period")
    start = date.fromisoformat(period + "-01")
    end = start.replace(day=calendar.monthrange(start.year, start.month)[1])
    require(snapshot.get("entity") == entity and snapshot.get("period") == period,
            "Snapshot does not match requested entity and period")

    sources = {}
    for name in ("crm", "pl", "policy"):
        record = mapping(snapshot.get(name), name)
        require(record.get("entity") == entity, f"Entity mismatch in {name}")
        sources[name] = ident(record.get("ref"), name + " reference")
    crm, pl, policy = (snapshot[key] for key in ("crm", "pl", "policy"))
    require(crm.get("currency") == pl.get("currency") == "USD", "Pilot requires USD sources")
    require(date_field(crm, "as_of") == end, "CRM needs a month-end snapshot")
    require(pl.get("period") == period and pl.get("closed") is True
            and pl.get("basis") == "accrual", "P&L must be closed, accrual and in period")
    require(date_field(policy, "effective_from") <= start and date_field(policy, "effective_through") >= end,
            "Policy must cover the entire period")

    deals = crm.get("open_deals")
    require(isinstance(deals, list), "Missing open deals snapshot")
    seen = set()
    pipeline = 0
    for deal in deals:
        mapping(deal, "Deal")
        deal_id = ident(deal.get("id"), "Deal ID")
        require(deal_id not in seen, "Duplicate deal ID")
        seen.add(deal_id)
        amount = integer(deal, "amount_cents")
        require(amount >= 0, "Negative deal value")
        pipeline += amount

    income = integer(pl, "income_cents")
    cogs = integer(pl, "cogs_cents")
    require(income > 0, "Positive recognized income required to calculate margin")
    gross = income - cogs
    require(gross == integer(pl, "gross_profit_cents"), "Gross profit fails source tie-out")
    floor = integer(policy, "floor_bps")
    require(0 <= floor <= 10000, "Policy floor must be 0 to 10000 basis points")
    margin = Decimal(gross) * 100 / income
    floor_pct = Decimal(floor) / 100
    gap = Decimal(gross) - Decimal(income) * floor / 10000
    return {
        "entity": entity, "period": period, "status": "draft_for_review", "currency": "USD",
        "sources": sources, "open_deal_count": len(deals), "open_pipeline_cents": pipeline,
        "income_cents": income, "cogs_cents": cogs, "gross_profit_cents": gross,
        "gross_margin_pct": str(rounded(margin)), "policy_floor_pct": str(rounded(floor_pct)),
        "variance_percentage_points": str(rounded(margin - floor_pct)),
        "profit_variance_usd": str(rounded(gap / 100)),
        "threshold_result": "below_floor" if gap < 0 else "meets_floor"
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SAMPLE)
    parser.add_argument("--entity", default=ENTITY)
    parser.add_argument("--period", default=PERIOD)
    args = parser.parse_args()
    try:
        packet = build_packet(load_snapshot(args.input), args.entity, args.period)
    except (ValueError, OSError) as exc:
        print(f"Report held: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(packet, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
