import { Moon, Sun } from '@gravity-ui/icons'
import { Switch } from '@heroui/react'

import { useTheme } from '../theme/useTheme'

/** Light (Coral & Cream) / dark (Dark Brut) switch: on = dark theme. */
export function ThemeSwitch() {
  const { theme, setTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <Switch
      size="lg"
      aria-label="Tema scuro"
      isSelected={isDark}
      onChange={(selected) => setTheme(selected ? 'dark' : 'light')}
    >
      <Switch.Content>
        <Switch.Control>
          <Switch.Thumb>
            <Switch.Icon>
              {isDark ? <Moon aria-hidden className="size-3.5" /> : <Sun aria-hidden className="size-3.5" />}
            </Switch.Icon>
          </Switch.Thumb>
        </Switch.Control>
      </Switch.Content>
    </Switch>
  )
}
