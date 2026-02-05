#!/usr/bin/env python3
"""
批量修復硬編碼文字
==================
自動替換組件中的硬編碼為 t() 調用
"""

import os
import re
import sys
import io
import json
from pathlib import Path
from typing import Dict, List, Tuple

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FRONTEND_PATH = Path(__file__).parent.parent / "frontend" / "src"

# 規範的翻譯 key 和內容
TRANSLATIONS = {
    # ==================== COMMON ====================
    'common.loading': {
        'zh-TW': '載入中...',
        'en': 'Loading...',
        'ja': '読み込み中...'
    },
    'common.searching': {
        'zh-TW': '搜尋中...',
        'en': 'Searching...',
        'ja': '検索中...'
    },
    'common.save': {
        'zh-TW': '儲存',
        'en': 'Save',
        'ja': '保存'
    },
    'common.saving': {
        'zh-TW': '儲存中...',
        'en': 'Saving...',
        'ja': '保存中...'
    },
    'common.cancel': {
        'zh-TW': '取消',
        'en': 'Cancel',
        'ja': 'キャンセル'
    },
    'common.confirm': {
        'zh-TW': '確認',
        'en': 'Confirm',
        'ja': '確認'
    },
    'common.delete': {
        'zh-TW': '刪除',
        'en': 'Delete',
        'ja': '削除'
    },
    'common.deleting': {
        'zh-TW': '刪除中...',
        'en': 'Deleting...',
        'ja': '削除中...'
    },
    'common.edit': {
        'zh-TW': '編輯',
        'en': 'Edit',
        'ja': '編集'
    },
    'common.add': {
        'zh-TW': '添加',
        'en': 'Add',
        'ja': '追加'
    },
    'common.remove': {
        'zh-TW': '移除',
        'en': 'Remove',
        'ja': '削除'
    },
    'common.retry': {
        'zh-TW': '重試',
        'en': 'Retry',
        'ja': '再試行'
    },
    'common.back': {
        'zh-TW': '返回',
        'en': 'Back',
        'ja': '戻る'
    },
    'common.next': {
        'zh-TW': '下一步',
        'en': 'Next',
        'ja': '次へ'
    },
    'common.previous': {
        'zh-TW': '上一步',
        'en': 'Previous',
        'ja': '前へ'
    },
    'common.submit': {
        'zh-TW': '提交',
        'en': 'Submit',
        'ja': '送信'
    },
    'common.close': {
        'zh-TW': '關閉',
        'en': 'Close',
        'ja': '閉じる'
    },
    'common.success': {
        'zh-TW': '成功',
        'en': 'Success',
        'ja': '成功'
    },
    'common.failed': {
        'zh-TW': '失敗',
        'en': 'Failed',
        'ja': '失敗'
    },
    'common.error': {
        'zh-TW': '錯誤',
        'en': 'Error',
        'ja': 'エラー'
    },
    'common.noData': {
        'zh-TW': '沒有找到資料',
        'en': 'No data found',
        'ja': 'データが見つかりません'
    },
    'common.copy': {
        'zh-TW': '複製',
        'en': 'Copy',
        'ja': 'コピー'
    },
    'common.copied': {
        'zh-TW': '已複製',
        'en': 'Copied',
        'ja': 'コピーしました'
    },
    'common.preview': {
        'zh-TW': '預覽',
        'en': 'Preview',
        'ja': 'プレビュー'
    },
    'common.view': {
        'zh-TW': '查看',
        'en': 'View',
        'ja': '表示'
    },
    'common.all': {
        'zh-TW': '全部',
        'en': 'All',
        'ja': 'すべて'
    },
    'common.more': {
        'zh-TW': '更多',
        'en': 'More',
        'ja': 'もっと見る'
    },
    
    # ==================== CHANNELS ====================
    'channels.title': {
        'zh-TW': '我的頻道',
        'en': 'My Channels',
        'ja': 'マイチャンネル'
    },
    'channels.create': {
        'zh-TW': '建立頻道',
        'en': 'Create Channel',
        'ja': 'チャンネル作成'
    },
    'channels.createNew': {
        'zh-TW': '建立新頻道',
        'en': 'Create New Channel',
        'ja': '新しいチャンネルを作成'
    },
    'channels.name': {
        'zh-TW': '頻道名稱',
        'en': 'Channel Name',
        'ja': 'チャンネル名'
    },
    'channels.description': {
        'zh-TW': '頻道描述',
        'en': 'Channel Description',
        'ja': 'チャンネル説明'
    },
    'channels.loadFailed': {
        'zh-TW': '載入頻道失敗',
        'en': 'Failed to load channels',
        'ja': 'チャンネルの読み込みに失敗しました'
    },
    'channels.deleted': {
        'zh-TW': '頻道已刪除',
        'en': 'Channel deleted',
        'ja': 'チャンネルが削除されました'
    },
    'channels.deleteFailed': {
        'zh-TW': '刪除失敗',
        'en': 'Delete failed',
        'ja': '削除に失敗しました'
    },
    'channels.createSuccess': {
        'zh-TW': '頻道建立成功！',
        'en': 'Channel created successfully!',
        'ja': 'チャンネルが作成されました！'
    },
    'channels.createFailed': {
        'zh-TW': '建立失敗',
        'en': 'Create failed',
        'ja': '作成に失敗しました'
    },
    'channels.collectTriggered': {
        'zh-TW': '收集任務已觸發',
        'en': 'Collection task triggered',
        'ja': '収集タスクが開始されました'
    },
    'channels.triggerFailed': {
        'zh-TW': '觸發失敗',
        'en': 'Trigger failed',
        'ja': 'トリガーに失敗しました'
    },
    'channels.selectCategory': {
        'zh-TW': '選擇類別',
        'en': 'Select Category',
        'ja': 'カテゴリを選択'
    },
    'channels.selectRegion': {
        'zh-TW': '選擇地區',
        'en': 'Select Region',
        'ja': '地域を選択'
    },
    'channels.customKeywords': {
        'zh-TW': '自定義關鍵字',
        'en': 'Custom Keywords',
        'ja': 'カスタムキーワード'
    },
    'channels.enterKeywords': {
        'zh-TW': '輸入關鍵字後按 Enter',
        'en': 'Enter keywords and press Enter',
        'ja': 'キーワードを入力してEnterを押してください'
    },
    'channels.maxKeywords': {
        'zh-TW': '最多 5 個關鍵字',
        'en': 'Maximum 5 keywords',
        'ja': '最大5つのキーワード'
    },
    'channels.noChannels': {
        'zh-TW': '還沒有頻道',
        'en': 'No channels yet',
        'ja': 'まだチャンネルがありません'
    },
    'channels.createFirst': {
        'zh-TW': '建立您的第一個頻道，開始接收個人化的內容推薦',
        'en': 'Create your first channel to start receiving personalized content',
        'ja': '最初のチャンネルを作成して、パーソナライズされたコンテンツを受け取りましょう'
    },
    'channels.topics': {
        'zh-TW': '個主題',
        'en': 'topics',
        'ja': 'トピック'
    },
    'channels.collectNow': {
        'zh-TW': '立即收集',
        'en': 'Collect Now',
        'ja': '今すぐ収集'
    },
    'channels.deleteChannel': {
        'zh-TW': '刪除頻道',
        'en': 'Delete Channel',
        'ja': 'チャンネルを削除'
    },
    'channels.editChannel': {
        'zh-TW': '編輯頻道',
        'en': 'Edit Channel',
        'ja': 'チャンネルを編集'
    },
    'channels.enterName': {
        'zh-TW': '請輸入頻道名稱',
        'en': 'Please enter channel name',
        'ja': 'チャンネル名を入力してください'
    },
    'channels.pleaseSelectCategory': {
        'zh-TW': '請選擇類別',
        'en': 'Please select a category',
        'ja': 'カテゴリを選択してください'
    },
    'channels.otherCategoryKeywords': {
        'zh-TW': '選擇「其他」類別時請輸入至少一個關鍵字',
        'en': 'Please enter at least one keyword when selecting "Other" category',
        'ja': '「その他」カテゴリを選択した場合は、少なくとも1つのキーワードを入力してください'
    },
    
    # ==================== DASHBOARD ====================
    'dashboard.title': {
        'zh-TW': '控制面板',
        'en': 'Dashboard',
        'ja': 'ダッシュボード'
    },
    'dashboard.todayTopics': {
        'zh-TW': '今日熱門主題',
        'en': 'Today\'s Hot Topics',
        'ja': '今日の人気トピック'
    },
    'dashboard.latestTopics': {
        'zh-TW': '最新熱門主題',
        'en': 'Latest Hot Topics',
        'ja': '最新の人気トピック'
    },
    'dashboard.generating': {
        'zh-TW': '正在生成今日主題...',
        'en': 'Generating today\'s topics...',
        'ja': '今日のトピックを生成中...'
    },
    'dashboard.generateStarted': {
        'zh-TW': '今日主題生成任務已啟動',
        'en': 'Today\'s topic generation task started',
        'ja': '今日のトピック生成タスクが開始されました'
    },
    'dashboard.generateFailed': {
        'zh-TW': '生成今日主題失敗',
        'en': 'Failed to generate today\'s topics',
        'ja': '今日のトピックの生成に失敗しました'
    },
    'dashboard.generateSuccess': {
        'zh-TW': '今日主題生成完成！',
        'en': 'Today\'s topics generated!',
        'ja': '今日のトピックが生成されました！'
    },
    'dashboard.deleteFailed': {
        'zh-TW': '刪除今日主題失敗',
        'en': 'Failed to delete today\'s topics',
        'ja': '今日のトピックの削除に失敗しました'
    },
    'dashboard.confirmDelete': {
        'zh-TW': '確定要刪除所有今日生成的主題嗎？此操作無法復原。',
        'en': 'Are you sure you want to delete all topics generated today? This action cannot be undone.',
        'ja': '今日生成されたすべてのトピックを削除してもよろしいですか？この操作は元に戻せません。'
    },
    'dashboard.dbNotConnected': {
        'zh-TW': '資料庫未連接，無法生成主題',
        'en': 'Database not connected, cannot generate topics',
        'ja': 'データベースに接続されていないため、トピックを生成できません'
    },
    'dashboard.serverError': {
        'zh-TW': '伺服器內部錯誤，請查看後端日誌',
        'en': 'Internal server error, please check backend logs',
        'ja': 'サーバー内部エラー、バックエンドログを確認してください'
    },
    'dashboard.cannotConnect': {
        'zh-TW': '無法連接到後端服務',
        'en': 'Cannot connect to backend service',
        'ja': 'バックエンドサービスに接続できません'
    },
    
    # ==================== TOPICS ====================
    'topics.title': {
        'zh-TW': '主題列表',
        'en': 'Topics',
        'ja': 'トピック'
    },
    'topics.notFound': {
        'zh-TW': '找不到主題',
        'en': 'Topic not found',
        'ja': 'トピックが見つかりません'
    },
    'topics.content': {
        'zh-TW': '內容',
        'en': 'Content',
        'ja': 'コンテンツ'
    },
    'topics.shortPost': {
        'zh-TW': '短文',
        'en': 'Short Post',
        'ja': 'ショートポスト'
    },
    'topics.script': {
        'zh-TW': '腳本',
        'en': 'Script',
        'ja': 'スクリプト'
    },
    'topics.interaction': {
        'zh-TW': '互動',
        'en': 'Interaction',
        'ja': 'インタラクション'
    },
    'topics.category': {
        'zh-TW': '分類',
        'en': 'Category',
        'ja': 'カテゴリ'
    },
    'topics.status': {
        'zh-TW': '狀態',
        'en': 'Status',
        'ja': 'ステータス'
    },
    'topics.source': {
        'zh-TW': '來源',
        'en': 'Source',
        'ja': 'ソース'
    },
    'topics.generatedAt': {
        'zh-TW': '生成時間',
        'en': 'Generated at',
        'ja': '生成時刻'
    },
    'topics.aiModel': {
        'zh-TW': 'AI 模型',
        'en': 'AI Model',
        'ja': 'AIモデル'
    },
    'topics.stats': {
        'zh-TW': '統計',
        'en': 'Statistics',
        'ja': '統計'
    },
    'topics.imageCount': {
        'zh-TW': '圖片數量',
        'en': 'Image count',
        'ja': '画像数'
    },
    'topics.wordCount': {
        'zh-TW': '字數',
        'en': 'Word count',
        'ja': '文字数'
    },
    'topics.duration': {
        'zh-TW': '預計時長',
        'en': 'Estimated duration',
        'ja': '予想時間'
    },
    
    # ==================== IMAGES ====================
    'images.matching': {
        'zh-TW': '正在智能匹配照片...',
        'en': 'Smart matching photos...',
        'ja': 'スマートマッチング中...'
    },
    'images.matchFailed': {
        'zh-TW': '匹配照片失敗',
        'en': 'Failed to match photos',
        'ja': '写真のマッチングに失敗しました'
    },
    'images.matchSuccess': {
        'zh-TW': '照片與文字匹配度良好',
        'en': 'Photos match well with text',
        'ja': '写真とテキストがよくマッチしています'
    },
    'images.verifyFailed': {
        'zh-TW': '驗證匹配度失敗',
        'en': 'Failed to verify match',
        'ja': 'マッチ度の検証に失敗しました'
    },
    'images.deleted': {
        'zh-TW': '圖片已成功刪除',
        'en': 'Image deleted successfully',
        'ja': '画像が正常に削除されました'
    },
    'images.deleteFailed': {
        'zh-TW': '刪除圖片失敗，請稍後再試',
        'en': 'Failed to delete image, please try again',
        'ja': '画像の削除に失敗しました。後でもう一度お試しください'
    },
    'images.orderUpdated': {
        'zh-TW': '圖片順序已更新',
        'en': 'Image order updated',
        'ja': '画像の順序が更新されました'
    },
    'images.orderFailed': {
        'zh-TW': '更新圖片順序失敗，請稍後再試',
        'en': 'Failed to update image order, please try again',
        'ja': '画像の順序の更新に失敗しました。後でもう一度お試しください'
    },
    'images.confirmDelete': {
        'zh-TW': '確定要刪除這張圖片嗎？',
        'en': 'Are you sure you want to delete this image?',
        'ja': 'この画像を削除してもよろしいですか？'
    },
    'images.verifying': {
        'zh-TW': '驗證中...',
        'en': 'Verifying...',
        'ja': '検証中...'
    },
    'images.verify': {
        'zh-TW': '驗證匹配度',
        'en': 'Verify match',
        'ja': 'マッチ度を検証'
    },
    'images.smartMatch': {
        'zh-TW': '智能匹配（補齊至8張）',
        'en': 'Smart match (fill to 8)',
        'ja': 'スマートマッチ（8枚まで補充）'
    },
    'images.saveOrder': {
        'zh-TW': '儲存順序',
        'en': 'Save order',
        'ja': '順序を保存'
    },
    'images.search': {
        'zh-TW': '搜尋圖片',
        'en': 'Search images',
        'ja': '画像を検索'
    },
    'images.searchPlaceholder': {
        'zh-TW': '輸入關鍵字搜尋圖片',
        'en': 'Enter keywords to search images',
        'ja': 'キーワードを入力して画像を検索'
    },
    'images.noResults': {
        'zh-TW': '沒有找到相關圖片',
        'en': 'No images found',
        'ja': '関連する画像が見つかりませんでした'
    },
    'images.adding': {
        'zh-TW': '新增中...',
        'en': 'Adding...',
        'ja': '追加中...'
    },
    'images.addSuccess': {
        'zh-TW': '圖片已新增',
        'en': 'Image added',
        'ja': '画像が追加されました'
    },
    'images.addFailed': {
        'zh-TW': '新增圖片失敗',
        'en': 'Failed to add image',
        'ja': '画像の追加に失敗しました'
    },
    
    # ==================== STYLE ====================
    'style.title': {
        'zh-TW': '風格檔案',
        'en': 'Style Profile',
        'ja': 'スタイルプロファイル'
    },
    'style.coldStart': {
        'zh-TW': '冷啟動',
        'en': 'Cold Start',
        'ja': 'コールドスタート'
    },
    'style.learning': {
        'zh-TW': '學習中',
        'en': 'Learning',
        'ja': '学習中'
    },
    'style.mature': {
        'zh-TW': '成熟',
        'en': 'Mature',
        'ja': '成熟'
    },
    
    # ==================== SOCIAL ====================
    'social.title': {
        'zh-TW': '平台連接',
        'en': 'Social Connect',
        'ja': 'ソーシャル連携'
    },
    'social.connected': {
        'zh-TW': '已連接',
        'en': 'Connected',
        'ja': '連携済み'
    },
    'social.notConnected': {
        'zh-TW': '未連接',
        'en': 'Not Connected',
        'ja': '未連携'
    },
    'social.connect': {
        'zh-TW': '連接',
        'en': 'Connect',
        'ja': '連携'
    },
    'social.disconnect': {
        'zh-TW': '斷開連接',
        'en': 'Disconnect',
        'ja': '連携解除'
    },
    'social.tips': {
        'zh-TW': '提示',
        'en': 'Tips',
        'ja': 'ヒント'
    },
    'social.tip1': {
        'zh-TW': '連接後可以一鍵發布內容到多個平台',
        'en': 'After connecting, you can publish content to multiple platforms with one click',
        'ja': '連携後、ワンクリックで複数のプラットフォームにコンテンツを公開できます'
    },
    'social.tip2': {
        'zh-TW': 'Meta 平台需要 Business 或 Creator 帳號',
        'en': 'Meta platforms require Business or Creator account',
        'ja': 'MetaプラットフォームにはBusinessまたはCreatorアカウントが必要です'
    },
    'social.tip3': {
        'zh-TW': '您可以隨時斷開連接',
        'en': 'You can disconnect at any time',
        'ja': 'いつでも連携を解除できます'
    },
    'social.tip4': {
        'zh-TW': '我們不會在未經您同意下發布任何內容',
        'en': 'We will not post anything without your consent',
        'ja': 'お客様の同意なしにコンテンツを投稿することはありません'
    },
    
    # ==================== SETTINGS ====================
    'settings.title': {
        'zh-TW': '設定',
        'en': 'Settings',
        'ja': '設定'
    },
    'settings.subtitle': {
        'zh-TW': '管理您的帳號和偏好設定',
        'en': 'Manage your account and preferences',
        'ja': 'アカウントと設定を管理'
    },
    'settings.darkMode': {
        'zh-TW': '深色模式',
        'en': 'Dark Mode',
        'ja': 'ダークモード'
    },
    'settings.lightMode': {
        'zh-TW': '淺色模式',
        'en': 'Light Mode',
        'ja': 'ライトモード'
    },
    'settings.appearance': {
        'zh-TW': '外觀',
        'en': 'Appearance',
        'ja': '外観'
    },
    'settings.emailNotifications': {
        'zh-TW': 'Email 通知',
        'en': 'Email Notifications',
        'ja': 'メール通知'
    },
    'settings.newFeatures': {
        'zh-TW': '新功能提醒',
        'en': 'New Feature Alerts',
        'ja': '新機能のお知らせ'
    },
    'settings.systemUpdates': {
        'zh-TW': '系統更新通知',
        'en': 'System Update Notifications',
        'ja': 'システム更新通知'
    },
    'settings.accountInfo': {
        'zh-TW': '帳號資訊',
        'en': 'Account Info',
        'ja': 'アカウント情報'
    },
    'settings.accountType': {
        'zh-TW': '帳號類型',
        'en': 'Account Type',
        'ja': 'アカウントタイプ'
    },
    'settings.registrationTime': {
        'zh-TW': '註冊時間',
        'en': 'Registration Time',
        'ja': '登録日時'
    },
    'settings.lastLogin': {
        'zh-TW': '上次登入',
        'en': 'Last Login',
        'ja': '最終ログイン'
    },
    
    # ==================== AUTH ====================
    'auth.sendFailed': {
        'zh-TW': '發送失敗，請稍後再試',
        'en': 'Failed to send, please try again later',
        'ja': '送信に失敗しました。後でもう一度お試しください'
    },
    'auth.invalidEmail': {
        'zh-TW': '請輸入有效的 Email 地址',
        'en': 'Please enter a valid email address',
        'ja': '有効なメールアドレスを入力してください'
    },
    'auth.verifying': {
        'zh-TW': '請稍候，正在驗證您的帳號',
        'en': 'Please wait, verifying your account',
        'ja': 'お待ちください、アカウントを確認中です'
    },
    
    # ==================== PUBLISH ====================
    'publish.title': {
        'zh-TW': '一鍵發布',
        'en': 'One-Click Publish',
        'ja': 'ワンクリック公開'
    },
    
    # ==================== INSPIRATION ====================
    'inspiration.title': {
        'zh-TW': '靈感策劃',
        'en': 'Inspiration',
        'ja': 'インスピレーション'
    },
    
    # ==================== PREFERENCES ====================
    'preferences.title': {
        'zh-TW': '偏好設定',
        'en': 'Preferences',
        'ja': '環境設定'
    },
    'preferences.developing': {
        'zh-TW': '偏好設定功能開發中...',
        'en': 'Preferences feature in development...',
        'ja': '環境設定機能は開発中です...'
    },
    
    # ==================== SCHEDULE ====================
    'schedule.title': {
        'zh-TW': '排程管理',
        'en': 'Schedule Management',
        'ja': 'スケジュール管理'
    },
    'schedule.developing': {
        'zh-TW': '排程管理功能開發中...',
        'en': 'Schedule management feature in development...',
        'ja': 'スケジュール管理機能は開発中です...'
    },
    
    # ==================== ERROR ====================
    'error.unknown': {
        'zh-TW': '未知錯誤',
        'en': 'Unknown error',
        'ja': '不明なエラー'
    },
    'error.notFound': {
        'zh-TW': '找不到請求的資源',
        'en': 'Resource not found',
        'ja': 'リソースが見つかりません'
    },
    'error.unauthorized': {
        'zh-TW': '未授權，請重新登入',
        'en': 'Unauthorized, please sign in again',
        'ja': '認証されていません。再度ログインしてください'
    },
    'error.forbidden': {
        'zh-TW': '無權限訪問此資源',
        'en': 'No permission to access this resource',
        'ja': 'このリソースへのアクセス権限がありません'
    },
    'error.serverError': {
        'zh-TW': '伺服器錯誤，請稍後再試',
        'en': 'Server error, please try again later',
        'ja': 'サーバーエラー、後でもう一度お試しください'
    },
    'error.networkError': {
        'zh-TW': '發生錯誤，請稍後再試',
        'en': 'An error occurred, please try again later',
        'ja': 'エラーが発生しました。後でもう一度お試しください'
    },
    'error.checkCors': {
        'zh-TW': '檢查 CORS 設定是否包含前端網域',
        'en': 'Check if CORS settings include frontend domain',
        'ja': 'CORS設定にフロントエンドドメインが含まれているか確認してください'
    },
    'error.checkNetwork': {
        'zh-TW': '檢查網路連接',
        'en': 'Check network connection',
        'ja': 'ネットワーク接続を確認してください'
    },
}

def generate_i18n_code():
    """生成 i18n 代碼"""
    zh_tw = []
    en = []
    ja = []
    
    # 按模組分組
    modules = {}
    for key, trans in TRANSLATIONS.items():
        module = key.split('.')[0]
        if module not in modules:
            modules[module] = []
        modules[module].append((key, trans))
    
    for module in sorted(modules.keys()):
        zh_tw.append(f"\n  // {module.upper()}")
        en.append(f"\n  // {module.upper()}")
        ja.append(f"\n  // {module.upper()}")
        
        for key, trans in modules[module]:
            zh_tw.append(f"  '{key}': '{trans['zh-TW']}',")
            en.append(f"  '{key}': '{trans['en']}',")
            ja.append(f"  '{key}': '{trans['ja']}',")
    
    return {
        'zh-TW': '\n'.join(zh_tw),
        'en': '\n'.join(en),
        'ja': '\n'.join(ja)
    }

def main():
    print("=" * 60)
    print("BATCH FIX - GENERATING I18N TRANSLATIONS")
    print("=" * 60)
    
    code = generate_i18n_code()
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    for lang, content in code.items():
        filename = f"i18n_additions_{lang.replace('-', '_')}.txt"
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[SAVE] {filepath}")
    
    print(f"\n[INFO] Generated {len(TRANSLATIONS)} translation keys")
    print("\n[NEXT] Copy these translations to frontend/src/i18n/index.ts")

if __name__ == "__main__":
    main()

