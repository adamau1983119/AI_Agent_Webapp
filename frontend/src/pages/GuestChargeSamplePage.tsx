/**
 * Sample only. zh-TW + ja credit offer cards. Does not replace TopicDetail modal.
 */
import { translateFor } from '@/i18n'
import { useNoindex } from '@/hooks/useNoindex'
import GuestCreditOfferCard from '@/components/welcome/GuestCreditOfferCard'

export default function GuestChargeSamplePage() {
  useNoindex()

  return (
    <div
      data-testid="page-guest-charge-sample"
      className="min-h-[calc(100vh-4rem)] bg-[#F7F5F2] px-4 py-8"
    >
      <p className="text-center text-[10px] text-[#a3a3a3] mb-6 max-w-3xl mx-auto">
        {translateFor('zh-TW', 'guestChargeSample.fontNote')}
      </p>
      <div className="mx-auto max-w-3xl grid gap-6 md:grid-cols-2 items-start">
        <GuestCreditOfferCard
          lang="zh-TW"
          cardTestId="card-guest-charge-sample-zh"
          kicker={`${translateFor('zh-TW', 'guestChargeSample.kicker')} · ${translateFor('zh-TW', 'language.zh-TW')}`}
          registerTestId="btn-guest-charge-sample-register-zh"
          loginTestId="btn-guest-charge-sample-login-zh"
          cancelTestId="btn-guest-charge-sample-cancel-zh"
          showCancel
        />
        <GuestCreditOfferCard
          lang="ja"
          cardTestId="card-guest-charge-sample-ja"
          kicker={`${translateFor('ja', 'guestChargeSample.kicker')} · ${translateFor('ja', 'language.ja')}`}
          registerTestId="btn-guest-charge-sample-register-ja"
          loginTestId="btn-guest-charge-sample-login-ja"
          cancelTestId="btn-guest-charge-sample-cancel-ja"
          showCancel
        />
      </div>
    </div>
  )
}
