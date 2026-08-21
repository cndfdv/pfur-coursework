import { useState } from 'react';

function scoreColor(score) {
  const s = Math.max(0, Math.min(1, score));
  if (s >= 0.8) return 'from-emerald-500 to-green-400 text-emerald-950';
  if (s >= 0.65) return 'from-emerald-600 to-emerald-400 text-emerald-50';
  if (s >= 0.5) return 'from-yellow-500 to-amber-400 text-amber-950';
  return 'from-slate-600 to-slate-500 text-slate-100';
}

export default function ResultCard({ article }) {
  const [expanded, setExpanded] = useState(false);
  const { arxiv_id, title, authors, year, categories, abstract, score } = article;

  const preview = abstract?.length > 300 && !expanded ? abstract.slice(0, 300) + '…' : abstract;
  const canExpand = abstract && abstract.length > 300;

  return (
    <article className="group rounded-xl border border-border bg-surface p-5 hover:border-accent/60 hover:shadow-[0_4px_24px_-8px_rgba(99,102,241,0.3)] transition">
      <div className="flex items-start gap-4">
        <div className="flex-1 min-w-0">
          <a
            href={`https://arxiv.org/abs/${arxiv_id}`}
            target="_blank"
            rel="noreferrer"
            className="text-lg font-semibold leading-snug hover:text-accent transition block"
          >
            {title}
          </a>

          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-text-secondary">
            {authors && authors.length > 0 && (
              <span className="truncate max-w-full">
                {authors.slice(0, 4).join(', ')}
                {authors.length > 4 ? ` +${authors.length - 4}` : ''}
              </span>
            )}
            {year && <span>· {year}</span>}
            <span className="font-mono text-xs opacity-70">· {arxiv_id}</span>
          </div>

          {categories && categories.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {categories.map((c) => (
                <span
                  key={c}
                  className="px-2 py-0.5 rounded-md bg-accent/15 text-accent text-xs border border-accent/20"
                >
                  {c}
                </span>
              ))}
            </div>
          )}

          {preview && (
            <p className="mt-3 text-sm text-text-primary/90 leading-relaxed whitespace-pre-line">
              {preview}
              {canExpand && (
                <button
                  onClick={() => setExpanded((v) => !v)}
                  className="ml-1 text-accent hover:underline"
                >
                  {expanded ? 'Show less' : 'Show more'}
                </button>
              )}
            </p>
          )}
        </div>

        <div
          className={`flex-shrink-0 px-2.5 py-1 rounded-md bg-gradient-to-br ${scoreColor(
            score,
          )} text-xs font-semibold tabular-nums`}
          title="cosine similarity"
        >
          {score?.toFixed(3)}
        </div>
      </div>
    </article>
  );
}
