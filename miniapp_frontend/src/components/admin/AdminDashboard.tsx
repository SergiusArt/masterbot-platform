/**
 * Admin Dashboard - main admin section container.
 */

import { useState, useCallback } from 'react'
import { UserStatsCards } from './UserStatsCards'
import { UserList } from './UserList'
import { AddUserModal } from './AddUserModal'
import { EditUserModal } from './EditUserModal'
import { ActiveUsersChart } from './ActiveUsersChart'
import { UserActivityTable } from './UserActivityTable'
import { ServiceHealth } from './ServiceHealth'
import { BroadcastForm } from './BroadcastForm'
import type { AdminUser } from '../../types/admin'

type AdminTab = 'users' | 'analytics' | 'system'

export function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<AdminTab>('users')
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleRefresh = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1)
  }, [])

  const tabs: { id: AdminTab; label: string; icon: string }[] = [
    { id: 'users', label: 'Пользователи', icon: '👥' },
    { id: 'analytics', label: 'Аналитика', icon: '📊' },
    { id: 'system', label: 'Система', icon: '⚙️' },
  ]

  return (
    <div className="p-4">
      {/* Sub-navigation */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-tg-button text-tg-button-text'
                : 'bg-tg-secondary-bg text-tg-hint'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Users tab */}
      {activeTab === 'users' && (
        <>
          <UserStatsCards />
          <UserList
            onEdit={setEditingUser}
            onAdd={() => setShowAddModal(true)}
            refreshTrigger={refreshTrigger}
          />
        </>
      )}

      {/* Analytics tab */}
      {activeTab === 'analytics' && (
        <>
          <ActiveUsersChart />
          <UserActivityTable />
        </>
      )}

      {/* System tab */}
      {activeTab === 'system' && (
        <>
          <ServiceHealth />
          <BroadcastForm />
        </>
      )}

      {/* Modals */}
      <AddUserModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={handleRefresh}
      />
      <EditUserModal
        user={editingUser}
        onClose={() => setEditingUser(null)}
        onSuccess={handleRefresh}
      />
    </div>
  )
}
