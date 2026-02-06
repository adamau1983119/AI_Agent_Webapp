/**
 * Email 驗證頁面
 * Phase 2: 會員系統
 * Style: Lane Crawford 風格 - 高端極簡、黑白為主
 * Font: Cormorant Garamond (display) + Montserrat (sans)
 */
import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { authApi } from '../api/auth';

// 統一品牌設定
const BRAND = {
  name: 'INFLUENCERS',
  slogan: 'AI-POWERED CONTENT CREATION',
};

export default function VerifyEmail() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setStatus('error');
        setMessage(t('auth.verify.error'));
        return;
      }

      try {
        const result = await authApi.verifyEmail(token);
        setStatus('success');
        setMessage(result.message || t('auth.verify.success'));
      } catch (err: any) {
        setStatus('error');
        const errorMsg = err?.response?.data?.detail || err?.message || t('auth.verify.error');
        setMessage(errorMsg);
      }
    };

    verify();
  }, [token]);

  return (
    <div className="min-h-screen bg-[#FAF9F7] flex font-sans">
      {/* 左側裝飾區 - 桌面版顯示 */}
      <div className="hidden lg:flex lg:w-1/2 bg-black items-center justify-center relative overflow-hidden">
        {/* 優雅的幾何裝飾 */}
        <div className="absolute inset-0 opacity-[0.08]">
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] border border-white rotate-45"></div>
        </div>
        
        <div className="relative z-10 text-center px-12">
          <h1 className="text-white font-display text-6xl font-light tracking-[0.4em] uppercase mb-8">
            {BRAND.name}
          </h1>
          <div className="w-24 h-px bg-white/50 mx-auto mb-8"></div>
          <p className="text-white/60 font-sans text-xs tracking-[0.25em] uppercase font-light">
            {BRAND.slogan}
          </p>
        </div>
      </div>

      {/* 右側內容區 */}
      <div className="w-full lg:w-1/2 flex flex-col">
        {/* 頂部導航 */}
        <header className="flex items-center justify-end px-8 py-6">
          <Link
            to="/login"
            className="text-gray-400 hover:text-black transition-colors text-[10px] tracking-[0.15em] uppercase"
          >
            {t('auth.login.title')}
          </Link>
        </header>

        {/* 主要內容區 */}
        <main className="flex-1 flex items-center justify-center px-8 py-8">
          <div className="w-full max-w-sm">
            {/* 移動端 Logo */}
            <div className="lg:hidden text-center mb-12">
              <h1 className="font-display text-3xl font-light tracking-[0.3em] uppercase text-black">
                {BRAND.name}
              </h1>
              <div className="w-16 h-px bg-black mx-auto mt-4 mb-4"></div>
              <p className="text-gray-400 text-[10px] tracking-[0.2em] uppercase font-light">
                {BRAND.slogan}
              </p>
            </div>

            {/* 驗證中 */}
            {status === 'verifying' && (
              <div className="text-center">
                <div className="mb-10">
                  <h2 className="font-display text-2xl tracking-[0.1em] font-light text-black mb-3">
                    {t('auth.verify.title')}
                  </h2>
                  <p className="text-gray-400 text-xs font-light tracking-[0.1em] uppercase">
                    {t('auth.verifying')}
                  </p>
                </div>

                {/* 優雅的載入動畫 */}
                <div className="flex justify-center mb-8">
                  <div className="w-8 h-8 border border-gray-300 border-t-black rounded-full animate-spin"></div>
                </div>

                <div className="w-16 h-px bg-gray-200 mx-auto"></div>
              </div>
            )}

            {/* 驗證成功 */}
            {status === 'success' && (
              <div className="text-center">
                <div className="mb-10">
                  {/* 成功圖標 */}
                  <div className="w-16 h-16 mx-auto mb-8 border border-black flex items-center justify-center">
                    <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>

                  <h2 className="font-display text-2xl tracking-[0.1em] font-light text-black mb-3">
                    {t('auth.verify.success')}
                  </h2>
                  <div className="w-16 h-px bg-gray-200 mx-auto mb-6"></div>
                  <p className="text-gray-400 text-xs font-light tracking-[0.1em]">
                    {t('auth.verify.checkEmail')}
                  </p>
                </div>

                {/* 前往登入按鈕 */}
                <Link
                  to="/login"
                  data-testid="btn-verify-login"
                  className="block w-full py-4 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors duration-300 text-center"
                >
                  {t('auth.login.submit')}
                </Link>

                {/* 底部裝飾線 */}
                <div className="mt-12 flex justify-center">
                  <div className="w-16 h-px bg-gray-200"></div>
                </div>
              </div>
            )}

            {/* 驗證失敗 */}
            {status === 'error' && (
              <div className="text-center">
                <div className="mb-10">
                  {/* 錯誤圖標 */}
                  <div className="w-16 h-16 mx-auto mb-8 border border-red-300 flex items-center justify-center">
                    <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>

                  <h2 className="font-display text-2xl tracking-[0.1em] font-light text-black mb-3">
                    {t('auth.verify.error')}
                  </h2>
                  <div className="w-16 h-px bg-gray-200 mx-auto mb-6"></div>
                  <p className="text-red-500 text-xs font-light tracking-wide">
                    {message}
                  </p>
                </div>

                {/* 重新發送按鈕 */}
                <Link
                  to="/register"
                  data-testid="btn-verify-resend"
                  className="block w-full py-4 bg-black text-white text-[11px] tracking-[0.2em] uppercase hover:bg-gray-900 transition-colors duration-300 text-center mb-4"
                >
                  {t('auth.verify.resend')}
                </Link>

                {/* 分隔線 */}
                <div className="w-full h-px bg-gray-200 my-8"></div>

                {/* 前往登入 */}
                <p className="text-center text-gray-400 text-xs font-light tracking-wide">
                  {t('auth.login.noAccount')}{' '}
                  <Link
                    to="/login"
                    data-testid="link-verify-login"
                    className="text-black underline hover:no-underline transition-all"
                  >
                    {t('auth.login.title')}
                  </Link>
                </p>

                {/* 底部裝飾線 */}
                <div className="mt-12 flex justify-center">
                  <div className="w-16 h-px bg-gray-200"></div>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* 底部版權 - 僅移動端顯示 */}
        <footer className="lg:hidden py-6 text-center">
          <p className="text-gray-400 text-[10px] tracking-[0.15em] uppercase">© 2026 {BRAND.name}</p>
        </footer>
      </div>
    </div>
  );
}
