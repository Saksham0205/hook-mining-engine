import { useCallback, useState } from 'react';

async function parseError(res) {
  let detail = `${res.status} ${res.statusText}`;
  try {
    const raw = await res.text();
    if (!raw) return detail;
    try {
      const j = JSON.parse(raw);
      if (typeof j?.detail === 'string') return j.detail;
      if (Array.isArray(j?.detail))
        return j.detail.map((x) => (typeof x?.msg === 'string' ? x.msg : JSON.stringify(x))).join('; ');
    } catch {
      detail = raw;
    }
  } catch {}
  return detail;
}

export function useApi(baseUrl = '') {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const prefix = `${baseUrl}`.replace(/\/$/, '');

  const health = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${prefix}/api/health`);
      if (!res.ok) throw new Error(await parseError(res));
      return await res.json();
    } catch (e) {
      const msg = e.message || String(e);
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [prefix]);

  const crawl = useCallback(
    async (categories, limit) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${prefix}/api/crawl`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ categories, limit }),
        });
        if (!res.ok) throw new Error(await parseError(res));
        return await res.json();
      } catch (e) {
        const msg = e.message || String(e);
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [prefix],
  );

  const getHooks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${prefix}/api/hooks`);
      if (!res.ok) throw new Error(await parseError(res));
      return await res.json();
    } catch (e) {
      const msg = e.message || String(e);
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [prefix]);

  const deleteHook = useCallback(
    async (id) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${prefix}/api/hooks/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error(await parseError(res));
        try {
          return await res.json();
        } catch {
          return {};
        }
      } catch (e) {
        const msg = e.message || String(e);
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [prefix],
  );

  const generate = useCallback(
    async (payload) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${prefix}/api/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(await parseError(res));
        return await res.json();
      } catch (e) {
        const msg = e.message || String(e);
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [prefix],
  );

  return { crawl, getHooks, deleteHook, generate, health, loading, error, setError };
}
