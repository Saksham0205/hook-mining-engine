import { useEffect, useState } from 'react';
import { MineTab } from './components/MineTab.jsx';
import { LibraryTab } from './components/LibraryTab.jsx';
import { GenerateTab } from './components/GenerateTab.jsx';

const TAB_MINE = 'mine';
const TAB_LIBRARY = 'library';
const TAB_GENERATE = 'generate';

export default function App({ apiBase = '' }) {
  const [tab, setTab] = useState(TAB_MINE);
  const [backendOk, setBackendOk] = useState(null);
  const [healthHint, setHealthHint] = useState('Connecting…');

  useEffect(() => {
    const prefix = `${apiBase}`.replace(/\/$/, '');
    let cancelled = false;
    fetch(`${prefix}/api/health`)
      .then((r) => {
        if (!r.ok) throw new Error('health failed');
        return r.json();
      })
      .then((h) => {
        if (!cancelled) {
          setBackendOk(true);
          const n = typeof h?.hooks_count === 'number' ? h.hooks_count : '—';
          setHealthHint(`Connected · hooks in DB: ${n}`);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setBackendOk(false);
          setHealthHint('Disconnected — start backend on :8000');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  return (
    <div className="pixii-app">
      <header className="pixii-navbar">
        <div className="pixii-brand">
          <div className="pixii-logo-box" aria-hidden>
            P
          </div>
          <div className="pixii-brand-text" style={{ minWidth: 0 }}>
            <div className="pixii-app-name">Pixii Hook Mining Engine</div>
            <div className="pixii-app-sub">
              Mine viral hooks, refine your library, generate Pixii posts
            </div>
          </div>
        </div>
        <div
          className={`pixii-status-pill ${backendOk ? 'pixii-status-pill--ok' : 'pixii-status-pill--bad'}`}
          role="status"
        >
          <span
            className={`pixii-status-dot ${backendOk ? 'pixii-status-dot--ok' : 'pixii-status-dot--bad'}`}
            aria-hidden
          />
          <span>{healthHint}</span>
        </div>
      </header>

      <nav className="pixii-tabs" aria-label="Primary">
        <button
          type="button"
          className={`pixii-tab ${tab === TAB_MINE ? 'pixii-tab--active' : ''}`}
          onClick={() => setTab(TAB_MINE)}
        >
          Mine
        </button>
        <button
          type="button"
          className={`pixii-tab ${tab === TAB_LIBRARY ? 'pixii-tab--active' : ''}`}
          onClick={() => setTab(TAB_LIBRARY)}
        >
          Library
        </button>
        <button
          type="button"
          className={`pixii-tab ${tab === TAB_GENERATE ? 'pixii-tab--active' : ''}`}
          onClick={() => setTab(TAB_GENERATE)}
        >
          Generate
        </button>
      </nav>

      <main className="pixii-main">
        <div className="pixii-content">
          {tab === TAB_MINE && <MineTab apiBase={apiBase} />}
          {tab === TAB_LIBRARY && <LibraryTab apiBase={apiBase} />}
          {tab === TAB_GENERATE && <GenerateTab apiBase={apiBase} />}
        </div>
      </main>

      <footer className="pixii-footer">
        Built for Pixii.ai · Powered by Groq (llama-3.3-70b-versatile)
      </footer>
    </div>
  );
}
