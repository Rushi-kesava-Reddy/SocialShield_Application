import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Initialize theme mode from localStorage immediately on boot to prevent flashing
const localDark = localStorage.getItem('ss_theme_dark');
if (localDark === '0') {
  document.documentElement.classList.add('light-theme');
} else {
  document.documentElement.classList.remove('light-theme');
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
