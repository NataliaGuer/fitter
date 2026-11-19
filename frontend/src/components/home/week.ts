import { type CalendarDate, getLocalTimeZone, startOfWeek, today } from '@internationalized/date'

export const LOCALE = 'it-IT'

/** The 7 days (Monday → Sunday) of the week containing `reference`. */
export function weekOf(reference: CalendarDate): CalendarDate[] {
  const monday = startOfWeek(reference, LOCALE, 'mon')
  return Array.from({ length: 7 }, (_, i) => monday.add({ days: i }))
}

/** The current week in the device time zone. */
export function currentWeek(timeZone: string = getLocalTimeZone()): CalendarDate[] {
  return weekOf(today(timeZone))
}

const weekdayFormatter = new Intl.DateTimeFormat(LOCALE, { weekday: 'short', timeZone: 'UTC' })

// Calendar dates have no time zone: format them as UTC midnight so the day never shifts.
function asUtc(date: CalendarDate): Date {
  return date.toDate('UTC')
}

/** Abbreviated weekday, e.g. "lun". */
export function weekdayName(date: CalendarDate): string {
  return weekdayFormatter.format(asUtc(date)).replace('.', '')
}

const shortMonthFormatter = new Intl.DateTimeFormat(LOCALE, { month: 'short', timeZone: 'UTC' })

/** Day range of a week without the year, e.g. "9 – 15 nov", "30 nov – 6 dic". */
export function weekLabel(days: CalendarDate[]): string {
  const first = days[0]
  const last = days[days.length - 1]
  const lastMonth = shortMonthFormatter.format(asUtc(last))
  if (first.month === last.month) {
    return `${first.day} – ${last.day} ${lastMonth}`
  }
  return `${first.day} ${shortMonthFormatter.format(asUtc(first))} – ${last.day} ${lastMonth}`
}
