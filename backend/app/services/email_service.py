"""
Email 服務
Phase 2: 會員系統
使用 Gmail SMTP 發送郵件（支援異步）
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from app.config_module import settings
from app.models.user import Language
import logging

logger = logging.getLogger(__name__)

# Gmail SMTP 設定
GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


class EmailService:
    """Email 服務（使用 Gmail SMTP）"""
    
    def __init__(self):
        self.smtp_host = GMAIL_SMTP_HOST
        self.smtp_port = GMAIL_SMTP_PORT
        self.username = settings.GMAIL_USER
        self.password = settings.GMAIL_APP_PASSWORD
        self.from_email = settings.GMAIL_USER
        self.from_name = "Influencers AI Agents"
    
    def is_configured(self) -> bool:
        """檢查 Email 服務是否已配置"""
        return bool(self.username and self.password)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        發送 Email
        
        Args:
            to_email: 收件人 Email
            subject: 郵件主題
            html_content: HTML 內容
            text_content: 純文字內容（可選）
            
        Returns:
            是否發送成功
        """
        if not self.is_configured():
            logger.warning("Email 服務未配置，跳過發送")
            return False
        
        try:
            # 建立郵件
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # 添加純文字版本
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)
            
            # 添加 HTML 版本
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # 發送郵件
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                start_tls=True
            )
            
            logger.info(f"Email 發送成功: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email 發送失敗: {e}")
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
# Email 模板
# ============================================

# 前端 URL（用於郵件中的連結）
FRONTEND_URL = "http://localhost:5173"  # 開發環境，生產環境需要更新


def get_verification_email_template(
    verification_token: str,
    language: Language = Language.ZH_TW
) -> Dict[str, str]:
    """
    取得 Email 驗證郵件模板
    
    Args:
        verification_token: 驗證 Token
        language: 語言
        
    Returns:
        包含 subject, html, text 的字典
    """
    verify_url = f"{FRONTEND_URL}/verify-email?token={verification_token}"
    
    templates = {
        Language.ZH_TW: {
            "subject": "請驗證您的 Email - Influencers AI Agents",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Noto Sans TC', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 歡迎加入 Influencers AI Agents！</h1>
        </div>
        <div class="content">
            <p>您好！</p>
            <p>感謝您註冊 Influencers AI Agents。請點擊下方按鈕驗證您的 Email 地址：</p>
            <p style="text-align: center;">
                <a href="{verify_url}" class="button">驗證 Email</a>
            </p>
            <p>如果按鈕無法點擊，請複製以下連結到瀏覽器：</p>
            <p style="word-break: break-all; color: #667eea;">{verify_url}</p>
            <p>此連結將在 24 小時後過期。</p>
            <p>如果您沒有註冊帳號，請忽略此郵件。</p>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
歡迎加入 Influencers AI Agents！

感謝您註冊。請點擊以下連結驗證您的 Email 地址：

{verify_url}

此連結將在 24 小時後過期。

如果您沒有註冊帳號，請忽略此郵件。

© 2026 Influencers AI Agents
            """
        },
        Language.EN: {
            "subject": "Verify Your Email - Influencers AI Agents",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to Influencers AI Agents!</h1>
        </div>
        <div class="content">
            <p>Hello!</p>
            <p>Thank you for signing up. Please click the button below to verify your email address:</p>
            <p style="text-align: center;">
                <a href="{verify_url}" class="button">Verify Email</a>
            </p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #667eea;">{verify_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
Welcome to Influencers AI Agents!

Thank you for signing up. Please click the link below to verify your email address:

{verify_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

© 2026 Influencers AI Agents
            """
        },
        Language.JA: {
            "subject": "メールアドレスの確認 - Influencers AI Agents",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Noto Sans JP', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Influencers AI Agents へようこそ！</h1>
        </div>
        <div class="content">
            <p>こんにちは！</p>
            <p>ご登録ありがとうございます。以下のボタンをクリックして、メールアドレスを確認してください：</p>
            <p style="text-align: center;">
                <a href="{verify_url}" class="button">メールを確認</a>
            </p>
            <p>ボタンが機能しない場合は、以下のリンクをブラウザにコピーしてください：</p>
            <p style="word-break: break-all; color: #667eea;">{verify_url}</p>
            <p>このリンクは 24 時間後に期限切れになります。</p>
            <p>アカウントを作成していない場合は、このメールを無視してください。</p>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
Influencers AI Agents へようこそ！

ご登録ありがとうございます。以下のリンクをクリックして、メールアドレスを確認してください：

{verify_url}

このリンクは 24 時間後に期限切れになります。

アカウントを作成していない場合は、このメールを無視してください。

© 2026 Influencers AI Agents
            """
        }
    }
    
    return templates.get(language, templates[Language.ZH_TW])


def get_password_reset_email_template(
    reset_token: str,
    language: Language = Language.ZH_TW
) -> Dict[str, str]:
    """
    取得密碼重設郵件模板
    """
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    
    templates = {
        Language.ZH_TW: {
            "subject": "重設密碼 - Influencers AI Agents",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Noto Sans TC', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
        .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 重設密碼</h1>
        </div>
        <div class="content">
            <p>您好！</p>
            <p>我們收到了重設您密碼的請求。請點擊下方按鈕設定新密碼：</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">重設密碼</a>
            </p>
            <p>如果按鈕無法點擊，請複製以下連結到瀏覽器：</p>
            <p style="word-break: break-all; color: #f5576c;">{reset_url}</p>
            <p>此連結將在 24 小時後過期。</p>
            <div class="warning">
                ⚠️ 如果您沒有請求重設密碼，請忽略此郵件。您的帳號安全無虞。
            </div>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
重設密碼 - Influencers AI Agents

我們收到了重設您密碼的請求。請點擊以下連結設定新密碼：

{reset_url}

此連結將在 24 小時後過期。

如果您沒有請求重設密碼，請忽略此郵件。

© 2026 Influencers AI Agents
            """
        },
        Language.EN: {
            "subject": "Reset Your Password - Influencers AI Agents",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
        .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Reset Your Password</h1>
        </div>
        <div class="content">
            <p>Hello!</p>
            <p>We received a request to reset your password. Click the button below to set a new password:</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #f5576c;">{reset_url}</p>
            <p>This link will expire in 24 hours.</p>
            <div class="warning">
                ⚠️ If you didn't request a password reset, please ignore this email. Your account is safe.
            </div>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
Reset Your Password - Influencers AI Agents

We received a request to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 24 hours.

If you didn't request a password reset, please ignore this email.

© 2026 Influencers AI Agents
            """
        },
        Language.JA: {
            "subject": "パスワードのリセット - Influencers AI Agents",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Noto Sans JP', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
        .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 パスワードのリセット</h1>
        </div>
        <div class="content">
            <p>こんにちは！</p>
            <p>パスワードリセットのリクエストを受け取りました。以下のボタンをクリックして新しいパスワードを設定してください：</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">パスワードをリセット</a>
            </p>
            <p>ボタンが機能しない場合は、以下のリンクをブラウザにコピーしてください：</p>
            <p style="word-break: break-all; color: #f5576c;">{reset_url}</p>
            <p>このリンクは 24 時間後に期限切れになります。</p>
            <div class="warning">
                ⚠️ パスワードリセットをリクエストしていない場合は、このメールを無視してください。アカウントは安全です。
            </div>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
パスワードのリセット - Influencers AI Agents

パスワードリセットのリクエストを受け取りました。以下のリンクをクリックして新しいパスワードを設定してください：

{reset_url}

このリンクは 24 時間後に期限切れになります。

パスワードリセットをリクエストしていない場合は、このメールを無視してください。

© 2026 Influencers AI Agents
            """
        }
    }
    
    return templates.get(language, templates[Language.ZH_TW])


def get_welcome_email_template(
    user_name: str,
    language: Language = Language.ZH_TW
) -> Dict[str, str]:
    """
    取得歡迎郵件模板
    """
    templates = {
        Language.ZH_TW: {
            "subject": "歡迎加入 Influencers AI Agents！🎉",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Noto Sans TC', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .feature {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 歡迎加入，{user_name}！</h1>
        </div>
        <div class="content">
            <p>您好 {user_name}！</p>
            <p>歡迎加入 Influencers AI Agents！我們很高興您成為我們的一員。</p>
            <p>以下是您可以開始使用的功能：</p>
            <div class="feature">✨ <strong>AI 內容生成</strong> - 自動生成高品質社交媒體內容</div>
            <div class="feature">📊 <strong>個人化風格</strong> - AI 學習您的風格偏好</div>
            <div class="feature">🌐 <strong>多平台發布</strong> - 一鍵發布到多個社交平台</div>
            <p>立即開始探索吧！</p>
            <p style="text-align: center;">
                <a href="{FRONTEND_URL}" style="display: inline-block; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">開始使用</a>
            </p>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
歡迎加入，{user_name}！

歡迎加入 Influencers AI Agents！我們很高興您成為我們的一員。

以下是您可以開始使用的功能：
- AI 內容生成 - 自動生成高品質社交媒體內容
- 個人化風格 - AI 學習您的風格偏好
- 多平台發布 - 一鍵發布到多個社交平台

立即開始探索：{FRONTEND_URL}

© 2026 Influencers AI Agents
            """
        },
        Language.EN: {
            "subject": "Welcome to Influencers AI Agents! 🎉",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .feature {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome, {user_name}!</h1>
        </div>
        <div class="content">
            <p>Hello {user_name}!</p>
            <p>Welcome to Influencers AI Agents! We're excited to have you on board.</p>
            <p>Here's what you can start with:</p>
            <div class="feature">✨ <strong>AI Content Generation</strong> - Auto-generate high-quality social media content</div>
            <div class="feature">📊 <strong>Personalized Style</strong> - AI learns your style preferences</div>
            <div class="feature">🌐 <strong>Multi-platform Publishing</strong> - One-click publish to multiple platforms</div>
            <p>Start exploring now!</p>
            <p style="text-align: center;">
                <a href="{FRONTEND_URL}" style="display: inline-block; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Get Started</a>
            </p>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
Welcome, {user_name}!

Welcome to Influencers AI Agents! We're excited to have you on board.

Here's what you can start with:
- AI Content Generation - Auto-generate high-quality social media content
- Personalized Style - AI learns your style preferences
- Multi-platform Publishing - One-click publish to multiple platforms

Start exploring: {FRONTEND_URL}

© 2026 Influencers AI Agents
            """
        },
        Language.JA: {
            "subject": "Influencers AI Agents へようこそ！🎉",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Noto Sans JP', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #fff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
        .feature {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 ようこそ、{user_name} さん！</h1>
        </div>
        <div class="content">
            <p>{user_name} さん、こんにちは！</p>
            <p>Influencers AI Agents へようこそ！ご参加いただきありがとうございます。</p>
            <p>以下の機能をお試しください：</p>
            <div class="feature">✨ <strong>AI コンテンツ生成</strong> - 高品質なソーシャルメディアコンテンツを自動生成</div>
            <div class="feature">📊 <strong>パーソナライズドスタイル</strong> - AI があなたのスタイル好みを学習</div>
            <div class="feature">🌐 <strong>マルチプラットフォーム投稿</strong> - ワンクリックで複数のプラットフォームに投稿</div>
            <p>今すぐ始めましょう！</p>
            <p style="text-align: center;">
                <a href="{FRONTEND_URL}" style="display: inline-block; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">始める</a>
            </p>
        </div>
        <div class="footer">
            <p>© 2026 Influencers AI Agents. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """,
            "text": f"""
ようこそ、{user_name} さん！

Influencers AI Agents へようこそ！ご参加いただきありがとうございます。

以下の機能をお試しください：
- AI コンテンツ生成 - 高品質なソーシャルメディアコンテンツを自動生成
- パーソナライズドスタイル - AI があなたのスタイル好みを学習
- マルチプラットフォーム投稿 - ワンクリックで複数のプラットフォームに投稿

今すぐ始める: {FRONTEND_URL}

© 2026 Influencers AI Agents
            """
        }
    }
    
    return templates.get(language, templates[Language.ZH_TW])


# 建立全域實例
email_service = EmailService()

