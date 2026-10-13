/**
 * 舊頻道列表改由「我的頻道」三格設立板承接。
 */
import { Navigate } from 'react-router-dom';

export default function Channels() {
  return <Navigate to="/my-channel" replace />;
}
