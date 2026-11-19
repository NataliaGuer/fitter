import { ChevronLeft, ChevronRight } from '@gravity-ui/icons'
import { Button, Card } from '@heroui/react'
import { getLocalTimeZone, isToday, today } from '@internationalized/date'
import { type TouchEvent, useRef, useState } from 'react'

import { weekdayName, weekLabel, weekOf } from './week'

/** Minimum horizontal movement (px) for a swipe to change week. */
const SWIPE_THRESHOLD = 50

/** Home card with a week (Monday → Sunday), today highlighted; swipe or arrows to change week. */
export function WeekCalendarCard() {
  const timeZone = getLocalTimeZone()
  // Weeks relative to the current one (0 = current). Not persisted: the app always opens on the current week.
  const [weekOffset, setWeekOffset] = useState(0)
  const touchStart = useRef<{ x: number; y: number } | null>(null)

  const days = weekOf(today(timeZone).add({ weeks: weekOffset }))
  const title = weekOffset === 0 ? 'questa settimana' : weekLabel(days)

  function handleTouchStart(event: TouchEvent) {
    const touch = event.touches[0]
    touchStart.current = { x: touch.clientX, y: touch.clientY }
  }

  function handleTouchEnd(event: TouchEvent) {
    const start = touchStart.current
    touchStart.current = null
    if (start === null) return
    const touch = event.changedTouches[0]
    const dx = touch.clientX - start.x
    const dy = touch.clientY - start.y
    // Only mostly-horizontal gestures change week, so vertical page scrolling stays free.
    if (Math.abs(dx) < SWIPE_THRESHOLD || Math.abs(dx) <= Math.abs(dy)) return
    // Swipe left → next week, swipe right → previous week.
    setWeekOffset((offset) => offset + (dx < 0 ? 1 : -1))
  }

  return (
    <Card>
      <Card.Header className="flex-row items-center justify-between gap-2">
        <Button
          isIconOnly
          size="sm"
          variant="ghost"
          aria-label="Settimana precedente"
          onPress={() => setWeekOffset((offset) => offset - 1)}
        >
          <ChevronLeft aria-hidden />
        </Button>
        <Card.Title aria-live="polite" className="text-center text-lg font-bold">
          {title}
        </Card.Title>
        <Button
          isIconOnly
          size="sm"
          variant="ghost"
          aria-label="Settimana successiva"
          onPress={() => setWeekOffset((offset) => offset + 1)}
        >
          <ChevronRight aria-hidden />
        </Button>
      </Card.Header>
      <Card.Content>
        <ol className="grid grid-cols-7 gap-1" onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
          {days.map((day) => {
            const current = isToday(day, timeZone)
            return (
              <li
                key={day.toString()}
                aria-current={current ? 'date' : undefined}
                className="flex flex-col items-center gap-1"
              >
                <span className={`text-xs ${current ? 'font-bold text-foreground' : 'text-muted'}`}>
                  {weekdayName(day)}
                </span>
                <span
                  className={`flex size-9 items-center justify-center rounded-full border-2 text-sm font-semibold ${
                    current
                      ? 'border-brut-ink bg-accent text-accent-foreground shadow-brut-sm'
                      : 'border-transparent'
                  }`}
                >
                  {day.day}
                </span>
                {/* Reserved for the routine indicator of the day (future feature). */}
                <span aria-hidden className="size-1.5" />
              </li>
            )
          })}
        </ol>
      </Card.Content>
    </Card>
  )
}
