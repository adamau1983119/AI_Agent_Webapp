/**
 * 隱私政策頁面
 * Style: Lane Crawford 風格 - 高端極簡
 * 支援多語言：zh-TW, en, ja
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
        <span className="font-display text-lg tracking-[0.2em] uppercase">{t('brand.name')}</span>
        <div className="w-16"></div>
      </header>
      
      {/* 內容區 */}
      <main className="max-w-3xl mx-auto px-8 py-16">
        <h1 className="font-display text-3xl tracking-[0.15em] font-light text-black mb-4 text-center">
          {t('legal.privacy.title')}
        </h1>
        <p className="text-gray-400 text-xs tracking-[0.15em] uppercase text-center mb-12">
          {t('legal.privacy.subtitle')}
        </p>
        
        <div className="w-16 h-px bg-black mx-auto mb-12"></div>
        
        <div className="prose prose-sm max-w-none text-gray-600 font-light leading-relaxed space-y-8">
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section1.title')}</h2>
            <p>{t('legal.privacy.section1.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section2.title')}</h2>
            <p>{t('legal.privacy.section2.content')}</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>{t('legal.privacy.section2.list1')}</li>
              <li>{t('legal.privacy.section2.list2')}</li>
              <li>{t('legal.privacy.section2.list3')}</li>
              <li>{t('legal.privacy.section2.list4')}</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section3.title')}</h2>
            <p>{t('legal.privacy.section3.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section4.title')}</h2>
            <p>{t('legal.privacy.section4.content')}</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>{t('legal.privacy.section4.list1')}</li>
              <li>{t('legal.privacy.section4.list2')}</li>
              <li>{t('legal.privacy.section4.list3')}</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section5.title')}</h2>
            <p>{t('legal.privacy.section5.content')}</p>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section6.title')}</h2>
            <p>{t('legal.privacy.section6.content')}</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>{t('legal.privacy.section6.list1')}</li>
              <li>{t('legal.privacy.section6.list2')}</li>
              <li>{t('legal.privacy.section6.list3')}</li>
              <li>{t('legal.privacy.section6.list4')}</li>
            </ul>
          </section>
          
          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section7.title')}</h2>
            <p>{t('legal.privacy.section7.content')}</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>{t('legal.privacy.section7.list1')}</li>
              <li>{t('legal.privacy.section7.list2')}</li>
              <li>{t('legal.privacy.section7.list3')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-black font-normal text-lg tracking-wide mb-4">{t('legal.privacy.section8.title')}</h2>
            <p>{t('legal.privacy.section8.content')}</p>
          </section>
        </div>
        
        <div className="mt-16 text-center">
          <p className="text-gray-400 text-xs tracking-wide">
            {t('legal.privacy.lastUpdate')}
          </p>
        </div>
      </main>
    </div>
  );
}
