// Same rules as the backend (CORE-002-BE-01): the backend stays the final check (422), D-013.
const NICKNAME_PATTERN = /^[A-Za-z0-9_.-]{3,30}$/
const PIN_PATTERN = /^[0-9]{4}$/

export const PIN_LENGTH = 4

export function nicknameError(nickname: string): string | null {
  if (nickname.length < 3 || nickname.length > 30) {
    return 'Il nickname deve avere da 3 a 30 caratteri'
  }
  if (!NICKNAME_PATTERN.test(nickname)) {
    return 'Solo lettere, numeri e i caratteri _ - . (niente spazi o accenti)'
  }
  return null
}

export function pinError(pin: string): string | null {
  return PIN_PATTERN.test(pin) ? null : 'Il PIN deve avere 4 cifre'
}
