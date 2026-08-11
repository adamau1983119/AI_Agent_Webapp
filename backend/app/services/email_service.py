"""
Email 服務
Phase 2: 會員系統
正式域優先 Resend HTTPS；本機可回退 Gmail SMTP。
"""
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

import aiosmtplib
import httpx

from app.config_module import settings
from app.models.user import Language

logger = logging.getLogger(__name__)

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587
RESEND_API_URL = "https://api.resend.com/emails"
DEFAULT_RESEND_FROM = "Alter Ego <onboarding@resend.dev>"


class EmailService:
    """Email 服務（Resend HTTPS 優先，否則 Gmail SMTP）"""

    def __init__(self):
        self.smtp_host = GMAIL_SMTP_HOST
        self.smtp_port = GMAIL_SMTP_PORT
        self.username = settings.GMAIL_USER
        self.password = settings.GMAIL_APP_PASSWORD
        self.from_email = settings.GMAIL_USER
        self.from_name = "Alter Ego"
        self.resend_api_key = (settings.RESEND_API_KEY or "").strip()
        self.email_from = (settings.EMAIL_FROM or "").strip()

    def is_configured(self) -> bool:
        if self.resend_api_key:
            return True
        return bool(self.username and self.password)

    def _from_header(self) -> str:
        if self.email_from:
            return self.email_from
        if self.resend_api_key:
            return DEFAULT_RESEND_FROM
        return f"{self.from_name} <{self.from_email}>"

    async def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        payload: Dict[str, Any] = {
            "from": self._from_header(),
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        if text_content:
            payload["text"] = text_content
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            if resp.status_code >= 400:
                logger.error(
                    "Email 發送失敗 (resend): %s %s",
                    resp.status_code,
                    resp.text[:500],
                )
                return False
            logger.info("Email 發送成功 (resend): %s", to_email)
            return True
        except Exception as e:
            logger.error("Email 發送失敗 (resend): %s", e)
            return False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        if not self.is_configured():
            logger.warning("Email 服務未配置，跳過發送")
            return False

        if self.resend_api_key:
            return await self._send_via_resend(
                to_email, subject, html_content, text_content
            )

        try:
            message = MIMEMultipart("alternative")
            message["From"] = self._from_header()
            message["To"] = to_email
            message["Subject"] = subject
            if text_content:
                message.attach(MIMEText(text_content, "plain", "utf-8"))
            message.attach(MIMEText(html_content, "html", "utf-8"))
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                start_tls=True,
            )
            logger.info("Email 發送成功 (smtp): %s", to_email)
            return True
        except Exception as e:
            logger.error("Email 發送失敗 (smtp): %s", e)
            return False
    
    async def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        language: Language = Language.ZH_TW
    ) -> bool:
        """
        發送 Email 驗證郵件
        
        Args:
            to_email: 收件人 Email
            verification_token: 驗證 Token
            language: 語言
            
        Returns:
            是否發送成功
        """
        # 取得郵件模板
        template = get_verification_email_template(
            verification_token=verification_token,
            language=language
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=template["subject"],
            html_content=template["html"],
            text_content=template["text"]
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        language: Language = Language.ZH_TW
    ) -> bool:
        """
        發送密碼重設郵件
        
        Args:
            to_email: 收件人 Email
            reset_token: 重設 Token
            language: 語言
            
        Returns:
            是否發送成功
        """
        # 取得郵件模板
        template = get_password_reset_email_template(
            reset_token=reset_token,
            language=language
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=template["subject"],
            html_content=template["html"],
            text_content=template["text"]
        )
    
    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        language: Language = Language.ZH_TW
    ) -> bool:
        """
        發送歡迎郵件
        
        Args:
            to_email: 收件人 Email
            user_name: 用戶名稱
            language: 語言
            
        Returns:
            是否發送成功
        """
        template = get_welcome_email_template(
            user_name=user_name,
            language=language
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=template["subject"],
            html_content=template["html"],
            text_content=template["text"]
        )


# ============================================
# Email 模板 — Lane Crawford 高端極簡風格
# 色彩：黑 #000000 / 白 #FFFFFF / 奶白 #FAF9F7
# 字體：系統 sans-serif（郵件不支援 Google Fonts）
# 無 emoji、無漸層、無圓角
# ============================================

# 前端 URL（用於郵件中的連結）— 從設定讀取
from app.config_module import settings as _email_settings
FRONTEND_URL = _email_settings.FRONTEND_URL


def _lane_crawford_base(body_content: str, font_family: str = "Arial, 'Helvetica Neue', sans-serif") -> str:
    """Lane Crawford 風格郵件基礎模板"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #FAF9F7; font-family: {font_family}; -webkit-font-smoothing: antialiased;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #FAF9F7;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%;">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #000000; padding: 48px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #FFFFFF; font-size: 28px; font-weight: 300; letter-spacing: 0.4em; text-transform: uppercase;">
                                INFLUENCERS
                            </h1>
                            <div style="width: 60px; height: 1px; background-color: rgba(255,255,255,0.3); margin: 20px auto;"></div>
                            <p style="margin: 0; color: rgba(255,255,255,0.5); font-size: 10px; letter-spacing: 0.25em; text-transform: uppercase; font-weight: 300;">
                                AI-POWERED CONTENT CREATION
                            </p>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="background-color: #FFFFFF; padding: 48px 40px; border-left: 1px solid #e5e5e5; border-right: 1px solid #e5e5e5;">
                            {body_content}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 32px 40px; text-align: center; border-top: 1px solid #e5e5e5;">
                            <p style="margin: 0; color: #999999; font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase;">
                                &copy; 2026 INFLUENCERS. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def get_verification_email_template(
    verification_token: str,
    language: Language = Language.ZH_TW
) -> Dict[str, str]:
    """
    取得 Email 驗證郵件模板（Lane Crawford 風格）
    """
    verify_url = f"{FRONTEND_URL}/verify-email?token={verification_token}"
    
    # 繁體中文
    zh_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    Email 驗證
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    您好，
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    感謝您註冊 Influencers AI Agents。請點擊下方按鈕驗證您的 Email 地址：
</p>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{verify_url}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        VERIFY EMAIL
    </a>
</p>
<div style="width: 100%; height: 1px; background-color: #f0f0f0; margin: 32px 0;"></div>
<p style="margin: 0 0 12px; color: #999999; font-size: 12px; line-height: 1.6; font-weight: 300;">
    如果按鈕無法點擊，請複製以下連結到瀏覽器：
</p>
<p style="margin: 0 0 20px; word-break: break-all; color: #999999; font-size: 11px; line-height: 1.6;">
    {verify_url}
</p>
<p style="margin: 0 0 8px; color: #999999; font-size: 12px; font-weight: 300;">
    此連結將在 24 小時後過期。
</p>
<p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">
    如果您沒有註冊帳號，請忽略此郵件。
</p>
"""
    
    # 英文
    en_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    Email Verification
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    Hello,
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    Thank you for signing up for Influencers AI Agents. Please click the button below to verify your email address:
</p>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{verify_url}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        VERIFY EMAIL
    </a>
</p>
<div style="width: 100%; height: 1px; background-color: #f0f0f0; margin: 32px 0;"></div>
<p style="margin: 0 0 12px; color: #999999; font-size: 12px; line-height: 1.6; font-weight: 300;">
    If the button doesn't work, copy and paste this link into your browser:
</p>
<p style="margin: 0 0 20px; word-break: break-all; color: #999999; font-size: 11px; line-height: 1.6;">
    {verify_url}
</p>
<p style="margin: 0 0 8px; color: #999999; font-size: 12px; font-weight: 300;">
    This link will expire in 24 hours.
</p>
<p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">
    If you didn't create an account, please ignore this email.
</p>
"""
    
    # 日文
    ja_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    メールアドレスの確認
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    こんにちは、
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    Influencers AI Agents にご登録いただきありがとうございます。以下のボタンをクリックして、メールアドレスを確認してください：
</p>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{verify_url}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        VERIFY EMAIL
    </a>
</p>
<div style="width: 100%; height: 1px; background-color: #f0f0f0; margin: 32px 0;"></div>
<p style="margin: 0 0 12px; color: #999999; font-size: 12px; line-height: 1.6; font-weight: 300;">
    ボタンが機能しない場合は、以下のリンクをブラウザにコピーしてください：
</p>
<p style="margin: 0 0 20px; word-break: break-all; color: #999999; font-size: 11px; line-height: 1.6;">
    {verify_url}
</p>
<p style="margin: 0 0 8px; color: #999999; font-size: 12px; font-weight: 300;">
    このリンクは 24 時間後に期限切れになります。
</p>
<p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">
    アカウントを作成していない場合は、このメールを無視してください。
</p>
"""
    
    templates = {
        Language.ZH_TW: {
            "subject": "INFLUENCERS — Email 驗證",
            "html": _lane_crawford_base(zh_body, "'Noto Sans TC', Arial, 'Helvetica Neue', sans-serif"),
            "text": f"INFLUENCERS — Email 驗證\n\n感謝您註冊。請點擊以下連結驗證您的 Email：\n\n{verify_url}\n\n此連結將在 24 小時後過期。\n如果您沒有註冊帳號，請忽略此郵件。\n\n© 2026 INFLUENCERS"
        },
        Language.EN: {
            "subject": "INFLUENCERS — Email Verification",
            "html": _lane_crawford_base(en_body),
            "text": f"INFLUENCERS — Email Verification\n\nThank you for signing up. Please click the link below to verify your email:\n\n{verify_url}\n\nThis link will expire in 24 hours.\nIf you didn't create an account, please ignore this email.\n\n© 2026 INFLUENCERS"
        },
        Language.JA: {
            "subject": "INFLUENCERS — メールアドレスの確認",
            "html": _lane_crawford_base(ja_body, "'Noto Sans JP', Arial, 'Helvetica Neue', sans-serif"),
            "text": f"INFLUENCERS — メールアドレスの確認\n\nご登録ありがとうございます。以下のリンクをクリックしてメールアドレスを確認してください：\n\n{verify_url}\n\nこのリンクは 24 時間後に期限切れになります。\nアカウントを作成していない場合は、このメールを無視してください。\n\n© 2026 INFLUENCERS"
        }
    }
    
    return templates.get(language, templates[Language.ZH_TW])


def get_password_reset_email_template(
    reset_token: str,
    language: Language = Language.ZH_TW
) -> Dict[str, str]:
    """
    取得密碼重設郵件模板（Lane Crawford 風格）
    """
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    
    # 繁體中文
    zh_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    重設密碼
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    您好，
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    我們收到了重設您密碼的請求。請點擊下方按鈕設定新密碼：
</p>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{reset_url}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        RESET PASSWORD
    </a>
</p>
<div style="width: 100%; height: 1px; background-color: #f0f0f0; margin: 32px 0;"></div>
<p style="margin: 0 0 12px; color: #999999; font-size: 12px; line-height: 1.6; font-weight: 300;">
    如果按鈕無法點擊，請複製以下連結到瀏覽器：
</p>
<p style="margin: 0 0 20px; word-break: break-all; color: #999999; font-size: 11px; line-height: 1.6;">
    {reset_url}
</p>
<p style="margin: 0 0 8px; color: #999999; font-size: 12px; font-weight: 300;">
    此連結將在 1 小時後過期。
</p>
<div style="margin: 24px 0; padding: 16px; border: 1px solid #e5e5e5;">
    <p style="margin: 0; color: #666666; font-size: 12px; font-weight: 300; line-height: 1.6;">
        如果您沒有請求重設密碼，請忽略此郵件。您的帳號安全無虞。
    </p>
</div>
"""
    
    # 英文
    en_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    Reset Password
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    Hello,
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    We received a request to reset your password. Click the button below to set a new password:
</p>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{reset_url}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        RESET PASSWORD
    </a>
</p>
<div style="width: 100%; height: 1px; background-color: #f0f0f0; margin: 32px 0;"></div>
<p style="margin: 0 0 12px; color: #999999; font-size: 12px; line-height: 1.6; font-weight: 300;">
    If the button doesn't work, copy and paste this link into your browser:
</p>
<p style="margin: 0 0 20px; word-break: break-all; color: #999999; font-size: 11px; line-height: 1.6;">
    {reset_url}
</p>
<p style="margin: 0 0 8px; color: #999999; font-size: 12px; font-weight: 300;">
    This link will expire in 1 hour.
</p>
<div style="margin: 24px 0; padding: 16px; border: 1px solid #e5e5e5;">
    <p style="margin: 0; color: #666666; font-size: 12px; font-weight: 300; line-height: 1.6;">
        If you didn't request a password reset, please ignore this email. Your account is safe.
    </p>
</div>
"""
    
    # 日文
    ja_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    パスワードのリセット
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    こんにちは、
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    パスワードリセットのリクエストを受け取りました。以下のボタンをクリックして新しいパスワードを設定してください：
</p>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{reset_url}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        RESET PASSWORD
    </a>
</p>
<div style="width: 100%; height: 1px; background-color: #f0f0f0; margin: 32px 0;"></div>
<p style="margin: 0 0 12px; color: #999999; font-size: 12px; line-height: 1.6; font-weight: 300;">
    ボタンが機能しない場合は、以下のリンクをブラウザにコピーしてください：
</p>
<p style="margin: 0 0 20px; word-break: break-all; color: #999999; font-size: 11px; line-height: 1.6;">
    {reset_url}
</p>
<p style="margin: 0 0 8px; color: #999999; font-size: 12px; font-weight: 300;">
    このリンクは 1 時間後に期限切れになります。
</p>
<div style="margin: 24px 0; padding: 16px; border: 1px solid #e5e5e5;">
    <p style="margin: 0; color: #666666; font-size: 12px; font-weight: 300; line-height: 1.6;">
        パスワードリセットをリクエストしていない場合は、このメールを無視してください。アカウントは安全です。
    </p>
</div>
"""
    
    templates = {
        Language.ZH_TW: {
            "subject": "INFLUENCERS — 重設密碼",
            "html": _lane_crawford_base(zh_body, "'Noto Sans TC', Arial, 'Helvetica Neue', sans-serif"),
            "text": f"INFLUENCERS — 重設密碼\n\n我們收到了重設您密碼的請求。請點擊以下連結設定新密碼：\n\n{reset_url}\n\n此連結將在 1 小時後過期。\n如果您沒有請求重設密碼，請忽略此郵件。\n\n© 2026 INFLUENCERS"
        },
        Language.EN: {
            "subject": "INFLUENCERS — Reset Password",
            "html": _lane_crawford_base(en_body),
            "text": f"INFLUENCERS — Reset Password\n\nWe received a request to reset your password. Click the link below:\n\n{reset_url}\n\nThis link will expire in 1 hour.\nIf you didn't request a password reset, please ignore this email.\n\n© 2026 INFLUENCERS"
        },
        Language.JA: {
            "subject": "INFLUENCERS — パスワードのリセット",
            "html": _lane_crawford_base(ja_body, "'Noto Sans JP', Arial, 'Helvetica Neue', sans-serif"),
            "text": f"INFLUENCERS — パスワードのリセット\n\nパスワードリセットのリクエストを受け取りました。以下のリンクをクリックしてください：\n\n{reset_url}\n\nこのリンクは 1 時間後に期限切れになります。\nリクエストしていない場合は、このメールを無視してください。\n\n© 2026 INFLUENCERS"
        }
    }
    
    return templates.get(language, templates[Language.ZH_TW])


def get_welcome_email_template(
    user_name: str,
    language: Language = Language.ZH_TW
) -> Dict[str, str]:
    """
    取得歡迎郵件模板（Lane Crawford 風格）
    """
    # 繁體中文
    zh_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    歡迎加入
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    {user_name}，您好！
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    歡迎加入 Influencers AI Agents。我們很高興您成為我們的一員。以下是您可以開始使用的功能：
</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 32px;">
    <tr>
        <td style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">AI Content Generation</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">自動生成高品質社交媒體內容</p>
        </td>
    </tr>
    <tr>
        <td style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">Personalized Style</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">AI 學習您的風格偏好</p>
        </td>
    </tr>
    <tr>
        <td style="padding: 16px 20px;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">Multi-platform Publishing</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">一鍵發布到多個社交平台</p>
        </td>
    </tr>
</table>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{FRONTEND_URL}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        GET STARTED
    </a>
</p>
"""
    
    # 英文
    en_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    Welcome
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    Hello {user_name},
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    Welcome to Influencers AI Agents. We're delighted to have you with us. Here's what you can explore:
</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 32px;">
    <tr>
        <td style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">AI Content Generation</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">Auto-generate high-quality social media content</p>
        </td>
    </tr>
    <tr>
        <td style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">Personalized Style</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">AI learns your unique style preferences</p>
        </td>
    </tr>
    <tr>
        <td style="padding: 16px 20px;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">Multi-platform Publishing</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">One-click publish to multiple social platforms</p>
        </td>
    </tr>
</table>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{FRONTEND_URL}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        GET STARTED
    </a>
</p>
"""
    
    # 日文
    ja_body = f"""
<h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 300; color: #000000; letter-spacing: 0.1em; text-align: center;">
    ようこそ
</h2>
<div style="width: 40px; height: 1px; background-color: #e5e5e5; margin: 0 auto 32px;"></div>
<p style="margin: 0 0 20px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    {user_name} さん、こんにちは！
</p>
<p style="margin: 0 0 32px; color: #666666; font-size: 14px; line-height: 1.8; font-weight: 300;">
    Influencers AI Agents へようこそ。ご参加いただきありがとうございます。以下の機能をお試しください：
</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 32px;">
    <tr>
        <td style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">AI Content Generation</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">高品質なソーシャルメディアコンテンツを自動生成</p>
        </td>
    </tr>
    <tr>
        <td style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">Personalized Style</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">AI があなたのスタイル好みを学習</p>
        </td>
    </tr>
    <tr>
        <td style="padding: 16px 20px;">
            <p style="margin: 0 0 4px; color: #000000; font-size: 12px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;">Multi-platform Publishing</p>
            <p style="margin: 0; color: #999999; font-size: 12px; font-weight: 300;">ワンクリックで複数のプラットフォームに投稿</p>
        </td>
    </tr>
</table>
<p style="text-align: center; margin: 0 0 32px;">
    <a href="{FRONTEND_URL}" style="display: inline-block; background-color: #000000; color: #FFFFFF; padding: 16px 48px; text-decoration: none; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 400;">
        GET STARTED
    </a>
</p>
"""
    
    templates = {
        Language.ZH_TW: {
            "subject": "INFLUENCERS — 歡迎加入",
            "html": _lane_crawford_base(zh_body, "'Noto Sans TC', Arial, 'Helvetica Neue', sans-serif"),
            "text": f"INFLUENCERS — 歡迎加入\n\n{user_name}，您好！\n\n歡迎加入 Influencers AI Agents！\n\n功能一覽：\n- AI 內容生成\n- 個人化風格\n- 多平台發布\n\n立即開始：{FRONTEND_URL}\n\n© 2026 INFLUENCERS"
        },
        Language.EN: {
            "subject": "INFLUENCERS — Welcome",
            "html": _lane_crawford_base(en_body),
            "text": f"INFLUENCERS — Welcome\n\nHello {user_name}!\n\nWelcome to Influencers AI Agents!\n\nFeatures:\n- AI Content Generation\n- Personalized Style\n- Multi-platform Publishing\n\nGet started: {FRONTEND_URL}\n\n© 2026 INFLUENCERS"
        },
        Language.JA: {
            "subject": "INFLUENCERS — ようこそ",
            "html": _lane_crawford_base(ja_body, "'Noto Sans JP', Arial, 'Helvetica Neue', sans-serif"),
            "text": f"INFLUENCERS — ようこそ\n\n{user_name} さん、こんにちは！\n\nInfluencers AI Agents へようこそ！\n\n機能一覧：\n- AI コンテンツ生成\n- パーソナライズドスタイル\n- マルチプラットフォーム投稿\n\n今すぐ始める：{FRONTEND_URL}\n\n© 2026 INFLUENCERS"
        }
    }
    
    return templates.get(language, templates[Language.ZH_TW])


# 建立全域實例
email_service = EmailService()

