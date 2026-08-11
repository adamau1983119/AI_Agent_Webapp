/**
 * Alter Ego 登入後導流（PD-AE1-F03 · v8 Dashboard-first）
 */
import { alterEgoApi, type DnaStatus } from '@/api/alterEgo';

export const ONBOARDING_PATH = '/onboarding/alter-ego';
export const MY_CHANNEL_PATH = '/my-channel';
export const DASHBOARD_PATH = '/dashboard';

const ALLOWED_POST_LOGIN = new Set([
  DASHBOARD_PATH,
  MY_CHANNEL_PATH,
  '/topics',
  '/inspiration',
]);

function envPostLoginPath(): string | null {
  const raw = import.meta.env.VITE_POST_LOGIN_PATH?.trim();
  if (!raw) return null;
  return ALLOWED_POST_LOGIN.has(raw) ? raw : null;
}

/** 僅明確完成態離開 onboarding；未知／缺欄位視為 pending */
export function pathAfterDnaStatus(status: DnaStatus | string | null | undefined): string {
  if (status === 'active' || status === 'skipped' || status === 'legacy_only') {
    return envPostLoginPath() ?? DASHBOARD_PATH;
  }
  return ONBOARDING_PATH;
}

export function isAlterEgoOnboardingDone(
  status: DnaStatus | string | null | undefined
): boolean {
  return status === 'active' || status === 'skipped' || status === 'legacy_only';
}

export async function resolvePostLoginPath(): Promise<string> {
  try {
    const status = await alterEgoApi.getStatus();
    const path = pathAfterDnaStatus(status?.dna_status);
    if (path === ONBOARDING_PATH) return ONBOARDING_PATH;
    return envPostLoginPath() ?? path;
  } catch {
    return ONBOARDING_PATH;
  }
}
