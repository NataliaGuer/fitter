import { Alert, Button, Card, FieldError, Form, Input, Label, Tabs, TextField } from '@heroui/react'
import { useState, type FormEvent } from 'react'

import { errorMessage } from '../api/errors'
import { useAuth } from '../auth/useAuth'
import { nicknameError, pinError } from '../auth/validation'
import { CenteredScreen } from '../components/CenteredScreen'
import { PinInput } from '../components/PinInput'

type Mode = 'login' | 'register'

type FieldErrors = {
  nickname: string | null
  pin: string | null
}

const NO_ERRORS: FieldErrors = { nickname: null, pin: null }

function validate(nickname: string, pin: string): FieldErrors {
  return { nickname: nicknameError(nickname), pin: pinError(pin) }
}

function AuthForm({ mode }: { mode: Mode }) {
  const auth = useAuth()
  const [nickname, setNickname] = useState('')
  const [pin, setPin] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>(NO_ERRORS)
  const [formError, setFormError] = useState<string | null>(null)
  const [isPending, setIsPending] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    const errors = validate(nickname, pin)
    setFieldErrors(errors)
    if (errors.nickname !== null || errors.pin !== null) {
      return // invalid input: no request is sent
    }

    setIsPending(true)
    try {
      const credentials = { nickname, pin }
      // On success the auth state changes and this screen is replaced by the home.
      await (mode === 'login' ? auth.login(credentials) : auth.register(credentials))
    } catch (error) {
      setFormError(
        errorMessage(error, mode === 'login' ? { 401: 'Nickname o PIN non corretti' } : { 409: 'Nickname già in uso' }),
      )
      setIsPending(false)
    }
  }

  return (
    <Form className="flex flex-col gap-4" validationBehavior="aria" onSubmit={handleSubmit}>
      {/* variant="secondary": fields inside a Card, otherwise they have the same color as the Card. */}
      <TextField
        fullWidth
        variant="secondary"
        name="nickname"
        value={nickname}
        onChange={setNickname}
        isInvalid={fieldErrors.nickname !== null}
        autoComplete="username"
      >
        <Label>Nickname</Label>
        <Input autoCapitalize="none" autoCorrect="off" spellCheck={false} />
        <FieldError>{fieldErrors.nickname}</FieldError>
      </TextField>

      {/* The PIN is not masked, so the user sees it while typing: no confirmation field. */}
      <PinInput
        label="PIN"
        value={pin}
        onChange={setPin}
        error={fieldErrors.pin}
        autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
      />

      {formError !== null && (
        <Alert status="danger">
          <Alert.Indicator />
          <Alert.Content>
            <Alert.Title>{formError}</Alert.Title>
          </Alert.Content>
        </Alert>
      )}

      <Button type="submit" variant="primary" fullWidth isPending={isPending}>
        {mode === 'login' ? 'Accedi' : 'Registrati'}
      </Button>
    </Form>
  )
}

export function AuthPage() {
  return (
    <CenteredScreen>
      <Card className="w-full max-w-sm">
        <Card.Header>
          <Card.Title>Fitter</Card.Title>
        </Card.Header>
        <Card.Content>
          <Tabs defaultSelectedKey="login">
            <Tabs.ListContainer>
              <Tabs.List aria-label="Accesso o registrazione">
                <Tabs.Tab id="login">
                  Accedi
                  <Tabs.Indicator />
                </Tabs.Tab>
                <Tabs.Tab id="register">
                  Registrati
                  <Tabs.Indicator />
                </Tabs.Tab>
              </Tabs.List>
            </Tabs.ListContainer>
            {/* Each panel has its own form: switching tab starts from empty fields. */}
            <Tabs.Panel id="login" className="pt-4">
              <AuthForm mode="login" />
            </Tabs.Panel>
            <Tabs.Panel id="register" className="pt-4">
              <AuthForm mode="register" />
            </Tabs.Panel>
          </Tabs>
        </Card.Content>
      </Card>
    </CenteredScreen>
  )
}
