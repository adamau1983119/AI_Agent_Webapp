/**
 * 服務條款頁面
 * Style: Lane Crawford 風格 - 高端極簡
 * 支援多語言：zh-TW, en, ja
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
        <span className="font-display text-lg tracking-[0.2em] uppercase">{t('brand.name')}</span>
        <div className="w-16"></div>
      </header>
      
      {/* 內容區 */}
      <main className="max-w-3xl mx-auto px-8 py-16">
        <h1 className="font-display text-3xl tracking-[0.15em] font-light text-black mb-4 text-center">
          {t('legal.terms.title')}
        </h1>
        <p className="text-gray-400 text-xs tracking-[0.15em] uppercase text-center mb-12">
          {t('legal.terms.subtitle')}
        </p>
        
        <div className="w-16 h-px bg-black mx-auto mb-12"></div>
        
        <div className="prose prose-sm max-w-none text-gray-600 font-light leading-relaxed space-y-8">
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.terms.section1.title')}</h2>
            <p>{t('legal.terms.section1.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.terms.section2.title')}</h2>
            <p>{t('legal.terms.section2.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.terms.section3.title')}</h2>
            <p>{t('legal.terms.section3.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.terms.section4.title')}</h2>
            <p>{t('legal.terms.section4.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.terms.section5.title')}</h2>
            <p>{t('legal.terms.section5.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.terms.section6.title')}</h2>
            <p>{t('legal.terms.section6.content')}</p>
          </section>
        </div>
        
        <div className="mt-16 text-center">
          <p className="text-gray-400 text-xs tracking-wide">
            {t('legal.terms.lastUpdate')}
          </p>
        </div>
      </main>
    </div>
  );
}
