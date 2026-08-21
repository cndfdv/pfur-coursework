import { useEffect, useState } from 'react';
import { fetchStats } from '../api.js';

function StatCard({ label, value, sub }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <div className="text-text-secondary text-xs uppercase tracking-wider">{label}</div>
      <div className="mt-2 text-3xl font-semibold tabular-nums">{value}</div>
      {sub && <div className="mt-1 text-xs text-text-secondary">{sub}</div>}
    </div>
  );
}

function BarChart({ data, valueKey, labelKey, unit = '' }) {
  const max = Math.max(1, ...data.map((d) => d[valueKey]));
  return (
    <div className="space-y-2">
      {data.map((d) => {
        const pct = (d[valueKey] / max) * 100;
        return (
          <div key={d[labelKey]} className="flex items-center gap-3 text-sm">
            <div className="w-20 flex-shrink-0 text-text-secondary tabular-nums">
              {d[labelKey]}
            </div>
            <div className="flex-1 bg-bg rounded-md h-5 overflow-hidden border border-border">
              <div
                className="h-full bg-gradient-to-r from-accent to-indigo-400 transition-all"
                style={{ width: `${pct}%` }}
              />
            </div>
            <div className="w-14 text-right tabular-nums text-text-secondary">
              {d[valueKey]}
              {unit}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function StatsPanel() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    fetchStats()
      .then((d) => alive && setStats(d))
      .catch((e) => alive && setError(e.message))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="pt-10 grid gap-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-24 rounded-xl" />
          ))}
        </div>
        <div className="skeleton h-64 rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="pt-10 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-red-300">
        {error}
      </div>
    );
  }

  if (!stats) return null;

  const totalTopQueries = stats.top_queries?.length || 0;

  return (
    <div className="pt-8 space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard label="Articles in index" value={stats.total_articles?.toLocaleString() ?? 0} />
        <StatCard label="Total searches" value={stats.total_searches?.toLocaleString() ?? 0} />
        <StatCard label="Distinct top queries" value={totalTopQueries} sub="in top-10" />
      </div>

      <section className="rounded-xl border border-border bg-surface p-5">
        <h2 className="font-semibold mb-4">Top queries</h2>
        {stats.top_queries?.length ? (
          <ol className="space-y-2">
            {stats.top_queries.map((q, i) => (
              <li
                key={q.query}
                className="flex items-center justify-between py-1.5 border-b border-border/40 last:border-0"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs text-text-secondary tabular-nums w-5">#{i + 1}</span>
                  <span className="truncate">{q.query}</span>
                </div>
                <span className="text-sm text-text-secondary tabular-nums">{q.count}</span>
              </li>
            ))}
          </ol>
        ) : (
          <div className="text-text-secondary text-sm">No searches yet.</div>
        )}
      </section>

      <section className="rounded-xl border border-border bg-surface p-5">
        <h2 className="font-semibold mb-4">Articles by year</h2>
        {stats.articles_by_year?.length ? (
          <BarChart
            data={stats.articles_by_year}
            labelKey="year"
            valueKey="count"
          />
        ) : (
          <div className="text-text-secondary text-sm">No data.</div>
        )}
      </section>

      <section className="rounded-xl border border-border bg-surface p-5">
        <h2 className="font-semibold mb-4">Articles by category</h2>
        {stats.articles_by_category?.length ? (
          <BarChart
            data={stats.articles_by_category}
            labelKey="category"
            valueKey="count"
          />
        ) : (
          <div className="text-text-secondary text-sm">No data.</div>
        )}
      </section>
    </div>
  );
}
