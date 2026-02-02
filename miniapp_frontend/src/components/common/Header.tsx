import { useTelegramApp } from '../../hooks/useTelegramApp'

interface HeaderProps {
  title: string
  subtitle?: string
}

export function Header({ title, subtitle }: HeaderProps) {
  const { user } = useTelegramApp()

  return (
    <header className="bg-tg-header-bg px-4 py-3 sticky top-0 z-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-tg-text">{title}</h1>
          {subtitle && (
            <p className="text-xs text-tg-hint">{subtitle}</p>
          )}
        </div>
        {user && (
          <div className="text-right">
            <span className="text-sm text-tg-text">{user.firstName}</span>
          </div>
        )}
      </div>
    </header>
  )
}
