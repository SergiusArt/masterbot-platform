interface AccessDeniedProps {
  message?: string
}

export function AccessDenied({ message }: AccessDeniedProps) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-tg-bg p-4">
      <div className="text-center max-w-sm">
        <span className="text-5xl mb-4 block">🔒</span>
        <h2 className="text-lg font-semibold text-tg-text mb-2">
          Доступ ограничен
        </h2>
        <p className="text-tg-hint mb-4">
          {message || 'У вас нет доступа к этому приложению.'}
        </p>
        <p className="text-tg-hint mb-4">
          Для получения доступа обратитесь к менеджеру:
        </p>
        <a
          href="https://t.me/SrgArtManager"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-tg-button text-tg-button-text px-6 py-3 rounded-xl font-medium"
        >
          @SrgArtManager
        </a>
      </div>
    </div>
  )
}
