/**
 * 服務條款頁面
 * Style: Lane Crawford 風格 - 高端極簡
 */
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n';

export default function Terms() {
  const { t } = useTranslation();
  
  return (
    <div className="min-h-screen bg-[#FAF9F7] font-sans">
      {/* 頂部導航 */}
      <header className="flex items-center justify-between px-8 py-6 border-b border-gray-100">
        <Link 
          to="/register"
          className="text-gray-400 hover:text-black transition-colors text-[10px] tracking-[0.15em] uppercase"
        >
          ← {t('common.back')}
        </Link>
        <span className="font-display text-lg tracking-[0.2em] uppercase">INFLUENCERS</span>
        <div className="w-16"></div>
      </header>
      
      {/* 內容區 */}
      <main className="max-w-3xl mx-auto px-8 py-16">
        <h1 className="font-display text-3xl tracking-[0.15em] font-light text-black mb-4 text-center">
          服務條款
        </h1>
        <p className="text-gray-400 text-xs tracking-[0.15em] uppercase text-center mb-12">
          TERMS OF SERVICE
        </p>
        
        <div className="w-16 h-px bg-black mx-auto mb-12"></div>
        
        <div className="prose prose-sm max-w-none text-gray-600 font-light leading-relaxed space-y-8">
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">1. 服務說明</h2>
            <p>
              Influencers AI（以下簡稱「本服務」）是一個 AI 驅動的內容創作平台，旨在幫助用戶生成高品質的社群媒體內容。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">2. 帳號註冊</h2>
            <p>
              您必須提供真實、準確的個人資訊來註冊帳號。您有責任保護您的帳號安全，並對帳號下的所有活動負責。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">3. 內容所有權</h2>
            <p>
              使用本服務生成的內容，其所有權歸您所有。但您同意授予本服務使用這些內容來改進 AI 模型的權利。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">4. 使用限制</h2>
            <p>
              您同意不會使用本服務來創建違法、有害、威脅性、辱罵性、騷擾性、誹謗性或其他令人反感的內容。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">5. 服務變更</h2>
            <p>
              本服務保留隨時修改或終止服務的權利，恕不另行通知。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">6. 免責聲明</h2>
            <p>
              本服務按「現狀」提供，不作任何明示或暗示的保證。對於因使用本服務而產生的任何損失，本服務不承擔責任。
            </p>
          </section>
        </div>
        
        <div className="mt-16 text-center">
          <p className="text-gray-400 text-xs tracking-wide">
            最後更新：2026 年 2 月
          </p>
        </div>
      </main>
    </div>
  );
}

