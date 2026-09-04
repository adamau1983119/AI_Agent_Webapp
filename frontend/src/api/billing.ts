/**
 * Billing API — wallet snapshot + Stripe Checkout (no secrets in client).
 */
import { fetchAPI, fetchAPIEnvelope } from './client';

export interface CreditPack {
  id: string;
  credits: number;
  amount_cents: number;
  currency: string;
}

export interface CreditBalance {
  balance: number;
  free: number;
  purchased: number;
  welcome_count: number;
}

export const billingApi = {
  getBalance: () => fetchAPIEnvelope<CreditBalance>('/billing/balance'),

  getPacks: () => fetchAPI<CreditPack[]>('/billing/packs'),

  startCheckout: (packId: string) =>
    fetchAPI<{ checkout_url: string }>('/billing/checkout', {
      method: 'POST',
      body: JSON.stringify({ pack_id: packId }),
      skipErrorHandler: true,
    }),
};
