import { useState, useCallback } from 'react'
import { useTelegramApp } from './hooks/useTelegramApp'
import { useWebSocket } from './hooks/useWebSocket'
import { Header } from './components/common/Header'
import { TabNavigation } from './components/common/TabNavigation'
import { CombinedDashboard } from './components/common/CombinedDashboard'
import { ImpulseDashboard } from './components/impulse/ImpulseDashboard'
import { BabloDashboard } from './components/bablo/BabloDashboard'
import type { TabType } from './types'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('combined')
  const { isReady, initDataRaw, isMiniApp } = useTelegramApp()

  // Connect WebSocket (dev mode if not in Telegram Mini App)
  const { isConnected, error: wsError } = useWebSocket({
    initDataRaw,
    devMode: !isMiniApp,
  })

  const handleTabChange = useCallback((tab: TabType) => {
    setActiveTab(tab)
  }, [])

  const getTitle = () => {
    switch (activeTab) {
      case 'combined':
        return 'MasterBot'
      case 'impulse':
        return 'Импульсы'
      case 'bablo':
        return 'Bablo'
    }
  }

  const getSubtitle = () => {
    if (wsError) return `Ошибка: ${wsError}`
    if (!isConnected) return 'Подключение...'
    return 'Онлайн'
  }

  // Show loading state while SDK initializes
  if (!isReady && isMiniApp) {
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
    <div className="min-h-screen bg-tg-bg flex flex-col">
      <Header title={getTitle()} subtitle={getSubtitle()} />

      {/* Main content area with scrolling */}
      <main className="flex-1 overflow-y-auto pb-16">
        {activeTab === 'combined' && (
          <CombinedDashboard
            onNavigateToImpulse={() => setActiveTab('impulse')}
            onNavigateToBablo={() => setActiveTab('bablo')}
          />
        )}
        {activeTab === 'impulse' && <ImpulseDashboard />}
        {activeTab === 'bablo' && <BabloDashboard />}
      </main>

      <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />
    </div>
  )
}

export default App
