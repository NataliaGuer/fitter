import { useAuth } from './auth/useAuth'
import { AuthPage } from './pages/AuthPage'
import { HomePage } from './pages/HomePage'
import { LoadingScreen } from './pages/LoadingScreen'
import { OfflineScreen } from './pages/OfflineScreen'

function App() {
  const { state } = useAuth()

  switch (state.status) {
    case 'loading':
      return <LoadingScreen />
    case 'offline':
      return <OfflineScreen />
    case 'anonymous':
      return <AuthPage />
    case 'authenticated':
      return <HomePage user={state.user} />
  }
}

export default App
