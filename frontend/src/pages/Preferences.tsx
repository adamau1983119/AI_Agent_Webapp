/**
 * 偏好設定頁 — Sidebar /preferences
 * 內容策展權重與關鍵字（GET/PUT /api/v1/user/preferences）
 * 帳號／語言請至 Header → /settings
 */
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'
import { useAuthStore } from '@/stores/authStore'
import {
  userPreferencesAPI,
  type UserPreferencesData,
} from '@/api/userPreferences'
import toast from 'react-hot-toast'

function normalizeWeights(f: number, food: number, trend: number) {
  const total = f + food + trend
  if (total <= 0) {
    return { fashion_weight: 1 / 3, food_weight: 1 / 3, trend_weight: 1 / 3 }
  }
  return {
    fashion_weight: f / total,
    food_weight: food / total,
    trend_weight: trend / total,
  }
}

export default function Preferences() {
  usePageTitle()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()

  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [fashion, setFashion] = useState(50)
  const [food, setFood] = useState(30)
  const [trend, setTrend] = useState(20)
  const [keywords, setKeywords] = useState('')
  const [excluded, setExcluded] = useState('')
  const [updatedAt, setUpdatedAt] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadPreferences()
  }, [isAuthenticated, navigate])

  const applyFromApi = (data: UserPreferencesData) => {
    setFashion(Math.round(data.fashion_weight * 100))
    setFood(Math.round(data.food_weight * 100))
    setTrend(Math.round(data.trend_weight * 100))
    setKeywords((data.keywords || []).join(', '))
    setExcluded((data.excluded_keywords || []).join(', '))
    setUpdatedAt(data.updated_at || null)
  }

  const loadPreferences = async () => {
    setIsLoading(true)
    try {
      const data = await userPreferencesAPI.getPreferences()
      applyFromApi(data)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t('common.failed')
      toast.error(message || t('preferences.loadFailed'))
    } finally {
      setIsLoading(false)
    }
  }

  const parseList = (raw: string): string[] =>
    raw
      .split(/[,，\n]/)
      .map((s) => s.trim())
      .filter(Boolean)

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const weights = normalizeWeights(fashion, food, trend)
      const data = await userPreferencesAPI.updatePreferences({
        ...weights,
        keywords: parseList(keywords),
        excluded_keywords: parseList(excluded),
      })
      applyFromApi(data)
      toast.success(t('preferences.saved'))
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t('common.failed')
      toast.error(message)
    } finally {
      setIsSaving(false)
    }
  }

  const weightSum = fashion + food + trend

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[40vh]">
        <p className="text-gray-500">{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{t('preferences.title')}</h1>
        <p className="text-gray-600 mt-1">{t('preferences.subtitle')}</p>
        {updatedAt && (
          <p className="text-xs text-gray-400 mt-2">
            {t('preferences.lastUpdated')}: {new Date(updatedAt).toLocaleString()}
          </p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6 space-y-8 mb-6">
        <section>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            {t('preferences.categoryWeights')}
          </h2>
          <p className="text-sm text-gray-500 mb-4">{t('preferences.weightHint')}</p>

          {(['fashion', 'food', 'trend'] as const).map((key) => {
            const labels = {
              fashion: t('preferences.fashion'),
              food: t('preferences.food'),
              trend: t('preferences.trend'),
            }
            const values = { fashion, food, trend }
            const setters = {
              fashion: setFashion,
              food: setFood,
              trend: setTrend,
            }
            return (
              <div key={key} className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-700">{labels[key]}</span>
                  <span className="font-medium text-purple-600">{values[key]}%</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={values[key]}
                  onChange={(e) => setters[key](Number(e.target.value))}
                  className="w-full accent-purple-600"
                  data-testid={`input-preferences-weight-${key}`}
                />
              </div>
            )
          })}

          <p
            className={`text-sm ${Math.abs(weightSum - 100) > 1 ? 'text-amber-600' : 'text-gray-500'}`}
          >
            {t('preferences.weightSum')}: {weightSum}% — {t('preferences.weightNormalizeOnSave')}
          </p>
        </section>

        <section>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('preferences.keywords')}
          </label>
          <p className="text-xs text-gray-500 mb-2">{t('preferences.keywordsHint')}</p>
          <textarea
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            rows={2}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            data-testid="input-preferences-keywords"
          />
        </section>

        <section>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('preferences.excludedKeywords')}
          </label>
          <p className="text-xs text-gray-500 mb-2">{t('preferences.excludedHint')}</p>
          <textarea
            value={excluded}
            onChange={(e) => setExcluded(e.target.value)}
            rows={2}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            data-testid="input-preferences-excluded"
          />
        </section>

        <button
          type="button"
          onClick={handleSave}
          disabled={isSaving}
          data-testid="btn-preferences-save"
          className="px-6 py-2.5 bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-cyan-600 disabled:opacity-50"
        >
          {isSaving ? t('common.loading') : t('profile.save')}
        </button>
      </div>

      <div className="bg-purple-50 border border-purple-100 rounded-lg p-4 text-sm text-gray-700">
        <p className="font-medium text-purple-800">{t('preferences.accountLinkTitle')}</p>
        <p className="mt-1 text-gray-600">{t('preferences.accountLinkDesc')}</p>
        <Link
          to="/settings"
          data-testid="link-preferences-to-settings"
          className="inline-block mt-2 text-purple-600 hover:text-purple-800 font-medium"
        >
          {t('preferences.accountLink')} →
        </Link>
      </div>
    </div>
  )
}
