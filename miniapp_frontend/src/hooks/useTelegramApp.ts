import { useEffect, useState } from 'react'
import { initApi } from '../api'

export interface TelegramUser {
  id: number
  firstName: string
  lastName?: string
  username?: string
  languageCode?: string
  isPremium?: boolean
}

export interface TelegramAppState {
  isReady: boolean
  user: TelegramUser | null
  initDataRaw: string
  isDark: boolean
  viewportHeight: number
  isMiniApp: boolean
}

// Global type declaration for Telegram
declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            first_name: string
            last_name?: string
            username?: string
            language_code?: string
            is_premium?: boolean
          }
        }
        ready: () => void
        expand: () => void
        close: () => void
        themeParams: Record<string, string>
        colorScheme: 'light' | 'dark'
        viewportHeight: number
        viewportStableHeight: number
        BackButton: {
          show: () => void
          hide: () => void
          onClick: (callback: () => void) => void
          offClick: (callback: () => void) => void
        }
      }
    }
  }
}

/**
 * Hook for accessing Telegram Mini App SDK.
 * Uses native Telegram WebApp API.
 */
export function useTelegramApp(): TelegramAppState {
  const [isReady, setIsReady] = useState(false)
  const [initDataRaw, setInitDataRaw] = useState('')
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [viewportHeight, setViewportHeight] = useState(window.innerHeight)
  const [isDark, setIsDark] = useState(false)

  // Check if running in Mini App context
  const isMiniApp = typeof window !== 'undefined' && !!window.Telegram?.WebApp

  useEffect(() => {
    const webApp = window.Telegram?.WebApp

    if (webApp) {
      // Mark as ready and capture all data
      webApp.ready()
      webApp.expand()

      // Set initData and initialize API
      const initData = webApp.initData || ''
      setInitDataRaw(initData)
      initApi(initData)

      // Set user data
      const tgUser = webApp.initDataUnsafe?.user
      if (tgUser) {
        setUser({
          id: tgUser.id,
          firstName: tgUser.first_name,
          lastName: tgUser.last_name,
          username: tgUser.username,
          languageCode: tgUser.language_code,
          isPremium: tgUser.is_premium,
        })
      }

      // Set other state
      setIsDark(webApp.colorScheme === 'dark')
      setViewportHeight(webApp.viewportHeight || window.innerHeight)
      setIsReady(true)
    } else {
      // Not in Telegram - still mark as ready for dev mode
      setIsReady(true)
    }
  }, [])

  return {
    isReady,
    user,
    initDataRaw,
    isDark,
    viewportHeight,
    isMiniApp,
  }
}

/**
 * Hook for managing back button.
 */
export function useTelegramBackButton(onBack: () => void, show: boolean = true) {
  useEffect(() => {
    const backButton = window.Telegram?.WebApp?.BackButton
    if (!backButton) return

    if (show) {
      backButton.show()
      backButton.onClick(onBack)
      return () => {
        backButton.offClick(onBack)
        backButton.hide()
      }
    } else {
      backButton.hide()
    }
  }, [onBack, show])
}
