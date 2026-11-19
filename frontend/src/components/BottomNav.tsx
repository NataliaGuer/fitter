import { ChartColumn, Flame, House, ListCheck, PlayFill } from '@gravity-ui/icons'
import { Button } from '@heroui/react'
import type { ComponentType, SVGProps } from 'react'

export type NavSection = 'home' | 'plan' | 'start' | 'stats' | 'calories'

type NavItem = {
  id: Exclude<NavSection, 'start'>
  label: string
  Icon: ComponentType<SVGProps<SVGSVGElement>>
}

const LEFT_ITEMS: NavItem[] = [
  { id: 'home', label: 'Home', Icon: House },
  { id: 'plan', label: 'Plan', Icon: ListCheck },
]

const RIGHT_ITEMS: NavItem[] = [
  { id: 'stats', label: 'Stats', Icon: ChartColumn },
  { id: 'calories', label: 'Calories', Icon: Flame },
]

/**
 * Floating bottom navigation bar (CORE-004): icons only, labels exposed to screen readers.
 * The entries do not navigate yet (no router, D-010).
 */
export function BottomNav({ active }: { active: NavSection }) {
  function renderItem({ id, label, Icon }: NavItem) {
    const isActive = id === active
    return (
      <Button
        key={id}
        isIconOnly
        variant="ghost"
        aria-label={label}
        aria-current={isActive ? 'page' : undefined}
        className={
          isActive
            ? 'border-2 border-brut-ink bg-brut-highlight text-brut-black'
            : 'text-muted'
        }
        onPress={() => {}}
      >
        <Icon aria-hidden />
      </Button>
    )
  }

  return (
    <nav
      aria-label="Sezioni"
      className="fixed inset-x-4 bottom-[calc(1rem+env(safe-area-inset-bottom))] z-10 mx-auto max-w-md rounded-xl border-2 border-brut-ink bg-surface px-2 shadow-brut"
    >
      {/* Five equal columns with centered content: Start sits exactly in the middle. The bar is lower than
          the Start button, which sticks out above and below it. */}
      <div className="grid h-12 grid-cols-5 grid-rows-1 place-items-center">
        {LEFT_ITEMS.map(renderItem)}
        <Button
          isIconOnly
          variant="primary"
          aria-label="Start"
          aria-current={active === 'start' ? 'page' : undefined}
          className="size-16 rounded-full"
          onPress={() => {}}
        >
          <PlayFill aria-hidden />
        </Button>
        {RIGHT_ITEMS.map(renderItem)}
      </div>
    </nav>
  )
}
