/**
 * i18n 多語言系統
 * Phase 2: 會員系統
 * 支援 zh-TW, en, ja
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 支援的語言
export type Language = 'zh-TW' | 'en' | 'ja';

// 翻譯類型
export type TranslationKey = keyof typeof zhTW;

// 繁體中文翻譯
const zhTW = {
  // 通用
  'common.loading': '載入中...',
  'common.error': '發生錯誤',
  'common.success': '成功',
  'common.cancel': '取消',
  'common.confirm': '確認',
  'common.save': '儲存',
  'common.delete': '刪除',
  'common.edit': '編輯',
  'common.back': '返回',
  'common.next': '下一步',
  'common.submit': '提交',
  'common.close': '關閉',
  'common.search': '搜尋',
  'common.retry': '重試',
  'common.or': '或',
  'common.show': '顯示',
  'common.hide': '隱藏',
  'common.language': '繁中',
  
  // 導航
  'nav.home': '首頁',
  'nav.dashboard': '控制面板',
  'nav.topics': '主題',
  'nav.channels': '我的頻道',
  'nav.inspiration': '靈感策劃',
  'nav.styleProfile': '風格檔案',
  'nav.publish': '一鍵發布',
  'nav.socialConnect': '平台連接',
  'nav.schedule': '排程',
  'nav.settings': '設定',
  'nav.login': '登入',
  'nav.register': '註冊',
  'nav.logout': '登出',
  'nav.profile': '個人資料',
  
  // 品牌
  'brand.name': 'Influencers AI',
  'brand.tagline': '網紅 AI 助手',
  
  // 問候語
  'greeting.hello': '你好',
  'greeting.guest': '訪客',
  'greeting.user': '{name}',
  
  // 認證 - 登入
  'auth.login.title': '登入',
  'auth.login.subtitle': '歡迎回來！請登入您的帳號',
  'auth.login.email': 'Email 地址',
  'auth.login.password': '密碼',
  'auth.login.rememberMe': '記住我',
  'auth.login.forgotPassword': '忘記密碼？',
  'auth.login.submit': '登入',
  'auth.login.noAccount': '還沒有帳號？',
  'auth.login.registerLink': '立即註冊',
  'auth.login.googleLogin': '使用 Google 登入',
  'auth.login.welcome': '歡迎回來',
  'auth.login.guestMode': '訪客瀏覽',
  'auth.login.success': '登入成功！',
  'auth.login.error': '登入失敗',
  'auth.login.invalidCredentials': 'Email 或密碼錯誤',
  
  // 認證 - 註冊
  'auth.register.title': '建立帳號',
  'auth.register.subtitle': '加入我們，開始您的 AI 創作之旅',
  'auth.register.name': '名稱',
  'auth.register.namePlaceholder': '您的名稱',
  'auth.register.email': 'Email 地址',
  'auth.register.emailPlaceholder': 'example@email.com',
  'auth.register.password': '密碼',
  'auth.register.passwordPlaceholder': '至少 8 位，包含 1 個大寫字母',
  'auth.register.confirmPassword': '確認密碼',
  'auth.register.confirmPasswordPlaceholder': '再次輸入密碼',
  'auth.register.language': '語言偏好',
  'auth.register.terms': '我同意',
  'auth.register.termsLink': '服務條款',
  'auth.register.and': '和',
  'auth.register.privacyLink': '隱私政策',
  'auth.register.submit': '建立帳號',
  'auth.register.hasAccount': '已經有帳號？',
  'auth.register.loginLink': '立即登入',
  'auth.register.googleRegister': '使用 Google 註冊',
  'auth.register.success': '註冊成功！請查收驗證郵件',
  'auth.register.error': '註冊失敗',
  
  // 認證 - Email 驗證
  'auth.verify.title': '驗證 Email',
  'auth.verify.subtitle': '我們已發送驗證郵件到您的信箱',
  'auth.verify.checkEmail': '請查收您的 Email 並點擊驗證連結',
  'auth.verify.resend': '重新發送驗證郵件',
  'auth.verify.resending': '發送中...',
  'auth.verify.resent': '驗證郵件已重新發送',
  'auth.verify.success': 'Email 驗證成功！',
  'auth.verify.error': '驗證失敗，連結可能已過期',
  'auth.verify.expired': '驗證連結已過期',
  
  // 認證 - 忘記密碼
  'auth.forgot.title': '忘記密碼',
  'auth.forgot.subtitle': '輸入您的 Email，我們將發送重設連結',
  'auth.forgot.email': 'Email 地址',
  'auth.forgot.submit': '發送重設連結',
  'auth.forgot.success': '重設郵件已發送',
  'auth.forgot.backToLogin': '返回登入',
  
  // 認證 - 重設密碼
  'auth.reset.title': '重設密碼',
  'auth.reset.subtitle': '請輸入您的新密碼',
  'auth.reset.newPassword': '新密碼',
  'auth.reset.confirmPassword': '確認新密碼',
  'auth.reset.submit': '重設密碼',
  'auth.reset.success': '密碼重設成功！',
  'auth.reset.error': '重設失敗，連結可能已過期',
  
  // 認證 - 密碼驗證
  'auth.password.minLength': '至少 8 個字元',
  'auth.password.uppercase': '至少 1 個大寫字母',
  'auth.password.match': '密碼不一致',
  
  // 認證 - 登入提示
  'auth.loginRequired': '需要登入',
  'auth.loginRequiredMessage': '此功能需要登入才能使用。請先登入或註冊帳號。',
  
  // 法律頁面 - 服務條款
  'legal.terms.title': '服務條款',
  'legal.terms.subtitle': 'TERMS OF SERVICE',
  'legal.terms.lastUpdate': '最後更新：2026 年 2 月',
  'legal.terms.section1.title': '1. 服務說明',
  'legal.terms.section1.content': 'Influencers AI（以下簡稱「本服務」）是一個 AI 驅動的內容創作平台，旨在幫助用戶生成高品質的社群媒體內容。',
  'legal.terms.section2.title': '2. 帳號註冊',
  'legal.terms.section2.content': '您必須提供真實、準確的個人資訊來註冊帳號。您有責任保護您的帳號安全，並對帳號下的所有活動負責。',
  'legal.terms.section3.title': '3. 內容所有權',
  'legal.terms.section3.content': '使用本服務生成的內容，其所有權歸您所有。但您同意授予本服務使用這些內容來改進 AI 模型的權利。',
  'legal.terms.section4.title': '4. 使用限制',
  'legal.terms.section4.content': '您同意不會使用本服務來創建違法、有害、威脅性、辱罵性、騷擾性、誹謗性或其他令人反感的內容。',
  'legal.terms.section5.title': '5. 服務變更',
  'legal.terms.section5.content': '本服務保留隨時修改或終止服務的權利，恕不另行通知。',
  'legal.terms.section6.title': '6. 免責聲明',
  'legal.terms.section6.content': '本服務按「現狀」提供，不作任何明示或暗示的保證。對於因使用本服務而產生的任何損失，本服務不承擔責任。',
  
  // 法律頁面 - 隱私政策
  'legal.privacy.title': '隱私政策',
  'legal.privacy.subtitle': 'PRIVACY POLICY',
  'legal.privacy.lastUpdate': '最後更新：2026 年 2 月',
  'legal.privacy.section1.title': '1. 資料收集',
  'legal.privacy.section1.content': '我們收集您提供的資訊，包括但不限於：電子郵件地址、姓名、語言偏好。我們也會自動收集使用數據，如瀏覽記錄和設備資訊。',
  'legal.privacy.section2.title': '2. 資料使用',
  'legal.privacy.section2.content': '我們使用收集的資料來：',
  'legal.privacy.section2.list1': '提供和維護服務',
  'legal.privacy.section2.list2': '個性化您的體驗',
  'legal.privacy.section2.list3': '改進我們的 AI 模型',
  'legal.privacy.section2.list4': '與您溝通服務相關事宜',
  'legal.privacy.section3.title': '3. 資料保護',
  'legal.privacy.section3.content': '我們採用業界標準的安全措施來保護您的個人資料，包括加密傳輸和安全存儲。',
  'legal.privacy.section4.title': '4. 資料分享',
  'legal.privacy.section4.content': '我們不會出售您的個人資料。我們可能在以下情況下分享您的資料：',
  'legal.privacy.section4.list1': '經您同意',
  'legal.privacy.section4.list2': '法律要求',
  'legal.privacy.section4.list3': '與服務提供商合作（受保密協議約束）',
  'legal.privacy.section5.title': '5. Cookie 使用',
  'legal.privacy.section5.content': '我們使用 Cookie 和類似技術來記住您的偏好設定和改善用戶體驗。',
  'legal.privacy.section6.title': '6. 您的權利',
  'legal.privacy.section6.content': '您有權：',
  'legal.privacy.section6.list1': '訪問您的個人資料',
  'legal.privacy.section6.list2': '更正不準確的資料',
  'legal.privacy.section6.list3': '請求刪除您的資料',
  'legal.privacy.section6.list4': '撤回同意',
  'legal.privacy.section7.title': '7. 聯繫我們',
  'legal.privacy.section7.content': '如有任何隱私相關問題，請聯繫：privacy@influencers.ai',
  
  // 用戶設定
  'settings.title': '設定',
  'settings.profile': '個人資料',
  'settings.profileDesc': '管理您的個人資訊',
  'settings.account': '帳號設定',
  'settings.accountDesc': '管理您的帳號安全',
  'settings.preferences': '偏好設定',
  'settings.preferencesDesc': '自訂您的使用體驗',
  'settings.notifications': '通知設定',
  'settings.notificationsDesc': '管理通知偏好',
  
  // 用戶資料
  'profile.name': '名稱',
  'profile.email': 'Email',
  'profile.avatar': '頭像',
  'profile.changeAvatar': '更換頭像',
  'profile.language': '語言',
  'profile.timezone': '時區',
  'profile.save': '儲存變更',
  'profile.saved': '已儲存',
  
  // 帳號設定
  'account.changePassword': '更改密碼',
  'account.currentPassword': '目前密碼',
  'account.newPassword': '新密碼',
  'account.confirmPassword': '確認新密碼',
  'account.linkedAccounts': '已連結帳號',
  'account.linkGoogle': '連結 Google 帳號',
  'account.unlinkGoogle': '解除連結',
  'account.deleteAccount': '刪除帳號',
  'account.deleteWarning': '此操作無法復原，所有資料將被永久刪除',
  
  // 功能相關
  'feature.unavailable': '此功能目前不可用',
  'feature.comingSoon': '即將推出',
  'feature.beta': 'Beta 測試中',
  
  // 錯誤訊息
  'error.network': '網路連線失敗',
  'error.server': '伺服器錯誤',
  'error.unauthorized': '請先登入',
  'error.forbidden': '沒有權限',
  'error.notFound': '找不到資源',
  'error.validation': '請檢查輸入資料',
  'error.maxUsers': '目前系統已達用戶上限',
  
  // 主題相關
  'topics.title': '主題',
  'topics.overview': '主題總覽',
  'topics.create': '建立主題',
  'topics.edit': '編輯主題',
  'topics.delete': '刪除主題',
  'topics.noTopics': '還沒有主題',
  'topics.noSearchResults': '沒有找到符合搜尋條件的主題',
  'topics.tryAdjustFilters': '嘗試調整篩選條件或稍後再試',
  'topics.loadMore': '載入更多',
  'topics.today': '今天',
  'topics.yesterday': '昨天',
  'topics.thisWeek': '本週',
  'topics.older': '更早',
  'topics.infiniteScroll': '無限滾動',
  'topics.searchPlaceholder': '搜尋主題...',
  'topics.pagination': '分頁',
  'topics.searchSource': '搜尋來源',
  'topics.total': '共 {count} 個主題',
  'topics.loaded': '已載入 {count} 個',
  'topics.source': '來源',
  'topics.noContent': '暫無內容撮要',
  'topics.contentProgress': '內容完成度',
  'topics.imageProgress': '圖片完成度',
  'topics.deleteConfirmMessage': '您確定要刪除此主題嗎？此操作無法復原。',
  
  // 內容生成
  'content.generate': '生成內容',
  'content.generating': '生成中...',
  'content.regenerate': '重新生成',
  'content.copy': '複製',
  'content.copied': '已複製',
  'content.platform': '平台',
  'content.style': '風格',
  
  // 圖片
  'images.search': '搜尋圖片',
  'images.upload': '上傳圖片',
  'images.select': '選擇圖片',
  'images.noResults': '找不到相關圖片',
  'images.searchTitle': '搜尋圖片',
  'images.suggestedKeywords': '建議關鍵字（從內容中提取）',
  'images.sourceLabel': '來源',
  'images.allSources': '所有來源',
  'images.diagnosticMode': '診斷模式',
  'images.tryDifferentKeywords': '嘗試使用不同的關鍵字',
  'images.validateMatch': '驗證匹配度',
  'images.reorder': '重新排序',
  'images.loadError': '圖片無法載入',
  'images.photographer': '攝影師',
  'images.license': '授權',
  'images.order': '順序',
  'images.imageUrl': '圖片 URL',
  
  // 篩選器
  'filters.title': '篩選條件',
  'filters.search': '搜尋',
  'filters.searchPlaceholder': '搜尋主題標題或來源...',
  'filters.category': '分類',
  'filters.status': '狀態',
  'filters.date': '日期',
  'filters.all': '全部',
  'filters.fashion': '時尚',
  'filters.food': '美食',
  'filters.trend': '趨勢',
  'filters.pending': '待審核',
  'filters.confirmed': '已確認',
  'filters.deleted': '已刪除',
  'filters.reset': '重置',
  
  // 通用 - 擴展
  'common.searching': '搜尋中...',
  'common.saving': '儲存中...',
  'common.deleting': '刪除中...',
  'common.add': '添加',
  'common.remove': '移除',
  'common.previous': '上一步',
  'common.failed': '失敗',
  'common.noData': '沒有找到資料',
  'common.noMoreData': '已顯示全部內容',
  'common.copy': '複製',
  'common.copied': '已複製',
  'common.preview': '預覽',
  'common.view': '查看',
  'common.viewDetails': '查看詳情',
  'common.all': '全部',
  'common.more': '更多',
  'common.confirmDelete': '確認刪除',
  
  // 認證 - 擴展
  'auth.sendFailed': '發送失敗，請稍後再試',
  'auth.invalidEmail': '請輸入有效的 Email 地址',
  'auth.verifying': '請稍候，正在驗證您的帳號',
  
  // 頻道管理
  'channels.title': '我的頻道',
  'channels.create': '建立頻道',
  'channels.createNew': '建立新頻道',
  'channels.name': '頻道名稱',
  'channels.description': '頻道描述',
  'channels.loadFailed': '載入頻道失敗',
  'channels.deleted': '頻道已刪除',
  'channels.deleteFailed': '刪除失敗',
  'channels.createSuccess': '頻道建立成功！',
  'channels.createFailed': '建立失敗',
  'channels.collectTriggered': '收集任務已觸發',
  'channels.triggerFailed': '觸發失敗',
  'channels.selectCategory': '選擇類別',
  'channels.selectRegion': '選擇地區',
  'channels.customKeywords': '自定義關鍵字',
  'channels.enterKeywords': '輸入關鍵字後按 Enter',
  'channels.maxKeywords': '最多 5 個關鍵字',
  'channels.noChannels': '還沒有頻道',
  'channels.createFirst': '建立您的第一個頻道，開始接收個人化的內容推薦',
  'channels.topics': '個主題',
  'channels.collectNow': '立即收集',
  'channels.deleteChannel': '刪除頻道',
  'channels.editChannel': '編輯頻道',
  'channels.enterName': '請輸入頻道名稱',
  'channels.pleaseSelectCategory': '請選擇類別',
  'channels.otherCategoryKeywords': '選擇「其他」類別時請輸入至少一個關鍵字',
  
  // 儀表板 - 擴展
  'dashboard.title': '控制面板',
  'dashboard.todayTopics': '今日熱門主題',
  'dashboard.latestTopics': '最新熱門主題',
  'dashboard.generating': '正在生成今日主題...',
  'dashboard.generateStarted': '今日主題生成任務已啟動',
  'dashboard.generateFailed': '生成今日主題失敗',
  'dashboard.generateSuccess': '今日主題生成完成！',
  'dashboard.deleteFailed': '刪除今日主題失敗',
  'dashboard.confirmDelete': '確定要刪除所有今日生成的主題嗎？此操作無法復原。',
  'dashboard.dbNotConnected': '資料庫未連接，無法生成主題',
  'dashboard.serverError': '伺服器內部錯誤，請查看後端日誌',
  'dashboard.cannotConnect': '無法連接到後端服務',
  'dashboard.welcome': '歡迎回來',
  'dashboard.greeting': '你好',
  'dashboard.inspiration': '靈感創作',
  'dashboard.noContent': '暫無內容',
  'dashboard.upcoming': '即將到來',
  'dashboard.noEvents': '暫無事件',
  'dashboard.recent': '最近活動',
  'dashboard.noActivity': '暫無活動',
  'dashboard.retry': '重試',
  'dashboard.delete': '刪除',
  'dashboard.generate': '生成',
  
  // 錯誤 - 擴展
  'error.unknown': '未知錯誤',
  'error.serverError': '伺服器錯誤，請稍後再試',
  'error.networkError': '發生錯誤，請稍後再試',
  'error.checkCors': '檢查 CORS 設定是否包含前端網域',
  'error.checkNetwork': '檢查網路連接',
  
  // 圖片 - 擴展
  'images.matching': '正在智能匹配照片...',
  'images.matchFailed': '匹配照片失敗',
  'images.matchSuccess': '照片與文字匹配度良好',
  'images.verifyFailed': '驗證匹配度失敗',
  'images.deleted': '圖片已成功刪除',
  'images.deleteFailed': '刪除圖片失敗，請稍後再試',
  'images.orderUpdated': '圖片順序已更新',
  'images.orderFailed': '更新圖片順序失敗，請稍後再試',
  'images.confirmDelete': '確定要刪除這張圖片嗎？',
  'images.verifying': '驗證中...',
  'images.verify': '驗證匹配度',
  'images.smartMatch': '智能匹配（補齊至8張）',
  'images.saveOrder': '儲存順序',
  'images.searchPlaceholder': '輸入關鍵字搜尋圖片',
  'images.adding': '新增中...',
  'images.addSuccess': '圖片已新增',
  'images.addFailed': '新增圖片失敗',
  
  // 靈感
  'inspiration.title': '靈感策劃',
  
  // 偏好設定
  'preferences.title': '偏好設定',
  'preferences.developing': '偏好設定功能開發中...',
  
  // 發布
  'publish.title': '一鍵發布',
  
  // 排程
  'schedule.title': '排程管理',
  'schedule.developing': '排程管理功能開發中...',
  
  // 設定 - 擴展
  'settings.subtitle': '管理您的帳號和偏好設定',
  'settings.darkMode': '深色模式',
  'settings.lightMode': '淺色模式',
  'settings.appearance': '外觀',
  'settings.emailNotifications': 'Email 通知',
  'settings.newFeatures': '新功能提醒',
  'settings.systemUpdates': '系統更新通知',
  'settings.accountInfo': '帳號資訊',
  'settings.accountType': '帳號類型',
  'settings.registrationTime': '註冊時間',
  'settings.lastLogin': '上次登入',
  
  // 社交連接
  'social.title': '平台連接',
  'social.connected': '已連接',
  'social.notConnected': '未連接',
  'social.connect': '連接',
  'social.disconnect': '斷開連接',
  'social.tips': '提示',
  'social.tip1': '連接後可以一鍵發布內容到多個平台',
  'social.tip2': 'Meta 平台需要 Business 或 Creator 帳號',
  'social.tip3': '您可以隨時斷開連接',
  'social.tip4': '我們不會在未經您同意下發布任何內容',
  
  // 風格
  'style.title': '風格檔案',
  'style.coldStart': '冷啟動',
  'style.learning': '學習中',
  'style.mature': '成熟',
  
  // 主題 - 擴展
  'topics.notFound': '找不到主題',
  'topics.content': '內容',
  'topics.shortPost': '短文',
  'topics.script': '腳本',
  'topics.interaction': '互動',
  'topics.category': '分類',
  'topics.status': '狀態',
  'topics.source': '來源',
  'topics.generatedAt': '生成時間',
  'topics.aiModel': 'AI 模型',
  'topics.stats': '統計',
  'topics.imageCount': '圖片數量',
  'topics.wordCount': '字數',
  'topics.duration': '預計時長',
};

// 英文翻譯
const en: typeof zhTW = {
  // Common
  'common.loading': 'Loading...',
  'common.error': 'Error occurred',
  'common.success': 'Success',
  'common.cancel': 'Cancel',
  'common.confirm': 'Confirm',
  'common.save': 'Save',
  'common.delete': 'Delete',
  'common.edit': 'Edit',
  'common.back': 'Back',
  'common.next': 'Next',
  'common.submit': 'Submit',
  'common.close': 'Close',
  'common.search': 'Search',
  'common.retry': 'Retry',
  'common.or': 'or',
  'common.show': 'Show',
  'common.hide': 'Hide',
  'common.language': 'EN',
  
  // Navigation
  'nav.home': 'Home',
  'nav.dashboard': 'Dashboard',
  'nav.topics': 'Topics',
  'nav.channels': 'My Channels',
  'nav.inspiration': 'Inspiration',
  'nav.styleProfile': 'Style Profile',
  'nav.publish': 'One-Click Publish',
  'nav.socialConnect': 'Connect Platforms',
  'nav.schedule': 'Schedule',
  'nav.settings': 'Settings',
  'nav.login': 'Login',
  'nav.register': 'Sign Up',
  'nav.logout': 'Logout',
  'nav.profile': 'Profile',
  
  // Brand
  'brand.name': 'Influencers AI',
  'brand.tagline': 'AI Assistant for Influencers',
  
  // Greeting
  'greeting.hello': 'Hello',
  'greeting.guest': 'Guest',
  'greeting.user': '{name}',
  
  // Auth - Login
  'auth.login.title': 'Login',
  'auth.login.subtitle': 'Welcome back! Please sign in to your account',
  'auth.login.email': 'Email Address',
  'auth.login.password': 'Password',
  'auth.login.rememberMe': 'Remember me',
  'auth.login.forgotPassword': 'Forgot password?',
  'auth.login.submit': 'Sign In',
  'auth.login.noAccount': "Don't have an account?",
  'auth.login.registerLink': 'Sign up now',
  'auth.login.googleLogin': 'Sign in with Google',
  'auth.login.welcome': 'Welcome Back',
  'auth.login.guestMode': 'Guest Mode',
  'auth.login.success': 'Login successful!',
  'auth.login.error': 'Login failed',
  'auth.login.invalidCredentials': 'Invalid email or password',
  
  // Auth - Register
  'auth.register.title': 'Create Account',
  'auth.register.subtitle': 'Join us and start your AI creative journey',
  'auth.register.name': 'Name',
  'auth.register.namePlaceholder': 'Your name',
  'auth.register.email': 'Email Address',
  'auth.register.emailPlaceholder': 'example@email.com',
  'auth.register.password': 'Password',
  'auth.register.passwordPlaceholder': 'Min 8 chars, 1 uppercase letter',
  'auth.register.confirmPassword': 'Confirm Password',
  'auth.register.confirmPasswordPlaceholder': 'Re-enter password',
  'auth.register.language': 'Language Preference',
  'auth.register.terms': 'I agree to the',
  'auth.register.termsLink': 'Terms of Service',
  'auth.register.and': 'and',
  'auth.register.privacyLink': 'Privacy Policy',
  'auth.register.submit': 'Create Account',
  'auth.register.hasAccount': 'Already have an account?',
  'auth.register.loginLink': 'Sign in',
  'auth.register.googleRegister': 'Sign up with Google',
  'auth.register.success': 'Registration successful! Please check your email',
  'auth.register.error': 'Registration failed',
  
  // Auth - Email Verification
  'auth.verify.title': 'Verify Email',
  'auth.verify.subtitle': 'We sent a verification email to your inbox',
  'auth.verify.checkEmail': 'Please check your email and click the verification link',
  'auth.verify.resend': 'Resend verification email',
  'auth.verify.resending': 'Sending...',
  'auth.verify.resent': 'Verification email resent',
  'auth.verify.success': 'Email verified successfully!',
  'auth.verify.error': 'Verification failed, link may have expired',
  'auth.verify.expired': 'Verification link has expired',
  
  // Auth - Forgot Password
  'auth.forgot.title': 'Forgot Password',
  'auth.forgot.subtitle': 'Enter your email and we will send a reset link',
  'auth.forgot.email': 'Email Address',
  'auth.forgot.submit': 'Send Reset Link',
  'auth.forgot.success': 'Reset email sent',
  'auth.forgot.backToLogin': 'Back to login',
  
  // Auth - Reset Password
  'auth.reset.title': 'Reset Password',
  'auth.reset.subtitle': 'Please enter your new password',
  'auth.reset.newPassword': 'New Password',
  'auth.reset.confirmPassword': 'Confirm New Password',
  'auth.reset.submit': 'Reset Password',
  'auth.reset.success': 'Password reset successful!',
  'auth.reset.error': 'Reset failed, link may have expired',
  
  // Auth - Password Validation
  'auth.password.minLength': 'At least 8 characters',
  'auth.password.uppercase': 'At least 1 uppercase letter',
  'auth.password.match': 'Passwords do not match',
  
  // Auth - Login Required
  'auth.loginRequired': 'Login Required',
  'auth.loginRequiredMessage': 'This feature requires login. Please sign in or create an account.',
  
  // Legal - Terms of Service
  'legal.terms.title': 'Terms of Service',
  'legal.terms.subtitle': 'TERMS OF SERVICE',
  'legal.terms.lastUpdate': 'Last updated: February 2026',
  'legal.terms.section1.title': '1. Service Description',
  'legal.terms.section1.content': 'Influencers AI (hereinafter referred to as "the Service") is an AI-powered content creation platform designed to help users generate high-quality social media content.',
  'legal.terms.section2.title': '2. Account Registration',
  'legal.terms.section2.content': 'You must provide true and accurate personal information to register an account. You are responsible for protecting your account security and all activities under your account.',
  'legal.terms.section3.title': '3. Content Ownership',
  'legal.terms.section3.content': 'Content generated using the Service belongs to you. However, you agree to grant the Service the right to use such content to improve AI models.',
  'legal.terms.section4.title': '4. Usage Restrictions',
  'legal.terms.section4.content': 'You agree not to use the Service to create illegal, harmful, threatening, abusive, harassing, defamatory, or otherwise objectionable content.',
  'legal.terms.section5.title': '5. Service Changes',
  'legal.terms.section5.content': 'The Service reserves the right to modify or terminate the service at any time without notice.',
  'legal.terms.section6.title': '6. Disclaimer',
  'legal.terms.section6.content': 'The Service is provided "as is" without any express or implied warranties. The Service is not liable for any damages arising from use of the Service.',
  
  // Legal - Privacy Policy
  'legal.privacy.title': 'Privacy Policy',
  'legal.privacy.subtitle': 'PRIVACY POLICY',
  'legal.privacy.lastUpdate': 'Last updated: February 2026',
  'legal.privacy.section1.title': '1. Data Collection',
  'legal.privacy.section1.content': 'We collect information you provide, including but not limited to: email address, name, and language preference. We also automatically collect usage data such as browsing history and device information.',
  'legal.privacy.section2.title': '2. Data Usage',
  'legal.privacy.section2.content': 'We use collected data to:',
  'legal.privacy.section2.list1': 'Provide and maintain the service',
  'legal.privacy.section2.list2': 'Personalize your experience',
  'legal.privacy.section2.list3': 'Improve our AI models',
  'legal.privacy.section2.list4': 'Communicate with you about service-related matters',
  'legal.privacy.section3.title': '3. Data Protection',
  'legal.privacy.section3.content': 'We employ industry-standard security measures to protect your personal data, including encrypted transmission and secure storage.',
  'legal.privacy.section4.title': '4. Data Sharing',
  'legal.privacy.section4.content': 'We do not sell your personal data. We may share your data in the following situations:',
  'legal.privacy.section4.list1': 'With your consent',
  'legal.privacy.section4.list2': 'Legal requirements',
  'legal.privacy.section4.list3': 'With service providers (bound by confidentiality agreements)',
  'legal.privacy.section5.title': '5. Cookie Usage',
  'legal.privacy.section5.content': 'We use cookies and similar technologies to remember your preferences and improve user experience.',
  'legal.privacy.section6.title': '6. Your Rights',
  'legal.privacy.section6.content': 'You have the right to:',
  'legal.privacy.section6.list1': 'Access your personal data',
  'legal.privacy.section6.list2': 'Correct inaccurate data',
  'legal.privacy.section6.list3': 'Request deletion of your data',
  'legal.privacy.section6.list4': 'Withdraw consent',
  'legal.privacy.section7.title': '7. Contact Us',
  'legal.privacy.section7.content': 'For any privacy-related questions, please contact: privacy@influencers.ai',
  
  // User Settings
  'settings.title': 'Settings',
  'settings.profile': 'Profile',
  'settings.profileDesc': 'Manage your personal information',
  'settings.account': 'Account',
  'settings.accountDesc': 'Manage your account security',
  'settings.preferences': 'Preferences',
  'settings.preferencesDesc': 'Customize your experience',
  'settings.notifications': 'Notifications',
  'settings.notificationsDesc': 'Manage notification preferences',
  
  // Profile
  'profile.name': 'Name',
  'profile.email': 'Email',
  'profile.avatar': 'Avatar',
  'profile.changeAvatar': 'Change Avatar',
  'profile.language': 'Language',
  'profile.timezone': 'Timezone',
  'profile.save': 'Save Changes',
  'profile.saved': 'Saved',
  
  // Account Settings
  'account.changePassword': 'Change Password',
  'account.currentPassword': 'Current Password',
  'account.newPassword': 'New Password',
  'account.confirmPassword': 'Confirm New Password',
  'account.linkedAccounts': 'Linked Accounts',
  'account.linkGoogle': 'Link Google Account',
  'account.unlinkGoogle': 'Unlink',
  'account.deleteAccount': 'Delete Account',
  'account.deleteWarning': 'This action cannot be undone. All data will be permanently deleted',
  
  // Features
  'feature.unavailable': 'This feature is currently unavailable',
  'feature.comingSoon': 'Coming Soon',
  'feature.beta': 'Beta Testing',
  
  // Errors
  'error.network': 'Network connection failed',
  'error.server': 'Server error',
  'error.unauthorized': 'Please login first',
  'error.forbidden': 'Access denied',
  'error.notFound': 'Resource not found',
  'error.validation': 'Please check your input',
  'error.maxUsers': 'System has reached user limit',
  
  // Topics
  'topics.title': 'Topics',
  'topics.overview': 'Topics Overview',
  'topics.create': 'Create Topic',
  'topics.edit': 'Edit Topic',
  'topics.delete': 'Delete Topic',
  'topics.noTopics': 'No topics yet',
  'topics.noSearchResults': 'No topics found matching your search',
  'topics.tryAdjustFilters': 'Try adjusting filters or try again later',
  'topics.loadMore': 'Load More',
  'topics.today': 'Today',
  'topics.yesterday': 'Yesterday',
  'topics.thisWeek': 'This Week',
  'topics.older': 'Older',
  'topics.infiniteScroll': 'Infinite Scroll',
  'topics.searchPlaceholder': 'Search topics...',
  'topics.pagination': 'Pagination',
  'topics.searchSource': 'Search source',
  'topics.total': '{count} topics total',
  'topics.loaded': '{count} loaded',
  'topics.source': 'Source',
  'topics.noContent': 'No content summary',
  'topics.contentProgress': 'Content Progress',
  'topics.imageProgress': 'Image Progress',
  'topics.deleteConfirmMessage': 'Are you sure you want to delete this topic? This action cannot be undone.',
  
  // Content Generation
  'content.generate': 'Generate Content',
  'content.generating': 'Generating...',
  'content.regenerate': 'Regenerate',
  'content.copy': 'Copy',
  'content.copied': 'Copied',
  'content.platform': 'Platform',
  'content.style': 'Style',
  
  // Images
  'images.search': 'Search Images',
  'images.upload': 'Upload Image',
  'images.select': 'Select Image',
  'images.noResults': 'No images found',
  'images.searchTitle': 'Search Images',
  'images.suggestedKeywords': 'Suggested Keywords (extracted from content)',
  'images.sourceLabel': 'Source',
  'images.allSources': 'All Sources',
  'images.diagnosticMode': 'Diagnostic Mode',
  'images.tryDifferentKeywords': 'Try different keywords',
  'images.validateMatch': 'Validate Match',
  'images.reorder': 'Reorder',
  'images.loadError': 'Image failed to load',
  'images.photographer': 'Photographer',
  'images.license': 'License',
  'images.order': 'Order',
  'images.imageUrl': 'Image URL',
  
  // Filters
  'filters.title': 'Filters',
  'filters.search': 'Search',
  'filters.searchPlaceholder': 'Search topic title or source...',
  'filters.category': 'Category',
  'filters.status': 'Status',
  'filters.date': 'Date',
  'filters.all': 'All',
  'filters.fashion': 'Fashion',
  'filters.food': 'Food',
  'filters.trend': 'Trend',
  'filters.pending': 'Pending',
  'filters.confirmed': 'Confirmed',
  'filters.deleted': 'Deleted',
  'filters.reset': 'Reset',
  
  // Common - Extended
  'common.searching': 'Searching...',
  'common.saving': 'Saving...',
  'common.deleting': 'Deleting...',
  'common.add': 'Add',
  'common.remove': 'Remove',
  'common.previous': 'Previous',
  'common.failed': 'Failed',
  'common.noData': 'No data found',
  'common.copy': 'Copy',
  'common.copied': 'Copied',
  'common.preview': 'Preview',
  'common.view': 'View',
  'common.all': 'All',
  'common.more': 'More',
  'common.noMoreData': 'All content displayed',
  'common.viewDetails': 'View Details',
  'common.confirmDelete': 'Confirm Delete',
  
  // Auth - Extended
  'auth.sendFailed': 'Failed to send, please try again later',
  'auth.invalidEmail': 'Please enter a valid email address',
  'auth.verifying': 'Please wait, verifying your account',
  
  // Channels
  'channels.title': 'My Channels',
  'channels.create': 'Create Channel',
  'channels.createNew': 'Create New Channel',
  'channels.name': 'Channel Name',
  'channels.description': 'Channel Description',
  'channels.loadFailed': 'Failed to load channels',
  'channels.deleted': 'Channel deleted',
  'channels.deleteFailed': 'Delete failed',
  'channels.createSuccess': 'Channel created successfully!',
  'channels.createFailed': 'Create failed',
  'channels.collectTriggered': 'Collection task triggered',
  'channels.triggerFailed': 'Trigger failed',
  'channels.selectCategory': 'Select Category',
  'channels.selectRegion': 'Select Region',
  'channels.customKeywords': 'Custom Keywords',
  'channels.enterKeywords': 'Enter keywords and press Enter',
  'channels.maxKeywords': 'Maximum 5 keywords',
  'channels.noChannels': 'No channels yet',
  'channels.createFirst': 'Create your first channel to start receiving personalized content',
  'channels.topics': 'topics',
  'channels.collectNow': 'Collect Now',
  'channels.deleteChannel': 'Delete Channel',
  'channels.editChannel': 'Edit Channel',
  'channels.enterName': 'Please enter channel name',
  'channels.pleaseSelectCategory': 'Please select a category',
  'channels.otherCategoryKeywords': 'Please enter at least one keyword when selecting "Other" category',
  
  // Dashboard - Extended
  'dashboard.title': 'Dashboard',
  'dashboard.todayTopics': "Today's Hot Topics",
  'dashboard.latestTopics': 'Latest Hot Topics',
  'dashboard.generating': "Generating today's topics...",
  'dashboard.generateStarted': "Today's topic generation task started",
  'dashboard.generateFailed': "Failed to generate today's topics",
  'dashboard.generateSuccess': "Today's topics generated!",
  'dashboard.deleteFailed': "Failed to delete today's topics",
  'dashboard.confirmDelete': 'Are you sure you want to delete all topics generated today? This action cannot be undone.',
  'dashboard.dbNotConnected': 'Database not connected, cannot generate topics',
  'dashboard.serverError': 'Internal server error, please check backend logs',
  'dashboard.cannotConnect': 'Cannot connect to backend service',
  'dashboard.welcome': 'Welcome Back',
  'dashboard.greeting': 'Hello',
  'dashboard.inspiration': 'Inspiration',
  'dashboard.noContent': 'No content',
  'dashboard.upcoming': 'Upcoming',
  'dashboard.noEvents': 'No events',
  'dashboard.recent': 'Recent',
  'dashboard.noActivity': 'No activity',
  'dashboard.retry': 'Retry',
  'dashboard.delete': 'Delete',
  'dashboard.generate': 'Generate',
  
  // Error - Extended
  'error.unknown': 'Unknown error',
  'error.serverError': 'Server error, please try again later',
  'error.networkError': 'An error occurred, please try again later',
  'error.checkCors': 'Check if CORS settings include frontend domain',
  'error.checkNetwork': 'Check network connection',
  
  // Images - Extended
  'images.matching': 'Smart matching photos...',
  'images.matchFailed': 'Failed to match photos',
  'images.matchSuccess': 'Photos match well with text',
  'images.verifyFailed': 'Failed to verify match',
  'images.deleted': 'Image deleted successfully',
  'images.deleteFailed': 'Failed to delete image, please try again',
  'images.orderUpdated': 'Image order updated',
  'images.orderFailed': 'Failed to update image order, please try again',
  'images.confirmDelete': 'Are you sure you want to delete this image?',
  'images.verifying': 'Verifying...',
  'images.verify': 'Verify match',
  'images.smartMatch': 'Smart match (fill to 8)',
  'images.saveOrder': 'Save order',
  'images.searchPlaceholder': 'Enter keywords to search images',
  'images.adding': 'Adding...',
  'images.addSuccess': 'Image added',
  'images.addFailed': 'Failed to add image',
  
  // Inspiration
  'inspiration.title': 'Inspiration',
  
  // Preferences
  'preferences.title': 'Preferences',
  'preferences.developing': 'Preferences feature in development...',
  
  // Publish
  'publish.title': 'One-Click Publish',
  
  // Schedule
  'schedule.title': 'Schedule Management',
  'schedule.developing': 'Schedule management feature in development...',
  
  // Settings - Extended
  'settings.subtitle': 'Manage your account and preferences',
  'settings.darkMode': 'Dark Mode',
  'settings.lightMode': 'Light Mode',
  'settings.appearance': 'Appearance',
  'settings.emailNotifications': 'Email Notifications',
  'settings.newFeatures': 'New Feature Alerts',
  'settings.systemUpdates': 'System Update Notifications',
  'settings.accountInfo': 'Account Info',
  'settings.accountType': 'Account Type',
  'settings.registrationTime': 'Registration Time',
  'settings.lastLogin': 'Last Login',
  
  // Social
  'social.title': 'Social Connect',
  'social.connected': 'Connected',
  'social.notConnected': 'Not Connected',
  'social.connect': 'Connect',
  'social.disconnect': 'Disconnect',
  'social.tips': 'Tips',
  'social.tip1': 'After connecting, you can publish content to multiple platforms with one click',
  'social.tip2': 'Meta platforms require Business or Creator account',
  'social.tip3': 'You can disconnect at any time',
  'social.tip4': 'We will not post anything without your consent',
  
  // Style
  'style.title': 'Style Profile',
  'style.coldStart': 'Cold Start',
  'style.learning': 'Learning',
  'style.mature': 'Mature',
  
  // Topics - Extended
  'topics.notFound': 'Topic not found',
  'topics.content': 'Content',
  'topics.shortPost': 'Short Post',
  'topics.script': 'Script',
  'topics.interaction': 'Interaction',
  'topics.category': 'Category',
  'topics.status': 'Status',
  'topics.source': 'Source',
  'topics.generatedAt': 'Generated at',
  'topics.aiModel': 'AI Model',
  'topics.stats': 'Statistics',
  'topics.imageCount': 'Image count',
  'topics.wordCount': 'Word count',
  'topics.duration': 'Estimated duration',
};

// 日文翻譯
const ja: typeof zhTW = {
  // 共通
  'common.loading': '読み込み中...',
  'common.error': 'エラーが発生しました',
  'common.success': '成功',
  'common.cancel': 'キャンセル',
  'common.confirm': '確認',
  'common.save': '保存',
  'common.delete': '削除',
  'common.edit': '編集',
  'common.back': '戻る',
  'common.next': '次へ',
  'common.submit': '送信',
  'common.close': '閉じる',
  'common.search': '検索',
  'common.retry': '再試行',
  'common.or': 'または',
  'common.show': '表示',
  'common.hide': '非表示',
  'common.language': '日本語',
  
  // ナビゲーション
  'nav.home': 'ホーム',
  'nav.dashboard': 'ダッシュボード',
  'nav.topics': 'トピック',
  'nav.channels': 'マイチャンネル',
  'nav.inspiration': 'インスピレーション',
  'nav.styleProfile': 'スタイルプロフィール',
  'nav.publish': 'ワンクリック公開',
  'nav.socialConnect': 'プラットフォーム連携',
  'nav.schedule': 'スケジュール',
  'nav.settings': '設定',
  'nav.login': 'ログイン',
  'nav.register': '新規登録',
  'nav.logout': 'ログアウト',
  'nav.profile': 'プロフィール',
  
  // ブランド
  'brand.name': 'Influencers AI',
  'brand.tagline': 'インフルエンサーAIアシスタント',
  
  // 挨拶
  'greeting.hello': 'こんにちは',
  'greeting.guest': 'ゲスト',
  'greeting.user': '{name}',
  
  // 認証 - ログイン
  'auth.login.title': 'ログイン',
  'auth.login.subtitle': 'おかえりなさい！アカウントにログインしてください',
  'auth.login.email': 'メールアドレス',
  'auth.login.password': 'パスワード',
  'auth.login.rememberMe': 'ログイン状態を保持',
  'auth.login.forgotPassword': 'パスワードをお忘れですか？',
  'auth.login.submit': 'ログイン',
  'auth.login.noAccount': 'アカウントをお持ちでない方',
  'auth.login.registerLink': '新規登録',
  'auth.login.googleLogin': 'Google でログイン',
  'auth.login.welcome': 'おかえりなさい',
  'auth.login.guestMode': 'ゲストモード',
  'auth.login.success': 'ログイン成功！',
  'auth.login.error': 'ログイン失敗',
  'auth.login.invalidCredentials': 'メールアドレスまたはパスワードが正しくありません',
  
  // 認証 - 登録
  'auth.register.title': 'アカウント作成',
  'auth.register.subtitle': '私たちに参加して、AI クリエイティブジャーニーを始めましょう',
  'auth.register.name': '名前',
  'auth.register.namePlaceholder': 'お名前',
  'auth.register.email': 'メールアドレス',
  'auth.register.emailPlaceholder': 'example@email.com',
  'auth.register.password': 'パスワード',
  'auth.register.passwordPlaceholder': '8文字以上、大文字1文字以上',
  'auth.register.confirmPassword': 'パスワード確認',
  'auth.register.confirmPasswordPlaceholder': 'パスワードを再入力',
  'auth.register.language': '言語設定',
  'auth.register.terms': '以下に同意します',
  'auth.register.termsLink': '利用規約',
  'auth.register.and': 'と',
  'auth.register.privacyLink': 'プライバシーポリシー',
  'auth.register.submit': 'アカウント作成',
  'auth.register.hasAccount': 'すでにアカウントをお持ちの方',
  'auth.register.loginLink': 'ログイン',
  'auth.register.googleRegister': 'Google で登録',
  'auth.register.success': '登録成功！確認メールをご確認ください',
  'auth.register.error': '登録失敗',
  
  // 認証 - メール確認
  'auth.verify.title': 'メール確認',
  'auth.verify.subtitle': '確認メールを送信しました',
  'auth.verify.checkEmail': 'メールを確認し、確認リンクをクリックしてください',
  'auth.verify.resend': '確認メールを再送信',
  'auth.verify.resending': '送信中...',
  'auth.verify.resent': '確認メールを再送信しました',
  'auth.verify.success': 'メール確認成功！',
  'auth.verify.error': '確認失敗、リンクが期限切れの可能性があります',
  'auth.verify.expired': '確認リンクが期限切れです',
  
  // 認証 - パスワードを忘れた
  'auth.forgot.title': 'パスワードをお忘れですか',
  'auth.forgot.subtitle': 'メールアドレスを入力してください。リセットリンクを送信します',
  'auth.forgot.email': 'メールアドレス',
  'auth.forgot.submit': 'リセットリンクを送信',
  'auth.forgot.success': 'リセットメールを送信しました',
  'auth.forgot.backToLogin': 'ログインに戻る',
  
  // 認証 - パスワードリセット
  'auth.reset.title': 'パスワードリセット',
  'auth.reset.subtitle': '新しいパスワードを入力してください',
  'auth.reset.newPassword': '新しいパスワード',
  'auth.reset.confirmPassword': '新しいパスワード確認',
  'auth.reset.submit': 'パスワードをリセット',
  'auth.reset.success': 'パスワードリセット成功！',
  'auth.reset.error': 'リセット失敗、リンクが期限切れの可能性があります',
  
  // 認証 - パスワード検証
  'auth.password.minLength': '8文字以上',
  'auth.password.uppercase': '大文字1文字以上',
  'auth.password.match': 'パスワードが一致しません',
  
  // 認証 - ログイン要求
  'auth.loginRequired': 'ログインが必要です',
  'auth.loginRequiredMessage': 'この機能を使用するにはログインが必要です。ログインまたはアカウントを作成してください。',
  
  // 法的 - 利用規約
  'legal.terms.title': '利用規約',
  'legal.terms.subtitle': 'TERMS OF SERVICE',
  'legal.terms.lastUpdate': '最終更新：2026年2月',
  'legal.terms.section1.title': '1. サービス説明',
  'legal.terms.section1.content': 'Influencers AI（以下「本サービス」）は、ユーザーが高品質なソーシャルメディアコンテンツを生成できるAI駆動のコンテンツ作成プラットフォームです。',
  'legal.terms.section2.title': '2. アカウント登録',
  'legal.terms.section2.content': 'アカウント登録には真実かつ正確な個人情報を提供する必要があります。アカウントのセキュリティを保護し、アカウント下のすべての活動に責任を負います。',
  'legal.terms.section3.title': '3. コンテンツの所有権',
  'legal.terms.section3.content': '本サービスを使用して生成されたコンテンツの所有権はお客様に帰属します。ただし、AIモデルの改善のために本サービスがそのコンテンツを使用する権利に同意するものとします。',
  'legal.terms.section4.title': '4. 使用制限',
  'legal.terms.section4.content': '本サービスを使用して、違法、有害、脅迫的、虐待的、嫌がらせ、名誉毀損、またはその他の不快なコンテンツを作成しないことに同意します。',
  'legal.terms.section5.title': '5. サービス変更',
  'legal.terms.section5.content': '本サービスは、事前の通知なくサービスを変更または終了する権利を留保します。',
  'legal.terms.section6.title': '6. 免責事項',
  'legal.terms.section6.content': '本サービスは「現状のまま」提供され、明示または黙示を問わずいかなる保証も行いません。本サービスの使用から生じる損害について、本サービスは責任を負いません。',
  
  // 法的 - プライバシーポリシー
  'legal.privacy.title': 'プライバシーポリシー',
  'legal.privacy.subtitle': 'PRIVACY POLICY',
  'legal.privacy.lastUpdate': '最終更新：2026年2月',
  'legal.privacy.section1.title': '1. データ収集',
  'legal.privacy.section1.content': 'メールアドレス、名前、言語設定を含む、お客様が提供する情報を収集します。また、閲覧履歴やデバイス情報などの使用データも自動的に収集します。',
  'legal.privacy.section2.title': '2. データ使用',
  'legal.privacy.section2.content': '収集したデータを以下の目的で使用します：',
  'legal.privacy.section2.list1': 'サービスの提供と維持',
  'legal.privacy.section2.list2': 'お客様の体験をパーソナライズ',
  'legal.privacy.section2.list3': 'AIモデルの改善',
  'legal.privacy.section2.list4': 'サービス関連の連絡',
  'legal.privacy.section3.title': '3. データ保護',
  'legal.privacy.section3.content': '暗号化された送信と安全なストレージを含む、業界標準のセキュリティ対策を採用してお客様の個人データを保護します。',
  'legal.privacy.section4.title': '4. データ共有',
  'legal.privacy.section4.content': 'お客様の個人データを販売することはありません。以下の状況でデータを共有する場合があります：',
  'legal.privacy.section4.list1': 'お客様の同意がある場合',
  'legal.privacy.section4.list2': '法的要件',
  'legal.privacy.section4.list3': 'サービスプロバイダーとの協力（機密保持契約に基づく）',
  'legal.privacy.section5.title': '5. Cookieの使用',
  'legal.privacy.section5.content': 'お客様の設定を記憶し、ユーザー体験を向上させるためにCookieおよび類似の技術を使用します。',
  'legal.privacy.section6.title': '6. お客様の権利',
  'legal.privacy.section6.content': 'お客様には以下の権利があります：',
  'legal.privacy.section6.list1': '個人データへのアクセス',
  'legal.privacy.section6.list2': '不正確なデータの訂正',
  'legal.privacy.section6.list3': 'データの削除を要求',
  'legal.privacy.section6.list4': '同意の撤回',
  'legal.privacy.section7.title': '7. お問い合わせ',
  'legal.privacy.section7.content': 'プライバシーに関するご質問は、privacy@influencers.ai までご連絡ください。',
  
  // ユーザー設定
  'settings.title': '設定',
  'settings.profile': 'プロフィール',
  'settings.profileDesc': '個人情報を管理',
  'settings.account': 'アカウント',
  'settings.accountDesc': 'アカウントセキュリティを管理',
  'settings.preferences': '環境設定',
  'settings.preferencesDesc': '使用体験をカスタマイズ',
  'settings.notifications': '通知',
  'settings.notificationsDesc': '通知設定を管理',
  
  // プロフィール
  'profile.name': '名前',
  'profile.email': 'メール',
  'profile.avatar': 'アバター',
  'profile.changeAvatar': 'アバターを変更',
  'profile.language': '言語',
  'profile.timezone': 'タイムゾーン',
  'profile.save': '変更を保存',
  'profile.saved': '保存済み',
  
  // アカウント設定
  'account.changePassword': 'パスワード変更',
  'account.currentPassword': '現在のパスワード',
  'account.newPassword': '新しいパスワード',
  'account.confirmPassword': '新しいパスワード確認',
  'account.linkedAccounts': '連携アカウント',
  'account.linkGoogle': 'Google アカウントを連携',
  'account.unlinkGoogle': '連携解除',
  'account.deleteAccount': 'アカウント削除',
  'account.deleteWarning': 'この操作は取り消せません。すべてのデータが完全に削除されます',
  
  // 機能
  'feature.unavailable': 'この機能は現在利用できません',
  'feature.comingSoon': '近日公開',
  'feature.beta': 'ベータテスト中',
  
  // エラー
  'error.network': 'ネットワーク接続失敗',
  'error.server': 'サーバーエラー',
  'error.unauthorized': 'ログインしてください',
  'error.forbidden': 'アクセス拒否',
  'error.notFound': 'リソースが見つかりません',
  'error.validation': '入力を確認してください',
  'error.maxUsers': 'システムがユーザー制限に達しました',
  
  // トピック
  'topics.title': 'トピック',
  'topics.overview': 'トピック一覧',
  'topics.create': 'トピック作成',
  'topics.edit': 'トピック編集',
  'topics.delete': 'トピック削除',
  'topics.noTopics': 'トピックがありません',
  'topics.noSearchResults': '検索条件に一致するトピックが見つかりません',
  'topics.tryAdjustFilters': 'フィルターを調整するか、後でもう一度お試しください',
  'topics.loadMore': 'もっと読み込む',
  'topics.today': '今日',
  'topics.yesterday': '昨日',
  'topics.thisWeek': '今週',
  'topics.older': 'それ以前',
  'topics.infiniteScroll': '無限スクロール',
  'topics.searchPlaceholder': 'トピックを検索...',
  'topics.pagination': 'ページネーション',
  'topics.searchSource': '検索ソース',
  'topics.total': '合計 {count} トピック',
  'topics.loaded': '{count} 件読み込み済み',
  'topics.source': 'ソース',
  'topics.noContent': 'コンテンツ概要なし',
  'topics.contentProgress': 'コンテンツ進捗',
  'topics.imageProgress': '画像進捗',
  'topics.deleteConfirmMessage': 'このトピックを削除しますか？この操作は元に戻せません。',
  
  // コンテンツ生成
  'content.generate': 'コンテンツ生成',
  'content.generating': '生成中...',
  'content.regenerate': '再生成',
  'content.copy': 'コピー',
  'content.copied': 'コピーしました',
  'content.platform': 'プラットフォーム',
  'content.style': 'スタイル',
  
  // 画像
  'images.search': '画像検索',
  'images.upload': '画像アップロード',
  'images.select': '画像選択',
  'images.noResults': '画像が見つかりません',
  'images.searchTitle': '画像検索',
  'images.suggestedKeywords': 'おすすめキーワード（コンテンツから抽出）',
  'images.sourceLabel': 'ソース',
  'images.allSources': 'すべてのソース',
  'images.diagnosticMode': '診断モード',
  'images.tryDifferentKeywords': '別のキーワードをお試しください',
  'images.validateMatch': 'マッチング検証',
  'images.reorder': '並び替え',
  'images.loadError': '画像を読み込めません',
  'images.photographer': '撮影者',
  'images.license': 'ライセンス',
  'images.order': '順番',
  'images.imageUrl': '画像 URL',
  
  // フィルター
  'filters.title': 'フィルター',
  'filters.search': '検索',
  'filters.searchPlaceholder': 'トピックタイトルまたはソースを検索...',
  'filters.category': 'カテゴリ',
  'filters.status': 'ステータス',
  'filters.date': '日付',
  'filters.all': 'すべて',
  'filters.fashion': 'ファッション',
  'filters.food': 'グルメ',
  'filters.trend': 'トレンド',
  'filters.pending': '審査中',
  'filters.confirmed': '確認済み',
  'filters.deleted': '削除済み',
  'filters.reset': 'リセット',
  
  // 共通 - 拡張
  'common.searching': '検索中...',
  'common.saving': '保存中...',
  'common.deleting': '削除中...',
  'common.add': '追加',
  'common.remove': '削除',
  'common.previous': '前へ',
  'common.failed': '失敗',
  'common.noData': 'データが見つかりません',
  'common.copy': 'コピー',
  'common.copied': 'コピーしました',
  'common.preview': 'プレビュー',
  'common.view': '表示',
  'common.all': 'すべて',
  'common.more': 'もっと見る',
  'common.noMoreData': 'すべてのコンテンツを表示済み',
  'common.viewDetails': '詳細を見る',
  'common.confirmDelete': '削除確認',
  
  // 認証 - 拡張
  'auth.sendFailed': '送信に失敗しました。後でもう一度お試しください',
  'auth.invalidEmail': '有効なメールアドレスを入力してください',
  'auth.verifying': 'お待ちください、アカウントを確認中です',
  
  // チャンネル
  'channels.title': 'マイチャンネル',
  'channels.create': 'チャンネル作成',
  'channels.createNew': '新しいチャンネルを作成',
  'channels.name': 'チャンネル名',
  'channels.description': 'チャンネル説明',
  'channels.loadFailed': 'チャンネルの読み込みに失敗しました',
  'channels.deleted': 'チャンネルが削除されました',
  'channels.deleteFailed': '削除に失敗しました',
  'channels.createSuccess': 'チャンネルが作成されました！',
  'channels.createFailed': '作成に失敗しました',
  'channels.collectTriggered': '収集タスクが開始されました',
  'channels.triggerFailed': 'トリガーに失敗しました',
  'channels.selectCategory': 'カテゴリを選択',
  'channels.selectRegion': '地域を選択',
  'channels.customKeywords': 'カスタムキーワード',
  'channels.enterKeywords': 'キーワードを入力してEnterを押してください',
  'channels.maxKeywords': '最大5つのキーワード',
  'channels.noChannels': 'まだチャンネルがありません',
  'channels.createFirst': '最初のチャンネルを作成して、パーソナライズされたコンテンツを受け取りましょう',
  'channels.topics': 'トピック',
  'channels.collectNow': '今すぐ収集',
  'channels.deleteChannel': 'チャンネルを削除',
  'channels.editChannel': 'チャンネルを編集',
  'channels.enterName': 'チャンネル名を入力してください',
  'channels.pleaseSelectCategory': 'カテゴリを選択してください',
  'channels.otherCategoryKeywords': '「その他」カテゴリを選択した場合は、少なくとも1つのキーワードを入力してください',
  
  // ダッシュボード - 拡張
  'dashboard.title': 'ダッシュボード',
  'dashboard.todayTopics': '今日の人気トピック',
  'dashboard.latestTopics': '最新の人気トピック',
  'dashboard.generating': '今日のトピックを生成中...',
  'dashboard.generateStarted': '今日のトピック生成タスクが開始されました',
  'dashboard.generateFailed': '今日のトピックの生成に失敗しました',
  'dashboard.generateSuccess': '今日のトピックが生成されました！',
  'dashboard.deleteFailed': '今日のトピックの削除に失敗しました',
  'dashboard.confirmDelete': '今日生成されたすべてのトピックを削除してもよろしいですか？この操作は元に戻せません。',
  'dashboard.dbNotConnected': 'データベースに接続されていないため、トピックを生成できません',
  'dashboard.serverError': 'サーバー内部エラー、バックエンドログを確認してください',
  'dashboard.cannotConnect': 'バックエンドサービスに接続できません',
  'dashboard.welcome': 'おかえりなさい',
  'dashboard.greeting': 'こんにちは',
  'dashboard.inspiration': 'インスピレーション',
  'dashboard.noContent': 'コンテンツなし',
  'dashboard.upcoming': '予定',
  'dashboard.noEvents': 'イベントなし',
  'dashboard.recent': '最近',
  'dashboard.noActivity': 'アクティビティなし',
  'dashboard.retry': '再試行',
  'dashboard.delete': '削除',
  'dashboard.generate': '生成',
  
  // エラー - 拡張
  'error.unknown': '不明なエラー',
  'error.serverError': 'サーバーエラー、後でもう一度お試しください',
  'error.networkError': 'エラーが発生しました。後でもう一度お試しください',
  'error.checkCors': 'CORS設定にフロントエンドドメインが含まれているか確認してください',
  'error.checkNetwork': 'ネットワーク接続を確認してください',
  
  // 画像 - 拡張
  'images.matching': 'スマートマッチング中...',
  'images.matchFailed': '写真のマッチングに失敗しました',
  'images.matchSuccess': '写真とテキストがよくマッチしています',
  'images.verifyFailed': 'マッチ度の検証に失敗しました',
  'images.deleted': '画像が正常に削除されました',
  'images.deleteFailed': '画像の削除に失敗しました。後でもう一度お試しください',
  'images.orderUpdated': '画像の順序が更新されました',
  'images.orderFailed': '画像の順序の更新に失敗しました。後でもう一度お試しください',
  'images.confirmDelete': 'この画像を削除してもよろしいですか？',
  'images.verifying': '検証中...',
  'images.verify': 'マッチ度を検証',
  'images.smartMatch': 'スマートマッチ（8枚まで補充）',
  'images.saveOrder': '順序を保存',
  'images.searchPlaceholder': 'キーワードを入力して画像を検索',
  'images.adding': '追加中...',
  'images.addSuccess': '画像が追加されました',
  'images.addFailed': '画像の追加に失敗しました',
  
  // インスピレーション
  'inspiration.title': 'インスピレーション',
  
  // 環境設定
  'preferences.title': '環境設定',
  'preferences.developing': '環境設定機能は開発中です...',
  
  // 公開
  'publish.title': 'ワンクリック公開',
  
  // スケジュール
  'schedule.title': 'スケジュール管理',
  'schedule.developing': 'スケジュール管理機能は開発中です...',
  
  // 設定 - 拡張
  'settings.subtitle': 'アカウントと設定を管理',
  'settings.darkMode': 'ダークモード',
  'settings.lightMode': 'ライトモード',
  'settings.appearance': '外観',
  'settings.emailNotifications': 'メール通知',
  'settings.newFeatures': '新機能のお知らせ',
  'settings.systemUpdates': 'システム更新通知',
  'settings.accountInfo': 'アカウント情報',
  'settings.accountType': 'アカウントタイプ',
  'settings.registrationTime': '登録日時',
  'settings.lastLogin': '最終ログイン',
  
  // ソーシャル
  'social.title': 'ソーシャル連携',
  'social.connected': '連携済み',
  'social.notConnected': '未連携',
  'social.connect': '連携',
  'social.disconnect': '連携解除',
  'social.tips': 'ヒント',
  'social.tip1': '連携後、ワンクリックで複数のプラットフォームにコンテンツを公開できます',
  'social.tip2': 'MetaプラットフォームにはBusinessまたはCreatorアカウントが必要です',
  'social.tip3': 'いつでも連携を解除できます',
  'social.tip4': 'お客様の同意なしにコンテンツを投稿することはありません',
  
  // スタイル
  'style.title': 'スタイルプロファイル',
  'style.coldStart': 'コールドスタート',
  'style.learning': '学習中',
  'style.mature': '成熟',
  
  // トピック - 拡張
  'topics.notFound': 'トピックが見つかりません',
  'topics.content': 'コンテンツ',
  'topics.shortPost': 'ショートポスト',
  'topics.script': 'スクリプト',
  'topics.interaction': 'インタラクション',
  'topics.category': 'カテゴリ',
  'topics.status': 'ステータス',
  'topics.source': 'ソース',
  'topics.generatedAt': '生成時刻',
  'topics.aiModel': 'AIモデル',
  'topics.stats': '統計',
  'topics.imageCount': '画像数',
  'topics.wordCount': '文字数',
  'topics.duration': '予想時間',
};

// 翻譯對照表
const translations: Record<Language, typeof zhTW> = {
  'zh-TW': zhTW,
  'en': en,
  'ja': ja,
};

// i18n Store 介面
interface I18nState {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKey, params?: Record<string, string>) => string;
}

// 建立 i18n Store
export const useI18n = create<I18nState>()(
  persist(
    (set, get) => ({
      language: 'zh-TW',
      
      setLanguage: (lang: Language) => {
        set({ language: lang });
        // 更新 HTML lang 屬性
        document.documentElement.lang = lang;
      },
      
      t: (key: TranslationKey, params?: Record<string, string>) => {
        const { language } = get();
        let text = translations[language][key] || translations['zh-TW'][key] || key;
        
        // 替換參數
        if (params) {
          Object.entries(params).forEach(([paramKey, value]) => {
            text = text.replace(new RegExp(`{${paramKey}}`, 'g'), value);
          });
        }
        
        return text;
      },
    }),
    {
      name: 'i18n-storage',
      partialize: (state) => ({ language: state.language }),
    }
  )
);

// 語言選項
export const languageOptions: { code: Language; name: string; shortName: string; icon: string }[] = [
  { code: 'zh-TW', name: '繁體中文', shortName: '繁', icon: '文' },
  { code: 'en', name: 'English', shortName: 'EN', icon: 'A' },
  { code: 'ja', name: '日本語', shortName: 'JP', icon: 'あ' },
];

// 導出翻譯 Hook
export const useTranslation = () => {
  const { t, language, setLanguage } = useI18n();
  return { t, language, setLanguage };
};

