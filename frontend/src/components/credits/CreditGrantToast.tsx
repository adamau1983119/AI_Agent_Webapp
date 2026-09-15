/**
 * Once-per-HKT-day toast when login grants landed. Not a modal.
 */
import { useEffect } from 'react'
import toast from 'react-hot-toast'
import type { CreditBalance } from '@/api/billing'
import { useTranslation } from '@/i18n'

const LS_KEY = 'credits-grant-toast-hkt'

export default function CreditGrantToast({ credits }: { credits?: CreditBalance }) {
  const { t } = useTranslation()

  useEffect(() => {
    if (!credits) return
    const day = String(credits.last_grant_hkt || '')
    const amount = Number(credits.last_grant_amount || 0)
    if (!day || amount <= 0) return
    try {
      if (localStorage.getItem(LS_KEY) === day) return
      localStorage.setItem(LS_KEY, day)
    } catch {
      return
    }
    const kind = String(credits.last_grant_kind || '')
    if (kind === 'welcome' || kind === 'legacy_topup') {
      toast.success(
        t('credits.grantWelcome', {
          n: String(amount),
          step: String(credits.welcome_count ?? 1),
        })
      )
      return
    }
    toast.success(t('credits.grantDaily', { n: String(amount) }))
  }, [credits, t])

  return null
}
