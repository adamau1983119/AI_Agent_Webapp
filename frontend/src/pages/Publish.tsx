/**
 * 一鍵發布：尚未開放，只顯示敬請期待。
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useTranslation } from '../i18n';

export default function Publish() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) navigate('/login');
  }, [isAuthenticated, navigate]);

  return (
    <div
      className="min-h-[50vh] flex items-center justify-center p-8"
      data-testid="page-publish-soon"
    >
      <p className="text-sm tracking-[0.12em] text-gray-800">{t('publish.soonOnly')}</p>
    </div>
  );
}
