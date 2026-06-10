/**
 * 排程管理頁 — Sidebar /schedule
 * 唯讀檢視今日時段與排程服務狀態（GET /schedules、/schedules/status）
 * 手動生成請至 Dashboard（避免本頁誤觸 DeepSeek 大量請求）
 */
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useTranslation } from '@/i18n'
import { useAuthStore } from '@/stores/authStore'
import { schedulesAPI } from '@/api/schedules'
import type { Schedule } from '@/types'
import toast from 'react-hot-toast'

type SchedulerStatus = {
  status: string
  jobs: Array<{ id: string; next_run_time: string | null }>
}

export default function Schedule() {
  usePageTitle()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()

  const [isLoading, setIsLoading] = useState(true)
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadData()
  }, [isAuthenticated, navigate])

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [list, status] = await Promise.all([
        schedulesAPI.getSchedules(),
        schedulesAPI.getSchedulerStatus(),
      ])
      setSchedules(list)
      setSchedulerStatus(status)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t('common.failed')
      toast.error(message || t('schedule.loadFailed'))
    } finally {
      setIsLoading(false)
    }
  }

  const statusLabel = (status: Schedule['status']) => {
    const key = `schedule.status.${status}` as const
    return t(key)
  }

  const serviceRunning =
    schedulerStatus?.status === 'running' ||
    schedulerStatus?.jobs?.some((j) => j.next_run_time)

  return (
    <div className="p-6 max-w-4xl">
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{t('schedule.title')}</h1>
          <p className="text-gray-600 mt-1">{t('schedule.subtitle')}</p>
        </div>
        <button
          type="button"
          onClick={loadData}
          disabled={isLoading}
          data-testid="btn-schedule-refresh"
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          {t('schedule.refresh')}
        </button>
      </div>

      {isLoading ? (
        <p className="text-gray-500">{t('common.loading')}</p>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">
              {t('schedule.serviceStatus')}
            </h2>
            <p className="text-sm text-gray-600 mb-2">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  serviceRunning
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {serviceRunning ? t('schedule.running') : t('schedule.stopped')}
              </span>
              {schedulerStatus?.status && (
                <span className="ml-2 text-gray-500">({schedulerStatus.status})</span>
              )}
            </p>
            {schedulerStatus?.jobs?.length ? (
              <ul className="text-sm text-gray-600 space-y-1 mt-3">
                {schedulerStatus.jobs.map((job) => (
                  <li key={job.id}>
                    <span className="font-mono text-xs bg-gray-100 px-1 rounded">{job.id}</span>
                    {job.next_run_time && (
                      <span className="ml-2">
                        → {new Date(job.next_run_time).toLocaleString()}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500 mt-2">{t('schedule.noJobs')}</p>
            )}
            <p className="text-xs text-gray-500 mt-4 border-t pt-3">{t('schedule.info6h')}</p>
          </div>

          <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
            <h2 className="text-lg font-semibold text-gray-800 px-6 pt-6 pb-2">
              {t('schedule.todaySlots')}
            </h2>
            {schedules.length === 0 ? (
              <p className="px-6 pb-6 text-gray-500 text-sm">{t('schedule.empty')}</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-left text-gray-600">
                    <tr>
                      <th className="px-6 py-3 font-medium">{t('schedule.date')}</th>
                      <th className="px-6 py-3 font-medium">{t('schedule.timeSlot')}</th>
                      <th className="px-6 py-3 font-medium">{t('schedule.statusLabel')}</th>
                      <th className="px-6 py-3 font-medium">{t('schedule.topicsCount')}</th>
                      <th className="px-6 py-3 font-medium">{t('schedule.completedAt')}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {schedules.map((row, i) => (
                      <tr key={`${row.date}-${row.timeSlot}-${i}`}>
                        <td className="px-6 py-3">{row.date}</td>
                        <td className="px-6 py-3 font-mono">{row.timeSlot}</td>
                        <td className="px-6 py-3">
                          <span
                            className={`inline-flex px-2 py-0.5 rounded text-xs ${
                              row.status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : row.status === 'processing'
                                  ? 'bg-blue-100 text-blue-800'
                                  : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {statusLabel(row.status)}
                          </span>
                        </td>
                        <td className="px-6 py-3">{row.topicsCount}</td>
                        <td className="px-6 py-3 text-gray-500">
                          {row.completedAt
                            ? new Date(row.completedAt).toLocaleString()
                            : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="bg-amber-50 border border-amber-100 rounded-lg p-4 text-sm">
            <p className="text-amber-900 font-medium">{t('schedule.generateHintTitle')}</p>
            <p className="text-amber-800 mt-1">{t('schedule.generateHint')}</p>
            <Link
              to="/dashboard"
              data-testid="link-schedule-to-dashboard"
              className="inline-block mt-2 text-purple-600 hover:text-purple-800 font-medium"
            >
              {t('nav.dashboard')} →
            </Link>
          </div>
        </>
      )}
    </div>
  )
}
