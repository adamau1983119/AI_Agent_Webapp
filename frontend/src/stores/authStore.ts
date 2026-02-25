/**
 * 認證 Store
 * Phase 2: 會員系統
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, tokenManager, User, LoginRequest, RegisterRequest, FeatureFlags } from '../api/auth';

interface AuthState {
  // 狀態
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  features: FeatureFlags;
  
  // 動作
  login: (data: LoginRequest) => Promise<boolean>;
  register: (data: RegisterRequest) => Promise<boolean>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  setUser: (user: User | null) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  fetchFeatures: () => Promise<void>;
  isFeatureEnabled: (featureName: string) => boolean;
  
  // OAuth
  handleOAuthCallback: (token: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始狀態
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      features: {},
      
      // 登入
      login: async (data: LoginRequest): Promise<boolean> => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authApi.login(data);
          
          // 儲存 Token
          tokenManager.setToken(response.access_token);
          
          // 更新狀態
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          });
          
          // 取得功能列表
          await get().fetchFeatures();
          
          return true;
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || 'Login failed';
          set({ error: message, isLoading: false });
          return false;
        }
      },
      
      // 註冊
      register: async (data: RegisterRequest): Promise<boolean> => {
        set({ isLoading: true, error: null });
        
        try {
          const user = await authApi.register(data);
          set({ isLoading: false });
          
          // 檢查是否有警告訊息（例如：郵件發送失敗）
          if (user.warning) {
            // 警告訊息會在前端顯示，但不阻止註冊成功
            // 前端頁面會處理這個警告
            set({ error: user.warning }); // 使用 error 字段顯示警告（前端會以警告樣式顯示）
          }
          
          return true;
        } catch (error: any) {
          const message = error.response?.data?.detail || error.message || 'Registration failed';
          set({ error: message, isLoading: false });
          return false;
        }
      },
      
      // 登出
      logout: () => {
        tokenManager.removeToken();
        set({
          user: null,
          isAuthenticated: false,
          features: {},
          error: null,
        });
      },
      
      // 取得當前用戶
      fetchCurrentUser: async () => {
        const token = tokenManager.getToken();
        if (!token) {
          set({ user: null, isAuthenticated: false });
          return;
        }
        
        set({ isLoading: true });
        
        try {
          const user = await authApi.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
          
          // 取得功能列表
          await get().fetchFeatures();
        } catch (error) {
          // Token 無效，清除登入狀態
          tokenManager.removeToken();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },
      
      // 設定用戶
      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user });
      },
      
      // 設定錯誤
      setError: (error: string | null) => {
        set({ error });
      },
      
      // 清除錯誤
      clearError: () => {
        set({ error: null });
      },
      
      // 取得功能列表
      fetchFeatures: async () => {
        try {
          const response = await authApi.getFeatures();
          set({ features: response.features });
        } catch (error) {
          // 靜默失敗，使用預設功能
          console.warn('Failed to fetch features:', error);
        }
      },
      
      // 檢查功能是否啟用
      isFeatureEnabled: (featureName: string): boolean => {
        const { features } = get();
        return features[featureName] ?? false;
      },
      
      // 處理 OAuth 回調
      handleOAuthCallback: async (token: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // 儲存 Token
          tokenManager.setToken(token);
          
          // 驗證 token 是否成功存儲
          const storedToken = tokenManager.getToken();
          if (!storedToken || storedToken !== token) {
            throw new Error('Token 存儲失敗');
          }
          
          // 短暫延遲確保 localStorage 已同步
          await new Promise(resolve => setTimeout(resolve, 50));
          
          // 取得用戶資訊
          const user = await authApi.getCurrentUser();
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
          
          // 取得功能列表
          await get().fetchFeatures();
        } catch (error: any) {
          console.error('OAuth callback error:', error);
          tokenManager.removeToken();
          // 注意：這裡無法直接使用 i18n，因為這是 store
          // 錯誤訊息應該從後端返回，後端已經使用 i18n
          // 如果後端沒有返回，使用默認訊息
          const message = error.response?.data?.detail || error.message || 'OAuth authentication failed';
          set({
            user: null,
            isAuthenticated: false,
            error: message,
            isLoading: false,
          });
          throw error; // 重新拋出錯誤，讓調用方知道失敗
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        // 只持久化 isAuthenticated 狀態，用戶資訊會在啟動時重新獲取
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// 初始化：檢查登入狀態
export const initializeAuth = async () => {
  const { fetchCurrentUser } = useAuthStore.getState();
  await fetchCurrentUser();
};

