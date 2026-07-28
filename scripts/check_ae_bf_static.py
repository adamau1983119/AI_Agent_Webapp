#!/usr/bin/env python3
"""Alter Ego static checks (PD-AE0/1 + CD-AE yaml/B formatter · program segment)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))

SPEC = ROOT / "docs/ALTER_EGO_SPEC.md"
DNA_MODEL = BACKEND / "app/models/alter_ego_dna.py"
API = BACKEND / "app/api/v1/alter_ego.py"
SERVICE = BACKEND / "app/services/alter_ego_service.py"
LLM_FACTORY = BACKEND / "app/services/ai/llm_factory.py"
SHELL_MGR = BACKEND / "app/services/shells/shell_manager.py"
SHELL_FMT = BACKEND / "app/services/shells/shell_formatter.py"
MAIN = BACKEND / "app/main.py"
SHELLS = BACKEND / "app/config/shells"
CONTENT_STYLE = BACKEND / "app/services/content_style_service.py"
BODY_GW = BACKEND / "app/middleware/alter_ego_body_gateway.py"
CONTENTS_API = BACKEND / "app/api/v1/contents.py"

GOLDEN_DNA = {
    "lexicon": ["誠實", "旺角", "車仔面"],
    "tone_descriptors": ["親切", "務實"],
    "voice_persona": "香港美食部落客，短句口語",
    "language_primary": "zh-TW",
    "exemplar_snippets": ["今日去咗旺角試咗間新開嘅車仔面檔，湯底合格。"],
}
GOLDEN_SOUL = "今日去旺角試車仔面。湯底合格，麵有咬口。$48 有找，值得一試。"
GOLDEN_TAGS = ["香港美食", "車仔面", "旺角", "平價午餐", "foodie"]


def main() -> int:
    fails = 0
    spec = SPEC.read_text(encoding="utf-8") if SPEC.exists() else ""
    api = API.read_text(encoding="utf-8")
    svc = SERVICE.read_text(encoding="utf-8")
    main_py = MAIN.read_text(encoding="utf-8")
    contents_py = CONTENTS_API.read_text(encoding="utf-8")
    css_py = CONTENT_STYLE.read_text(encoding="utf-8") if CONTENT_STYLE.exists() else ""
    body_gw_py = BODY_GW.read_text(encoding="utf-8") if BODY_GW.exists() else ""

    checks: list[tuple[str, bool, str]] = [
        ("PD-AE0-01 ALTER_EGO_SPEC.md exists", SPEC.exists() and len(spec) > 500, ""),
        ("PD-AE0-01 DNA model AlterEgoDnaJson", DNA_MODEL.exists() and "extra=\"forbid\"" in DNA_MODEL.read_text(encoding="utf-8"), ""),
        ("PD-AE0-05 facebook.yaml", (SHELLS / "facebook.yaml").exists(), ""),
        ("PD-AE0-05 threads.yaml", (SHELLS / "threads.yaml").exists(), ""),
        ("PD-AE0-05 x.yaml", (SHELLS / "x.yaml").exists(), ""),
        ("PD-AE0-05 ShellManager", SHELL_MGR.exists() and "class ShellManager" in SHELL_MGR.read_text(encoding="utf-8"), ""),
        ("PD-AE1-01 extract route", '"/extract"' in api and "alter_ego_service" in api, ""),
        ("PD-AE1-02 preview route", '"/preview"' in api and "_build_soul_prompt" in svc, ""),
        ("PD-AE1-02 shell flash prompt", "_build_shell_prompt" in svc and "SOUL_PREVIEW_FAIL" in svc, ""),
        ("PD-AE1-01 router registered", "alter_ego.router" in main_py, ""),
        ("PD-AE1-04 AlterEgoLLMClient", "class AlterEgoLLMClient" in LLM_FACTORY.read_text(encoding="utf-8"), ""),
        ("PD-AE1-04 alter_ego namespace", 'namespace == "alter_ego"' in LLM_FACTORY.read_text(encoding="utf-8"), ""),
        ("CD-AE-A3 log tag in service", "[ALTER_EGO_DNA_EXTRACT_FAIL]" in svc, ""),
        ("health alter_ego version", "alter_ego_health_payload" in MAIN.read_text(encoding="utf-8"), ""),
        ("PD-AE1-03 AlterEgoBodyGateway", BODY_GW.exists() and "AlterEgoBodyGatewayMiddleware" in body_gw_py, ""),
        ("PD-AE1-03 gateway registered", "AlterEgoBodyGatewayMiddleware" in main_py, ""),
        ("PD-AE1-05 ContentStyleService", CONTENT_STYLE.exists() and "compress_for_generate" in css_py, ""),
        ("PD-AE1-05 resolve_for_route", "resolve_for_route" in css_py, ""),
        ("PD-AE1-06 generation_meta in contents", "generation_meta" in contents_py and "content_style_service" in contents_py, ""),
        ("PD-AE1-06 no _style_dna_hint", "_style_dna_hint" not in contents_py, ""),
        ("PD-AE1-07 rollback route", '"/dna/rollback"' in api and "rollback" in svc, ""),
        ("PD-AE1-F02 skip route", '"/skip"' in api and "skip_onboarding" in svc, ""),
        ("PD-AE1-F05 adopt-copy route", '"/adopt-copy"' in api and "adopted_without_edit" in svc, ""),
        ("PD-AE2-01 weekly batch service", (BACKEND / "app/services/alter_ego_weekly_batch.py").exists(), ""),
        ("PD-AE2-02 feedback route", '"/feedback"' in api and "UserFeedbackRepository" in svc, ""),
        ("PD-AE2-04 reextract gate", (BACKEND / "app/services/alter_ego_reextract.py").exists(), ""),
    ]

    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            fails += 1
        extra = f" | {detail}" if detail else ""
        print(f"{status} | {name}{extra}")

    # Runtime: Pydantic + ShellManager + formatter (CD-AE-B)
    try:
        from app.services.alter_ego_health import alter_ego_health_payload

        ae_h = alter_ego_health_payload()
        ae_ver_ok = (
            ae_h.get("pipeline_version", 0) >= 4
            and ae_h.get("preview_includes_soul") is True
            and ae_h.get("content_style_service") is True
            and ae_h.get("rollback_api") is True
            and ae_h.get("onboarding_skip_api") is True
        )
        print(f"{'PASS' if ae_ver_ok else 'FAIL'} | alter_ego health payload v{ae_h.get('pipeline_version')}")
        if not ae_ver_ok:
            fails += 1

        from app.models.alter_ego_dna import AlterEgoDnaJson
        from app.services.shells import get_shell_manager
        from app.services.shells.shell_formatter import build_shell_output

        dna = AlterEgoDnaJson.model_validate(GOLDEN_DNA)
        plats = get_shell_manager().list_platforms()
        pydantic_ok = dna.voice_persona == GOLDEN_DNA["voice_persona"]
        plats_ok = plats == ["facebook", "threads", "x"]
        print(f"{'PASS' if pydantic_ok else 'FAIL'} | CD-AE-A1 golden DNA Pydantic strict")
        if not pydantic_ok:
            fails += 1

        fb = build_shell_output(GOLDEN_SOUL, "facebook", GOLDEN_TAGS)
        fb_ok = fb["lead_len"] <= 90 and 4 <= len(fb["hashtags"]) <= 6
        print(f"{'PASS' if fb_ok else 'FAIL'} | CD-AE-B1 FB lead<=90 + hashtags 4-6 (lead_len={fb['lead_len']} tags={len(fb['hashtags'])})")
        if not fb_ok:
            fails += 1

        th = build_shell_output(GOLDEN_SOUL, "threads", GOLDEN_TAGS[:1])
        th_ok = th["hashtag_count"] <= 1
        print(f"{'PASS' if th_ok else 'FAIL'} | CD-AE-B2 Threads hashtags 0-1 (count={th['hashtag_count']})")
        if not th_ok:
            fails += 1

        xo = build_shell_output(GOLDEN_SOUL, "x", GOLDEN_TAGS[:2])
        x_ok = xo["post_len"] <= 280
        print(f"{'PASS' if x_ok else 'FAIL'} | CD-AE-B3 X post<=280 (len={xo['post_len']})")
        if not x_ok:
            fails += 1

        print(f"{'PASS' if plats_ok else 'FAIL'} | Shell platforms list")
        if not plats_ok:
            fails += 1

        from app.services.ai.llm_factory import get_llm_client
        from app.config import settings

        pro_model = getattr(settings, "DEEPSEEK_MODEL_PRO", "deepseek-v4-pro")
        ae_client = get_llm_client("alter_ego")
        pro_blocked = False
        try:
            import asyncio

            async def _try_pro() -> None:
                await ae_client.generate("test", model=pro_model)

            asyncio.run(_try_pro())
        except ValueError as exc:
            pro_blocked = "pro_forbidden" in str(exc) or "pro" in str(exc).lower()
        print(f"{'PASS' if pro_blocked else 'FAIL'} | PD-AE1-04 Pro call rejected on alter_ego")
        if not pro_blocked:
            fails += 1

        from app.services.content_style_service import ContentStyleService
        from app.models.alter_ego_dna import AlterEgoDnaJson

        dna_compress = AlterEgoDnaJson.model_validate(GOLDEN_DNA)
        compressed = ContentStyleService.compress_for_generate(dna_compress)
        compress_ok = 0 < len(compressed) <= 500
        print(f"{'PASS' if compress_ok else 'FAIL'} | PD-AE1-05 compress_for_generate <=500 (len={len(compressed)})")
        if not compress_ok:
            fails += 1
    except Exception as exc:
        fails += 1
        print(f"FAIL | runtime imports | {exc}")

    total_printed = len(checks) + 6
    print("---")
    print(f"NOTE: CD-AE-A2 manual spot-check; CD-AE-C* E2E → check_ae_live.py + test week.")
    print(f"Static track: {'PASS' if fails == 0 else 'FAIL'} ({fails} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
