import { useMemo, useState } from 'react';
import { useApi } from '../hooks/useApi.js';

const NICHES = [
  { label: 'Ecommerce', slug: 'ecommerce' },
  { label: 'Marketing', slug: 'marketing' },
  { label: 'AI Tools', slug: 'ai_tools' },
  { label: 'Startups', slug: 'startups' },
  { label: 'Content', slug: 'content' },
  { label: 'Photography', slug: 'photography' },
];

const LIMITS = [15, 25, 40];

export function MineTab({ apiBase = '' }) {
  const api = useApi(apiBase);
  const [selected, setSelected] = useState(() => new Set(NICHES.map((n) => n.slug)));
  const [limit, setLimit] = useState(25);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Pick niches and run a crawl.');
  const [posts, setPosts] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [localError, setLocalError] = useState(null);

  const nicheCountLabel = useMemo(() => `${selected.size} selected`, [selected]);

  function toggleNiche(slug) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  }

  async function mine() {
    if (loading) return;
    if (!selected.size) {
      setLocalError('Choose at least one niche.');
      return;
    }

    const categories = Array.from(selected);
    setLoading(true);
    setLocalError(null);
    setProgress(10);
    setStatus('Fetching stories from sources…');

    let t45;
    let t70;
    try {
      t45 = setTimeout(() => setProgress((p) => Math.max(p, 45)), 300);
      t70 = setTimeout(() => setProgress((p) => Math.max(p, 70)), 900);

      const data = await api.crawl(categories, limit);

      clearTimeout(t45);
      clearTimeout(t70);

      const nextPosts = Array.isArray(data?.posts) ? data.posts : [];
      const nextHooks = Array.isArray(data?.hooks) ? data.hooks : [];
      setPosts(nextPosts);
      setPatterns(nextHooks);

      setProgress(100);
      setStatus('Mining complete.');
      console.log('[crawl]', data);
      setTimeout(() => setProgress(0), 600);
    } catch (e) {
      if (t45) clearTimeout(t45);
      if (t70) clearTimeout(t70);
      setProgress(0);
      setLocalError(e.message || String(e));
      setStatus('Crawl failed. Check backend logs and GROQ_API_KEY.');
      console.error('[crawl]', e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="pixii-stack">
      {localError && <div className="pixii-banner-error">{localError}</div>}

      <div>
        <p className="pixii-section-label">Select niches</p>
        <div className="pixii-chip-row">
          {NICHES.map((n) => {
            const on = selected.has(n.slug);
            return (
              <button
                key={n.slug}
                type="button"
                onClick={() => toggleNiche(n.slug)}
                className={`pixii-chip${on ? ' pixii-chip--active' : ''}`}
              >
                {n.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="pixii-row-end">
        <div>
          <span className="pixii-label">Posts to analyze</span>
          <div className="pixii-limit-group" style={{ marginTop: 8 }}>
            {LIMITS.map((x) => (
              <button
                key={x}
                type="button"
                onClick={() => setLimit(x)}
                className={`pixii-limit-btn${limit === x ? ' pixii-limit-btn--active' : ''}`}
              >
                {x}
              </button>
            ))}
          </div>
        </div>

        <button type="button" disabled={loading} onClick={mine} className="pixii-btn-primary">
          {loading ? 'Mining…' : 'Mine hooks'}
        </button>
      </div>

      <div>
        <div className="pixii-progress-track">
          <div className="pixii-progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="pixii-status-bar">{status}</div>
      </div>

      <section className="pixii-metric-grid">
        <Metric label="Posts analyzed" value={posts.length ? String(posts.length) : '—'} />
        <Metric label="Hook patterns (last run)" value={patterns.length ? String(patterns.length) : '—'} />
        <Metric label="Niches active" value={nicheCountLabel} />
      </section>

      {patterns.length > 0 && (
        <section>
          <p className="pixii-section-label">Fresh patterns (last run)</p>
          <div className="pixii-chip-row">
            {patterns.map((hp) => (
              <span key={hp.id != null ? String(hp.id) : hp.pattern} className="pixii-pattern-chip">
                {hp.pattern}
              </span>
            ))}
          </div>
        </section>
      )}

      {posts.length === 0 && !loading ? (
        <div className="pixii-empty">
          No mined posts yet. Run a crawl to populate this feed — results depend on trending titles matching your niche
          keywords.
        </div>
      ) : (
        <section>
          <p className="pixii-section-label">Sources & traction</p>
          <div className="pixii-grid-mine-posts">
            {posts.map((p) => (
              <article key={`${p.url}-${p.title}`} className="pixii-card pixii-card--in-grid">
                <div className="pixii-post-card-meta">
                  <span className="pixii-pill-muted">{p.source}</span>
                  <span className="pixii-pill-score">Score {p.score}</span>
                  <span className="pixii-pill-lane">Hook lane · {p.category}</span>
                </div>
                <h4 className="pixii-card-title" style={{ marginTop: 10 }}>
                  {p.title}
                </h4>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="pixii-metric-card">
      <p className="pixii-metric-label">{label}</p>
      <p className="pixii-metric-value">{value}</p>
    </div>
  );
}
