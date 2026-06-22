import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// base is set to '/SocialShield_Application/' for GitHub Pages deployment
// (the site is served at https://rushi-kesava-reddy.github.io/SocialShield_Application/)
export default defineConfig({
  plugins: [react()],
  base: '/SocialShield_Application/',
})
