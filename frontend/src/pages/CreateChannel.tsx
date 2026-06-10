/**
 * 建立頻道頁面
 * Phase 3: 內容功能
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n';
import { useAuthStore } from '../stores/authStore';
import {
  channelsApi,
  ChannelCategory,
  ChannelRegion,
  ChannelCreateRequest,
  ChannelFeedEntry,
  categoryI18nKeys,
  regionI18nKeys,
  categoryIcons,
} from '../api/channels';
import toast from 'react-hot-toast';
import { APIError } from '../api/errors';

const MAX_STEP2_SELECTED_FEEDS = 10;

/** 依後端 429 body.detail.code 選 i18n（見 feed_validate_rate_limit.py） */
function rateLimitToastI18nKey(err: unknown): string {
  const code = err instanceof APIError ? err.code : undefined;
  if (code === 'feed_search_rate_limit') return 'channels.feedSearch.rateLimited';
  if (code === 'feed_validate_rate_limit_minute' || code === 'feed_validate_rate_limit_hour') {
    return 'channels.feedValidate.rateLimited';
  }
  return 'channels.rateLimit.generic';
}

/** assist／wizard 429 或網路／逾時時選 i18n（Phase C） */
function assistFailureI18nKey(err: unknown): string {
  if (err instanceof APIError) {
    if (err.status === 429) {
      return rateLimitToastI18nKey(err);
    }
  }
  const msg = err instanceof Error ? err.message : '';
  if (
    msg.includes('timeout') ||
    msg.includes('Failed to fetch') ||
    msg.includes('NetworkError') ||
    msg.includes('Request timeout')
  ) {
    return 'channels.assist.networkOrTimeout';
  }
  return 'channels.assist.failed';
}

function mergeFeedsByUrl(primary: ChannelFeedEntry[], secondary: ChannelFeedEntry[]): ChannelFeedEntry[] {
  const seen = new Set<string>();
  const out: ChannelFeedEntry[] = [];
  for (const list of [primary, secondary]) {
    for (const s of list) {
      const u = (s.url || '').trim();
      if (!u || seen.has(u)) continue;
      seen.add(u);
      out.push({
        name: s.name || '',
        url: u,
        role: s.role || '',
      });
    }
  }
  return out;
}

type AssistChatTurn = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

function CreateChannelSummaryPanel(props: {
  t: (key: string, options?: Record<string, string>) => string;
  name: string;
  description: string;
  category: ChannelCategory | null;
  region: ChannelRegion;
  step: number;
  selectedCount: number;
  maxFeeds: number;
}) {
  const { t, name, description, category, region, step, selectedCount, maxFeeds } = props;
  return (
    <div
      className="mb-6 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800/80 p-4 shadow-sm"
      data-testid="panel-channels-create-summary"
    >
      <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 mb-3">{t('channels.phaseB.summaryTitle')}</p>
      <dl className="space-y-2 text-sm text-gray-700 dark:text-gray-200">
        <div>
          <dt className="text-xs text-gray-500">{t('channels.channelName')}</dt>
          <dd className="font-medium break-words">{name.trim() || t('channels.phaseB.summaryEmpty')}</dd>
        </div>
        <div>
          <dt className="text-xs text-gray-500">{t('channels.channelDescription')}</dt>
          <dd className="break-words whitespace-pre-line">{description.trim() || t('channels.phaseB.summaryEmpty')}</dd>
        </div>
        <div>
          <dt className="text-xs text-gray-500">{t('channels.phaseB.summaryCategory')}</dt>
          <dd>{category ? t(categoryI18nKeys[category]) : t('channels.phaseB.summaryCategoryUnset')}</dd>
        </div>
        <div>
          <dt className="text-xs text-gray-500">{t('channels.phaseB.summaryRegion')}</dt>
          <dd>{t(regionI18nKeys[region])}</dd>
        </div>
        <div>
          <dt className="text-xs text-gray-500">{t('channels.phaseB.summaryFeeds')}</dt>
          <dd>
            {step < 2
              ? t('channels.phaseB.summaryFeedsHint')
              : t('channels.phaseB.summaryFeedsCount', {
                  count: String(selectedCount),
                  max: String(maxFeeds),
                })}
          </dd>
        </div>
      </dl>
    </div>
  );
}

function CreateChannelStepNav(props: {
  step: number;
  t: (key: string) => string;
}) {
  const { step, t } = props;
  return (
    <nav aria-label={t('channels.phaseC.stepsNavAria')} className="mb-8">
      <ol className="flex items-center justify-center list-none p-0 m-0">
        {[1, 2, 3].map((s) => (
          <li key={s} className="flex items-center" aria-current={step === s ? 'step' : undefined}>
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-medium transition-all ${
                s < step
                  ? 'bg-green-500 text-white'
                  : s === step
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
              }`}
            >
              {s < step ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                s
              )}
            </div>
            {s < 3 && (
              <div
                className={`w-20 h-1 ${s < step ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'}`}
                aria-hidden="true"
              />
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

const categories: { value: ChannelCategory; label: string; icon: string }[] = [
  { value: 'fashion', label: categoryI18nKeys.fashion, icon: categoryIcons.fashion },
  { value: 'food', label: categoryI18nKeys.food, icon: categoryIcons.food },
  { value: 'trend', label: categoryI18nKeys.trend, icon: categoryIcons.trend },
  { value: 'finance', label: categoryI18nKeys.finance, icon: categoryIcons.finance },
  { value: 'sports', label: categoryI18nKeys.sports, icon: categoryIcons.sports },
  { value: 'tech', label: categoryI18nKeys.tech, icon: categoryIcons.tech },
  { value: 'entertainment', label: categoryI18nKeys.entertainment, icon: categoryIcons.entertainment },
  { value: 'other', label: categoryI18nKeys.other, icon: categoryIcons.other },
];

const regions: { value: ChannelRegion; label: string }[] = [
  { value: 'global', label: regionI18nKeys.global },
  { value: 'hong_kong', label: regionI18nKeys.hong_kong },
  { value: 'taiwan', label: regionI18nKeys.taiwan },
  { value: 'japan', label: regionI18nKeys.japan },
  { value: 'korea', label: regionI18nKeys.korea },
  { value: 'china', label: regionI18nKeys.china },
  { value: 'usa', label: regionI18nKeys.usa },
  { value: 'uk', label: regionI18nKeys.uk },
];

export default function CreateChannel() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  // 表單狀態
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [category, setCategory] = useState<ChannelCategory | null>(null);
  const [region, setRegion] = useState<ChannelRegion>('global');
  const [customKeywords, setCustomKeywords] = useState<string[]>([]);
  const [keywordInput, setKeywordInput] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  /** Step 2：候選池（系統預設 + AI 推薦合併）；建立時送出的選取以 selectedReferenceSourceUrls 為準 */
  const [step2PoolSources, setStep2PoolSources] = useState<ChannelFeedEntry[]>([]);
  const [step2PoolLoading, setStep2PoolLoading] = useState(false);
  const [step2PoolError, setStep2PoolError] = useState(false);
  const [step2PasteUrl, setStep2PasteUrl] = useState('');
  const [step2PasteValidating, setStep2PasteValidating] = useState(false);
  const [step2PastedValidated, setStep2PastedValidated] = useState<{
    name: string;
    url: string;
  } | null>(null);
  const [step2WhitelistQuery, setStep2WhitelistQuery] = useState('');
  const [step2WhitelistSearching, setStep2WhitelistSearching] = useState(false);
  const [step3Wizard, setStep3Wizard] = useState<{
    suggested_channel_name: string | null;
    suggested_channel_description: string | null;
  } | null>(null);
  /** 最近一次 assist 回傳之 AI 建議命名（#32/#33） */
  const [assistAiNaming, setAssistAiNaming] = useState<{ name: string; desc: string } | null>(null);
  const [selectedReferenceSourceUrls, setSelectedReferenceSourceUrls] = useState<Set<string>>(() => new Set());
  /** AI「確認應用」時併入候選池頂部（手動從 Step 1 進 Step 2 時清空） */
  const assistPoolBoostRef = useRef<ChannelFeedEntry[]>([]);
  /** 上一輪 assist 已展示之推薦 URL，供「再分析」時 exclude，換一批白名單候選 */
  const assistShownSourceUrlsRef = useRef<string[]>([]);

  // AI 助手狀態（E 階段 B：進頁預設開啟助手為主舞台）
  const [showAssist, setShowAssist] = useState(true);
  const [assistInput, setAssistInput] = useState('');
  const [isAssisting, setIsAssisting] = useState(false);
  const [assistResult, setAssistResult] = useState<{
    category: string | null;
    region: string | null;
    keywords: string[];
    confidence: number;
    clarification_needed: boolean;
    clarification_question: string | null;
    recommended_sources: Array<{ name: string; url: string; role: string }>;
    suggested_channel_name: string | null;
    suggested_channel_description: string | null;
  } | null>(null);
  /** 多輪對話紀錄（畫面保留 + 送後端上下文） */
  const [assistHistory, setAssistHistory] = useState<AssistChatTurn[]>([]);
  const assistChatEndRef = useRef<HTMLDivElement>(null);

  /** 後端精靈結構化選項（檢索 MVP：RSS 白名單）；Step 1＝類別，Step 2＝地區＋扣已選後之 feed */
  const [guidedOptions, setGuidedOptions] = useState<{
    step: number;
    retrieval_mvp: string;
    quick_options: Array<{ kind: 'category' | 'region'; value: string; label_key: string }>;
    feed_options: Array<{ kind: 'feed'; name: string; url: string; role: string }>;
    suggested_channel_name?: string | null;
    suggested_channel_description?: string | null;
  } | null>(null);
  const [guidedLoading, setGuidedLoading] = useState(false);
  /** Phase C：精靈載入失敗時顯示助手內重試 */
  const [guidedLoadError, setGuidedLoadError] = useState(false);
  const [guidedRetryToken, setGuidedRetryToken] = useState(0);
  /** Phase C：分析失敗時助手內橫幅（與 toast 並列） */
  const [assistRequestError, setAssistRequestError] = useState<string | null>(null);
  /** Phase C：表單區（RSS 池／白名單搜尋／驗證／建立）錯誤同步顯示於助手內 */
  const [feedActionBanner, setFeedActionBanner] = useState<string | null>(null);
  const [mobileSummaryOpen, setMobileSummaryOpen] = useState(false);
  /** Phase B：大螢幕且助手開啟時，表單預設收合（進階）；關閉助手時一律展開 */
  const [desktopFormExpanded, setDesktopFormExpanded] = useState(false);
  const showAssistRef = useRef(showAssist);
  const mobileSummaryDrawerRef = useRef<HTMLDivElement>(null);
  const mobileSummaryTriggerRef = useRef<HTMLButtonElement>(null);

  const selectedUrlsSignature = [...selectedReferenceSourceUrls].sort().join('|');
  const customKeywordsSig = customKeywords.join('\u0001');

  useEffect(() => {
    showAssistRef.current = showAssist;
  }, [showAssist]);

  useEffect(() => {
    if (!showAssist) {
      setDesktopFormExpanded(true);
    } else {
      setDesktopFormExpanded(false);
    }
  }, [showAssist]);

  /** Step 3 須使用表單送出：大螢幕＋助手開啟時自動展開，避免收合狀態無法按「建立」 */
  useEffect(() => {
    if (showAssist && step === 3) {
      setDesktopFormExpanded(true);
    }
  }, [showAssist, step]);

  useEffect(() => {
    if (!showAssist) return;
    assistChatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [showAssist, assistHistory, isAssisting]);

  useEffect(() => {
    setFeedActionBanner(null);
    setMobileSummaryOpen(false);
  }, [step]);

  useEffect(() => {
    if (!mobileSummaryOpen || !showAssist) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileSummaryOpen(false);
        window.setTimeout(() => mobileSummaryTriggerRef.current?.focus(), 0);
        return;
      }
      if (e.key !== 'Tab') return;
      const drawer = mobileSummaryDrawerRef.current;
      if (!drawer) return;
      const nodes = drawer.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      const list = Array.from(nodes).filter((el) => drawer.contains(el));
      if (list.length === 0) return;
      const first = list[0];
      const last = list[list.length - 1];
      const active = document.activeElement as Node | null;
      if (e.shiftKey) {
        if (active === first || !drawer.contains(active as Node)) {
          e.preventDefault();
          last.focus();
        }
      } else if (active === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [mobileSummaryOpen, showAssist]);

  useEffect(() => {
    if (!showAssist) {
      setGuidedOptions(null);
      setGuidedLoadError(false);
      setAssistRequestError(null);
      setFeedActionBanner(null);
      setMobileSummaryOpen(false);
      return;
    }
    let cancelled = false;
    setGuidedLoadError(false);
    setGuidedLoading(true);
    (async () => {
      try {
        const lang = localStorage.getItem('language') || 'zh-TW';
        const data =
          step === 3 && category
            ? await channelsApi.getAssistWizardOptions({
                step: 3,
                category,
                region,
                language: lang,
                customKeywords: customKeywords,
              })
            : step === 2 && category
            ? await channelsApi.getAssistWizardOptions({
                step: 2,
                category,
                region,
                excludeUrls: Array.from(selectedReferenceSourceUrls),
                language: lang,
              })
            : await channelsApi.getAssistWizardOptions({ step: 1, language: lang });
        if (!cancelled) {
          setGuidedOptions(data);
          setGuidedLoadError(false);
        }
      } catch {
        if (!cancelled) {
          setGuidedOptions(null);
          setGuidedLoadError(true);
          toast.error(t('channels.guided.loadFailed'));
        }
      } finally {
        if (!cancelled) setGuidedLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [
    showAssist,
    step,
    category,
    region,
    selectedUrlsSignature,
    customKeywordsSig,
    guidedRetryToken,
    t,
  ]);

  useEffect(() => {
    if (step !== 3 || !category) {
      setStep3Wizard(null);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const lang = localStorage.getItem('language') || 'zh-TW';
        const data = await channelsApi.getAssistWizardOptions({
          step: 3,
          category,
          region,
          language: lang,
          customKeywords: customKeywords,
        });
        if (!cancelled) setStep3Wizard(data);
      } catch {
        if (!cancelled) setStep3Wizard(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [step, category, region, customKeywordsSig]);

  useEffect(() => {
    if (step !== 2 || !category) return;
    let cancelled = false;
    setStep2PoolLoading(true);
    setStep2PoolError(false);
    (async () => {
      try {
        const { sources } = await channelsApi.getDefaultRssSources(category, region);
        if (cancelled) return;
        const boost = assistPoolBoostRef.current;
        const merged = mergeFeedsByUrl(boost, sources);
        setStep2PoolSources(merged);
        if (showAssistRef.current) setFeedActionBanner(null);
        setSelectedReferenceSourceUrls((prev) => {
          const poolUrls = new Set(merged.map((s) => s.url));
          const boostUrls = boost.map((s) => s.url).filter((u) => poolUrls.has(u));
          if (boostUrls.length > 0) {
            return new Set(boostUrls.slice(0, MAX_STEP2_SELECTED_FEEDS));
          }
          const kept = [...prev].filter((u) => poolUrls.has(u)).slice(0, MAX_STEP2_SELECTED_FEEDS);
          if (kept.length > 0) return new Set(kept);
          const n = Math.min(MAX_STEP2_SELECTED_FEEDS, merged.length);
          return new Set(merged.slice(0, n).map((s) => s.url));
        });
      } catch {
        if (!cancelled) {
          setStep2PoolError(true);
          setStep2PoolSources([]);
          if (showAssistRef.current) {
            setFeedActionBanner(t('channels.step2.poolLoadError'));
          }
        }
      } finally {
        if (!cancelled) setStep2PoolLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [step, category, region]);
  
  // 未登入
  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }
  
  // 添加關鍵字
  const addKeyword = () => {
    const keyword = keywordInput.trim();
    if (keyword && !customKeywords.includes(keyword) && customKeywords.length < 5) {
      setCustomKeywords([...customKeywords, keyword]);
      setKeywordInput('');
    }
  };
  
  // 移除關鍵字
  const removeKeyword = (index: number) => {
    setCustomKeywords(customKeywords.filter((_, i) => i !== index));
  };
  
  // 處理按 Enter
  const handleKeywordKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addKeyword();
    }
  };
  
  // AI 助手：快捷按鈕點擊（類別）
  // 若已選「非全球」地區，輸入框改為類別+地區一句話，避免先選類別再選地區時被覆寫成只剩地區。
  const handleQuickCategoryClick = (cat: ChannelCategory) => {
    setCategory(cat);
    const categoryText = t(categoryI18nKeys[cat]);
    const regionText = t(regionI18nKeys[region]);
    if (region !== 'global') {
      setAssistInput(t('channels.assist.quickPreset', { category: categoryText, region: regionText }));
    } else {
      setAssistInput(t('channels.assist.quickCategory', { category: categoryText }));
    }
  };

  // AI 助手：快捷按鈕點擊（地區）
  const handleQuickRegionClick = (reg: ChannelRegion) => {
    setRegion(reg);
    const regionText = t(regionI18nKeys[reg]);
    const categoryText = category ? t(categoryI18nKeys[category]) : '';
    if (category !== null) {
      setAssistInput(t('channels.assist.quickPreset', { category: categoryText, region: regionText }));
    } else {
      setAssistInput(t('channels.assist.quickRegion', { region: regionText }));
    }
  };

  // AI 助手：預設組合快捷按鈕
  const quickPresets = [
    { key: 'japanFashion', category: 'fashion' as ChannelCategory, region: 'japan' as ChannelRegion, icon: '🇯🇵👗' },
    { key: 'hkFood', category: 'food' as ChannelCategory, region: 'hong_kong' as ChannelRegion, icon: '🇭🇰🍜' },
    { key: 'globalTrend', category: 'trend' as ChannelCategory, region: 'global' as ChannelRegion, icon: '🌍📊' },
    { key: 'taiwanTech', category: 'tech' as ChannelCategory, region: 'taiwan' as ChannelRegion, icon: '🇹🇼💻' },
    { key: 'koreaEntertainment', category: 'entertainment' as ChannelCategory, region: 'korea' as ChannelRegion, icon: '🇰🇷🎬' },
  ];

  // AI 助手：預設組合點擊（插入翻譯後描述，供後端解析）
  const handlePresetClick = (preset: (typeof quickPresets)[0]) => {
    setCategory(preset.category);
    setRegion(preset.region);
    const categoryText = t(categoryI18nKeys[preset.category]);
    const regionText = t(regionI18nKeys[preset.region]);
    setAssistInput(
      t('channels.assist.quickPreset', { category: categoryText, region: regionText })
    );
  };

  // AI 助手：處理用戶輸入（多輪：保留對話並附帶 conversation_history）
  const handleAssistSubmit = async () => {
    if (!assistInput.trim()) {
      toast.error(t('channels.assist.inputRequired'));
      return;
    }

    const userText = assistInput.trim();
    const conversationHistory = assistHistory.map(({ role, content }) => ({ role, content }));
    if (conversationHistory.length === 0) {
      assistShownSourceUrlsRef.current = [];
    }
    const excludeSet = new Set<string>();
    selectedReferenceSourceUrls.forEach((u) => excludeSet.add(u));
    assistShownSourceUrlsRef.current.forEach((u) => excludeSet.add(u));
    const excludeUrls = [...excludeSet].slice(0, 50);

    const userId = `u-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

    setAssistHistory((prev) => [...prev, { id: userId, role: 'user', content: userText }]);
    setAssistInput('');
    setIsAssisting(true);
    setAssistResult(null);
    setAssistRequestError(null);
    setFeedActionBanner(null);

    let replyText = '';

    try {
      const userLanguage = localStorage.getItem('language') || 'zh-TW';
      const result = await channelsApi.assistChannel(
        userText,
        userLanguage,
        conversationHistory,
        excludeUrls
      );
      setAssistResult(result);

      if (result.recommended_sources?.length) {
        assistShownSourceUrlsRef.current = result.recommended_sources
          .map((s) => (s.url || '').trim())
          .filter(Boolean);
      }

      if (result.clarification_needed) {
        setAssistAiNaming(null);
      } else if (
        result.confidence >= 0.7 &&
        result.category &&
        result.region &&
        (result.suggested_channel_name?.trim() || result.suggested_channel_description?.trim())
      ) {
        setAssistAiNaming({
          name: (result.suggested_channel_name || '').trim().slice(0, 50),
          desc: (result.suggested_channel_description || '').trim().slice(0, 200),
        });
      }

      if (result.clarification_needed) {
        replyText = result.clarification_question || t('channels.assist.clarificationDefault');
      } else if (result.confidence >= 0.7 && result.category && result.region) {
        const categoryName = t(categoryI18nKeys[result.category as ChannelCategory]);
        const regionName = t(regionI18nKeys[result.region as ChannelRegion]);
        replyText =
          result.keywords.length > 0
            ? t('channels.assist.responseWithKeywords', {
                category: categoryName,
                region: regionName,
                keywords: result.keywords.join(', '),
              })
            : t('channels.assist.responseWithoutKeywords', {
                category: categoryName,
                region: regionName,
              });

        setCategory(result.category as ChannelCategory);
        setRegion(result.region as ChannelRegion);
        if (result.keywords.length > 0) {
          setCustomKeywords(result.keywords);
        }
        toast.success(t('channels.assist.autoFilled'));
      } else if (result.confidence >= 0.5) {
        const categoryName = result.category ? t(categoryI18nKeys[result.category as ChannelCategory]) : '-';
        const regionName = result.region ? t(regionI18nKeys[result.region as ChannelRegion]) : '-';
        replyText = t('channels.assist.responseWithoutKeywords', {
          category: categoryName,
          region: regionName,
        });
      } else {
        replyText = t('channels.assist.lowConfidence');
      }
    } catch (err: unknown) {
      const key = assistFailureI18nKey(err);
      const msg = t(key as any);
      setAssistRequestError(msg);
      toast.error(msg);
      replyText = msg;

      if (process.env.NODE_ENV === 'development') {
        console.error('AI Assistant Error:', err);
      }
    } finally {
      const assistantId = `a-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
      setAssistHistory((prev) => [...prev, { id: assistantId, role: 'assistant', content: replyText }]);
      setIsAssisting(false);
    }
  };
  
  // AI 助手：確認並應用結果 → 先進 Step 2（推薦來源為核心），使用者按下一步再到 Step 3
  const handleAssistConfirm = () => {
    if (assistResult && assistResult.category && assistResult.region) {
      const rec = assistResult.recommended_sources || [];
      assistPoolBoostRef.current = rec.map((s) => ({
        name: s.name || '',
        url: (s.url || '').trim(),
        role: s.role || '',
      }));
      setCategory(assistResult.category as ChannelCategory);
      setRegion(assistResult.region as ChannelRegion);
      if (assistResult.keywords.length > 0) {
        setCustomKeywords(assistResult.keywords);
      }
      setStep(2);
      setShowAssist(false);
      setAssistInput('');
      setAssistResult(null);
      setAssistHistory([]);
      setAssistRequestError(null);
      setFeedActionBanner(null);
      toast.success(t('channels.assist.applied'));
    }
  };
  
  // AI 助手：關閉
  const handleAssistClose = () => {
    assistPoolBoostRef.current = [];
    assistShownSourceUrlsRef.current = [];
    setAssistAiNaming(null);
    setAssistRequestError(null);
    setFeedActionBanner(null);
    setShowAssist(false);
    setAssistInput('');
    setAssistResult(null);
    setAssistHistory([]);
  };
  
  // AI 助手：重置對話
  const handleAssistReset = () => {
    assistShownSourceUrlsRef.current = [];
    setAssistAiNaming(null);
    setAssistRequestError(null);
    setFeedActionBanner(null);
    setAssistInput('');
    setAssistResult(null);
    setAssistHistory([]);
  };

  const handleStep2WhitelistSearch = async () => {
    const q = step2WhitelistQuery.trim();
    if (!q) {
      toast.error(t('channels.step2.whitelistSearchRequired'));
      return;
    }
    setStep2WhitelistSearching(true);
    try {
      const { results } = await channelsApi.searchWhitelistFeeds(q, 30);
      if (!results.length) {
        toast(t('channels.step2.whitelistNoResults'));
        return;
      }
      const asFeeds: ChannelFeedEntry[] = results.map((r) => ({
        name: r.name || 'RSS',
        url: r.url.trim(),
        role: r.role || '',
      }));
      setStep2PoolSources((prev) => mergeFeedsByUrl(asFeeds, prev));
      toast.success(t('channels.step2.whitelistSearchOk', { count: String(results.length) }));
      if (showAssist) setFeedActionBanner(null);
    } catch (err: unknown) {
      const st = err instanceof APIError ? err.status : undefined;
      let msg: string;
      if (st === 429) {
        msg = t(rateLimitToastI18nKey(err));
      } else if (err instanceof APIError) {
        msg = err.message;
      } else if (err && typeof err === 'object' && 'message' in err && typeof (err as { message?: unknown }).message === 'string') {
        msg = (err as { message: string }).message;
      } else {
        msg = t('channels.step2.whitelistSearchFailed');
      }
      toast.error(msg);
      if (showAssist) setFeedActionBanner(msg);
    } finally {
      setStep2WhitelistSearching(false);
    }
  };

  const handleStep2ValidatePastedUrl = async () => {
    const raw = step2PasteUrl.trim();
    if (!raw) {
      toast.error(t('channels.step2.pasteUrlRequired'));
      return;
    }
    setStep2PasteValidating(true);
    setStep2PastedValidated(null);
    try {
      const res = await channelsApi.validateFeedUrl(raw);
      if (res.valid) {
        const name = (res.suggested_name || res.title || 'RSS').slice(0, 120);
        const url = raw.split(/\s/)[0].trim();
        setStep2PastedValidated({ name, url });
        toast.success(t('channels.feedValidate.success'));
        if (showAssist) setFeedActionBanner(null);
      } else {
        const code = res.error_code || 'unknown';
        const msgKey = `channels.feedValidate.${code}` as const;
        const msg = t(msgKey as any);
        const resolved = msg !== msgKey ? msg : t('channels.feedValidate.unknown');
        toast.error(resolved);
        if (showAssist) setFeedActionBanner(resolved);
      }
    } catch (err: unknown) {
      const st = err instanceof APIError ? err.status : undefined;
      let msg: string;
      if (st === 429) {
        msg = t(rateLimitToastI18nKey(err));
      } else if (err instanceof APIError) {
        msg = err.message;
      } else if (err && typeof err === 'object' && 'message' in err && typeof (err as { message?: unknown }).message === 'string') {
        msg = (err as { message: string }).message;
      } else {
        msg = t('channels.feedValidate.unknown');
      }
      toast.error(msg);
      if (showAssist) setFeedActionBanner(msg);
    } finally {
      setStep2PasteValidating(false);
    }
  };
  
  // 提交表單
  const handleSubmit = async () => {
    if (!name.trim()) {
      toast.error(t('channels.validation.nameRequired'));
      return;
    }
    
    if (!category) {
      toast.error(t('channels.validation.categoryRequired'));
      return;
    }
    
    if (category === 'other' && customKeywords.length === 0) {
      toast.error(t('channels.validation.keywordsRequired'));
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const selectedFeeds = step2PoolSources
        .filter((s) => selectedReferenceSourceUrls.has(s.url))
        .slice(0, MAX_STEP2_SELECTED_FEEDS)
        .map((s) => ({
          name: s.name || 'RSS',
          url: s.url,
          role: s.role || '',
        }));

      const data: ChannelCreateRequest = {
        name: name.trim(),
        category,
        region,
        custom_keywords: customKeywords,
        description: description.trim() || undefined,
        ...(selectedFeeds.length > 0 ? { selected_feeds: selectedFeeds } : {}),
      };

      await channelsApi.createChannel(data);
      assistPoolBoostRef.current = [];
      toast.success(t('channels.createSuccess'));
      navigate('/channels');
    } catch (err: unknown) {
      const msg =
        err instanceof APIError
          ? err.message
          : err instanceof Error
            ? err.message
            : t('common.failed');
      toast.error(msg);
      if (showAssist) setFeedActionBanner(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addFeedToSelected = (url: string) => {
    setSelectedReferenceSourceUrls((prev) => {
      if (prev.has(url)) return prev;
      if (prev.size >= MAX_STEP2_SELECTED_FEEDS) {
        toast.error(t('channels.step2.maxFeedsToast', { max: String(MAX_STEP2_SELECTED_FEEDS) }));
        return prev;
      }
      const next = new Set(prev);
      next.add(url);
      return next;
    });
  };

  const removeFeedFromSelected = (url: string) => {
    setSelectedReferenceSourceUrls((prev) => {
      const next = new Set(prev);
      next.delete(url);
      return next;
    });
  };

  /** 精靈建議的 RSS：若尚未在候選池，先併入再勾選 */
  const addGuidedFeedToPoolAndSelected = (feed: { name: string; url: string; role: string }) => {
    const entry: ChannelFeedEntry = {
      name: feed.name || 'RSS',
      url: (feed.url || '').trim(),
      role: feed.role || '',
    };
    if (!entry.url) return;
    setStep2PoolSources((prev) => mergeFeedsByUrl([entry], prev));
    addFeedToSelected(entry.url);
  };

  return (
    <main className="relative min-h-screen bg-gray-50 py-8 dark:bg-gray-900">
      <a
        href="#channel-create-form"
        data-testid="link-channels-phasec-skip-to-form"
        onClick={(e) => {
          e.preventDefault();
          const el = document.getElementById('channel-create-form') as HTMLElement | null;
          el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          window.setTimeout(() => el?.focus({ preventScroll: true }), 200);
        }}
        className="fixed left-4 top-0 z-[70] -translate-y-full rounded-lg bg-white px-4 py-3 text-sm font-semibold text-gray-900 shadow-lg ring-2 ring-purple-500 transition-transform focus:translate-y-4 focus:outline-none dark:bg-gray-800 dark:text-white"
      >
        {t('channels.phaseC.skipToForm')}
      </a>
      <div
        className={`mx-auto px-4 sm:px-6 lg:px-8 ${
          showAssist ? 'max-w-6xl pb-28 lg:pb-8' : 'max-w-2xl'
        }`}
      >
        {/* 返回按鈕 */}
        <button
          type="button"
          data-testid="btn-channels-create-back"
          onClick={() => navigate('/channels')}
          className="mb-6 flex items-center gap-2 rounded-lg text-gray-500 hover:text-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-50 dark:text-gray-400 dark:hover:text-gray-200 dark:focus-visible:ring-offset-gray-900"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          {t('channels.backToList')}
        </button>
        
        {/* 標題 */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t('channels.create')}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {t('channels.createDescription')}
          </p>
        </div>
            {/* AI 助手按鈕：Step 1／Step 2 可開（Step 2 同步精靈地區與尚可加入之 RSS） */}
            {(step === 1 || step === 2 || step === 3) && (
              <button
                type="button"
                onClick={() => setShowAssist((open) => !open)}
                data-testid={showAssist ? 'btn-channels-assist-minimize' : 'btn-channels-assist'}
                className={
                  showAssist
                    ? 'flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 transition-all hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700 dark:focus-visible:ring-offset-gray-900'
                    : 'flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-cyan-500 px-4 py-2 text-white shadow-lg transition-all hover:from-purple-600 hover:to-cyan-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-50 dark:focus-visible:ring-offset-gray-900'
                }
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span className="font-medium">
                  {showAssist ? t('channels.assist.minimizePanel') : t('channels.assist.title')}
                </span>
              </button>
            )}
          </div>
        </div>
        
        {/* AI 助手對話框 + 表單欄（Phase B：大螢幕並排，助手為主欄） */}
        <div className={showAssist ? 'flex flex-col lg:flex-row lg:gap-8 lg:items-start' : ''}>
        {showAssist && (
          <div className="mb-8 lg:mb-0 w-full lg:flex-[1.15] min-w-0">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 sm:p-6 shadow-lg border-2 border-purple-200 dark:border-purple-800 lg:h-full flex flex-col max-h-[min(88vh,760px)] lg:max-h-[calc(100vh-10rem)]">
            <div className="flex items-center justify-between mb-4 shrink-0">
              <h3
                id="channels-assist-panel-title"
                className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2"
              >
                <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                {t('channels.assist.title')}
              </h3>
              <button
                type="button"
                onClick={handleAssistClose}
                data-testid="btn-channels-assist-close"
                className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 dark:hover:bg-gray-700 dark:hover:text-gray-200"
                aria-label={t('channels.assist.closePanelAria')}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {assistRequestError && (
              <div
                role="alert"
                className="mb-3 flex flex-col gap-2 rounded-lg border border-amber-200 dark:border-amber-700 bg-amber-50/90 dark:bg-amber-950/30 px-3 py-2 text-amber-950 dark:text-amber-100 sm:flex-row sm:items-center sm:justify-between"
                data-testid="panel-channels-assist-request-error"
              >
                <p className="text-sm min-w-0">{assistRequestError}</p>
                <button
                  type="button"
                  onClick={() => setAssistRequestError(null)}
                  className="shrink-0 text-sm font-medium text-amber-900 dark:text-amber-200 underline min-h-[44px] sm:min-h-0 px-1 text-left sm:text-right"
                  data-testid="btn-channels-assist-error-dismiss"
                >
                  {t('channels.assist.dismissError')}
                </button>
              </div>
            )}

            {feedActionBanner && (
              <div
                role="alert"
                className="mb-3 flex flex-col gap-2 rounded-lg border border-red-200 bg-red-50/90 px-3 py-2 text-red-950 dark:border-red-800 dark:bg-red-950/30 dark:text-red-100 sm:flex-row sm:items-center sm:justify-between"
                data-testid="panel-channels-assist-feed-action-error"
              >
                <p className="min-w-0 text-sm">{feedActionBanner}</p>
                <div className="flex shrink-0 flex-col gap-2 sm:flex-row sm:items-center">
                  <button
                    type="button"
                    onClick={() => setFeedActionBanner(null)}
                    className="min-h-[44px] px-1 text-left text-sm font-medium text-red-900 underline dark:text-red-200 sm:min-h-0 sm:text-right"
                    data-testid="btn-channels-assist-feed-error-dismiss"
                  >
                    {t('channels.assist.dismissError')}
                  </button>
                  <a
                    href="#channel-create-form"
                    onClick={(e) => {
                      e.preventDefault();
                      setMobileSummaryOpen(false);
                      const el = document.getElementById('channel-create-form') as HTMLElement | null;
                      el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      window.setTimeout(() => el?.focus({ preventScroll: true }), 200);
                    }}
                    className="min-h-[44px] text-sm font-medium text-red-800 underline dark:text-red-200 sm:min-h-0"
                    data-testid="link-channels-assist-go-to-form"
                  >
                    {t('channels.phaseC.goToForm')}
                  </a>
                </div>
              </div>
            )}

            <div
              className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden space-y-1 pr-0.5"
              role="region"
              aria-labelledby="channels-assist-panel-title"
            >

            {guidedLoading && (
              <p
                className="text-sm text-gray-500 dark:text-gray-400 mb-3"
                data-testid="text-channels-guided-loading"
              >
                {t('channels.guided.loading')}
              </p>
            )}
            {guidedLoadError && !guidedLoading && (
              <div
                role="alert"
                className="mb-3 rounded-lg border border-red-200 dark:border-red-800 bg-red-50/90 dark:bg-red-950/25 px-3 py-3 text-sm text-red-900 dark:text-red-100"
                data-testid="panel-channels-guided-load-error"
              >
                <p className="mb-2">{t('channels.guided.loadFailed')}</p>
                <button
                  type="button"
                  onClick={() => setGuidedRetryToken((n) => n + 1)}
                  className="font-medium text-red-800 dark:text-red-200 underline min-h-[44px]"
                  data-testid="btn-channels-guided-retry"
                >
                  {t('channels.guided.retry')}
                </button>
              </div>
            )}
            {!guidedLoading && guidedOptions && guidedOptions.step === 1 && guidedOptions.quick_options.length > 0 && (
              <div
                className="mb-4 rounded-xl border border-dashed border-purple-200 dark:border-purple-700 bg-purple-50/50 dark:bg-purple-950/20 p-3 sm:p-4"
                data-testid="panel-channels-guided"
              >
                <p className="text-sm text-gray-700 dark:text-gray-200 mb-2">{t('channels.guided.intro')}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  {t('channels.guided.serverSyncTitle')}
                </p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {guidedOptions.quick_options
                    .filter((o) => o.kind === 'category')
                    .map((o) => (
                      <button
                        key={o.value}
                        type="button"
                        data-testid={`btn-channels-guided-category-${o.value}`}
                        disabled={isAssisting}
                        onClick={() => handleQuickCategoryClick(o.value as ChannelCategory)}
                        className={`px-3 py-1.5 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] border flex items-center gap-1 ${
                          category === o.value
                            ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                            : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-100 hover:border-purple-300 dark:hover:border-purple-600'
                        }`}
                      >
                        <span className="text-base sm:text-lg">
                          {categoryIcons[o.value as ChannelCategory] ?? '•'}
                        </span>
                        <span>{t(o.label_key as any)}</span>
                      </button>
                    ))}
                </div>
                <button
                  type="button"
                  data-testid="btn-channels-guided-escape"
                  onClick={handleAssistClose}
                  className="text-xs text-purple-600 dark:text-purple-400 hover:underline"
                >
                  {t('channels.guided.escapeAdvanced')}
                </button>
              </div>
            )}

            {!guidedLoading && guidedOptions && guidedOptions.step === 2 && (
              <div
                className="mb-4 rounded-xl border border-dashed border-purple-200 dark:border-purple-700 bg-purple-50/50 dark:bg-purple-950/20 p-3 sm:p-4"
                data-testid="panel-channels-guided-step2"
              >
                <p className="text-sm text-gray-700 dark:text-gray-200 mb-2">{t('channels.guided.introStep2')}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  {t('channels.guided.serverSyncTitleStep2')}
                </p>
                {guidedOptions.quick_options.filter((o) => o.kind === 'region').length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {guidedOptions.quick_options
                      .filter((o) => o.kind === 'region')
                      .map((o) => (
                        <button
                          key={o.value}
                          type="button"
                          data-testid={`btn-channels-guided-region-${o.value}`}
                          disabled={isAssisting}
                          onClick={() => handleQuickRegionClick(o.value as ChannelRegion)}
                          className={`px-3 py-1.5 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] border ${
                            region === o.value
                              ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                              : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-100 hover:border-purple-300 dark:hover:border-purple-600'
                          }`}
                        >
                          {t(o.label_key as any)}
                        </button>
                      ))}
                  </div>
                )}
                {guidedOptions.feed_options.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs font-medium text-gray-600 dark:text-gray-300 mb-2">
                      {t('channels.guided.suggestedFeedsTitle')}
                    </p>
                    <ul className="space-y-2 max-h-48 overflow-y-auto">
                      {guidedOptions.feed_options.map((f, idx) => (
                        <li
                          key={`${f.url}-${idx}`}
                          className="flex items-start justify-between gap-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-white/80 dark:bg-gray-800/80 p-2"
                        >
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{f.name}</p>
                            <p className="text-xs text-gray-500 truncate" title={f.url}>
                              {f.url}
                            </p>
                          </div>
                          <button
                            type="button"
                            data-testid={`btn-channels-guided-feed-add-${idx}`}
                            disabled={isAssisting || selectedReferenceSourceUrls.has(f.url.trim())}
                            onClick={() => addGuidedFeedToPoolAndSelected(f)}
                            className="shrink-0 px-2 py-1.5 text-xs font-medium rounded-lg bg-purple-100 dark:bg-purple-900/40 text-purple-800 dark:text-purple-200 hover:bg-purple-200 dark:hover:bg-purple-800/50 disabled:opacity-50 min-h-[44px] md:min-h-0"
                          >
                            {t('channels.guided.addSuggestedFeed')}
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {guidedOptions.feed_options.length === 0 && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">{t('channels.guided.noMoreFeedsHint')}</p>
                )}
                <button
                  type="button"
                  data-testid="btn-channels-guided-escape-step2"
                  onClick={handleAssistClose}
                  className="text-xs text-purple-600 dark:text-purple-400 hover:underline"
                >
                  {t('channels.guided.escapeAdvanced')}
                </button>
              </div>
            )}

            {!guidedLoading && guidedOptions && guidedOptions.step === 3 && category && (
              <div
                className="mb-4 rounded-xl border border-dashed border-purple-200 dark:border-purple-700 bg-purple-50/50 dark:bg-purple-950/20 p-3 sm:p-4"
                data-testid="panel-channels-guided-step3"
              >
                <p className="text-sm text-gray-700 dark:text-gray-200 mb-2">{t('channels.guided.introStep3')}</p>
                {(guidedOptions.suggested_channel_name || guidedOptions.suggested_channel_description) && (
                  <div className="rounded-lg border border-gray-200 dark:border-gray-600 bg-white/80 dark:bg-gray-800/80 p-3 mb-3 space-y-2">
                    {guidedOptions.suggested_channel_name ? (
                      <p className="text-sm text-gray-900 dark:text-white">
                        <span className="text-xs text-gray-500 block">{t('channels.channelName')}</span>
                        {guidedOptions.suggested_channel_name}
                      </p>
                    ) : null}
                    {guidedOptions.suggested_channel_description ? (
                      <p className="text-sm text-gray-700 dark:text-gray-200 whitespace-pre-wrap">
                        <span className="text-xs text-gray-500 block">{t('channels.channelDescription')}</span>
                        {guidedOptions.suggested_channel_description}
                      </p>
                    ) : null}
                    <button
                      type="button"
                      data-testid="btn-channels-guided-step3-apply"
                      disabled={isAssisting}
                      onClick={() => {
                        if (guidedOptions.suggested_channel_name) {
                          setName(guidedOptions.suggested_channel_name.slice(0, 50));
                        }
                        if (guidedOptions.suggested_channel_description) {
                          setDescription(guidedOptions.suggested_channel_description.slice(0, 200));
                        }
                        toast.success(t('channels.step3.applyWizardOk'));
                      }}
                      className="w-full sm:w-auto px-4 py-2 text-sm font-medium rounded-lg bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 min-h-[44px]"
                    >
                      {t('channels.step3.applyWizardNaming')}
                    </button>
                  </div>
                )}
                <button
                  type="button"
                  data-testid="btn-channels-guided-escape-step3"
                  onClick={handleAssistClose}
                  className="text-xs text-purple-600 dark:text-purple-400 hover:underline"
                >
                  {t('channels.guided.escapeAdvanced')}
                </button>
              </div>
            )}
            
            {/* 快捷按鈕區域（Step 2／3 開助手時隱藏） */}
            {!((step === 2 || step === 3) && showAssist) && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                {t('channels.assist.quickButtons')}
              </p>
              <div className="space-y-3">
                {/* 常見組合預設 */}
                <div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-1.5">
                    {t('channels.assist.presets')}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {quickPresets.map((preset) => (
                      <button
                        key={preset.key}
                        onClick={() => handlePresetClick(preset)}
                        data-testid={`btn-channels-assist-preset-${preset.key}`}
                        disabled={isAssisting}
                        className={`px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 min-h-[44px] border ${
                          category === preset.category && region === preset.region
                            ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                            : 'bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-sm'
                        }`}
                      >
                        <span className="text-sm">{preset.icon}</span>
                        <span>{t(`channels.assist.preset.${preset.key}` as any)}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* 類別快捷按鈕 - 顯示其他類型（非時尚/美食/趨勢） */}
                <div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-1.5">
                    {t('channels.assist.quickCategoryLabel')}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {categories
                      .filter((cat) => !['fashion', 'food', 'trend'].includes(cat.value))
                      .map((cat) => (
                        <button
                          key={cat.value}
                          onClick={() => handleQuickCategoryClick(cat.value)}
                          data-testid={`btn-channels-assist-quick-category-${cat.value}`}
                          disabled={isAssisting}
                          className={`px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 min-h-[44px] border ${
                            category === cat.value
                              ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                              : 'bg-gray-100 dark:bg-gray-700 border-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                          }`}
                        >
                          <span className="text-base sm:text-lg">{cat.icon}</span>
                          <span className="hidden sm:inline">{t(cat.label)}</span>
                          <span className="sm:hidden">{t(cat.label).substring(0, 2)}</span>
                        </button>
                      ))}
                  </div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 px-1">
                    {t('channels.assist.quickCategoryNote')}
                  </p>
                </div>

                {/* 地區快捷按鈕 - 顯示全部 8 個地區 */}
                <div>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-1.5">
                    {t('channels.assist.quickRegionLabel')}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {regions.map((reg) => (
                      <button
                        key={reg.value}
                        onClick={() => handleQuickRegionClick(reg.value)}
                        data-testid={`btn-channels-assist-quick-region-${reg.value}`}
                        disabled={isAssisting}
                        className={`px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] border ${
                          region === reg.value
                            ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-400 dark:border-purple-600 text-purple-700 dark:text-purple-300 ring-1 ring-purple-300 dark:ring-purple-700'
                            : 'bg-gray-100 dark:bg-gray-700 border-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {t(reg.label)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            )}
            
            {/* 對話紀錄（保留多輪，與後端 conversation_history 對齊） */}
            <div className="mb-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                {t('channels.assist.chatHistory')}
              </p>
              <div
                className="max-h-64 overflow-y-auto rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50/90 dark:bg-gray-900/50 p-3 space-y-3"
                aria-live="polite"
                aria-relevant="additions text"
              >
                {assistHistory.map((turn) => (
                  <div
                    key={turn.id}
                    className={`flex ${turn.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[88%] rounded-2xl px-3 py-2 text-sm sm:text-base break-words whitespace-pre-line ${
                        turn.role === 'user'
                          ? 'bg-purple-600 text-white'
                          : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600'
                      }`}
                    >
                      {turn.content}
                    </div>
                  </div>
                ))}
                {isAssisting && (
                  <div className="flex justify-start">
                    <div className="rounded-2xl px-3 py-2 text-sm text-gray-500 dark:text-gray-400 border border-dashed border-gray-300 dark:border-gray-600">
                      {t('common.loading')}…
                    </div>
                  </div>
                )}
                <div ref={assistChatEndRef} />
              </div>
            </div>
            
            {/* 輸入區域 */}
            <div className="mb-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {t('channels.assist.prompt')}
              </p>
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  value={assistInput}
                  onChange={(e) => setAssistInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleAssistSubmit();
                    }
                  }}
                  placeholder={t('channels.assist.placeholder')}
                  data-testid="input-channels-assist"
                  disabled={isAssisting}
                  className="flex-1 px-4 py-3 sm:py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 text-sm sm:text-base min-h-[44px]"
                />
                <button
                  onClick={handleAssistSubmit}
                  disabled={!assistInput.trim() || isAssisting}
                  data-testid="btn-channels-assist-submit"
                  className="px-6 py-3 sm:py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 min-h-[44px] text-sm sm:text-base font-medium"
                >
                  {isAssisting ? (
                    <>
                      <svg className="animate-spin h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span className="hidden sm:inline">{t('common.loading')}</span>
                    </>
                  ) : (
                    t('channels.assist.submit')
                  )}
                </button>
              </div>
            </div>
            
            {/* 錯誤訊息顯示 */}
            {!isAssisting && assistResult && assistResult.confidence < 0.5 && !assistResult.clarification_needed && (
              <div className="mb-4 p-3 sm:p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm sm:text-base text-yellow-800 dark:text-yellow-200">
                      {t('channels.assist.lowConfidenceWarning')}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* 結果顯示 */}
            {assistResult && (
              <div className="mt-4 p-3 sm:p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                {assistResult.clarification_needed ? (
                  <p className="text-sm text-gray-600 dark:text-gray-400">{t('channels.assist.continueConversation')}</p>
                ) : (
                  <div className="space-y-3 sm:space-y-4">
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.category')}</p>
                      <p className="font-medium text-sm sm:text-base text-gray-900 dark:text-white">
                        {assistResult.category ? t(categoryI18nKeys[assistResult.category as ChannelCategory]) : '-'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.region')}</p>
                      <p className="font-medium text-sm sm:text-base text-gray-900 dark:text-white">
                        {assistResult.region ? t(regionI18nKeys[assistResult.region as ChannelRegion]) : '-'}
                      </p>
                    </div>
                    {assistResult.keywords.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('channels.assist.keywords')}</p>
                        <div className="flex flex-wrap gap-2">
                          {assistResult.keywords.map((kw, idx) => (
                            <span key={idx} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded text-xs sm:text-sm">
                              {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {(assistResult.suggested_channel_name?.trim() ||
                      assistResult.suggested_channel_description?.trim()) && (
                      <div className="rounded-lg border border-emerald-200 dark:border-emerald-800 p-3 bg-emerald-50/60 dark:bg-emerald-950/25">
                        <p className="text-xs font-medium text-emerald-800 dark:text-emerald-200 mb-2">
                          {t('channels.assist.suggestedNamingTitle')}
                        </p>
                        {assistResult.suggested_channel_name?.trim() ? (
                          <p className="text-sm text-gray-900 dark:text-white mb-1">
                            {assistResult.suggested_channel_name.trim()}
                          </p>
                        ) : null}
                        {assistResult.suggested_channel_description?.trim() ? (
                          <p className="text-xs text-gray-600 dark:text-gray-300 whitespace-pre-wrap mb-2">
                            {assistResult.suggested_channel_description.trim()}
                          </p>
                        ) : null}
                        <button
                          type="button"
                          data-testid="btn-channels-assist-apply-naming"
                          onClick={() => {
                            const n = assistResult.suggested_channel_name?.trim();
                            const d = assistResult.suggested_channel_description?.trim();
                            if (n) setName(n.slice(0, 50));
                            if (d) setDescription(d.slice(0, 200));
                            toast.success(t('channels.step3.applyAssistOk'));
                          }}
                          className="text-sm px-3 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 min-h-[44px]"
                        >
                          {t('channels.step3.applyAssistNaming')}
                        </button>
                      </div>
                    )}
                    {assistResult.recommended_sources.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{t('channels.assist.sources')}</p>
                        <div className="space-y-2">
                          {assistResult.recommended_sources.slice(0, 5).map((source, idx) => {
                            // 從 URL 解析網域與 favicon
                            let domain = '';
                            let faviconUrl = '';
                            let sourceType: 'rss' | 'web' | 'api' = 'web';
                            let websiteUrl = source.url; // 預設使用原始 URL
                            
                            try {
                              const urlObj = new URL(source.url);
                              domain = urlObj.hostname.replace(/^www\./, '');
                              faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
                              
                              // 猜測來源類型
                              if (source.url.includes('/rss') || source.url.includes('/feed') || source.url.endsWith('.xml')) {
                                sourceType = 'rss';
                                // 如果是 RSS feed URL，提取網站首頁 URL
                                websiteUrl = `${urlObj.protocol}//${urlObj.hostname}`;
                              } else if (source.url.includes('/api') || source.url.includes('api.')) {
                                sourceType = 'api';
                              }
                            } catch {
                              domain = source.url;
                            }

                            const sourceTypeColors = {
                              rss: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
                              web: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
                              api: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
                            };

                            return (
                              <div 
                                key={idx} 
                                className="group p-3 sm:p-4 bg-white dark:bg-gray-600 rounded-xl border border-gray-200 dark:border-gray-500 hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-md transition-all duration-200"
                                data-testid={`source-preview-${idx}`}
                              >
                                <div className="flex items-start gap-3">
                                  {/* Favicon */}
                                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gray-100 dark:bg-gray-500 flex items-center justify-center overflow-hidden">
                                    {faviconUrl ? (
                                      <img 
                                        src={faviconUrl} 
                                        alt="" 
                                        className="w-5 h-5 sm:w-6 sm:h-6"
                                        onError={(e) => {
                                          (e.target as HTMLImageElement).style.display = 'none';
                                          (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                                        }}
                                      />
                                    ) : null}
                                    <svg className={`w-4 h-4 sm:w-5 sm:h-5 text-gray-400 ${faviconUrl ? 'hidden' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                    </svg>
                                  </div>

                                  {/* 來源資訊 */}
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                      <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-white truncate">
                                        {source.name}
                                      </p>
                                      {/* 來源類型標籤 */}
                                      <span className={`flex-shrink-0 px-1.5 py-0.5 text-[10px] sm:text-xs font-medium rounded ${sourceTypeColors[sourceType]}`}>
                                        {t(`channels.assist.sourceType.${sourceType}` as any)}
                                      </span>
                                    </div>
                                    {/* 網域 */}
                                    {domain && (
                                      <p className="text-xs text-gray-400 dark:text-gray-500 truncate mb-1">
                                        {domain}
                                      </p>
                                    )}
                                    {/* 角色描述 */}
                                    {source.role && (
                                      <p className="text-xs text-gray-500 dark:text-gray-400 break-words line-clamp-2">
                                        {source.role}
                                      </p>
                                    )}
                                  </div>

                                  {/* 訪問按鈕 */}
                                  {websiteUrl && (
                                    <a
                                      href={websiteUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="flex-shrink-0 p-2 text-gray-400 hover:text-purple-500 group-hover:bg-purple-50 dark:group-hover:bg-purple-900/20 rounded-lg transition-all min-w-[44px] min-h-[44px] flex items-center justify-center"
                                      data-testid={`source-link-${idx}`}
                                      onClick={(e) => e.stopPropagation()}
                                      aria-label={t('channels.assist.visitSource')}
                                      title={t('channels.assist.visitSource')}
                                    >
                                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                      </svg>
                                    </a>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        {assistResult.recommended_sources.length > 5 && (
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 text-center">
                            {t('channels.assist.moreSources', { count: assistResult.recommended_sources.length - 5 })}
                          </p>
                        )}
                      </div>
                    )}
                    <div className="flex flex-col sm:flex-row gap-2 pt-2">
                      <button
                        onClick={handleAssistConfirm}
                        data-testid="btn-channels-assist-confirm"
                        className="flex-1 px-4 py-3 sm:py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors min-h-[44px] text-sm sm:text-base font-medium"
                      >
                        {t('channels.assist.confirm')}
                      </button>
                      <button
                        onClick={handleAssistReset}
                        data-testid="btn-channels-assist-modify"
                        className="flex-1 px-4 py-3 sm:py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors min-h-[44px] text-sm sm:text-base font-medium"
                      >
                        {t('channels.assist.modify')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
            </div>
          </div>
          </div>
        )}

        <div className={`min-w-0 ${showAssist ? 'lg:flex-1 lg:max-w-md xl:max-w-lg' : 'w-full'}`}>
          <div className={showAssist ? 'hidden lg:block' : ''}>
            {showAssist && (
              <>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  {t('channels.phaseB.formColumnTitle')}
                </p>
                <CreateChannelSummaryPanel
                  t={t}
                  name={name}
                  description={description}
                  category={category}
                  region={region}
                  step={step}
                  selectedCount={selectedReferenceSourceUrls.size}
                  maxFeeds={MAX_STEP2_SELECTED_FEEDS}
                />
              </>
            )}
            <CreateChannelStepNav step={step} t={t} />
            {showAssist && (
              <p
                className="mx-auto mb-6 max-w-lg px-2 text-center text-xs text-gray-500 dark:text-gray-400"
                data-testid="text-channels-phasec-step-hint"
              >
                {t('channels.phaseC.stepHint')}
              </p>
            )}
          </div>

        {/* 表單內容：lg＋助手開啟時預設收合（進階），符合 E 階段 表單收斂 */}
        <div
          id="channel-create-form"
          tabIndex={-1}
          className="outline-none focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-50 dark:focus-visible:ring-offset-gray-900"
        >
          {showAssist && !desktopFormExpanded ? (
            <div
              className="mb-6 hidden rounded-2xl border-2 border-dashed border-purple-200 bg-purple-50/50 p-6 text-center dark:border-purple-800 dark:bg-purple-950/20 lg:block"
              data-testid="panel-channels-form-collapsed-hint"
            >
              <p className="mb-4 text-sm text-gray-600 dark:text-gray-300">
                {t('channels.phaseB.expandFormHint')}
              </p>
              <button
                type="button"
                data-testid="btn-channels-expand-wizard-form"
                onClick={() => setDesktopFormExpanded(true)}
                className="min-h-[44px] rounded-lg bg-purple-600 px-4 py-3 text-sm font-semibold text-white hover:bg-purple-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400"
              >
                {t('channels.phaseB.expandForm')}
              </button>
            </div>
          ) : null}

          <div
            data-testid="panel-channels-create-form"
            className={`rounded-2xl bg-white p-8 shadow-lg dark:bg-gray-800 ${
              showAssist && !desktopFormExpanded ? 'lg:hidden' : ''
            }`}
          >
            {showAssist && desktopFormExpanded && step < 3 ? (
              <div className="mb-6 hidden justify-end lg:flex">
                <button
                  type="button"
                  data-testid="btn-channels-collapse-wizard-form"
                  onClick={() => setDesktopFormExpanded(false)}
                  className="min-h-[44px] px-1 text-sm font-medium text-purple-600 underline hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300"
                >
                  {t('channels.phaseB.collapseForm')}
                </button>
              </div>
            ) : null}
          {/* 步驟 1: 選擇類別 */}
          {step === 1 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('channels.step1.title')}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {t('channels.step1.description')}
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                {categories.map((cat) => (
                  <button
                    key={cat.value}
                    type="button"
                    data-testid={`btn-channels-step1-category-${cat.value}`}
                    onClick={() => setCategory(cat.value)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 flex items-center gap-3 ${
                      category === cat.value
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <span className="text-2xl">{cat.icon}</span>
                    <span className={`font-medium ${
                      category === cat.value
                        ? 'text-purple-600 dark:text-purple-400'
                        : 'text-gray-700 dark:text-gray-200'
                    }`}>
                      {t(cat.label)}
                    </span>
                  </button>
                ))}
              </div>
              
              <div className="mt-8 flex justify-end">
                <button
                  type="button"
                  data-testid="btn-channels-step1-next"
                  onClick={() => {
                    if (!category) return;
                    assistPoolBoostRef.current = [];
                    setStep(2);
                  }}
                  disabled={!category}
                  className="px-6 py-3 bg-purple-500 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
                >
                  {t('common.next')}
                </button>
              </div>
            </div>
          )}
          
          {/* 步驟 2: 地區與內容來源 */}
          {step === 2 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('channels.step2.title')}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {t('channels.step2.description')}
              </p>

              <div className="grid grid-cols-2 gap-4">
                {regions.map((reg) => (
                  <button
                    key={reg.value}
                    type="button"
                    data-testid={`btn-channels-step2-region-${reg.value}`}
                    onClick={() => setRegion(reg.value)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                      region === reg.value
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <span className={`font-medium ${
                      region === reg.value
                        ? 'text-purple-600 dark:text-purple-400'
                        : 'text-gray-700 dark:text-gray-200'
                    }`}>
                      {t(reg.label)}
                    </span>
                  </button>
                ))}
              </div>

              {/* 自定義關鍵字（當類別為 other 時） */}
              {category === 'other' && (
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                    {t('channels.customKeywords')} <span className="text-red-500">*</span>
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      data-testid="input-channels-step2-keyword"
                      value={keywordInput}
                      onChange={(e) => setKeywordInput(e.target.value)}
                      onKeyDown={handleKeywordKeyDown}
                      placeholder={t('channels.keywordPlaceholder')}
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <button
                      type="button"
                      data-testid="btn-channels-step2-keyword-add"
                      onClick={addKeyword}
                      disabled={!keywordInput.trim() || customKeywords.length >= 5}
                      className="px-4 py-2 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {t('common.add')}
                    </button>
                  </div>

                  {customKeywords.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {customKeywords.map((keyword, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full"
                        >
                          {keyword}
                          <button
                            type="button"
                            data-testid={`btn-channels-step2-keyword-remove-${index}`}
                            onClick={() => removeKeyword(index)}
                            className="hover:text-purple-800 dark:hover:text-purple-200"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </span>
                      ))}
                    </div>
                  )}

                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    {t('channels.keywordsMax')} ({customKeywords.length}/5)
                  </p>
                </div>
              )}

              <div className="mt-8 border-t border-gray-200 dark:border-gray-600 pt-8">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  {t('channels.step2.feedSourcesSection')}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                  {t('channels.step2.feedSourcesHint')}
                </p>
                <p className="text-xs text-purple-600 dark:text-purple-400 mb-4">
                  {t('channels.step2.maxFeedsHint', {
                    max: String(MAX_STEP2_SELECTED_FEEDS),
                    count: String(selectedReferenceSourceUrls.size),
                  })}
                </p>

                <div className="mb-6 rounded-xl border border-dashed border-gray-300 dark:border-gray-600 p-4 bg-gray-50/80 dark:bg-gray-900/30">
                  <h4 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-1">
                    {t('channels.step2.pasteUrlSection')}
                  </h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                    {t('channels.step2.pasteUrlHint')}
                  </p>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <input
                      type="url"
                      inputMode="url"
                      value={step2PasteUrl}
                      onChange={(e) => {
                        setStep2PasteUrl(e.target.value);
                        setStep2PastedValidated(null);
                      }}
                      placeholder={t('channels.step2.pasteUrlPlaceholder')}
                      data-testid="input-channels-step2-paste-url"
                      disabled={step2PasteValidating}
                      className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white min-h-[44px]"
                    />
                    <button
                      type="button"
                      onClick={handleStep2ValidatePastedUrl}
                      disabled={step2PasteValidating || !step2PasteUrl.trim()}
                      data-testid="btn-channels-step2-validate-url"
                      className="px-4 py-2 text-sm font-medium rounded-lg bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-900 disabled:opacity-50 min-h-[44px]"
                    >
                      {step2PasteValidating ? t('common.loading') : t('channels.step2.pasteUrlValidate')}
                    </button>
                  </div>
                  {step2PastedValidated && (
                    <div className="mt-3 flex flex-col sm:flex-row sm:items-center gap-2 rounded-lg border border-green-200 dark:border-green-800 bg-green-50/80 dark:bg-green-950/30 p-3">
                      <p className="text-sm text-gray-800 dark:text-gray-100 flex-1 min-w-0">
                        <span className="font-medium">{step2PastedValidated.name}</span>
                        <span className="block text-xs text-gray-500 truncate" title={step2PastedValidated.url}>
                          {step2PastedValidated.url}
                        </span>
                      </p>
                      <button
                        type="button"
                        data-testid="btn-channels-step2-add-pasted-url"
                        onClick={() => {
                          addGuidedFeedToPoolAndSelected({
                            name: step2PastedValidated.name,
                            url: step2PastedValidated.url,
                            role: 'custom',
                          });
                          setStep2PastedValidated(null);
                          setStep2PasteUrl('');
                          toast.success(t('channels.step2.pasteUrlAdded'));
                        }}
                        className="shrink-0 px-4 py-2 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-700 min-h-[44px]"
                      >
                        {t('channels.step2.pasteUrlAdd')}
                      </button>
                    </div>
                  )}
                </div>

                <div className="mb-6 rounded-xl border border-gray-200 dark:border-gray-600 p-4 bg-white dark:bg-gray-800/40">
                  <h4 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-1">
                    {t('channels.step2.whitelistSearchTitle')}
                  </h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                    {t('channels.step2.whitelistSearchHint')}
                  </p>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <input
                      type="search"
                      value={step2WhitelistQuery}
                      onChange={(e) => setStep2WhitelistQuery(e.target.value)}
                      placeholder={t('channels.step2.whitelistSearchPlaceholder')}
                      data-testid="input-channels-step2-whitelist-search"
                      disabled={step2WhitelistSearching}
                      className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white min-h-[44px]"
                    />
                    <button
                      type="button"
                      onClick={handleStep2WhitelistSearch}
                      disabled={step2WhitelistSearching || !step2WhitelistQuery.trim()}
                      data-testid="btn-channels-step2-whitelist-search"
                      className="px-4 py-2 text-sm font-medium rounded-lg bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 min-h-[44px]"
                    >
                      {step2WhitelistSearching ? t('common.loading') : t('channels.step2.whitelistSearchButton')}
                    </button>
                  </div>
                </div>

                {step2PoolLoading && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">{t('common.loading')}</p>
                )}
                {step2PoolError && !step2PoolLoading && (
                  <p className="text-sm text-red-600 dark:text-red-400">{t('channels.step2.poolLoadError')}</p>
                )}
                {!step2PoolLoading && !step2PoolError && step2PoolSources.length === 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">{t('channels.step2.poolEmpty')}</p>
                )}

                {!step2PoolLoading && step2PoolSources.length > 0 && (
                  <div className="grid gap-6 md:grid-cols-2">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        {t('channels.step2.candidatePool')}
                      </h4>
                      <div className="space-y-2 max-h-[min(320px,50vh)] overflow-y-auto pr-1">
                        {step2PoolSources
                          .filter((s) => !selectedReferenceSourceUrls.has(s.url))
                          .map((src, idx) => (
                            <div
                              key={src.url}
                              className="flex gap-2 items-start rounded-lg border border-gray-200 dark:border-gray-600 p-3 bg-white dark:bg-gray-800/50"
                            >
                              <div className="min-w-0 flex-1">
                                <p className="font-medium text-gray-900 dark:text-white text-sm">{src.name}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400 truncate" title={src.url}>
                                  {src.url}
                                </p>
                                {src.role ? (
                                  <p className="text-xs text-purple-600 dark:text-purple-400 mt-0.5">{src.role}</p>
                                ) : null}
                              </div>
                              <button
                                type="button"
                                data-testid={`btn-channels-step2-pool-add-${idx}`}
                                onClick={() => addFeedToSelected(src.url)}
                                className="shrink-0 px-3 py-1.5 text-xs font-medium rounded-lg bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-800/50 min-h-[44px] md:min-h-0"
                              >
                                {t('channels.step2.addToSelected')}
                              </button>
                            </div>
                          ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        {t('channels.step2.selectedFeedsTitle', {
                          count: String(selectedReferenceSourceUrls.size),
                          max: String(MAX_STEP2_SELECTED_FEEDS),
                        })}
                      </h4>
                      <div className="space-y-2 max-h-[min(320px,50vh)] overflow-y-auto pr-1">
                        {step2PoolSources
                          .filter((s) => selectedReferenceSourceUrls.has(s.url))
                          .map((src, idx) => (
                            <div
                              key={src.url}
                              className="flex gap-2 items-start rounded-lg border-2 border-purple-300 dark:border-purple-700 p-3 bg-purple-50/80 dark:bg-purple-900/20"
                            >
                              <div className="min-w-0 flex-1">
                                <p className="font-medium text-gray-900 dark:text-white text-sm">{src.name}</p>
                                <p className="text-xs text-gray-500 dark:text-gray-400 truncate" title={src.url}>
                                  {src.url}
                                </p>
                                {src.role ? (
                                  <p className="text-xs text-purple-600 dark:text-purple-400 mt-0.5">{src.role}</p>
                                ) : null}
                              </div>
                              <button
                                type="button"
                                data-testid={`btn-channels-step2-selected-remove-${idx}`}
                                onClick={() => removeFeedFromSelected(src.url)}
                                className="shrink-0 px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-gray-500 min-h-[44px] md:min-h-0"
                              >
                                {t('channels.step2.removeFromSelected')}
                              </button>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-8 flex justify-between">
                <button
                  type="button"
                  data-testid="btn-channels-step2-prev"
                  onClick={() => setStep(1)}
                  className="px-6 py-3 text-gray-600 dark:text-gray-300 font-medium hover:text-gray-800 dark:hover:text-white"
                >
                  {t('common.previous')}
                </button>
                <button
                  type="button"
                  data-testid="btn-channels-step2-next"
                  onClick={() => setStep(3)}
                  disabled={category === 'other' && customKeywords.length === 0}
                  className="px-6 py-3 bg-purple-500 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-600 transition-colors"
                >
                  {t('common.next')}
                </button>
              </div>
            </div>
          )}
          
          {/* 步驟 3: 命名頻道 */}
          {step === 3 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t('channels.step3.title')}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                {t('channels.step3.description')}
              </p>

              {assistAiNaming && (assistAiNaming.name || assistAiNaming.desc) && (
                <div
                  className="mb-6 rounded-xl border border-emerald-200 dark:border-emerald-800 p-4 bg-emerald-50/50 dark:bg-emerald-950/20"
                  data-testid="panel-channels-step3-assist-naming"
                >
                  <h3 className="text-sm font-medium text-emerald-900 dark:text-emerald-100 mb-2">
                    {t('channels.step3.assistNamingCard')}
                  </h3>
                  {assistAiNaming.name ? (
                    <p className="text-sm text-gray-900 dark:text-white mb-1">{assistAiNaming.name}</p>
                  ) : null}
                  {assistAiNaming.desc ? (
                    <p className="text-xs text-gray-600 dark:text-gray-300 mb-3 whitespace-pre-wrap">{assistAiNaming.desc}</p>
                  ) : null}
                  <button
                    type="button"
                    data-testid="btn-channels-step3-apply-assist-naming"
                    onClick={() => {
                      if (assistAiNaming.name) setName(assistAiNaming.name.slice(0, 50));
                      if (assistAiNaming.desc) setDescription(assistAiNaming.desc.slice(0, 200));
                      toast.success(t('channels.step3.applyAssistOk'));
                    }}
                    className="px-4 py-2 text-sm font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 min-h-[44px]"
                  >
                    {t('channels.step3.applyAssistNaming')}
                  </button>
                </div>
              )}

              {(step3Wizard?.suggested_channel_name || step3Wizard?.suggested_channel_description) && (
                <div
                  className="mb-6 rounded-xl border border-purple-200 dark:border-purple-800 p-4 bg-purple-50/50 dark:bg-purple-950/20"
                  data-testid="panel-channels-step3-wizard-naming"
                >
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {t('channels.step3.wizardNamingCard')}
                  </h3>
                  {step3Wizard.suggested_channel_name ? (
                    <p className="text-sm text-gray-900 dark:text-white mb-1">{step3Wizard.suggested_channel_name}</p>
                  ) : null}
                  {step3Wizard.suggested_channel_description ? (
                    <p className="text-xs text-gray-600 dark:text-gray-300 mb-3 whitespace-pre-wrap">
                      {step3Wizard.suggested_channel_description}
                    </p>
                  ) : null}
                  <button
                    type="button"
                    data-testid="btn-channels-step3-apply-wizard-naming"
                    onClick={() => {
                      if (step3Wizard.suggested_channel_name) {
                        setName(step3Wizard.suggested_channel_name.slice(0, 50));
                      }
                      if (step3Wizard.suggested_channel_description) {
                        setDescription(step3Wizard.suggested_channel_description.slice(0, 200));
                      }
                      toast.success(t('channels.step3.applyWizardOk'));
                    }}
                    className="px-4 py-2 text-sm font-medium rounded-lg bg-purple-600 text-white hover:bg-purple-700 min-h-[44px]"
                  >
                    {t('channels.step3.applyWizardNaming')}
                  </button>
                </div>
              )}
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                    {t('channels.channelName')} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    data-testid="input-channels-step3-name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder={t('channels.channelNamePlaceholder')}
                    maxLength={50}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 text-right">
                    {name.length}/50
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                    {t('channels.channelDescription')}
                  </label>
                  <textarea
                    data-testid="input-channels-step3-description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder={t('channels.channelDescriptionPlaceholder')}
                    maxLength={200}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  />
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 text-right">
                    {description.length}/200
                  </p>
                </div>
              </div>
              
              {/* 預覽 */}
              <div
                className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl"
                data-testid="panel-channels-step3-preview"
              >
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">
                  {t('channels.preview')}
                </h3>
                <div className="flex items-center gap-3">
                  <span className="text-3xl">
                    {category && categoryIcons[category]}
                  </span>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {name || t('channels.unnamed')}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {category && t(categoryI18nKeys[category])} · {t(regionI18nKeys[region])}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mt-8 flex justify-between">
                <button
                  type="button"
                  data-testid="btn-channels-step3-prev"
                  onClick={() => setStep(2)}
                  className="px-6 py-3 text-gray-600 dark:text-gray-300 font-medium hover:text-gray-800 dark:hover:text-white"
                >
                  {t('common.previous')}
                </button>
                <button
                  type="button"
                  data-testid="btn-channels-step3-submit"
                  onClick={handleSubmit}
                  disabled={!name.trim() || isSubmitting}
                  className="px-8 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:from-purple-600 hover:to-cyan-600 transition-all flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      {t('common.loading')}
                    </>
                  ) : (
                    t('channels.create')
                  )}
                </button>
              </div>
            </div>
          )}
          </div>
        </div>
        </div>
        </div>

        {showAssist && (
          <>
            <div className="pointer-events-none fixed inset-x-0 bottom-0 z-40 px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2 lg:hidden">
              <div className="pointer-events-auto">
                <button
                  ref={mobileSummaryTriggerRef}
                  type="button"
                  data-testid="btn-channels-mobile-summary-drawer"
                  onClick={() => setMobileSummaryOpen(true)}
                  className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm font-semibold text-gray-900 shadow-lg dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                >
                  {t('channels.phaseC.openSummaryDrawer')}
                </button>
              </div>
            </div>

            {mobileSummaryOpen ? (
              <div className="fixed inset-0 z-50 flex flex-col justify-end lg:hidden" role="presentation">
                <button
                  type="button"
                  tabIndex={-1}
                  className="absolute inset-0 bg-black/50"
                  aria-label={t('channels.phaseC.closeDrawer')}
                  data-testid="btn-channels-mobile-drawer-backdrop"
                  onClick={() => {
                    setMobileSummaryOpen(false);
                    window.setTimeout(() => mobileSummaryTriggerRef.current?.focus(), 0);
                  }}
                />
                <div
                  ref={mobileSummaryDrawerRef}
                  className="relative z-10 max-h-[min(85vh,640px)] overflow-y-auto rounded-t-2xl border border-gray-200 bg-white p-4 pb-8 shadow-xl dark:border-gray-600 dark:bg-gray-900"
                  role="dialog"
                  aria-modal="true"
                  aria-labelledby="mobile-channel-summary-drawer-title"
                >
                  <div className="mb-4 flex items-start justify-between gap-2">
                    <h2
                      id="mobile-channel-summary-drawer-title"
                      className="text-base font-semibold text-gray-900 dark:text-white"
                    >
                      {t('channels.phaseC.drawerTitle')}
                    </h2>
                    <button
                      type="button"
                      autoFocus
                      data-testid="btn-channels-mobile-drawer-close"
                      onClick={() => {
                        setMobileSummaryOpen(false);
                        window.setTimeout(() => mobileSummaryTriggerRef.current?.focus(), 0);
                      }}
                      className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 dark:hover:bg-gray-800 dark:hover:text-gray-200"
                      aria-label={t('channels.phaseC.closeDrawer')}
                    >
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <CreateChannelSummaryPanel
                    t={t}
                    name={name}
                    description={description}
                    category={category}
                    region={region}
                    step={step}
                    selectedCount={selectedReferenceSourceUrls.size}
                    maxFeeds={MAX_STEP2_SELECTED_FEEDS}
                  />
                  <CreateChannelStepNav step={step} t={t} />
                  <p
                    className="mx-auto mb-4 max-w-lg px-2 text-center text-xs text-gray-500 dark:text-gray-400"
                    data-testid="text-channels-mobile-drawer-step-hint"
                  >
                    {t('channels.phaseC.stepHint')}
                  </p>
                  <button
                    type="button"
                    data-testid="btn-channels-mobile-drawer-go-form"
                    onClick={() => {
                      setMobileSummaryOpen(false);
                      const el = document.getElementById('channel-create-form') as HTMLElement | null;
                      el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      window.setTimeout(() => el?.focus({ preventScroll: true }), 150);
                    }}
                    className="w-full rounded-lg border border-purple-200 bg-purple-50 px-4 py-3 text-sm font-semibold text-purple-900 dark:border-purple-800 dark:bg-purple-950/40 dark:text-purple-100"
                  >
                    {t('channels.phaseC.goToForm')}
                  </button>
                </div>
              </div>
            ) : null}
          </>
        )}
      </div>
    </main>
  );
}

