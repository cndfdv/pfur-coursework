export default function Loader() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="rounded-xl border border-border bg-surface p-5 space-y-3"
        >
          <div className="skeleton h-5 w-3/4 rounded" />
          <div className="skeleton h-3 w-1/2 rounded" />
          <div className="flex gap-2">
            <div className="skeleton h-5 w-14 rounded-md" />
            <div className="skeleton h-5 w-14 rounded-md" />
          </div>
          <div className="space-y-1.5">
            <div className="skeleton h-3 w-full rounded" />
            <div className="skeleton h-3 w-[95%] rounded" />
            <div className="skeleton h-3 w-[80%] rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}
