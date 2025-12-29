"""
AI 服務抽象層
定義 AI 服務的通用介面
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.schemas.content import GenerateContentRequest


class AIServiceBase(ABC):
    """AI 服務基礎類別"""
    
    @abstractmethod
    async def generate_article(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        length: int = 500
    ) -> str:
        """
        生成短文
        
        Args:
            topic_title: 主題標題
            topic_category: 主題分類
            keywords: 關鍵字列表
            length: 目標長度（字）
            
        Returns:
            生成的短文內容
        """
        pass
    
    @abstractmethod
    async def generate_script(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        duration: int = 30
    ) -> str:
        """
        生成腳本
        
        Args:
            topic_title: 主題標題
            topic_category: 主題分類
            keywords: 關鍵字列表
            duration: 目標時長（秒）
            
        Returns:
            生成的腳本內容
        """
        pass
    
    @abstractmethod
    async def generate_both(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        article_length: int = 500,
        script_duration: int = 30
    ) -> Dict[str, str]:
        """
        同時生成短文和腳本
        
        Args:
            topic_title: 主題標題
            topic_category: 主題分類
            keywords: 關鍵字列表
            article_length: 短文目標長度
            script_duration: 腳本目標時長
            
        Returns:
            包含 article 和 script 的字典
        """
        pass
