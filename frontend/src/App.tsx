import { Card } from '@heroui/react'

import { useAuth } from './auth/useAuth'
import { CenteredScreen } from './components/CenteredScreen'
import { LoadingScreen } from './pages/LoadingScreen'
import { OfflineScreen } from './pages/OfflineScreen'

// Temporary placeholder: replaced by AuthPage (step 4) and HomePage (step 5) of CORE-002-FE-01.
function Placeholder({ title }: { title: string }) {
  return (
    <CenteredScreen>
      <Card className="w-full max-w-sm">
        <Card.Header>
          <Card.Title>{title}</Card.Title>
        </Card.Header>
      </Card>
    </CenteredScreen>
  )
}

function App() {
  const { state } = useAuth()

  switch (state.status) {
    case 'loading':
      return <LoadingScreen />
    case 'offline':
      return <OfflineScreen />
    case 'anonymous':
      return <Placeholder title="Accesso" />
    case 'authenticated':
      return <Placeholder title={`Ciao, ${state.user.nickname}`} />
  }
}

export default App
