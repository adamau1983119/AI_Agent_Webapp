/**
 * 設定頁面
 * Phase 2: 會員系統
 */
import { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useTranslation, languageOptions, Language } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../api/auth';
import { alterEgoApi } from '../api/alterEgo';
import CreditsBillingPanel from '../components/features/CreditsBillingPanel';
import toast from 'react-hot-toast';

export default function Settings() {
  const { t, language, setLanguage } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, isAuthenticated, logout } = useAuthStore();
  
  const [activeTab, setActiveTab] = useState<'profile' | 'account' | 'preferences' | 'billing'>('profile');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [dnaStatus, setDnaStatus] = useState<string | null>(null);

  useEffect(() => {
    alterEgoApi
      .getStatus()
      .then((s) => setDnaStatus(s.dna_status))
      .catch(() => setDnaStatus(null));
  }, []);

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab === 'profile' || tab === 'account' || tab === 'preferences' || tab === 'billing') {
      setActiveTab(tab);
    }
  }, [searchParams]);
  
  // 表單狀態
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    language: user?.language || language,
  });
  
  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      await authApi.updateProfile({
        name: profileData.name || undefined,
        language: profileData.language,
      });
      
      // 更新語言
      if (profileData.language !== language) {
        setLanguage(profileData.language as Language);
      }
      
      toast.success(t('profile.saved'));
      setSaveMessage(t('profile.saved'));
    } catch (err: any) {
      toast.error(err.message || t('common.failed'));
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  // 未登入時顯示提示
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-white mb-4">
            {t('error.unauthorized')}
          </h2>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-lg"
          >
            {t('nav.login')}
          </button>
        </div>
      </div>
    );
  }
  
  const tabs = [
    { id: 'profile', label: t('settings.profile'), icon: '👤' },
    { id: 'account', label: t('settings.account'), icon: '🔐' },
    { id: 'billing', label: t('settings.billing'), icon: '💳' },
    { id: 'preferences', label: t('settings.preferences'), icon: '⚙️' },
  ];
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 標題 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
            {t('settings.title')}
          </h1>
          <p className="text-gray-400 mt-2">{t('settings.subtitle')}</p>
        </div>
        
        <div className="flex gap-8">
          {/* 側邊導航 */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-2">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  data-testid={tab.id === 'billing' ? 'btn-settings-tab-billing' : undefined}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                      : 'text-gray-400 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <span className="text-xl">{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
            
            {/* 登出按鈕 */}
            <button
              onClick={handleLogout}
              className="w-full mt-8 flex items-center gap-3 px-4 py-3 rounded-lg text-left text-red-400 hover:bg-red-500/10 transition-all duration-200"
            >
              <span className="text-xl">🚪</span>
              <span>{t('nav.logout')}</span>
            </button>
          </div>
          
          {/* 主要內容 */}
          <div className="flex-1">
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl p-8 border border-slate-700/50">
              {/* 個人資料 */}
              {activeTab === 'profile' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold mb-6">{t('settings.profile')}</h2>
                  
                  {/* 頭像 */}
                  <div className="flex items-center gap-6">
                    <div className="w-24 h-24 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 flex items-center justify-center text-3xl font-bold">
                      {user.avatar_url ? (
                        <img src={user.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                      ) : (
                        user.name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()
                      )}
                    </div>
                    <div>
                      <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors">
                        {t('profile.changeAvatar')}
                      </button>
                    </div>
                  </div>
                  
                  {/* 名稱 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('profile.name')}
                    </label>
                    <input
                      type="text"
                      value={profileData.name}
                      onChange={(e) => setProfileData(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  
                  {/* Email（只讀） */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('profile.email')}
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="email"
                        value={user.email}
                        disabled
                        className="flex-1 px-4 py-3 bg-slate-700/30 border border-slate-600 rounded-lg text-gray-400 cursor-not-allowed"
                      />
                      {user.email_verified && (
                        <span className="px-3 py-1 bg-green-500/20 text-green-400 text-sm rounded-full">
                          ✓ {t('auth.verify.success').replace('!', '')}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* 語言 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('profile.language')}
                    </label>
                    <select
                      value={profileData.language}
                      onChange={(e) => setProfileData(prev => ({ ...prev, language: e.target.value as Language }))}
                      className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      {languageOptions.map(option => (
                        <option key={option.code} value={option.code}>
                          {option.icon} {option.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {(dnaStatus === 'skipped' || dnaStatus === 'pending') && (
                    <div className="pt-2 border-t border-slate-700/50">
                      <p className="text-sm text-gray-400 mb-3">{t('alterEgo.settingsHint')}</p>
                      <Link
                        to="/onboarding/alter-ego"
                        data-testid="btn-settings-alter-ego-setup"
                        className="inline-flex items-center px-4 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg text-sm font-medium min-h-[44px]"
                      >
                        {t('alterEgo.settingsCta')}
                      </Link>
                    </div>
                  )}
                  
                  {/* 儲存按鈕 */}
                  <div className="flex items-center gap-4 pt-4">
                    <button
                      onClick={handleSaveProfile}
                      disabled={isSaving}
                      className="px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50"
                    >
                      {isSaving ? t('common.loading') : t('profile.save')}
                    </button>
                    {saveMessage && (
                      <span className="text-green-400">{saveMessage}</span>
                    )}
                  </div>
                </div>
              )}
              
              {activeTab === 'billing' && <CreditsBillingPanel />}

              {/* 帳號設定 */}
              {activeTab === 'account' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold mb-6">{t('settings.account')}</h2>
                  
                  {/* 更改密碼 */}
                  {!user.google_id && (
                    <div className="p-6 bg-slate-700/30 rounded-lg">
                      <h3 className="font-medium mb-4">{t('account.changePassword')}</h3>
                      <div className="space-y-4">
                        <input
                          type="password"
                          placeholder={t('account.currentPassword')}
                          className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        <input
                          type="password"
                          placeholder={t('account.newPassword')}
                          className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        <input
                          type="password"
                          placeholder={t('account.confirmPassword')}
                          className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                        <button className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors">
                          {t('common.save')}
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* 已連結帳號 */}
                  <div className="p-6 bg-slate-700/30 rounded-lg">
                    <h3 className="font-medium mb-4">{t('account.linkedAccounts')}</h3>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                          <svg className="w-6 h-6" viewBox="0 0 24 24">
                            <path
                              fill="#4285F4"
                              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            />
                            <path
                              fill="#34A853"
                              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            />
                            <path
                              fill="#FBBC05"
                              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            />
                            <path
                              fill="#EA4335"
                              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            />
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium">Google</p>
                          {user.google_id ? (
                            <p className="text-sm text-green-400">{t('social.connected')}</p>
                          ) : (
                            <p className="text-sm text-gray-400">{t('social.notConnected')}</p>
                          )}
                        </div>
                      </div>
                      {user.google_id ? (
                        <button className="px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
                          {t('account.unlinkGoogle')}
                        </button>
                      ) : (
                        <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg transition-colors">
                          {t('account.linkGoogle')}
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {/* 刪除帳號 */}
                  <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <h3 className="font-medium text-red-400 mb-2">{t('account.deleteAccount')}</h3>
                    <p className="text-sm text-gray-400 mb-4">{t('account.deleteWarning')}</p>
                    <button className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors">
                      {t('account.deleteAccount')}
                    </button>
                  </div>
                </div>
              )}
              
              {/* 偏好設定 */}
              {activeTab === 'preferences' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold mb-6">{t('settings.preferences')}</h2>
                  
                  {/* 主題 */}
                  <div className="p-6 bg-slate-700/30 rounded-lg">
                    <h3 className="font-medium mb-4">{t('settings.appearance')}</h3>
                    <div className="flex gap-4">
                      <button className="flex-1 p-4 bg-slate-800 border-2 border-purple-500 rounded-lg text-center">
                        <span className="text-2xl mb-2 block">🌙</span>
                        <span className="text-sm">{t('settings.darkMode')}</span>
                      </button>
                      <button className="flex-1 p-4 bg-slate-700/50 border-2 border-transparent rounded-lg text-center opacity-50 cursor-not-allowed">
                        <span className="text-2xl mb-2 block">☀️</span>
                        <span className="text-sm">{t('settings.lightMode')}</span>
                        <span className="text-xs text-gray-500 block mt-1">{t('feature.comingSoon')}</span>
                      </button>
                    </div>
                  </div>
                  
                  {/* 通知 */}
                  <div className="p-6 bg-slate-700/30 rounded-lg">
                    <h3 className="font-medium mb-4">{t('settings.notifications')}</h3>
                    <div className="space-y-4">
                      <label className="flex items-center justify-between">
                        <span className="text-gray-300">{t('settings.emailNotifications')}</span>
                        <input
                          type="checkbox"
                          defaultChecked
                          className="w-5 h-5 rounded bg-slate-700 border-slate-600 text-purple-500 focus:ring-purple-500"
                        />
                      </label>
                      <label className="flex items-center justify-between">
                        <span className="text-gray-300">{t('settings.newFeatures')}</span>
                        <input
                          type="checkbox"
                          defaultChecked
                          className="w-5 h-5 rounded bg-slate-700 border-slate-600 text-purple-500 focus:ring-purple-500"
                        />
                      </label>
                      <label className="flex items-center justify-between">
                        <span className="text-gray-300">{t('settings.systemUpdates')}</span>
                        <input
                          type="checkbox"
                          className="w-5 h-5 rounded bg-slate-700 border-slate-600 text-purple-500 focus:ring-purple-500"
                        />
                      </label>
                    </div>
                  </div>
                  
                  {/* 角色資訊 */}
                  <div className="p-6 bg-slate-700/30 rounded-lg">
                    <h3 className="font-medium mb-4">{t('settings.accountInfo')}</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">{t('settings.accountType')}</span>
                        <span className="text-white">{t(`settings.roles.${user.role}`)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">{t('settings.registrationTime')}</span>
                        <span className="text-white">{new Date(user.created_at).toLocaleDateString()}</span>
                      </div>
                      {user.last_login_at && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">{t('settings.lastLogin')}</span>
                          <span className="text-white">{new Date(user.last_login_at).toLocaleString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// getRoleLabel is now handled inside component with i18n

