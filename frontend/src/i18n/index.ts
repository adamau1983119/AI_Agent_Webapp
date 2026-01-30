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
  
  // 導航
  'nav.home': '首頁',
  'nav.dashboard': '儀表板',
  'nav.topics': '主題',
  'nav.schedule': '排程',
  'nav.settings': '設定',
  'nav.login': '登入',
  'nav.register': '註冊',
  'nav.logout': '登出',
  'nav.profile': '個人資料',
  
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
  'topics.create': '建立主題',
  'topics.edit': '編輯主題',
  'topics.delete': '刪除主題',
  'topics.noTopics': '還沒有主題',
  'topics.loadMore': '載入更多',
  'topics.today': '今天',
  'topics.yesterday': '昨天',
  'topics.thisWeek': '本週',
  'topics.older': '更早',
  
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
  
  // Navigation
  'nav.home': 'Home',
  'nav.dashboard': 'Dashboard',
  'nav.topics': 'Topics',
  'nav.schedule': 'Schedule',
  'nav.settings': 'Settings',
  'nav.login': 'Login',
  'nav.register': 'Sign Up',
  'nav.logout': 'Logout',
  'nav.profile': 'Profile',
  
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
  'topics.create': 'Create Topic',
  'topics.edit': 'Edit Topic',
  'topics.delete': 'Delete Topic',
  'topics.noTopics': 'No topics yet',
  'topics.loadMore': 'Load More',
  'topics.today': 'Today',
  'topics.yesterday': 'Yesterday',
  'topics.thisWeek': 'This Week',
  'topics.older': 'Older',
  
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
  
  // ナビゲーション
  'nav.home': 'ホーム',
  'nav.dashboard': 'ダッシュボード',
  'nav.topics': 'トピック',
  'nav.schedule': 'スケジュール',
  'nav.settings': '設定',
  'nav.login': 'ログイン',
  'nav.register': '新規登録',
  'nav.logout': 'ログアウト',
  'nav.profile': 'プロフィール',
  
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
  'topics.create': 'トピック作成',
  'topics.edit': 'トピック編集',
  'topics.delete': 'トピック削除',
  'topics.noTopics': 'トピックがありません',
  'topics.loadMore': 'もっと読み込む',
  'topics.today': '今日',
  'topics.yesterday': '昨日',
  'topics.thisWeek': '今週',
  'topics.older': 'それ以前',
  
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
export const languageOptions = [
  { value: 'zh-TW', label: '繁體中文' },
  { value: 'en', label: 'English' },
  { value: 'ja', label: '日本語' },
];

// 導出翻譯 Hook
export const useTranslation = () => {
  const { t, language, setLanguage } = useI18n();
  return { t, language, setLanguage };
};

