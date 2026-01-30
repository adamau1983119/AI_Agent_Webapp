/**
 * OAuth 回調頁面
 * Phase 2: 會員系統
 * 處理 Google OAuth 登入後的 Token
 */
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useTranslation } from '../i18n';

export default function OAuthCallback() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { handleOAuthCallback, error } = useAuthStore();
  const [isProcessing, setIsProcessing] = useState(true);
  
  useEffect(() => {
    const processCallback = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        // 沒有 Token，重定向到登入頁面
        navigate('/login?error=no_token');
        return;
      }
      
      try {
        await handleOAuthCallback(token);
        // 成功後重定向到首頁
        navigate('/');
      } catch (err) {
        // 失敗後重定向到登入頁面
        navigate('/login?error=oauth_failed');
      } finally {
        setIsProcessing(false);
      }
    };
    
    processCallback();
  }, [searchParams, handleOAuthCallback, navigate]);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="text-center">
        {isProcessing ? (
          <>
            <div className="w-16 h-16 mx-auto mb-6">
              <svg className="animate-spin w-full h-full text-purple-400" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">
              正在處理登入...
            </h2>
            <p className="text-gray-400">請稍候，正在驗證您的帳號</p>
          </>
        ) : error ? (
          <>
            <div className="w-16 h-16 mx-auto mb-6 bg-red-500/20 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">
              {t('auth.login.error')}
            </h2>
            <p className="text-gray-400 mb-6">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-lg transition-all duration-200"
            >
              {t('auth.forgot.backToLogin')}
            </button>
          </>
        ) : null}
      </div>
    </div>
  );
}

