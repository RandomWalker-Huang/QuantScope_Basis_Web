#!/usr/bin/env python3
"""Validate a self-contained QuantScope Basis GitHub Pages artifact."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_TENORS = {"近月", "次近月", "次远月", "最远月"}
EXPECTED_SYMBOLS = {"IM", "IC", "IH", "IF"}
TOP_LEVEL_KEYS = {"generated_at", "date_start", "date_end", "analysis", "default"}
ANALYSIS_KEYS = {
    "products", "series", "convergence", "errors", "tenors", "formula",
}
PRODUCT_KEYS = {"symbol", "future_name", "spot_code", "spot_name", "tenors"}
ROW_KEYS = {"date", "spot_price", "contracts"}
CONTRACT_KEYS = {"contract", "price", "expiry_date", "days_to_expiry"}
CONVERGENCE_ROW_KEYS = {
    "signal_date", "outcome_date", "near_contract", "far_contract",
    "holding_days", "far_days_to_expiry", "q_initial", "q_terminal",
    "static_roll_down", "actual_convergence", "toward_zero_convergence",
    "unexpected_convergence", "annualized_actual_convergence",
    "adverse_widening",
}
FORMULA_KEYS = {
    "difference", "annualized_spot_future", "annualized_future_spread",
    "log_basis", "annualized_log_spot_future",
    "annualized_log_future_spread", "day_count", "q_curve",
    "static_roll_down", "historical_convergence",
}
DEFAULT_KEYS = {
    "symbol", "display", "construction", "source_s", "source_f",
    "compare_f1", "compare_f2", "mode", "show_details",
}
SENSITIVE_KEY = re.compile(
    r"password|passwd|secret|token|api[_-]?key|credential|username|user_name",
    re.IGNORECASE,
)
FORBIDDEN_DATA_KEYS = {
    "open", "high", "low", "volume", "turnover", "open_interest",
    "bid", "ask", "settlement", "prev_settlement", "prev_close",
}


def fail(message: str) -> None:
    raise ValueError(message)


def assert_allowed_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    extra = set(value) - allowed
    if extra:
        fail(f"{label}出现未允许字段：{', '.join(sorted(extra))}")


def walk_keys(value: Any, path: str = "data") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_KEY.search(str(key)):
                fail(f"发现敏感字段：{path}.{key}")
            if str(key).lower() in FORBIDDEN_DATA_KEYS:
                fail(f"发现原始全量行情字段：{path}.{key}")
            walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_keys(child, f"{path}[{index}]")


def extract_payload(html: str) -> dict[str, Any]:
    match = re.search(
        r'<script\s+type="application/json"\s+id="basis-report-data">([\s\S]*?)</script>',
        html,
        re.IGNORECASE,
    )
    if not match:
        fail("没有找到 basis-report-data 处理后数据")
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        fail(f"处理后数据JSON无法解析：{exc}")
    if not isinstance(payload, dict):
        fail("处理后数据顶层必须是对象")
    return payload


def validate_payload(payload: dict[str, Any]) -> dict[str, int]:
    assert_allowed_keys(payload, TOP_LEVEL_KEYS, "顶层数据")
    analysis = payload.get("analysis")
    defaults = payload.get("default")
    if not isinstance(analysis, dict):
        fail("缺少 analysis 对象")
    if not isinstance(defaults, dict):
        fail("缺少 default 对象")
    assert_allowed_keys(analysis, ANALYSIS_KEYS, "analysis")
    assert_allowed_keys(defaults, DEFAULT_KEYS, "default")

    products = analysis.get("products")
    series = analysis.get("series")
    tenors = analysis.get("tenors")
    convergence = analysis.get("convergence", {})
    errors = analysis.get("errors", {})
    formula = analysis.get("formula", {})
    if not isinstance(products, list) or not products:
        fail("products为空")
    if not isinstance(series, dict) or not series:
        fail("series为空")
    if not isinstance(tenors, list) or not set(tenors).issubset(EXPECTED_TENORS):
        fail("tenors结构不正确")

    product_symbols: set[str] = set()
    for index, product in enumerate(products):
        if not isinstance(product, dict):
            fail(f"products[{index}]不是对象")
        assert_allowed_keys(product, PRODUCT_KEYS, f"products[{index}]")
        symbol = str(product.get("symbol") or "")
        if symbol not in EXPECTED_SYMBOLS:
            fail(f"不支持的期货品种：{symbol}")
        product_symbols.add(symbol)
        product_tenors = product.get("tenors")
        if not isinstance(product_tenors, list) or not set(product_tenors).issubset(EXPECTED_TENORS):
            fail(f"{symbol}的期限列表不正确")

    counts: dict[str, int] = {}
    for symbol, rows in series.items():
        if symbol not in product_symbols:
            fail(f"series包含未声明品种：{symbol}")
        if not isinstance(rows, list) or not rows:
            fail(f"{symbol}序列为空")
        previous_date = ""
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                fail(f"{symbol}[{row_index}]不是对象")
            assert_allowed_keys(row, ROW_KEYS, f"{symbol}[{row_index}]")
            date = str(row.get("date") or "")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                fail(f"{symbol}[{row_index}]日期格式错误")
            if previous_date and date <= previous_date:
                fail(f"{symbol}日期没有严格递增：{date}")
            previous_date = date
            if not isinstance(row.get("spot_price"), (int, float)):
                fail(f"{symbol}[{row_index}]缺少指数价格")
            contracts = row.get("contracts")
            if not isinstance(contracts, dict) or not contracts:
                fail(f"{symbol}[{row_index}]合约信息为空")
            if not set(contracts).issubset(EXPECTED_TENORS):
                fail(f"{symbol}[{row_index}]包含未知期限")
            for tenor, contract in contracts.items():
                if not isinstance(contract, dict):
                    fail(f"{symbol}[{row_index}].{tenor}不是对象")
                assert_allowed_keys(contract, CONTRACT_KEYS, f"{symbol}[{row_index}].{tenor}")
                if not contract.get("contract"):
                    fail(f"{symbol}[{row_index}].{tenor}缺少合约代码")
                if not isinstance(contract.get("price"), (int, float)):
                    fail(f"{symbol}[{row_index}].{tenor}缺少期货价格")
                if not isinstance(contract.get("days_to_expiry"), (int, float)):
                    fail(f"{symbol}[{row_index}].{tenor}缺少剩余期限")
        counts[symbol] = len(rows)

    if not isinstance(convergence, dict):
        fail("convergence必须是对象")
    for symbol, tenor_groups in convergence.items():
        if symbol not in product_symbols:
            fail(f"convergence包含未声明品种：{symbol}")
        if not isinstance(tenor_groups, dict):
            fail(f"convergence.{symbol}必须是对象")
        for tenor, rows in tenor_groups.items():
            if tenor not in EXPECTED_TENORS:
                fail(f"convergence.{symbol}包含未知期限：{tenor}")
            if not isinstance(rows, list):
                fail(f"convergence.{symbol}.{tenor}必须是数组")
            for row_index, row in enumerate(rows):
                if not isinstance(row, dict):
                    fail(f"convergence.{symbol}.{tenor}[{row_index}]不是对象")
                assert_allowed_keys(
                    row,
                    CONVERGENCE_ROW_KEYS,
                    f"convergence.{symbol}.{tenor}[{row_index}]",
                )

    if not isinstance(errors, dict):
        fail("errors必须是对象")
    for symbol, message in errors.items():
        if symbol not in EXPECTED_SYMBOLS:
            fail(f"errors包含未知品种：{symbol}")
        if not isinstance(message, str):
            fail(f"errors.{symbol}必须是文字")

    if not isinstance(formula, dict):
        fail("formula必须是对象")
    assert_allowed_keys(formula, FORMULA_KEYS, "formula")
    for name, expression in formula.items():
        if not isinstance(expression, str):
            fail(f"formula.{name}必须是文字")

    walk_keys(payload)
    return counts


def validate_html(path: Path) -> dict[str, int]:
    if not path.is_file():
        fail(f"文件不存在：{path}")
    html = path.read_text(encoding="utf-8")
    if "<title>QuantScope · 升贴水离线分析</title>" not in html:
        fail("网页标题或报告类型不正确")
    if "id=\"basis-report-chart\"" not in html:
        fail("缺少升贴水交互图表容器")
    if re.search(r'<(?:script|link)[^>]+(?:src|href)=["\']https?://', html, re.IGNORECASE):
        fail("发现外部脚本或外部样式依赖")
    for marker in ("127.0.0.1", "localhost", "file://", "C:\\Users\\", "/api/"):
        if marker.lower() in html.lower():
            fail(f"发现不应发布的本地或API地址：{marker}")
    return validate_payload(extract_payload(html))


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 QuantScope 升贴水静态网站发布边界")
    parser.add_argument("html", nargs="?", default="index.html", help="待检查的HTML文件")
    args = parser.parse_args()
    try:
        counts = validate_html(Path(args.html))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[不通过] {exc}", file=sys.stderr)
        return 1
    details = "，".join(f"{symbol} {count}日" for symbol, count in sorted(counts.items()))
    print(f"[检查通过] 自包含交互网站；处理后数据：{details}；未发现敏感字段或原始全量行情字段。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
