/**
 * 隱私政策頁面
 * Style: Lane Crawford 風格 - 高端極簡
 */
import { Link } from 'react-router-dom';
import { useTranslation } from '../i18n';

export default function Privacy() {
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
          隱私政策
        </h1>
        <p className="text-gray-400 text-xs tracking-[0.15em] uppercase text-center mb-12">
          PRIVACY POLICY
        </p>
        
        <div className="w-16 h-px bg-black mx-auto mb-12"></div>
        
        <div className="prose prose-sm max-w-none text-gray-600 font-light leading-relaxed space-y-8">
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">1. 資料收集</h2>
            <p>
              我們收集您提供的資訊，包括但不限於：電子郵件地址、姓名、語言偏好。我們也會自動收集使用數據，如瀏覽記錄和設備資訊。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">2. 資料使用</h2>
            <p>
              我們使用收集的資料來：
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>提供和維護服務</li>
              <li>個性化您的體驗</li>
              <li>改進我們的 AI 模型</li>
              <li>與您溝通服務相關事宜</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">3. 資料保護</h2>
            <p>
              我們採用業界標準的安全措施來保護您的個人資料，包括加密傳輸和安全存儲。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">4. 資料分享</h2>
            <p>
              我們不會出售您的個人資料。我們可能在以下情況下分享您的資料：
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>經您同意</li>
              <li>法律要求</li>
              <li>與服務提供商合作（受保密協議約束）</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">5. Cookie 使用</h2>
            <p>
              我們使用 Cookie 和類似技術來記住您的偏好設定和改善用戶體驗。
            </p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">6. 您的權利</h2>
            <p>
              您有權：
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>訪問您的個人資料</li>
              <li>更正不準確的資料</li>
              <li>請求刪除您的資料</li>
              <li>撤回同意</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">7. 聯繫我們</h2>
            <p>
              如有任何隱私相關問題，請聯繫：privacy@influencers.ai
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

