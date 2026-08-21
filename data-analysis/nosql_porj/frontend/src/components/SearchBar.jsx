import { useEffect, useRef, useState } from 'react';

export default function SearchBar({ onSearch, value = '', autoFocus = false, compact = false }) {
  const [q, setQ] = useState(value);
  const inputRef = useRef(null);

  useEffect(() => setQ(value), [value]);

  useEffect(() => {
    if (autoFocus && inputRef.current) inputRef.current.focus();
  }, [autoFocus]);

  const submit = (e) => {
    e.preventDefault();
    onSearch(q);
  };

  return (
    <form onSubmit={submit} className="w-full">
      <div
        className={`group flex items-center gap-3 bg-surface border border-border rounded-xl transition focus-within:border-accent focus-within:shadow-[0_0_0_4px_rgba(99,102,241,0.15)] ${
          compact ? 'px-4 py-2.5' : 'px-5 py-4'
        }`}
      >
        <svg
          className="w-5 h-5 text-text-secondary flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-4.35-4.35M17 10.5a6.5 6.5 0 11-13 0 6.5 6.5 0 0113 0z"
          />
        </svg>
        <input
          ref={inputRef}
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="e.g. attention mechanism for image segmentation"
          className={`flex-1 bg-transparent outline-none placeholder:text-text-secondary/70 ${
            compact ? 'text-sm' : 'text-lg'
          }`}
        />
        <button
          type="submit"
          className={`rounded-lg bg-accent hover:bg-indigo-500 text-white font-medium transition ${
            compact ? 'px-3 py-1.5 text-sm' : 'px-5 py-2'
          }`}
        >
          Search
        </button>
      </div>
    </form>
  );
}
