import { InputOTP, Label, REGEXP_ONLY_DIGITS } from '@heroui/react'
import { useId } from 'react'

import { PIN_LENGTH } from '../auth/validation'

type PinInputProps = {
  label: string
  value: string
  onChange: (value: string) => void
  error: string | null
  autoComplete: 'current-password' | 'new-password'
}

/** 4-digit PIN with one box per digit and the numeric keypad on phones. */
export function PinInput({ label, value, onChange, error, autoComplete }: PinInputProps) {
  const labelId = useId()
  const errorId = useId()

  return (
    <div className="flex flex-col gap-1">
      <Label id={labelId}>{label}</Label>
      <InputOTP
        maxLength={PIN_LENGTH}
        className="justify-center"
        pattern={REGEXP_ONLY_DIGITS}
        inputMode="numeric"
        autoComplete={autoComplete}
        value={value}
        onChange={onChange}
        isInvalid={error !== null}
        aria-labelledby={labelId}
        aria-describedby={error !== null ? errorId : undefined}
      >
        <InputOTP.Group>
          {Array.from({ length: PIN_LENGTH }, (_, index) => (
            <InputOTP.Slot key={index} index={index} />
          ))}
        </InputOTP.Group>
      </InputOTP>
      {error !== null && (
        <p id={errorId} className="text-sm text-danger">
          {error}
        </p>
      )}
    </div>
  )
}
