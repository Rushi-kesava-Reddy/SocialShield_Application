// ─── API Client — Connected to SocialShield FastAPI Backend ──────────────────
import axios from 'axios';

// Backend URL — set VITE_API_URL in frontend/.env to override
export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 2 min — large file uploads
  headers: { 'Content-Type': 'application/json' },
});

// ─── Auth Token Injector ──────────────────────────────────────────────────────
// Reads the token stored by AuthContext (Firebase ID token or demo token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// ─── Response Error Handler ───────────────────────────────────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      // Token expired — clear auth and reload
      localStorage.removeItem('auth_token');
      localStorage.removeItem('ss_user');
      window.location.href = '/auth';
    }
    return Promise.reject(err);
  }
);

// ─── Helpers ──────────────────────────────────────────────────────────────────
const makeFormData = (file) => {
  const fd = new FormData();
  fd.append('file', file);
  return fd;
};

// ─── Scan Endpoints ───────────────────────────────────────────────────────────
export const scanImage   = (file)   => api.post('/api/v1/scan/image',   makeFormData(file), { headers: { 'Content-Type': 'multipart/form-data' } });
export const scanVideo   = (file)   => api.post('/api/v1/scan/video',   makeFormData(file), { headers: { 'Content-Type': 'multipart/form-data' } });
export const scanAudio   = (file)   => api.post('/api/v1/scan/audio',   makeFormData(file), { headers: { 'Content-Type': 'multipart/form-data' } });
export const scanText    = (text)   => api.post('/api/v1/scan/text',    { text });
export const scanUrl     = (url)    => api.post('/api/v1/scan/url',     { url });
export const scanProfile = (data)   => api.post('/api/v1/scan/profile', data);

// ─── History Endpoints ────────────────────────────────────────────────────────
export const getHistory    = (type)  => api.get('/api/v1/history', { params: type ? { media_type: type } : {} });
export const getScanDetail = (id)    => api.get(`/api/v1/history/${id}`);
export const deleteScan    = (id)    => api.delete(`/api/v1/history/${id}`);
export const getUserStats  = ()      => api.get('/api/v1/stats');

// ─── Health Check ─────────────────────────────────────────────────────────────
export const healthCheck   = ()      => api.get('/health');

export default api;
