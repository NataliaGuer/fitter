import { ArrowRightFromSquare, ChartColumn, Flame } from '@gravity-ui/icons'
import { Alert, Button } from '@heroui/react'
import { useState } from 'react'

import type { User } from '../api/auth'
import { errorMessage } from '../api/errors'
import { useAuth } from '../auth/useAuth'
import { BottomNav } from '../components/BottomNav'
import { PlaceholderCard } from '../components/home/PlaceholderCard'
import { WeekCalendarCard } from '../components/home/WeekCalendarCard'
import { Sparkle } from '../components/Sparkle'
import { ThemeSwitch } from '../components/ThemeSwitch'

/** Home dashboard (CORE-004): summary cards and the bottom navigation bar. */
export function HomePage({ user }: { user: User }) {
  const { logout } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [isPending, setIsPending] = useState(false)

  async function handleLogout() {
    setError(null)
    setIsPending(true)
    try {
      // On success the auth state becomes "anonymous" and this screen is replaced by the login.
      await logout()
    } catch (logoutError) {
      // The request did not reach the server: the session is still valid, so we stay here.
      setError(errorMessage(logoutError))
      setIsPending(false)
    }
  }

  return (
    <>
      {/* Bottom padding keeps the last card above the fixed navigation bar. */}
      <main className="mx-auto flex min-h-dvh max-w-md flex-col gap-5 px-4 pt-6 pb-[calc(7rem+env(safe-area-inset-bottom))]">
        <header className="flex items-center justify-between gap-2">
          <div className="flex min-w-0 items-center gap-2">
            <h1 className="truncate text-3xl font-extrabold tracking-tight">ciao, {user.nickname}</h1>
            <Sparkle className="size-7 -rotate-12" />
          </div>
          <div className="flex shrink-0 items-center gap-1">
            <ThemeSwitch />
            <Button isIconOnly variant="ghost" aria-label="Esci" isPending={isPending} onPress={handleLogout}>
              <ArrowRightFromSquare width={20} height={20} aria-hidden />
            </Button>
          </div>
        </header>

        {error !== null && (
          <Alert status="danger">
            <Alert.Indicator />
            <Alert.Content>
              <Alert.Title>{error}</Alert.Title>
            </Alert.Content>
          </Alert>
        )}

        <WeekCalendarCard />
        <PlaceholderCard title="calorie" Icon={Flame} iconBgClassName="bg-brut-pink" />
        <PlaceholderCard title="statistiche" Icon={ChartColumn} iconBgClassName="bg-brut-mint" />
      </main>

      <BottomNav active="home" />
    </>
  )
}
