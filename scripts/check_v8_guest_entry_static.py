#!/usr/bin/env python3
"""A0 static gate for the v8 guest-entry slices.

Scans only SCOPE_FILES. It does not change topic generation.
Fails on unknown in-app links, navigate(-1), empty targets,
testids missing from either button table, and new UI strings
whose Japanese is empty or copied from zh-TW.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "frontend/src/app/App.tsx"
I18N = ROOT / "frontend/src/i18n/index.ts"
TESTID_TABLE = ROOT / "按鈕測試ID架構表.md"
BUTTON_TABLE = ROOT / "按鈕架構表.md"

SCOPE_FILES = [
    ROOT / "frontend/src/pages/GuestSamplePage.tsx",
    ROOT / "frontend/src/pages/WelcomeSamplePage.tsx",
    ROOT / "frontend/src/pages/TopicLayoutSamplePage.tsx",
    ROOT / "frontend/src/pages/GuestChargeSamplePage.tsx",
    ROOT / "frontend/src/components/welcome/GuestCreditOfferCard.tsx",
    ROOT / "frontend/src/components/topics/MobileTopicList.tsx",
]

WATCH_KEYS = (
    "composer.regenTitle",
    "composer.regenBody",
    "composer.regenTags",
    "guestCharge.title",
    "guestCharge.body",
    "guestCharge.bodyPlain",
    "guestChargeSample.kicker",
    "guestChargeSample.lead",
    "guestChargeSample.sectionEarn",
    "guestChargeSample.welcomeLabel",
    "guestChargeSample.dailyLabel",
    "guestChargeSample.useLine",
    "guestChargeSample.costLabel",
    "guestChargeSample.costUnit",
    "guestChargeSample.fontNote",
    "welcomeOffer.title",
    "welcomeOffer.cta",
    "welcomeSample.daily",
    "welcomeSample.themesIntro",
    "welcomeSample.library",
    "welcomeSample.loading",
    "welcomeSample.empty",
    "topicLayout.related",
    "topicLayout.preview",
    "topicLayout.fullText",
    "topicLayout.jump",
    "topicLayout.empty",
    "topicLayout.back",
)

CJK = re.compile(r"[\u4e00-\u9fff]")
LANG_NAME_KEY = re.compile(r"^language\.")


def parse_ts_dict(content: str, var_name: str) -> dict[str, str]:
    pattern = rf"const\s+{var_name}(?:\s*:\s*[^=]+)?\s*=\s*\{{"
    match = re.search(pattern, content)
    if not match:
        return {}
    start = match.end() - 1
    depth = 0
    end = start
    for index, char in enumerate(content[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    result: dict[str, str] = {}
    for line in content[start:end].splitlines():
        stripped = line.strip()
        if stripped.startswith(("//", "/*", "*")):
            continue
        found = re.match(
            r"^['\"]([^'\"]+)['\"]\s*:\s*(?:'([^']*)'|\"([^\"]*)\"|`([^`]*)`),?",
            stripped,
        )
        if found:
            value = found.group(2)
            if value is None:
                value = found.group(3) if found.group(3) is not None else found.group(4)
            result[found.group(1)] = value or ""
    return result


def parse_routes(app_text: str) -> set[str]:
    return set(re.findall(r"""path=["']([^"']+)["']""", app_text))


def route_known(target: str, routes: set[str]) -> bool:
    path = target.split("?", 1)[0].split("#", 1)[0]
    if not path.startswith("/"):
        return False
    if path in routes:
        return True
    parts = path.strip("/").split("/")
    for route in routes:
        route_parts = route.strip("/").split("/")
        if len(route_parts) != len(parts):
            continue
        if all(
            left.startswith(":") or left == right
            for left, right in zip(route_parts, parts)
        ):
            return True
    return False


def check_links(source: str, routes: set[str]) -> list[str]:
    errors: list[str] = []
    if re.search(r"navigate\(\s*-1\s*\)", source):
        errors.append("navigate(-1) is not a fixed return path")
    if re.search(r"""to=\s*["']\s*["']""", source) or re.search(
        r"""navigate\(\s*["']\s*["']\s*\)""", source
    ):
        errors.append("empty link target")
    for match in re.finditer(r"""href=["']([^"']*)["']""", source):
        href = match.group(1).strip()
        if href in {"", "#"} or href.lower().startswith("javascript:"):
            errors.append(f"empty or dead href: {href!r}")
    targets = re.findall(r"""(?:to=|navigate\(\s*)["']([^"']+)["']""", source)
    targets += re.findall(r"""(?:to=|navigate\(\s*)\{`([^`]+)`\}""", source)
    for target in targets:
        target = target.strip()
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        concrete = re.sub(r"\$\{[^}]+\}", "sample", target)
        if not route_known(concrete, routes):
            errors.append(f"link is not a known route: {target}")
    return errors


def testids_in(source: str) -> set[str]:
    found = set(re.findall(r"""data-testid=["']([^"'$]+)["']""", source))
    for prefix in re.findall(r"""data-testid=\{`([^`$]+)\$\{""", source):
        for suffix in ("zh", "en", "ja"):
            found.add(f"{prefix}{suffix}")
    return found


def keys_in(source: str) -> set[str]:
    found = set(re.findall(r"""(?<![A-Za-z0-9_.])t\(\s*['"]([^'"]+)['"]""", source))
    if "language.${" in source:
        found.update({"language.zh-TW", "language.en", "language.ja"})
    return found


def check_copy(
    keys: set[str],
    zh: dict[str, str],
    en: dict[str, str],
    ja: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    for key in sorted(keys):
        if key not in zh or key not in en or key not in ja:
            errors.append(f"missing i18n key: {key}")
            continue
        if LANG_NAME_KEY.match(key):
            continue
        if not ja[key].strip():
            errors.append(f"ja empty: {key}")
        elif ja[key].strip() == zh[key].strip():
            errors.append(f"ja copies zh-TW: {key}")
        if CJK.search(en[key]):
            errors.append(f"en contains Chinese: {key}")
    return errors


def self_test() -> list[str]:
    routes = {"/dashboard", "/topics/:id", "/welcome"}
    errors: list[str] = []
    probes = [
        ("navigate(-1)", "navigate(-1)"),
        ("href=\"#\"", "dead href"),
        ("navigate('/missing-page')", "not a known route"),
        ("to=\"\"", "empty link"),
    ]
    for source, needle in probes:
        found = check_links(source, routes)
        if not any(needle.split()[0] in item or needle in item for item in found):
            if not found:
                errors.append(f"self-test missed: {source}")
    ok = check_links("navigate('/dashboard')", routes)
    if ok:
        errors.append(f"self-test flagged a known route: {ok}")
    topic = check_links("to={`/topics/${id}`}", routes)
    if topic:
        errors.append(f"self-test flagged topic id route: {topic}")
    copy_errors = check_copy(
        {"sample.line"},
        {"sample.line": "每天十五張"},
        {"sample.line": "Fifteen cards a day"},
        {"sample.line": "每天十五張"},
    )
    if not any("copies zh-TW" in item for item in copy_errors):
        errors.append("self-test missed copied Japanese")
    return errors


def main() -> int:
    fails: list[str] = []
    fails.extend(self_test())
    app_text = APP.read_text(encoding="utf-8")
    routes = parse_routes(app_text)
    if "/dashboard" not in routes or "/welcome" not in routes:
        fails.append("App.tsx is missing /dashboard or /welcome")
    i18n_text = I18N.read_text(encoding="utf-8")
    zh = parse_ts_dict(i18n_text, "zhTW")
    en = parse_ts_dict(i18n_text, "en")
    ja = parse_ts_dict(i18n_text, "ja")
    testid_table = TESTID_TABLE.read_text(encoding="utf-8")
    button_table = BUTTON_TABLE.read_text(encoding="utf-8")

    for path in SCOPE_FILES:
        if not path.exists():
            fails.append(f"missing scope file: {path.name}")
            continue
        source = path.read_text(encoding="utf-8")
        for item in check_links(source, routes):
            fails.append(f"{path.name}: {item}")
        for testid in sorted(testids_in(source)):
            if testid not in testid_table or testid not in button_table:
                fails.append(f"{path.name}: testid not in both button tables: {testid}")
        for item in check_copy(keys_in(source), zh, en, ja):
            fails.append(f"{path.name}: {item}")
    for item in check_copy(set(WATCH_KEYS), zh, en, ja):
        fails.append(f"watch: {item}")

    if fails:
        print(f"FAIL | v8 guest-entry static | {len(fails)}")
        for item in fails:
            print(f"  - {item}")
        return 1
    print(
        "PASS | v8 guest-entry static | "
        f"routes={len(routes)} scope={len(SCOPE_FILES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
