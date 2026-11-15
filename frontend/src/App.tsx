import { Card } from '@heroui/react'

function App() {
  return (
    <main className="flex min-h-dvh items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <Card.Header>
          <Card.Title>Fitter</Card.Title>
          <Card.Description>Allenamento e calorie, dal telefono.</Card.Description>
        </Card.Header>
      </Card>
    </main>
  )
}

export default App
