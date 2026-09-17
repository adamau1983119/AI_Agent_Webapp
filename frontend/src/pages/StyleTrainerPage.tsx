/**
 * Ops Style Trainer — allowlist only; paste → analyze → confirm Mongo.
 */
import { useCallback, useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useTranslation } from '@/i18n'
import {
  opsTrainerApi,
  type AnalyzeResult,
  type CoverageLang,
  type RefType,
  type StructureSlots,
  type TrainerDomain,
  type TrainerLang,
  type TrainerLength,
  type WriteProfile,
} from '@/api/opsTrainer'

const emptySlots = (): StructureSlots => ({
  prefix: '',
  fact: '',
  quote: '',
  context: '',
  ending: '',
})

export default function StyleTrainerPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()
  const [allowed, setAllowed] = useState<boolean | null>(null)
  const [coverage, setCoverage] = useState<CoverageLang[]>([])
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [imageDataUrl, setImageDataUrl] = useState<string | null>(null)
  const [pasteText, setPasteText] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [language, setLanguage] = useState<TrainerLang>('zh-TW')
  const [domain, setDomain] = useState<TrainerDomain>('trend')
  const [lengthBucket, setLengthBucket] = useState<TrainerLength>('short')
  const [writeProfile, setWriteProfile] = useState<WriteProfile>('news_recap')
  const [refType, setRefType] = useState<RefType>('positive')
  const [structure, setStructure] = useState<StructureSlots>(emptySlots())
  const [bodyText, setBodyText] = useState('')

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    opsTrainerApi
      .access()
      .then((r) => {
        setAllowed(r.allowed)
        if (!r.allowed) return
        return opsTrainerApi.coverage().then((c) => setCoverage(c.languages))
      })
      .catch(() => setAllowed(false))
  }, [isAuthenticated, navigate])

  const applyAnalyze = (r: AnalyzeResult) => {
    setLanguage(r.language)
    setDomain(r.domain)
    setLengthBucket(r.length_bucket)
    setWriteProfile(r.write_profile)
    setRefType(r.ref_type)
    setStructure(r.structure || emptySlots())
    setBodyText(r.body_text || '')
  }

  const runAnalyze = useCallback(async () => {
    if (!imageDataUrl && !pasteText.trim() && !sourceUrl.trim()) {
      toast.error(t('ops.trainer.needInput'))
      return
    }
    setAnalyzing(true)
    try {
      const r = await opsTrainerApi.analyze({
        text: pasteText,
        image_data_url: imageDataUrl || undefined,
        source_url: sourceUrl || undefined,
      })
      applyAnalyze(r)
      toast.success(t('ops.trainer.analyzeOk'))
    } catch {
      toast.error(t('ops.trainer.analyzeFail'))
    } finally {
      setAnalyzing(false)
    }
  }, [imageDataUrl, pasteText, sourceUrl, t])

  useEffect(() => {
    const onPaste = (e: ClipboardEvent) => {
      const item = Array.from(e.clipboardData?.items || []).find((i) => i.type.startsWith('image/'))
      if (!item) return
      const file = item.getAsFile()
      if (!file) return
      e.preventDefault()
      const reader = new FileReader()
      reader.onload = () => {
        const data = String(reader.result || '')
        setImageDataUrl(data)
        setPreviewUrl(data)
      }
      reader.readAsDataURL(file)
    }
    window.addEventListener('paste', onPaste)
    return () => window.removeEventListener('paste', onPaste)
  }, [])

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (!file || !file.type.startsWith('image/')) return
    const reader = new FileReader()
    reader.onload = () => {
      const data = String(reader.result || '')
      setImageDataUrl(data)
      setPreviewUrl(data)
    }
    reader.readAsDataURL(file)
  }

  const onConfirm = async () => {
    setSaving(true)
    try {
      await opsTrainerApi.confirm({
        language,
        domain,
        length_bucket: lengthBucket,
        write_profile: writeProfile,
        ref_type: refType,
        structure,
        body_text: bodyText,
        source_url: sourceUrl || undefined,
        publish: true,
      })
      toast.success(t('ops.trainer.confirmOk'))
      const c = await opsTrainerApi.coverage()
      setCoverage(c.languages)
    } catch {
      toast.error(t('ops.trainer.confirmFail'))
    } finally {
      setSaving(false)
    }
  }

  const setSlot = (key: keyof StructureSlots, value: string) => {
    setStructure((prev) => ({ ...prev, [key]: value }))
  }

  if (allowed === null) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10" data-testid="page-ops-style-trainer-loading">
        <p className="text-sm text-gray-500">{t('common.loading')}</p>
      </div>
    )
  }

  if (!allowed) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10" data-testid="page-ops-style-trainer-forbidden">
        <h1 className="font-display text-2xl text-gray-900">{t('ops.trainer.forbidden')}</h1>
        <p className="text-sm text-gray-600 mt-2">{t('ops.trainer.forbiddenHint')}</p>
      </div>
    )
  }

  const covLine = coverage
    .map((c) => `${c.language} ${c.filled}/${c.target} Mode ${c.mode}`)
    .join(' · ')

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6" data-testid="page-ops-style-trainer">
      <header className="space-y-2">
        <p className="text-xs tracking-[0.2em] uppercase text-gray-500">
          {t('ops.trainer.badge')} · {user?.email}
        </p>
        <h1 className="font-display text-3xl text-gray-900" data-testid="heading-ops-style-trainer">
          {t('ops.trainer.title')}
        </h1>
        <p className="text-sm text-gray-600" data-testid="ops-trainer-coverage">
          {t('ops.trainer.coverage')}: {covLine || t('common.loading')}
        </p>
        <p className="text-xs text-gray-500">{t('ops.trainer.modeNote')}</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="space-y-4 border border-gray-200 p-4 rounded-sm bg-white">
          <h2 className="font-sans text-sm tracking-wide text-gray-800">{t('ops.trainer.pasteTitle')}</h2>
          <div
            className="border border-dashed border-gray-300 min-h-[180px] flex items-center justify-center bg-gray-50 cursor-pointer"
            data-testid="ops-trainer-dropzone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
          >
            {previewUrl ? (
              <img src={previewUrl} alt="" className="max-h-56 object-contain" />
            ) : (
              <p className="text-sm text-gray-500 px-4 text-center">{t('ops.trainer.dropHint')}</p>
            )}
          </div>
          <label className="block text-xs text-gray-500">{t('ops.trainer.orText')}</label>
          <textarea
            data-testid="input-ops-trainer-text"
            className="w-full min-h-[88px] border border-gray-200 p-2 text-sm"
            value={pasteText}
            onChange={(e) => setPasteText(e.target.value)}
            placeholder={t('ops.trainer.textPlaceholder')}
          />
          <label className="block text-xs text-gray-500">{t('ops.trainer.orUrl')}</label>
          <input
            data-testid="input-ops-trainer-url"
            className="w-full border border-gray-200 p-2 text-sm"
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            placeholder="https://"
          />
          <button
            type="button"
            data-testid="btn-ops-trainer-analyze"
            className="min-h-[44px] w-full bg-black text-white text-sm disabled:opacity-50"
            disabled={analyzing}
            onClick={runAnalyze}
          >
            {analyzing ? t('ops.trainer.analyzing') : t('ops.trainer.analyze')}
          </button>
          {analyzing && (
            <p className="text-xs text-gray-500 animate-pulse" data-testid="ops-trainer-left-busy">
              {t('ops.trainer.processing')}
            </p>
          )}
        </section>

        <section className="space-y-3 border border-gray-200 p-4 rounded-sm bg-white">
          <h2 className="font-sans text-sm tracking-wide text-gray-800">{t('ops.trainer.confirmTitle')}</h2>
          {analyzing ? (
            <div
              className="space-y-3"
              data-testid="ops-trainer-skeleton"
              role="status"
              aria-busy="true"
              aria-label={t('ops.trainer.processing')}
            >
              <p className="text-xs text-gray-500 animate-pulse">{t('ops.trainer.processing')}</p>
              <div className="flex flex-wrap gap-2">
                <div className="h-7 w-16 rounded bg-gray-200 animate-pulse" />
                <div className="h-7 w-20 rounded bg-gray-200 animate-pulse" />
                <div className="h-7 w-14 rounded bg-gray-200 animate-pulse" />
                <div className="h-7 w-24 rounded bg-gray-200 animate-pulse" />
              </div>
              {(['prefix', 'fact', 'quote', 'context', 'ending'] as const).map((key) => (
                <div key={key} className="space-y-1">
                  <div className="h-3 w-12 rounded bg-gray-100 animate-pulse" />
                  <div className="h-12 w-full rounded bg-gray-200 animate-pulse" />
                </div>
              ))}
              <div className="h-20 w-full rounded bg-gray-200 animate-pulse" />
              <div className="flex gap-2">
                <div className="h-11 flex-1 rounded bg-gray-200 animate-pulse" />
                <div className="h-11 flex-1 rounded bg-gray-300 animate-pulse" />
              </div>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap gap-2 text-xs">
                <select data-testid="select-ops-trainer-lang" value={language} onChange={(e) => setLanguage(e.target.value as TrainerLang)} className="border p-1">
                  <option value="zh-TW">zh-TW</option>
                  <option value="en">en</option>
                  <option value="ja">ja</option>
                </select>
                <select data-testid="select-ops-trainer-domain" value={domain} onChange={(e) => setDomain(e.target.value as TrainerDomain)} className="border p-1">
                  <option value="fashion">fashion</option>
                  <option value="food">food</option>
                  <option value="trend">trend</option>
                </select>
                <select data-testid="select-ops-trainer-length" value={lengthBucket} onChange={(e) => setLengthBucket(e.target.value as TrainerLength)} className="border p-1">
                  <option value="short">short</option>
                  <option value="long">long</option>
                </select>
                <select data-testid="select-ops-trainer-profile" value={writeProfile} onChange={(e) => setWriteProfile(e.target.value as WriteProfile)} className="border p-1">
                  <option value="news_recap">news_recap</option>
                  <option value="hook_gossip">hook_gossip</option>
                </select>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  data-testid="chk-ops-trainer-negative"
                  checked={refType === 'negative'}
                  onChange={(e) => setRefType(e.target.checked ? 'negative' : 'positive')}
                />
                {t('ops.trainer.negative')}
              </label>
              {(['prefix', 'fact', 'quote', 'context', 'ending'] as const).map((key) => (
                <div key={key}>
                  <label className="text-xs text-gray-500">{key}</label>
                  <textarea
                    data-testid={`input-ops-trainer-slot-${key}`}
                    className="w-full border border-gray-200 p-2 text-sm min-h-[48px]"
                    value={structure[key]}
                    onChange={(e) => setSlot(key, e.target.value)}
                  />
                </div>
              ))}
              <textarea
                data-testid="input-ops-trainer-body"
                className="w-full border border-gray-200 p-2 text-sm min-h-[80px]"
                value={bodyText}
                onChange={(e) => setBodyText(e.target.value)}
                placeholder={t('ops.trainer.bodyPlaceholder')}
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  data-testid="btn-ops-trainer-reanalyze"
                  className="min-h-[44px] flex-1 border border-gray-300 text-sm"
                  onClick={runAnalyze}
                >
                  {t('ops.trainer.reanalyze')}
                </button>
                <button
                  type="button"
                  data-testid="btn-ops-trainer-confirm"
                  className="min-h-[44px] flex-1 bg-black text-white text-sm disabled:opacity-50"
                  disabled={saving}
                  onClick={onConfirm}
                >
                  {saving ? t('common.processing') : t('ops.trainer.confirmMongo')}
                </button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
