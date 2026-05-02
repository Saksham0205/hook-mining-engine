import { useCallback, useEffect, useMemo, useState } from 'react';
import { useApi } from '../hooks/useApi.js';

function badgeClass(cat) {
  const k = `${cat || ''}`.trim().toLowerCase();
  const map = {
    curiosity: 'pixii-badge--curiosity',
    pain: 'pixii-badge--pain',
    number: 'pixii-badge--number',
    story: 'pixii-badge--story',
    controversy: 'pixii-badge--controversy',
    transformation: 'pixii-badge--transformation',
    social_proof: 'pixii-badge--social_proof',
  };
  const mod = map[k] || 'pixii-badge--default';
  return `pixii-badge ${mod}`;
}

export function LibraryTab({ apiBase = '' }) {
  const api = useApi(apiBase);
  const [hooks, setHooks] = useState([]);
  const [totalMinedPosts, setTotalMinedPosts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [actionError, setActionError] = useState(null);

  const categoryCount = useMemo(() => {
    const s = new Set(hooks.map((h) => `${h.category || ''}`.trim()).filter(Boolean));
    return s.size;
  }, [hooks]);

  const reload = useCallback(async () => {
    setFetchError(null);
    setLoading(true);
    try {
      const prefix = `${apiBase}`.replace(/\/$/, '');
      const [hooksRes, statsRes] = await Promise.all([
        fetch(`${prefix}/api/hooks`),
        fetch(`${prefix}/api/hooks/stats`),
      ]);
      if (!hooksRes.ok) throw new Error(`Hooks: ${hooksRes.status}`);
      if (!statsRes.ok) throw new Error(`Stats: ${statsRes.status}`);
      const hooksJson = await hooksRes.json();
      const statsJson = await statsRes.json();
      setHooks(Array.isArray(hooksJson?.hooks) ? hooksJson.hooks : []);
      const tp = statsJson?.total_posts_crawled;
      setTotalMinedPosts(typeof tp === 'number' ? tp : null);
    } catch (e) {
      setFetchError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  useEffect(() => {
    reload();
  }, [reload]);

  async function onDelete(id, patternLabel) {
    if (!window.confirm(`Delete hook “${patternLabel}”?`)) return;
    setActionError(null);
    try {
      await api.deleteHook(id);
      await reload();
    } catch (e) {
      setActionError(e.message || String(e));
    }
  }

  return (
    <div className="pixii-stack pixii-stack-lg">
      <div>
        <h2 className="pixii-page-title">Hook library</h2>
        <p className="pixii-page-subtitle">
          Patterns mined from trending titles — delete what you never want to revisit.
        </p>
      </div>

      {fetchError && <div className="pixii-banner-error">{fetchError}</div>}
      {actionError && <div className="pixii-banner-error">{actionError}</div>}

      <section className="pixii-metric-grid">
        <div className="pixii-metric-card">
          <p className="pixii-metric-label">Total patterns</p>
          <p className="pixii-metric-value">{loading ? '…' : hooks.length}</p>
        </div>
        <div className="pixii-metric-card">
          <p className="pixii-metric-label">Posts mined</p>
          <p className="pixii-metric-value">
            {loading ? '…' : totalMinedPosts !== null ? totalMinedPosts : '—'}
          </p>
        </div>
        <div className="pixii-metric-card">
          <p className="pixii-metric-label">Hook categories</p>
          <p className="pixii-metric-value">{loading ? '…' : categoryCount}</p>
        </div>
      </section>

      {loading ? (
        <div className="pixii-empty pixii-empty--solid">Loading hooks…</div>
      ) : hooks.length === 0 ? (
        <div className="pixii-empty">
          No hooks yet. Run Mine to extract patterns — they’ll accumulate here automatically.
        </div>
      ) : (
        <section>
          <p className="pixii-section-label">Your hook library</p>
          <div className="pixii-library-list">
            {hooks.map((h) => (
              <article key={h.id} className="pixii-card pixii-card--last-no-mb">
                <div className="pixii-library-card-row">
                  <div className="pixii-library-main">
                    <div className="pixii-hook-head">
                      <h3 className="pixii-hook-pattern-title">{h.pattern}</h3>
                      <span className={badgeClass(h.category)}>{h.category}</span>
                    </div>
                    <div className="pixii-template-box">{h.template}</div>
                    <p className="pixii-example">{h.example}</p>
                    <p className="pixii-usage-line">
                      Used <strong>{h.usage_count}</strong> times · strength <strong>{h.strength}</strong>
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => onDelete(h.id, h.pattern)}
                    className="pixii-btn-delete"
                    aria-label={`Delete hook ${h.pattern}`}
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
