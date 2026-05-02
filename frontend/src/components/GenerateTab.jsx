import { useEffect, useState } from 'react';
import { useApi } from '../hooks/useApi.js';

const TOPICS = [
  'AI product photography',
  'Pixii lifestyle photos',
  'Replacing photo shoots',
  'Standing out on Amazon',
  'Ecommerce brand growth',
];

const PLATFORMS = ['LinkedIn', 'Instagram', 'Twitter/X'];

export function GenerateTab({ apiBase = '' }) {
  const api = useApi(apiBase);
  const [hooksOptions, setHooksOptions] = useState([]);
  const [selectedHookId, setSelectedHookId] = useState('');
  const [topic, setTopic] = useState(TOPICS[0]);
  const [platform, setPlatform] = useState(PLATFORMS[0]);
  const [variations, setVariations] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [generateError, setGenerateError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.getHooks();
        if (cancelled) return;
        const list = Array.isArray(data?.hooks) ? data.hooks : [];
        setHooksOptions(list);
        if (list.length && !selectedHookId) setSelectedHookId(String(list[0].id));
        setLoadError(null);
      } catch (e) {
        if (!cancelled) setLoadError(e.message || String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function runGenerate() {
    if (!selectedHookId || generating) return;
    const hookIdNum = Number(selectedHookId);
    if (!hookIdNum) {
      setGenerateError('Pick a hook pattern.');
      return;
    }
    setGenerating(true);
    setGenerateError(null);
    setVariations([]);
    try {
      const data = await api.generate({
        hook_id: hookIdNum,
        topic,
        platform,
      });
      const vars = Array.isArray(data?.variations) ? data.variations : [];
      setVariations(vars);
      console.log('[generate]', data);
      if (!vars.length) setGenerateError('No variations returned.');
    } catch (e) {
      setGenerateError(e.message || String(e));
    } finally {
      setGenerating(false);
    }
  }

  async function copyText(text, idx) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIdx(idx);
      setTimeout(() => setCopiedIdx(null), 1500);
    } catch {
      setGenerateError('Could not copy — check clipboard permissions.');
    }
  }

  return (
    <div className="pixii-stack pixii-stack-lg">
      <div>
        <h2 className="pixii-page-title">Generate Pixii posts</h2>
        <p className="pixii-page-subtitle">
          Feed Groq one of your mined hooks plus a Pixii-aligned topic — get three swipe-ready captions.
        </p>
      </div>

      {loadError && <div className="pixii-banner-error">{loadError}</div>}
      {generateError && <div className="pixii-banner-error">{generateError}</div>}

      <section className="pixii-controls-card">
        <div className="pixii-gen-controls-grid">
          <div>
            <label htmlFor="hookSelect" className="pixii-label">
              Hook pattern
            </label>
            <select
              id="hookSelect"
              className="pixii-select"
              value={selectedHookId}
              onChange={(e) => setSelectedHookId(e.target.value)}
            >
              {hooksOptions.length === 0 ? (
                <option value="">No hooks — Mine first</option>
              ) : (
                hooksOptions.map((h) => (
                  <option key={h.id} value={h.id}>
                    {h.pattern}
                  </option>
                ))
              )}
            </select>
          </div>

          <div>
            <label htmlFor="topicSelect" className="pixii-label">
              Topic
            </label>
            <select
              id="topicSelect"
              className="pixii-select"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            >
              {TOPICS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="pixii-gen-actions">
            <div style={{ flex: '1 1 170px', minWidth: '170px' }}>
              <label htmlFor="platformSelect" className="pixii-label">
                Platform
              </label>
              <select
                id="platformSelect"
                className="pixii-select"
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
              >
                {PLATFORMS.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="button"
              onClick={runGenerate}
              disabled={generating || !hooksOptions.length}
              className="pixii-btn-primary"
            >
              Generate ↗
            </button>
          </div>
        </div>
      </section>

      {generating ? (
        <div className="pixii-empty pixii-empty--solid">Generating with Groq…</div>
      ) : variations.length === 0 ? (
        <div className="pixii-empty">
          Outputs appear here once you generate — variants use your hook verbatim and Pixii-safe CTAs.
        </div>
      ) : (
        <section className="pixii-gen-grid">
          {variations.map((txt, idx) => (
            <article key={`${idx}-${txt.slice(0, 22)}`} className="pixii-card pixii-card--in-grid pixii-gen-card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                <span className="pixii-variation-badge">Variation {idx + 1}</span>
                <button
                  type="button"
                  onClick={() => copyText(txt, idx)}
                  className={`pixii-btn-copy${copiedIdx === idx ? ' pixii-btn-copy--success' : ''}`}
                >
                  {copiedIdx === idx ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <p className="pixii-post-text" style={{ marginTop: 12 }}>
                {txt}
              </p>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
