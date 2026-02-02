interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

export function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4 border',
    md: 'w-6 h-6 border-2',
    lg: 'w-10 h-10 border-2',
  }

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`spinner ${sizeClasses[size]}`} />
      {text && <p className="mt-2 text-sm text-tg-hint">{text}</p>}
    </div>
  )
}
