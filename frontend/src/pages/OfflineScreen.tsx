import { Button, Card } from '@heroui/react'

import { useAuth } from '../auth/useAuth'
import { CenteredScreen } from '../components/CenteredScreen'

export function OfflineScreen() {
  const { retry } = useAuth()

  return (
    <CenteredScreen>
      <Card className="w-full max-w-sm">
        <Card.Header>
          <Card.Title>Server non raggiungibile</Card.Title>
          <Card.Description>Controlla la connessione (o la VPN) e riprova.</Card.Description>
        </Card.Header>
        <Card.Footer>
          <Button fullWidth variant="primary" onPress={retry}>
            Riprova
          </Button>
        </Card.Footer>
      </Card>
    </CenteredScreen>
  )
}
