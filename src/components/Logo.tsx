/** A tiny heap: 1 / 2 / 3 nodes stacked like a binary heap, the top node highlighted. */
export default function Logo({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2 font-semibold tracking-tight ${className}`}>
      <svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true">
        <circle cx="11" cy="4" r="3" fill="var(--color-accent)" />
        <circle cx="6" cy="11" r="2.6" fill="currentColor" opacity="0.75" />
        <circle cx="16" cy="11" r="2.6" fill="currentColor" opacity="0.75" />
        <circle cx="3" cy="18" r="2.2" fill="currentColor" opacity="0.45" />
        <circle cx="11" cy="18" r="2.2" fill="currentColor" opacity="0.45" />
        <circle cx="19" cy="18" r="2.2" fill="currentColor" opacity="0.45" />
      </svg>
      <span>
        Heap<span className="text-accent">Race</span>
      </span>
    </span>
  );
}
