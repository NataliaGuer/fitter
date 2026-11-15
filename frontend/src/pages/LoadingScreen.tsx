import { Spinner } from '@heroui/react'

import { CenteredScreen } from '../components/CenteredScreen'

export function LoadingScreen() {
  return (
    <CenteredScreen>
      <Spinner size="lg" aria-label="Caricamento" />
    </CenteredScreen>
  )
}
