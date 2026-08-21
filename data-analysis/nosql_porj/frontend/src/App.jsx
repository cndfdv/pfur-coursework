import { useState } from 'react';
import SearchBar from './components/SearchBar.jsx';
import ResultCard from './components/ResultCard.jsx';
import StatsPanel from './components/StatsPanel.jsx';
import Loader from './components/Loader.jsx';
import { searchArticles } from './api.js';

export default function App() {
  const [tab, setTab] = useState('search');
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (q) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    setQuery(trimmed);
    setLoading(true);
    setError(null);
    try {
      const res = await searchArticles(trimmed, 10);
      setData(res);
    } catch (e) {
      setError(e.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const hasResults = data && data.results && data.results.length > 0;
  const isInitial = !data && !loading && !error && tab === 'search';

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-border/60 bg-surface/40 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-indigo-400 flex items-center justify-center font-bold">
              α
            </div>
            <span className="font-semibold tracking-tight">arxiv.search</span>
          </div>
          <nav className="flex gap-1 bg-surface rounded-lg p-1 border border-border">
            <button
              onClick={() => setTab('search')}
              className={`px-4 py-1.5 rounded-md text-sm transition ${
                tab === 'search'
                  ? 'bg-accent text-white'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Search
            </button>
            <button
              onClick={() => setTab('analytics')}
              className={`px-4 py-1.5 rounded-md text-sm transition ${
                tab === 'analytics'
                  ? 'bg-accent text-white'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Analytics
            </button>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 pb-16">
        {tab === 'search' && (
          <>
            {isInitial ? (
              <div className="flex flex-col items-center justify-center min-h-[70vh] gap-6">
                <div className="text-center space-y-3">
                  <h1 className="text-4xl font-semibold tracking-tight">
                    Semantic search over arXiv
                  </h1>
                  <p className="text-text-secondary max-w-lg mx-auto">
                    Describe what you're looking for — not just keywords. Vectors do the rest.
                  </p>
                </div>
                <div className="w-full max-w-2xl">
                  <SearchBar onSearch={handleSearch} autoFocus />
                </div>
              </div>
            ) : (
              <div className="pt-6 space-y-6">
                <SearchBar onSearch={handleSearch} value={query} compact />

                {loading && <Loader />}

                {error && (
                  <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-red-300">
                    {error}
                  </div>
                )}

                {!loading && data && (
                  <div className="flex items-center justify-between text-sm text-text-secondary">
                    <span>
                      {data.total} result{data.total === 1 ? '' : 's'}
                      {' · '}
                      {data.query_time_ms} ms
                    </span>
                    {data.cached && (
                      <span className="px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-300 text-xs border border-emerald-500/30">
                        cached
                      </span>
                    )}
                  </div>
                )}

                {!loading && hasResults && (
                  <div className="space-y-3">
                    {data.results.map((r) => (
                      <ResultCard key={r.arxiv_id} article={r} />
                    ))}
                  </div>
                )}

                {!loading && data && !hasResults && (
                  <div className="text-center py-16 text-text-secondary">
                    No results. Try a different query.
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {tab === 'analytics' && <StatsPanel />}
      </main>

      <footer className="border-t border-border/40 py-4 text-center text-xs text-text-secondary">
        Qdrant · Redis · ClickHouse · MongoDB · FastAPI · React
      </footer>
    </div>
  );
}
