/** Decorative 4-point star (neobrutalist style, D-015). Hidden from screen readers. */
export function Sparkle({ className = '', fillClassName = 'fill-brut-yellow' }: { className?: string; fillClassName?: string }) {
  return (
    <svg viewBox="0 0 32 32" aria-hidden className={`pointer-events-none shrink-0 ${className}`}>
      <path
        d="M16 2 L17.5 14.5 L30 16 L17.5 17.5 L16 30 L14.5 17.5 L2 16 L14.5 14.5 Z"
        className={`${fillClassName} stroke-brut-ink`}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  )
}
