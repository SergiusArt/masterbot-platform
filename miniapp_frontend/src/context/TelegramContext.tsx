import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { initApi } from '../api'

interface TelegramContextValue {
  isReady: boolean
  initData: string
  isMiniApp: boolean
}

const TelegramContext = createContext<TelegramContextValue>({
  isReady: false,
  initData: '',
  isMiniApp: false,
})

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [isReady, setIsReady] = useState(false)
  const [initData, setInitData] = useState('')
  const [isMiniApp, setIsMiniApp] = useState<boolean | null>(null) // null = still checking

  useEffect(() => {
    // Wait a tick to ensure Telegram SDK is injected
    const checkTelegram = () => {
      const webApp = window.Telegram?.WebApp

      if (webApp) {
        // We're in Telegram Mini App
        setIsMiniApp(true)

        // Get and store initData
        const data = webApp.initData || ''
        setInitData(data)
        initApi(data)

        // Notify Telegram we're ready
        webApp.ready()
        webApp.expand()
        setIsReady(true)
      } else {
        // Not in Telegram - dev mode
        setIsMiniApp(false)
        setIsReady(true)
      }
    }

    // Small delay to ensure Telegram SDK has time to inject
    const timer = setTimeout(checkTelegram, 10)
    return () => clearTimeout(timer)
  }, [])

  // Show loading while checking environment or while Mini App initializes
  if (isMiniApp === null || (isMiniApp && (!isReady || !initData))) {
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
    <TelegramContext.Provider value={{ isReady, initData, isMiniApp: isMiniApp ?? false }}>
      {children}
    </TelegramContext.Provider>
  )
}

export function useTelegram() {
  return useContext(TelegramContext)
}
