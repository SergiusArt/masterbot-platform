import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, initApi } from '../api'
import { AccessDenied } from '../components/common/AccessDenied'

interface TelegramContextValue {
  isReady: boolean
  initData: string
  isMiniApp: boolean
  accessDenied: boolean
  accessDeniedMessage: string
}

const TelegramContext = createContext<TelegramContextValue>({
  isReady: false,
  initData: '',
  isMiniApp: false,
  accessDenied: false,
  accessDeniedMessage: '',
})

// Max retries and delays for Telegram SDK detection
const MAX_RETRIES = 10
const RETRY_DELAY = 50 // ms

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [isReady, setIsReady] = useState(false)
  const [initData, setInitData] = useState('')
  const [isMiniApp, setIsMiniApp] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [accessDenied, setAccessDenied] = useState(false)
  const [accessDeniedMessage, setAccessDeniedMessage] = useState('')

  useEffect(() => {
    let retryCount = 0
    let timeoutId: ReturnType<typeof setTimeout>

    const checkAccess = async () => {
      try {
        // Make a simple API call to check if user has access
        await api.getSummary()
        setIsReady(true)
      } catch (err: unknown) {
        const error = err as { status?: number; message?: string }
        if (error.status === 403) {
          // Access denied
          setAccessDenied(true)
          setAccessDeniedMessage(error.message || 'Access denied')
          setIsReady(true)
        } else {
          // Other errors - still allow app to load, will show error in dashboard
          setIsReady(true)
        }
      }
    }

    const checkTelegram = () => {
      const webApp = window.Telegram?.WebApp

      if (webApp && webApp.initData) {
        // Telegram SDK is ready with initData
        setIsMiniApp(true)
        setInitData(webApp.initData)
        initApi(webApp.initData)
        webApp.ready()
        webApp.expand()
        // Check access after initializing API
        checkAccess()
      } else if (webApp && !webApp.initData && retryCount < MAX_RETRIES) {
        // SDK exists but initData not ready yet - retry
        retryCount++
        timeoutId = setTimeout(checkTelegram, RETRY_DELAY)
      } else if (!webApp && retryCount < MAX_RETRIES) {
        // SDK not loaded yet - retry
        retryCount++
        timeoutId = setTimeout(checkTelegram, RETRY_DELAY)
      } else if (webApp && !webApp.initData) {
        // SDK loaded but no initData after all retries - probably opened in browser
        setIsMiniApp(true)
        setError('no_init_data')
        setIsReady(true)
      } else {
        // No Telegram SDK after all retries - dev mode
        setIsMiniApp(false)
        setIsReady(true)
      }
    }

    // Start checking immediately
    checkTelegram()

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [])

  // Show loading while checking
  if (isMiniApp === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-tg-bg">
        <div className="text-center">
          <div className="spinner mb-4" />
          <p className="text-tg-hint">Загрузка...</p>
        </div>
      </div>
    )
  }

  // Show error if Mini App but no initData
  if (error === 'no_init_data' || (isMiniApp && !initData && !accessDenied)) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-tg-bg p-4">
        <div className="text-center max-w-sm">
          <span className="text-5xl mb-4 block">⚠️</span>
          <h2 className="text-lg font-semibold text-tg-text mb-2">
            Не удалось загрузить
          </h2>
          <p className="text-tg-hint mb-4">
            Пожалуйста, закройте приложение и откройте его заново из Telegram.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="bg-tg-button text-tg-button-text px-6 py-3 rounded-xl font-medium"
          >
            Перезагрузить
          </button>
        </div>
      </div>
    )
  }

  // Show access denied screen
  if (accessDenied) {
    return <AccessDenied message={accessDeniedMessage} />
  }

  return (
    <TelegramContext.Provider value={{ isReady, initData, isMiniApp, accessDenied, accessDeniedMessage }}>
      {children}
    </TelegramContext.Provider>
  )
}

export function useTelegram() {
  return useContext(TelegramContext)
}
