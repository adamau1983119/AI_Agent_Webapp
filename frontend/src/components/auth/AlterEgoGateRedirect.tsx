import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { resolvePostLoginPath } from '@/lib/alterEgoRouting';

/** 已登入使用者進控制面板。自設頻道由面板上的選擇進入。 */
export function AlterEgoGateRedirect() {
  const [target, setTarget] = useState<string | null>(null);

  useEffect(() => {
    resolvePostLoginPath().then(setTarget);
  }, []);

  if (!target) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF9F7]">
        <LoadingSpinner />
      </div>
    );
  }

  return <Navigate to={target} replace />;
}
