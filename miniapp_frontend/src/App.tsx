import { useState, useCallback } from 'react'
import { useTelegram } from './context/TelegramContext'
import { useWebSocket } from './hooks/useWebSocket'
import { Header } from './components/common/Header'
import { TabNavigation } from './components/common/TabNavigation'
import { CombinedDashboard } from './components/common/CombinedDashboard'
import { ImpulseDashboard } from './components/impulse/ImpulseDashboard'
import { BabloDashboard } from './components/bablo/BabloDashboard'
import { ReportsDashboard } from './components/reports/ReportsDashboard'
import { AdminDashboard } from './components/admin/AdminDashboard'
import type { TabType } from './types'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('combined')
  const { initData, isMiniApp, isAdmin } = useTelegram()

  // Connect WebSocket (dev mode if not in Telegram Mini App)
  const { isConnected, error: wsError } = useWebSocket({
    initDataRaw: initData,
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
      case 'reports':
        return 'Отчёты'
      case 'admin':
        return 'Админ-панель'
    }
  }

  const getSubtitle = () => {
    if (wsError) return `Ошибка: ${wsError}`
    if (!isConnected) return 'Подключение...'
    return 'Онлайн'
  }

  // TelegramProvider handles loading state, so App only renders when ready
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
        {activeTab === 'reports' && <ReportsDashboard />}
        {activeTab === 'admin' && isAdmin && <AdminDashboard />}
      </main>

      <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} isAdmin={isAdmin} />
    </div>
  )
}

export default App
