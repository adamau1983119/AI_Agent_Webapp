"""
i18n 工具模組
提供多語言錯誤訊息支援
"""
from typing import Dict, Optional


class I18nErrorMessages:
    """i18n 錯誤訊息管理類"""
    
    # 錯誤訊息字典
    ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
        # 認證相關
        "auth.register_failed": {
            "zh-TW": "註冊失敗，請稍後再試",
            "en": "Registration failed, please try again later",
            "ja": "登録に失敗しました。後でもう一度お試しください"
        },
        "auth.invalid_credentials": {
            "zh-TW": "Email 或密碼錯誤",
            "en": "Invalid email or password",
            "ja": "メールアドレスまたはパスワードが正しくありません"
        },
        "auth.verification_invalid": {
            "zh-TW": "驗證連結無效或已過期",
            "en": "Verification link is invalid or expired",
            "ja": "確認リンクが無効または期限切れです"
        },
        "auth.verification_success": {
            "zh-TW": "Email 驗證成功",
            "en": "Email verification successful",
            "ja": "メール確認が成功しました"
        },
        "auth.verification_sent": {
            "zh-TW": "如果該 Email 已註冊，驗證郵件已發送",
            "en": "If the email is registered, a verification email has been sent",
            "ja": "メールアドレスが登録されている場合、確認メールが送信されました"
        },
        "auth.email_send_failed": {
            "zh-TW": "註冊成功，但驗證郵件發送失敗。請稍後使用「重新發送驗證郵件」功能",
            "en": "Registration successful, but verification email failed to send. Please use 'Resend verification email' later",
            "ja": "登録は成功しましたが、確認メールの送信に失敗しました。後で「確認メールを再送信」機能をご利用ください"
        },
        "auth.email_not_configured": {
            "zh-TW": "註冊成功，但郵件服務未配置，無法發送驗證郵件。請聯繫管理員",
            "en": "Registration successful, but email service is not configured. Please contact administrator",
            "ja": "登録は成功しましたが、メールサービスが設定されていません。管理者にお問い合わせください"
        },
        "auth.invalid_email_format": {
            "zh-TW": "請輸入有效的 Email 地址",
            "en": "Please enter a valid email address",
            "ja": "有効なメールアドレスを入力してください"
        },
        "auth.email_already_registered": {
            "zh-TW": "此 Email 已被註冊，請使用此 Email 登入",
            "en": "This email is already registered. Please sign in with this email",
            "ja": "このメールアドレスは既に登録されています。このメールアドレスでログインしてください"
        },
        "auth.already_verified": {
            "zh-TW": "Email 已驗證，無需重新驗證",
            "en": "Email is already verified, no need to verify again",
            "ja": "メールアドレスは既に確認済みです"
        },
        "auth.reset_link_invalid": {
            "zh-TW": "重設連結無效或已過期",
            "en": "Reset link is invalid or expired",
            "ja": "リセットリンクが無効または期限切れです"
        },
        "auth.reset_success": {
            "zh-TW": "密碼重設成功",
            "en": "Password reset successful",
            "ja": "パスワードリセットが成功しました"
        },
        "auth.oauth_not_configured": {
            "zh-TW": "Google OAuth 未配置",
            "en": "Google OAuth is not configured",
            "ja": "Google OAuthが設定されていません"
        },
        
        # 頻道相關
        "channel.not_found": {
            "zh-TW": "頻道不存在",
            "en": "Channel not found",
            "ja": "チャンネルが見つかりません"
        },
        "channel.max_reached": {
            "zh-TW": "已達到頻道數量上限",
            "en": "Maximum number of channels reached",
            "ja": "チャンネル数の上限に達しました"
        },
        "channel.update_failed": {
            "zh-TW": "更新頻道失敗",
            "en": "Failed to update channel",
            "ja": "チャンネルの更新に失敗しました"
        },
        "channel.delete_failed": {
            "zh-TW": "刪除頻道失敗",
            "en": "Failed to delete channel",
            "ja": "チャンネルの削除に失敗しました"
        },
        "channel.collect_failed": {
            "zh-TW": "收集頻道內容失敗",
            "en": "Failed to collect channel content",
            "ja": "チャンネルコンテンツの収集に失敗しました"
        },
        
        # 內容生成相關
        "generate.failed": {
            "zh-TW": "內容生成失敗",
            "en": "Content generation failed",
            "ja": "コンテンツ生成に失敗しました"
        },
        "generate.regenerate_failed": {
            "zh-TW": "重新生成失敗",
            "en": "Regeneration failed",
            "ja": "再生成に失敗しました"
        },
        
        # 圖片相關
        "image.match_failed": {
            "zh-TW": "圖片匹配失敗",
            "en": "Image matching failed",
            "ja": "画像マッチングに失敗しました"
        },
        "image.search_failed": {
            "zh-TW": "圖片搜尋失敗",
            "en": "Image search failed",
            "ja": "画像検索に失敗しました"
        },
        
        # 通用錯誤
        "common.not_found": {
            "zh-TW": "資源不存在",
            "en": "Resource not found",
            "ja": "リソースが見つかりません"
        },
        "common.unauthorized": {
            "zh-TW": "未授權，請先登入",
            "en": "Unauthorized, please login first",
            "ja": "認証されていません。ログインしてください"
        },
        "common.forbidden": {
            "zh-TW": "無權限訪問此資源",
            "en": "Forbidden to access this resource",
            "ja": "このリソースにアクセスする権限がありません"
        },
        "common.validation_error": {
            "zh-TW": "資料驗證失敗",
            "en": "Data validation failed",
            "ja": "データ検証に失敗しました"
        },
        "common.server_error": {
            "zh-TW": "伺服器內部錯誤",
            "en": "Internal server error",
            "ja": "サーバー内部エラー"
        },
        "common.rate_limit": {
            "zh-TW": "請求過於頻繁，請稍後再試",
            "en": "Too many requests, please try again later",
            "ja": "リクエストが多すぎます。後でもう一度お試しください"
        },
        
        # 主題相關
        "topic.not_found": {
            "zh-TW": "主題不存在",
            "en": "Topic not found",
            "ja": "トピックが見つかりません"
        },
        "topic.update_failed": {
            "zh-TW": "更新主題失敗",
            "en": "Failed to update topic",
            "ja": "トピックの更新に失敗しました"
        },
        "topic.delete_failed": {
            "zh-TW": "刪除主題失敗",
            "en": "Failed to delete topic",
            "ja": "トピックの削除に失敗しました"
        },
        "topic.database_unavailable": {
            "zh-TW": "資料庫服務暫時不可用，請稍後再試",
            "en": "Database service temporarily unavailable, please try again later",
            "ja": "データベースサービスが一時的に利用できません。後でもう一度お試しください"
        },
        "topic.database_not_connected": {
            "zh-TW": "資料庫未連接，無法刪除主題",
            "en": "Database not connected, unable to delete topic",
            "ja": "データベースに接続されていません。トピックを削除できません"
        },
        
        # 風格相關
        "style.not_found": {
            "zh-TW": "風格不存在",
            "en": "Style not found",
            "ja": "スタイルが見つかりません"
        },
        "style.format_not_found": {
            "zh-TW": "格式不存在",
            "en": "Format not found",
            "ja": "フォーマットが見つかりません"
        },
        
        # 社交平台相關
        "social.invalid_state": {
            "zh-TW": "無效的 state",
            "en": "Invalid state",
            "ja": "無効なstate"
        },
        "social.publish_task_not_found": {
            "zh-TW": "發布任務不存在",
            "en": "Publish task not found",
            "ja": "公開タスクが見つかりません"
        },
        
        # 圖片相關
        "image.invalid_url": {
            "zh-TW": "無效的 URL 格式，必須以 http:// 或 https:// 開頭",
            "en": "Invalid URL format, must start with http:// or https://",
            "ja": "無効なURL形式です。http://またはhttps://で始まる必要があります"
        },
        "image.domain_not_allowed": {
            "zh-TW": "URL 不在允許的域名白名單中",
            "en": "URL is not in the allowed domain whitelist",
            "ja": "URLが許可されたドメインホワイトリストにありません"
        },
        "image.update_failed": {
            "zh-TW": "更新圖片失敗",
            "en": "Failed to update image",
            "ja": "画像の更新に失敗しました"
        },
        "image.delete_failed": {
            "zh-TW": "刪除圖片失敗",
            "en": "Failed to delete image",
            "ja": "画像の削除に失敗しました"
        },
        "image.reorder_failed": {
            "zh-TW": "重新排序失敗",
            "en": "Failed to reorder images",
            "ja": "画像の並び替えに失敗しました"
        },
        "image.content_empty": {
            "zh-TW": "文章內容為空，無法進行智能匹配。請先生成完整的文章內容或確保主題有原文內容。",
            "en": "Article content is empty, unable to perform smart matching. Please generate complete article content first or ensure the topic has original content.",
            "ja": "記事の内容が空です。スマートマッチングを実行できません。まず完全な記事内容を生成するか、トピックに元の内容があることを確認してください。"
        },
        
        # 功能標誌相關
        "feature_flag.admin_required": {
            "zh-TW": "需要管理員權限",
            "en": "Administrator privileges required",
            "ja": "管理者権限が必要です"
        },
        
        # 用戶相關
        "user.preference_update_failed": {
            "zh-TW": "更新偏好失敗",
            "en": "Failed to update preferences",
            "ja": "設定の更新に失敗しました"
        },
        
        # 排程相關
        "schedule.database_unavailable": {
            "zh-TW": "資料庫服務暫時不可用，請稍後再試",
            "en": "Database service temporarily unavailable, please try again later",
            "ja": "データベースサービスが一時的に利用できません。後でもう一度お試しください"
        },
        "schedule.database_not_connected": {
            "zh-TW": "資料庫未連接，無法生成主題",
            "en": "Database not connected, unable to generate topics",
            "ja": "データベースに接続されていません。トピックを生成できません"
        },
        "schedule.suggestion.check_mongodb": {
            "zh-TW": "請檢查 MONGODB_URL 並確保 MongoDB 服務正在運行",
            "en": "Please check MONGODB_URL and ensure MongoDB service is running",
            "ja": "MONGODB_URLを確認し、MongoDBサービスが実行されていることを確認してください"
        },
        "schedule.suggestion.check_mongodb_config": {
            "zh-TW": "請檢查 MONGODB_URL 配置和 MongoDB 服務狀態",
            "en": "Please check MONGODB_URL configuration and MongoDB service status",
            "ja": "MONGODB_URL設定とMongoDBサービスの状態を確認してください"
        },
        
        # 快取相關
        "cache.admin_required": {
            "zh-TW": "無權限清除快取（需要管理員權限）",
            "en": "No permission to clear cache (administrator privileges required)",
            "ja": "キャッシュをクリアする権限がありません（管理者権限が必要です）"
        },
        
        # 頻道服務相關
        "channel.max_reached_detail": {
            "zh-TW": "已達頻道上限（最多 {max} 個）",
            "en": "Maximum number of channels reached (max {max})",
            "ja": "チャンネル数の上限に達しました（最大{max}個）"
        },
        "channel.custom_keywords_required": {
            "zh-TW": "選擇「其他」類別時必須提供自定義關鍵字",
            "en": "Custom keywords are required when category is 'other'",
            "ja": "「その他」カテゴリを選択する場合は、カスタムキーワードが必要です"
        },
        "channel.create_failed": {
            "zh-TW": "建立頻道失敗",
            "en": "Failed to create channel",
            "ja": "チャンネルの作成に失敗しました"
        },
        "channel.delete_success": {
            "zh-TW": "頻道已刪除",
            "en": "Channel deleted successfully",
            "ja": "チャンネルが削除されました"
        },
        "channel.collect_success": {
            "zh-TW": "收集完成",
            "en": "Collection completed",
            "ja": "収集が完了しました"
        },
        "channel.assist_error": {
            "zh-TW": "處理請求時發生錯誤",
            "en": "An error occurred while processing the request",
            "ja": "リクエストの処理中にエラーが発生しました"
        },
        
        # 內容相關
        "content.not_found": {
            "zh-TW": "內容不存在",
            "en": "Content not found",
            "ja": "コンテンツが見つかりません"
        },
        "content.topic_not_found": {
            "zh-TW": "主題不存在",
            "en": "Topic not found",
            "ja": "トピックが見つかりません"
        },
        
        # 圖片相關（擴展）
        "image.not_found": {
            "zh-TW": "圖片不存在",
            "en": "Image not found",
            "ja": "画像が見つかりません"
        },
        "image.topic_not_found": {
            "zh-TW": "主題不存在",
            "en": "Topic not found",
            "ja": "トピックが見つかりません"
        },
        "image.topic_content_not_found": {
            "zh-TW": "主題內容不存在",
            "en": "Topic content not found",
            "ja": "トピックコンテンツが見つかりません"
        },
        "image.fetch_failed": {
            "zh-TW": "無法獲取圖片",
            "en": "Failed to fetch image",
            "ja": "画像の取得に失敗しました"
        },
        "image.invalid_content_type": {
            "zh-TW": "響應不是圖片類型",
            "en": "Response is not an image type",
            "ja": "レスポンスが画像タイプではありません"
        },
        "image.file_too_large": {
            "zh-TW": "圖片文件過大（最大 10MB）",
            "en": "Image file is too large (max 10MB)",
            "ja": "画像ファイルが大きすぎます（最大10MB）"
        },
        "image.request_timeout": {
            "zh-TW": "請求超時",
            "en": "Request timeout",
            "ja": "リクエストタイムアウト"
        },
        "image.server_connection_failed": {
            "zh-TW": "無法連接到圖片伺服器",
            "en": "Failed to connect to image server",
            "ja": "画像サーバーに接続できませんでした"
        },
        "image.server_error": {
            "zh-TW": "伺服器內部錯誤",
            "en": "Internal server error",
            "ja": "サーバー内部エラー"
        },
        
        # 主題相關（擴展）
        "topic.data_incomplete": {
            "zh-TW": "主題資料不完整，缺少欄位",
            "en": "Topic data is incomplete, missing field",
            "ja": "トピックデータが不完全です。フィールドが不足しています"
        },
        "topic.detail_response_failed": {
            "zh-TW": "建立主題詳情回應失敗",
            "en": "Failed to create topic detail response",
            "ja": "トピック詳細レスポンスの作成に失敗しました"
        },
        "topic.search_failed": {
            "zh-TW": "搜尋失敗",
            "en": "Search failed",
            "ja": "検索に失敗しました"
        },
        "topic.url_check_failed": {
            "zh-TW": "檢查失敗",
            "en": "Check failed",
            "ja": "チェックに失敗しました"
        },
        "topic.popular_queries_failed": {
            "zh-TW": "獲取熱門查詢失敗",
            "en": "Failed to get popular queries",
            "ja": "人気クエリの取得に失敗しました"
        },
        "topic.cache_clear_failed": {
            "zh-TW": "清除快取失敗",
            "en": "Failed to clear cache",
            "ja": "キャッシュのクリアに失敗しました"
        },
        "topic.health_check_failed": {
            "zh-TW": "健康檢查失敗",
            "en": "Health check failed",
            "ja": "ヘルスチェックに失敗しました"
        },
        
        # Feed 相關
        "feed.invalid_category": {
            "zh-TW": "無效的分類，有效值為: fashion, food, trend",
            "en": "Invalid category, valid values are: fashion, food, trend",
            "ja": "無効なカテゴリです。有効な値は：fashion、food、trend"
        },
        
        # 功能標誌相關（擴展）
        "feature_flag.not_found": {
            "zh-TW": "未知的功能",
            "en": "Unknown feature",
            "ja": "不明な機能"
        },
        
        # 用戶相關（擴展）
        "user.weight_sum_invalid": {
            "zh-TW": "權重總和必須為 1.0，當前總和為 {total}",
            "en": "Weight sum must be 1.0, current sum is {total}",
            "ja": "重みの合計は1.0である必要があります。現在の合計は{total}です"
        },
        
        # 自動化工作流相關
        "workflow.image_api_keys_not_set": {
            "zh-TW": "所有圖片服務的 API Key 都未設定，圖片搜尋失敗",
            "en": "All image service API keys are not set, image search failed",
            "ja": "すべての画像サービスAPIキーが設定されていません。画像検索に失敗しました"
        },
        
        # 分發服務相關
        "distribution.disconnect_failed": {
            "zh-TW": "斷開連接失敗",
            "en": "Failed to disconnect",
            "ja": "切断に失敗しました"
        },
        "distribution.token_exchange_failed": {
            "zh-TW": "Token 交換失敗",
            "en": "Token exchange failed",
            "ja": "トークン交換に失敗しました"
        },
        "distribution.get_user_info_failed": {
            "zh-TW": "無法取得用戶資訊",
            "en": "Failed to get user information",
            "ja": "ユーザー情報の取得に失敗しました"
        },
        "distribution.tiktok_not_implemented": {
            "zh-TW": "TikTok API 整合尚未完成",
            "en": "TikTok API integration is not yet implemented",
            "ja": "TikTok API統合はまだ実装されていません"
        },
        "distribution.no_valid_connection": {
            "zh-TW": "沒有有效的平台連接",
            "en": "No valid platform connection",
            "ja": "有効なプラットフォーム接続がありません"
        },
        
        # 風格學習服務相關
        "style.update_failed": {
            "zh-TW": "更新風格失敗",
            "en": "Failed to update style",
            "ja": "スタイルの更新に失敗しました"
        },
        "style.reset_failed": {
            "zh-TW": "重置失敗",
            "en": "Reset failed",
            "ja": "リセットに失敗しました"
        },
        
        # 驗證相關
        "validation.invalid_language": {
            "zh-TW": "不支援的語言選項",
            "en": "Unsupported language option",
            "ja": "サポートされていない言語オプション"
        },
        "validation.no_fields": {
            "zh-TW": "請提供至少一個要更新的欄位",
            "en": "Please provide at least one field to update",
            "ja": "少なくとも1つの更新フィールドを指定してください"
        },
        "auth.user_not_found": {
            "zh-TW": "找不到使用者",
            "en": "User not found",
            "ja": "ユーザーが見つかりません"
        },
    }
    
    @classmethod
    def get_error_message(cls, error_key: str, language: str = "zh-TW", **kwargs) -> str:
        """
        根據語言返回對應的錯誤訊息
        
        Args:
            error_key: 錯誤鍵（例如：auth.invalid_credentials）
            language: 用戶語言（zh-TW/en/ja）
            **kwargs: 格式化參數（例如：max=3）
            
        Returns:
            對應語言的錯誤訊息，如果找不到則返回英文版本
        """
        if error_key not in cls.ERROR_MESSAGES:
            # 如果找不到錯誤鍵，返回錯誤鍵本身
            return error_key
        
        error_dict = cls.ERROR_MESSAGES[error_key]
        
        # 如果語言不在字典中，使用英文作為預設
        if language not in error_dict:
            language = "en"
        
        message = error_dict.get(language, error_dict.get("en", error_key))
        
        # 如果有格式化參數，進行格式化
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                # 如果格式化失敗，返回原始訊息
                pass
        
        return message
    
    @classmethod
    def get_user_language(cls, user: Optional[dict] = None, request: Optional[object] = None) -> str:
        """
        從用戶或請求中獲取語言偏好
        
        Args:
            user: 用戶字典（包含 language 字段）
            request: FastAPI Request 對象（從 headers 中獲取 Accept-Language）
            
        Returns:
            語言代碼（zh-TW/en/ja）
        """
        # 1. 最高優先：前端傳來的 X-Language header（用戶在 UI 上選擇的語言）
        if request and hasattr(request, "headers"):
            x_language = request.headers.get("X-Language", "")
            if x_language in ["zh-TW", "en", "ja"]:
                return x_language
        
        # 2. 從用戶資料獲取
        if user and user.get("language"):
            lang = user.get("language")
            # 標準化語言代碼
            if lang in ["zh-TW", "zh", "zh_CN"]:
                return "zh-TW"
            elif lang in ["en", "en-US", "en_US"]:
                return "en"
            elif lang in ["ja", "ja-JP", "ja_JP"]:
                return "ja"
            return "zh-TW"  # 預設
        
        # 3. 從 Accept-Language header 獲取（按優先順序解析）
        if request and hasattr(request, "headers"):
            accept_language = request.headers.get("Accept-Language", "")
            # 解析 Accept-Language，取最高優先級的語言
            if accept_language:
                # 先檢查是否有明確的中文優先
                parts = [p.strip().split(';')[0].strip() for p in accept_language.split(',')]
                for part in parts:
                    part_lower = part.lower()
                    if part_lower.startswith("zh"):
                        return "zh-TW"
                    elif part_lower.startswith("ja"):
                        return "ja"
                    elif part_lower.startswith("en"):
                        return "en"
        
        # 預設繁體中文
        return "zh-TW"


# 便捷函數
def get_error_message(error_key: str, language: str = "zh-TW", **kwargs) -> str:
    """便捷函數：獲取錯誤訊息"""
    return I18nErrorMessages.get_error_message(error_key, language, **kwargs)


def get_user_language(user: Optional[dict] = None, request: Optional[object] = None) -> str:
    """便捷函數：獲取用戶語言"""
    return I18nErrorMessages.get_user_language(user, request)

