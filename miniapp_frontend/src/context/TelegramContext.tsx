import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { initApi } from '../api'

interface TelegramContextValue {
  isReady: boolean
  initData: string
  isMiniApp: boolean
}

// Initialize API SYNCHRONOUSLY at module load time
// This runs before any React component renders
const webAppInitData = typeof window !== 'undefined'
  ? window.Telegram?.WebApp?.initData || ''
  : ''

if (webAppInitData) {
  initApi(webAppInitData)
}

const TelegramContext = createContext<TelegramContextValue>({
  isReady: false,
  initData: '',
  isMiniApp: false,
})

export function TelegramProvider({ children }: { children: ReactNode }) {
  // Use the already-captured initData (no need for state, it's captured at load time)
  const [isReady, setIsReady] = useState(false)
  const initData = webAppInitData

  // Check synchronously if we're in Mini App
  const isMiniApp = typeof window !== 'undefined' && !!window.Telegram?.WebApp

  useEffect(() => {
    const webApp = window.Telegram?.WebApp

    if (webApp) {
      // Notify Telegram we're ready
      webApp.ready()
      webApp.expand()
      setIsReady(true)
    } else {
      // Dev mode - no Telegram
      setIsReady(true)
    }
  }, [])

  // Don't render children until ready (and initData is available in Mini App mode)
  if (isMiniApp && (!isReady || !initData)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mb-4" />
          <p className="text-tg-hint">Загрузка...</p>
        </div>
      </div>
    )
  }

  return (
    <TelegramContext.Provider value={{ isReady, initData, isMiniApp }}>
      {children}
    </TelegramContext.Provider>
  )
}

export function useTelegram() {
  return useContext(TelegramContext)
}
