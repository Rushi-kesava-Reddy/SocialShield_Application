// ─── App Router ───────────────────────────────────────────────────────────────
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import SplashPage     from './pages/SplashPage';
import OnboardingPage from './pages/OnboardingPage';
import AuthPage       from './pages/AuthPage';
import Layout         from './components/Layout';
import HomePage       from './pages/HomePage';
import ScanPage       from './pages/ScanPage';
import ResultPage     from './pages/ResultPage';
import HistoryPage    from './pages/HistoryPage';
import FraudMapPage   from './pages/FraudMapPage';
import SettingsPage   from './pages/SettingsPage';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  return user ? children : <Navigate to="/auth" replace />;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  return !user ? children : <Navigate to="/home" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"           element={<SplashPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/auth"       element={<PublicRoute><AuthPage /></PublicRoute>} />
          <Route path="/"           element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route path="home"      element={<HomePage />} />
            <Route path="scan/:type" element={<ScanPage />} />
            <Route path="result/:id" element={<ResultPage />} />
            <Route path="history"   element={<HistoryPage />} />
            <Route path="map"       element={<FraudMapPage />} />
            <Route path="settings"  element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
