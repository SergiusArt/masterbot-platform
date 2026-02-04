import { useMemo } from 'react'
import type { TabType } from '../../types'

interface TabNavigationProps {
  activeTab: TabType
  onTabChange: (tab: TabType) => void
  isAdmin?: boolean
}

const baseTabs: { id: TabType; label: string; icon: string }[] = [
  { id: 'combined', label: 'Обзор', icon: '📊' },
  { id: 'impulse', label: 'Импульсы', icon: '⚡' },
  { id: 'bablo', label: 'Bablo', icon: '💰' },
  { id: 'reports', label: 'Отчёты', icon: '📈' },
]

const adminTab: { id: TabType; label: string; icon: string } = {
  id: 'admin',
  label: 'Админ',
  icon: '👑',
}

export function TabNavigation({ activeTab, onTabChange, isAdmin = false }: TabNavigationProps) {
  const tabs = useMemo(() => {
    if (isAdmin) {
      return [...baseTabs, adminTab]
    }
    return baseTabs
  }, [isAdmin])

  return (
    <nav className="flex bg-tg-secondary-bg sticky bottom-0 border-t border-tg-hint/10">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`tab ${activeTab === tab.id ? 'tab-active' : 'tab-inactive'}`}
        >
          <span className="text-lg">{tab.icon}</span>
          <span className="block text-xs mt-0.5">{tab.label}</span>
        </button>
      ))}
    </nav>
  )
}
