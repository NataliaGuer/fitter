import type { ComponentType, SVGProps } from 'react'

/** Icon inside a bordered pastel circle with a hard shadow (neobrutalist style, D-015). */
export function IconCircle({
  Icon,
  bgClassName,
}: {
  Icon: ComponentType<SVGProps<SVGSVGElement>>
  /** Pastel background, e.g. "bg-brut-mint": the icon is always black on it. */
  bgClassName: string
}) {
  return (
    <span
      aria-hidden
      className={`flex size-10 shrink-0 items-center justify-center rounded-full border-2 border-brut-ink text-brut-black shadow-brut-sm ${bgClassName}`}
    >
      <Icon width={20} height={20} />
    </span>
  )
}
