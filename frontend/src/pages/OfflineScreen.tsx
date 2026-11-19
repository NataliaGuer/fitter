import { Button, Card } from '@heroui/react'

import { useAuth } from '../auth/useAuth'
import { CenteredScreen } from '../components/CenteredScreen'

export function OfflineScreen() {
  const { retry } = useAuth()

  return (
    <CenteredScreen>
      <Card className="w-full max-w-sm shadow-brut-lg">
        <Card.Header>
          <Card.Title className="text-2xl font-extrabold tracking-tight">server non raggiungibile</Card.Title>
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
