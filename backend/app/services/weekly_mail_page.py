"""退訂結果頁。三語固定句，跟驗證信同一做法，不進前端字典。"""
from __future__ import annotations

_PAGES = {
    "zh-TW": {
        "ok_title": "已停止每週通訊",
        "ok_body": "之後不會再寄每週通訊。驗證信與重設密碼信仍會寄出。",
        "bad_title": "這個連結已失效",
        "bad_body": "請從最近一封每週通訊裡的退訂連結再開一次。",
    },
    "en": {
        "ok_title": "Weekly letter stopped",
        "ok_body": "You will not receive the weekly letter. Verification and password reset mail still arrives.",
        "bad_title": "This link has expired",
        "bad_body": "Open the unsubscribe link from the latest weekly letter.",
    },
    "ja": {
        "ok_title": "週次メールを停止しました",
        "ok_body": "今後、週次メールは届きません。確認メールとパスワード再設定メールは届きます。",
        "bad_title": "このリンクは無効です",
        "bad_body": "最新の週次メールにある解除リンクから開き直してください。",
    },
}


def render_unsubscribe_page(language: str, ok: bool) -> str:
    pack = _PAGES.get(language) or _PAGES["zh-TW"]
    title = pack["ok_title"] if ok else pack["bad_title"]
    body = pack["ok_body"] if ok else pack["bad_body"]
    lang = language if language in _PAGES else "zh-TW"
    return (
        "<!doctype html><html lang=\"%s\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>%s</title></head><body style=\"font-family:sans-serif;padding:2rem\">"
        "<h1>%s</h1><p>%s</p></body></html>"
    ) % (lang, title, title, body)
