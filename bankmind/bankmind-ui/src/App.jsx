import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CustomerDetail from './pages/CustomerDetail';
import Customers from './pages/Customers';
import ActivityLog from './pages/ActivityLog';
import DemoControls from './pages/DemoControls';

function RequireAuth({ children }) {
  const token = localStorage.getItem('bankmind_token');
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const { hydrate } = useAuthStore();

  useEffect(() => {
    hydrate();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/customers" element={<RequireAuth><Customers /></RequireAuth>} />
        <Route path="/customers/:id" element={<RequireAuth><CustomerDetail /></RequireAuth>} />
        <Route path="/activity" element={<RequireAuth><ActivityLog /></RequireAuth>} />
        <Route path="/demo" element={<RequireAuth><DemoControls /></RequireAuth>} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
