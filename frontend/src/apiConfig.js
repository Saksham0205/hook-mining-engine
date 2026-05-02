/**
 * API origin with no trailing slash.
 * - Local dev: leave VITE_API_BASE_URL unset → '' (`/api` proxied via vite.config → :8000).
 * - Vercel production build: always use '' so fetches hit `/api` (vercel.json → Render). A stale
 *   VITE_API_BASE_URL would call Render from the browser and fail CORS even though opening
 *   /api/health in a tab works via the proxy.
 * - Non-Vercel production: set VITE_API_BASE_URL and configure backend CORS.
 */
export function getApiBase() {
  if (import.meta.env.VITE_IS_VERCEL_BUILD === '1') {
    return '';
  }
  const raw = import.meta.env.VITE_API_BASE_URL;
  if (raw == null || String(raw).trim() === '') return '';
  return String(raw).trim().replace(/\/$/, '');
}
