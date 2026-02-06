/**
 * 認證 API
 * Phase 2: 會員系統
 */
import { fetchAPI, API_BASE_URL } from './client';

// 類型定義
export interface User {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  language: 'zh-TW' | 'en' | 'ja';
  role: 'user' | 'admin' | 'tester' | 'premium';
  status: 'active' | 'inactive' | 'suspended' | 'deleted';
  email_verified: boolean;
  google_id?: string;
  created_at: string;
  last_login_at?: string;
  warning?: string; // 警告訊息（例如：郵件發送失敗）
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
  language?: 'zh-TW' | 'en' | 'ja';
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface FeatureFlags {
  [key: string]: boolean;
}

// API 函數
export const authApi = {
  /**
   * 檢查 Email 是否可用
   */
  checkEmailAvailable: async (email: string): Promise<{ available: boolean; message: string | null }> => {
    return fetchAPI<{ available: boolean; message: string | null }>(`/auth/check-email?email=${encodeURIComponent(email)}`, {
      method: 'GET',
    });
  },

  /**
   * 註冊新用戶
   */
  register: async (data: RegisterRequest): Promise<User> => {
    return fetchAPI<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * 登入
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return fetchAPI<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * 取得當前用戶資訊
   */
  getCurrentUser: async (): Promise<User> => {
    return fetchAPI<User>('/auth/me');
  },

  /**
   * 驗證 Email
   */
  verifyEmail: async (token: string): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>(`/auth/verify-email?token=${encodeURIComponent(token)}`, {
      method: 'POST',
    });
  },

  /**
   * 重新發送驗證郵件
   */
  resendVerification: async (email: string): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>('/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  /**
   * 忘記密碼
   */
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  /**
   * 重設密碼
   */
  resetPassword: async (data: PasswordResetConfirm): Promise<{ message: string }> => {
    return fetchAPI<{ message: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Google OAuth 登入 URL
   */
  getGoogleLoginUrl: (): string => {
    const baseUrl = API_BASE_URL.replace('/api/v1', '');
    return `${baseUrl}/api/v1/auth/google/login`;
  },

  /**
   * 取得當前用戶可用的功能
   */
  getFeatures: async (): Promise<{ features: FeatureFlags }> => {
    return fetchAPI<{ features: FeatureFlags }>('/features/me', {
      skipErrorHandler: true,
    });
  },

  /**
   * 檢查特定功能是否啟用
   */
  checkFeature: async (featureName: string): Promise<{ name: string; enabled: boolean }> => {
    return fetchAPI<{ name: string; enabled: boolean }>(`/features/check/${featureName}`, {
      skipErrorHandler: true,
    });
  },
};

// Token 管理
const TOKEN_KEY = 'auth_token';

export const tokenManager = {
  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken: (token: string): void => {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken: (): void => {
    localStorage.removeItem(TOKEN_KEY);
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem(TOKEN_KEY);
  },
};
