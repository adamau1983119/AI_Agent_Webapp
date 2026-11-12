/**
 * Sample only. Welcome mono vs modal brand. Does not replace TopicDetail modal.
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
          kicker={`${translateFor('zh-TW', 'guestChargeSample.kicker')} · Welcome mono`}
          registerTestId="btn-guest-charge-sample-register-zh"
          showLogin={false}
          monoActions
          costValue={null}
          analyticsEnabled={false}
        />
        <GuestCreditOfferCard
          lang="ja"
          cardTestId="card-guest-charge-sample-ja"
          kicker={`${translateFor('ja', 'guestChargeSample.kicker')} · modal`}
          registerTestId="btn-guest-charge-sample-register-ja"
          loginTestId="btn-guest-charge-sample-login-ja"
          cancelTestId="btn-guest-charge-sample-cancel-ja"
          showCancel
          analyticsEnabled={false}
        />
      </div>
    </div>
  )
}
