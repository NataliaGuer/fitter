import { Alert, Button, Card } from '@heroui/react'
import { useState } from 'react'

import type { User } from '../api/auth'
import { errorMessage } from '../api/errors'
import { useAuth } from '../auth/useAuth'
import { CenteredScreen } from '../components/CenteredScreen'

/** Placeholder home until the first real feature (CORE-002). */
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
    <CenteredScreen>
      <Card className="w-full max-w-sm">
        <Card.Header>
          <Card.Title>Ciao, {user.nickname}</Card.Title>
        </Card.Header>
        {error !== null && (
          <Card.Content>
            <Alert status="danger">
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>{error}</Alert.Title>
              </Alert.Content>
            </Alert>
          </Card.Content>
        )}
        <Card.Footer>
          <Button fullWidth variant="secondary" isPending={isPending} onPress={handleLogout}>
            Esci
          </Button>
        </Card.Footer>
      </Card>
    </CenteredScreen>
  )
}
