"""One-off: embed markdown into HTML script#md-embed."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html_path = root / "docs" / "deepseek_asset_distillation_third_party_brief.html"
md_path = root / "docs" / "deepseek_asset_distillation_third_party_brief.md"
marker = '<script type="text/plain" id="md-embed"></script>'
html = html_path.read_text(encoding="utf-8")
md = md_path.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
replacement = f'<script type="text/plain" id="md-embed">{md}</script>'
if marker not in html:
    raise SystemExit("marker not found")
html_path.write_text(html.replace(marker, replacement, 1), encoding="utf-8")
print("embedded", len(md), "chars")
