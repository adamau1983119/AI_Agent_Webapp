/**
 * Alter Ego 登入後導流（PD-AE1-F03）
 */
import { alterEgoApi, type DnaStatus } from '@/api/alterEgo';

export const ONBOARDING_PATH = '/onboarding/alter-ego';
export const MY_CHANNEL_PATH = '/my-channel';

/** 僅明確完成態離開 onboarding；未知／缺欄位視為 pending（避免誤跳 my-channel） */
export function pathAfterDnaStatus(status: DnaStatus | string | null | undefined): string {
  if (status === 'active' || status === 'skipped' || status === 'legacy_only') {
    return MY_CHANNEL_PATH;
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
    return pathAfterDnaStatus(status?.dna_status);
  } catch {
    // 狀態讀取失敗時進 onboarding，利於 E0-AE-1 手測（勿默默進 my-channel）
    return ONBOARDING_PATH;
  }
}
