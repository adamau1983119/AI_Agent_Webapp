"""
分發服務
Phase 5: 分發與整合
處理內容發布到各社交平台
"""
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import httpx
from app.services.repositories.social_connection_repository import SocialConnectionRepository
from app.services.repositories.publish_queue_repository import PublishQueueRepository
from app.models.social_connection import (
    SocialPlatform, ConnectionStatus, PublishStatus, PublishRequest,
    PLATFORM_CONFIGS,
    META_FACEBOOK_PAGE_SCOPES,
    META_INSTAGRAM_OAUTH_SCOPES,
    META_FACEBOOK_OAUTH_SCOPES_PUBLISH,
    TIKTOK_OAUTH_SCOPES,
    optimize_content_for_platform,
)
from app.config_module import settings
from app.utils.i18n import get_error_message
import logging

logger = logging.getLogger(__name__)


class DistributionService:
    """分發服務"""
    
    def __init__(self):
        self.connection_repo = SocialConnectionRepository()
        self.publish_repo = PublishQueueRepository()
    
    # ============================================
    # 帳號連接管理
    # ============================================
    
    async def get_user_connections(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """取得用戶的所有社交連接"""
        return await self.connection_repo.get_user_connections(user_id)
    
    async def get_connection(
        self,
        user_id: str,
        platform: SocialPlatform
    ) -> Optional[Dict[str, Any]]:
        """取得特定平台的連接"""
        return await self.connection_repo.get_user_connection(user_id, platform)
    
    async def disconnect_platform(
        self,
        user_id: str,
        platform: SocialPlatform,
        language: str = "zh-TW"
    ) -> Tuple[bool, Optional[str]]:
        """斷開平台連接"""
        success = await self.connection_repo.disconnect(user_id, platform)
        if not success:
            return False, get_error_message("distribution.disconnect_failed", language)
        
        logger.info(f"用戶 {user_id} 斷開 {platform.value} 連接")
        return True, None
    
    # ============================================
    # Meta OAuth (Instagram + Facebook + Threads)
    # ============================================
    
    def _meta_oauth_scopes_for(self, target: str) -> List[str]:
        """依連線目標選 scope（facebook 與 instagram 分開，不可混用無效 scope）"""
        if target == "instagram":
            scopes = list(META_INSTAGRAM_OAUTH_SCOPES)
        else:
            scopes = list(META_FACEBOOK_PAGE_SCOPES)
        if getattr(settings, "META_OAUTH_INCLUDE_PUBLISH", False):
            scopes.extend(META_FACEBOOK_OAUTH_SCOPES_PUBLISH)
        return scopes

    def get_meta_oauth_url(self, state: str, target: str = "facebook") -> str:
        """取得 Meta OAuth 授權 URL；target: facebook | instagram"""
        client_id = settings.META_APP_ID
        redirect_uri = f"{settings.BACKEND_URL}/api/v1/social/meta/callback"
        scopes = ",".join(self._meta_oauth_scopes_for(target))
        
        return (
            f"https://www.facebook.com/v18.0/dialog/oauth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
            f"&response_type=code"
        )
    
    async def handle_meta_callback(
        self,
        user_id: str,
        code: str,
        target: str = "facebook",
        language: str = "zh-TW"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """處理 Meta OAuth 回調；target: facebook | instagram"""
        try:
            # 交換 access token
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "code": code,
                "redirect_uri": f"{settings.BACKEND_URL}/api/v1/social/meta/callback"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(token_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Meta token exchange failed: {response.text}")
                    return None, get_error_message("distribution.token_exchange_failed", language)
                
                token_data = response.json()
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 5184000)  # 預設 60 天
                
                # 取得用戶資訊
                user_info = await self._get_meta_user_info(access_token)
                if not user_info:
                    return None, get_error_message("distribution.get_user_info_failed", language)
                
                scopes_used = self._meta_oauth_scopes_for(target)
                connections = []
                connect_facebook = target == "facebook"
                connect_instagram = target == "instagram"

                if connect_facebook:
                    fb_connection = await self.connection_repo.create_connection(user_id, {
                        "platform": SocialPlatform.FACEBOOK.value,
                        "platform_user_id": user_info.get("id"),
                        "platform_username": user_info.get("name", ""),
                        "platform_name": user_info.get("name"),
                        "profile_image_url": user_info.get("picture", {}).get("data", {}).get("url"),
                        "access_token": access_token,
                        "token_expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
                        "scopes": scopes_used,
                    })
                    page = await self._get_first_facebook_page(access_token)
                    if page:
                        fb_connection = await self.connection_repo.update_connection(
                            user_id,
                            SocialPlatform.FACEBOOK,
                            {
                                "page_id": page.get("id"),
                                "page_access_token": page.get("access_token"),
                                "page_name": page.get("name"),
                            },
                        ) or fb_connection
                    connections.append(fb_connection)

                if connect_instagram:
                    ig_account = await self._get_instagram_account(access_token)
                    if not ig_account:
                        if not connections:
                            return None, get_error_message("distribution.instagram_not_linked", language)
                    else:
                        ig_connection = await self.connection_repo.create_connection(user_id, {
                            "platform": SocialPlatform.INSTAGRAM.value,
                            "platform_user_id": ig_account.get("id"),
                            "platform_username": ig_account.get("username", ""),
                            "platform_name": ig_account.get("name"),
                            "profile_image_url": ig_account.get("profile_picture_url"),
                            "access_token": access_token,
                            "token_expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
                            "scopes": scopes_used,
                        })
                        connections.append(ig_connection)

                if not connections:
                    return None, get_error_message("distribution.connect_failed", language)

                logger.info(f"用戶 {user_id} 連接 Meta ({target}): {len(connections)} 個帳號")
                
                return {"connections": connections}, None
                
        except Exception as e:
            logger.error(f"Meta OAuth callback error: {e}")
            return None, str(e)
    
    async def _get_first_facebook_page(self, access_token: str) -> Optional[Dict[str, Any]]:
        """取得第一個可管理的 Facebook 粉絲專頁（含 page access token）"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.facebook.com/v18.0/me/accounts",
                    params={"access_token": access_token},
                )
                if response.status_code != 200:
                    logger.warning("me/accounts 失敗: %s", response.text[:300])
                    return None
                pages = response.json().get("data", [])
                return pages[0] if pages else None
        except Exception as e:
            logger.error("取得 Facebook Page 失敗: %s", e)
            return None

    async def _get_meta_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """取得 Meta 用戶資訊"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.facebook.com/v18.0/me",
                    params={
                        "access_token": access_token,
                        "fields": "id,name,picture"
                    }
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Get Meta user info error: {e}")
        return None
    
    async def _get_instagram_account(self, access_token: str) -> Optional[Dict[str, Any]]:
        """取得關聯的 Instagram 商業帳號"""
        try:
            async with httpx.AsyncClient() as client:
                # 取得 Pages
                pages_response = await client.get(
                    "https://graph.facebook.com/v18.0/me/accounts",
                    params={"access_token": access_token}
                )
                
                if pages_response.status_code != 200:
                    return None
                
                pages = pages_response.json().get("data", [])
                if not pages:
                    return None
                
                # 取得第一個 Page 的 Instagram 帳號
                page = pages[0]
                page_id = page.get("id")
                page_token = page.get("access_token")
                
                ig_response = await client.get(
                    f"https://graph.facebook.com/v18.0/{page_id}",
                    params={
                        "access_token": page_token,
                        "fields": "instagram_business_account"
                    }
                )
                
                if ig_response.status_code != 200:
                    return None
                
                ig_data = ig_response.json()
                ig_account = ig_data.get("instagram_business_account")
                
                if not ig_account:
                    return None
                
                # 取得 IG 帳號詳情
                ig_id = ig_account.get("id")
                details_response = await client.get(
                    f"https://graph.facebook.com/v18.0/{ig_id}",
                    params={
                        "access_token": access_token,
                        "fields": "id,username,name,profile_picture_url"
                    }
                )
                
                if details_response.status_code == 200:
                    return details_response.json()
                
        except Exception as e:
            logger.error(f"Get Instagram account error: {e}")
        
        return None
    
    # ============================================
    # TikTok OAuth
    # ============================================
    
    def get_tiktok_oauth_url(self, state: str) -> str:
        """取得 TikTok OAuth 授權 URL"""
        # TikTok OAuth 配置（需要 TikTok Developer 帳號）
        client_key = getattr(settings, "TIKTOK_CLIENT_KEY", "")
        redirect_uri = f"{settings.BACKEND_URL}/api/v1/social/tiktok/callback"
        scopes = ",".join(TIKTOK_OAUTH_SCOPES)
        
        return (
            f"https://www.tiktok.com/v2/auth/authorize/"
            f"?client_key={client_key}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
            f"&response_type=code"
        )
    
    async def handle_tiktok_callback(
        self,
        user_id: str,
        code: str,
        language: str = "zh-TW"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """處理 TikTok OAuth 回調"""
        # TikTok API 整合（需要 TikTok Developer 帳號）
        return None, get_error_message("distribution.tiktok_not_implemented", language)
    
    # ============================================
    # 發布功能
    # ============================================
    
    async def publish_content(
        self,
        user_id: str,
        publish_request: PublishRequest,
        language: str = "zh-TW"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        發布內容到多個平台
        
        Args:
            user_id: 用戶 ID
            publish_request: 發布請求
            language: 用戶語言
            
        Returns:
            (發布結果, 錯誤訊息)
        """
        # 驗證平台連接
        valid_platforms = []
        for platform in publish_request.platforms:
            connection = await self.connection_repo.get_user_connection(user_id, platform)
            if connection and connection.get("status") == ConnectionStatus.CONNECTED.value:
                valid_platforms.append(platform)
            else:
                logger.warning(f"用戶 {user_id} 的 {platform.value} 未連接")
        
        if not valid_platforms:
            return None, get_error_message("distribution.no_valid_connection", language)
        
        # 建立發布任務
        publish_job = await self.publish_repo.create_publish_job(user_id, {
            "content_id": publish_request.content_id,
            "content": publish_request.content,
            "platforms": valid_platforms,
            "hashtags": publish_request.hashtags,
            "image_urls": publish_request.image_urls,
            "scheduled_at": publish_request.scheduled_at,
        })
        
        # 如果沒有排程時間，立即發布
        if not publish_request.scheduled_at or publish_request.scheduled_at <= datetime.utcnow():
            await self._execute_publish(user_id, publish_job, language=language)
        
        # 重新取得更新後的任務
        publish_job = await self.publish_repo.get_publish_job(publish_job["id"])
        
        return publish_job, None
    
    async def _execute_publish(
        self,
        user_id: str,
        publish_job: Dict[str, Any],
        language: str = "zh-TW",
    ):
        """執行發布任務"""
        publish_id = publish_job["id"]
        platforms = publish_job.get("platforms", [])
        content = publish_job.get("content", "")
        hashtags = publish_job.get("hashtags", [])
        image_urls = publish_job.get("image_urls", [])
        
        # 更新狀態為發布中
        await self.publish_repo.update_by_id(publish_id, {"$set": {
            "status": PublishStatus.PUBLISHING.value,
            "updated_at": datetime.utcnow()
        }})
        
        for platform_value in platforms:
            platform = SocialPlatform(platform_value)
            
            try:
                # 取得連接
                connection = await self.connection_repo.get_user_connection(user_id, platform)
                if not connection:
                    await self.publish_repo.mark_platform_failed(
                        publish_id, platform, "平台未連接"
                    )
                    continue
                
                access_token = connection.get("access_token")
                if not access_token:
                    await self.publish_repo.mark_platform_failed(
                        publish_id, platform, "Access Token 無效"
                    )
                    continue
                
                # 優化內容
                optimized = optimize_content_for_platform(content, hashtags, platform)
                publish_content = optimized["full_content"]
                
                # 根據平台發布
                if platform == SocialPlatform.INSTAGRAM:
                    result = await self._publish_to_instagram(
                        connection, publish_content, image_urls
                    )
                elif platform == SocialPlatform.FACEBOOK:
                    result = await self._publish_to_facebook(
                        connection, publish_content, image_urls, language=language
                    )
                elif platform == SocialPlatform.THREADS:
                    result = await self._publish_to_threads(
                        connection, publish_content
                    )
                elif platform == SocialPlatform.TIKTOK:
                    result = await self._publish_to_tiktok(
                        connection, publish_content, image_urls
                    )
                else:
                    result = {"success": False, "error": "不支援的平台"}
                
                if result.get("success"):
                    await self.publish_repo.mark_platform_success(
                        publish_id, platform,
                        result.get("post_id", ""),
                        result.get("post_url")
                    )
                    
                    # 更新連接使用時間
                    await self.connection_repo.update_last_used(user_id, platform)
                else:
                    await self.publish_repo.mark_platform_failed(
                        publish_id, platform, result.get("error", "發布失敗")
                    )
                    
            except Exception as e:
                logger.error(f"發布到 {platform.value} 失敗: {e}")
                await self.publish_repo.mark_platform_failed(
                    publish_id, platform, str(e)
                )
    
    async def _publish_to_instagram(
        self,
        connection: Dict[str, Any],
        content: str,
        image_urls: List[str]
    ) -> Dict[str, Any]:
        """發布到 Instagram"""
        if not image_urls:
            return {"success": False, "error": "Instagram 發布需要至少一張圖片"}
        
        access_token = connection.get("access_token")
        ig_user_id = connection.get("platform_user_id")
        
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: 建立媒體容器
                container_response = await client.post(
                    f"https://graph.facebook.com/v18.0/{ig_user_id}/media",
                    params={
                        "access_token": access_token,
                        "image_url": image_urls[0],
                        "caption": content,
                    }
                )
                
                if container_response.status_code != 200:
                    return {"success": False, "error": container_response.text}
                
                container_id = container_response.json().get("id")
                
                # Step 2: 發布媒體
                publish_response = await client.post(
                    f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish",
                    params={
                        "access_token": access_token,
                        "creation_id": container_id,
                    }
                )
                
                if publish_response.status_code != 200:
                    return {"success": False, "error": publish_response.text}
                
                post_id = publish_response.json().get("id")
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "post_url": f"https://www.instagram.com/p/{post_id}/"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _publish_to_facebook(
        self,
        connection: Dict[str, Any],
        content: str,
        image_urls: List[str],
        language: str = "zh-TW",
    ) -> Dict[str, Any]:
        """發布到 Facebook 粉絲專頁（Page feed）"""
        access_token = connection.get("access_token")
        page_id = connection.get("page_id")
        page_token = connection.get("page_access_token")

        if not page_id or not page_token:
            page = await self._get_first_facebook_page(access_token)
            if page:
                page_id = page.get("id")
                page_token = page.get("access_token")
            else:
                return {
                    "success": False,
                    "error": get_error_message("distribution.facebook_no_page", language),
                }

        try:
            async with httpx.AsyncClient() as client:
                post_params = {
                    "access_token": page_token,
                    "message": content,
                }
                if image_urls:
                    post_params["link"] = image_urls[0]

                post_response = await client.post(
                    f"https://graph.facebook.com/v18.0/{page_id}/feed",
                    params=post_params,
                )

                if post_response.status_code != 200:
                    err_text = post_response.text
                    if "pages_manage_posts" in err_text or "(#200)" in err_text or "permission" in err_text.lower():
                        return {
                            "success": False,
                            "error": get_error_message(
                                "distribution.facebook_publish_permission", language
                            ),
                        }
                    return {"success": False, "error": err_text}

                post_id = post_response.json().get("id")

                return {
                    "success": True,
                    "post_id": post_id,
                    "post_url": f"https://www.facebook.com/{post_id}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _publish_to_threads(
        self,
        connection: Dict[str, Any],
        content: str
    ) -> Dict[str, Any]:
        """發布到 Threads"""
        access_token = connection.get("access_token")
        threads_user_id = connection.get("platform_user_id")
        
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: 建立媒體容器
                container_response = await client.post(
                    f"https://graph.threads.net/v1.0/{threads_user_id}/threads",
                    params={
                        "access_token": access_token,
                        "media_type": "TEXT",
                        "text": content,
                    }
                )
                
                if container_response.status_code != 200:
                    return {"success": False, "error": container_response.text}
                
                container_id = container_response.json().get("id")
                
                # Step 2: 發布
                publish_response = await client.post(
                    f"https://graph.threads.net/v1.0/{threads_user_id}/threads_publish",
                    params={
                        "access_token": access_token,
                        "creation_id": container_id,
                    }
                )
                
                if publish_response.status_code != 200:
                    return {"success": False, "error": publish_response.text}
                
                post_id = publish_response.json().get("id")
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "post_url": f"https://www.threads.net/@{connection.get('platform_username')}/post/{post_id}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _publish_to_tiktok(
        self,
        connection: Dict[str, Any],
        content: str,
        image_urls: List[str]
    ) -> Dict[str, Any]:
        """發布到 TikTok（需要影片）"""
        # TikTok 主要是影片平台，文字發布有限制
        return {"success": False, "error": "TikTok 發布需要影片內容"}
    
    # ============================================
    # 發布歷史和狀態
    # ============================================
    
    async def get_publish_history(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """取得發布歷史"""
        skip = (page - 1) * limit
        items = await self.publish_repo.get_user_publish_history(user_id, skip, limit)
        total = await self.publish_repo.count_user_publishes(user_id)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    async def get_publish_status(
        self,
        user_id: str,
        publish_id: str
    ) -> Optional[Dict[str, Any]]:
        """取得發布狀態"""
        job = await self.publish_repo.get_publish_job(publish_id)
        if job and job.get("user_id") == user_id:
            return job
        return None


# 建立全域實例
distribution_service = DistributionService()

