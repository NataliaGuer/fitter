import type { ReactNode } from 'react'

/** Full-height screen with its content centered, mobile-first. */
export function CenteredScreen({ children }: { children: ReactNode }) {
  return <main className="flex min-h-dvh flex-col items-center justify-center p-4">{children}</main>
}
