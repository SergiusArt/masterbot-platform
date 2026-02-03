import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: string
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: '' }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: '' }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
    this.setState({
      errorInfo: errorInfo.componentStack || ''
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen bg-tg-bg p-4">
          <div className="text-center max-w-sm">
            <span className="text-5xl mb-4 block">💥</span>
            <h2 className="text-lg font-semibold text-tg-text mb-2">
              Произошла ошибка
            </h2>
            <p className="text-tg-destructive text-sm mb-4 break-words">
              {this.state.error?.message || 'Unknown error'}
            </p>
            <pre className="text-xs text-tg-hint text-left overflow-auto max-h-40 bg-tg-secondary-bg p-2 rounded mb-4">
              {this.state.errorInfo}
            </pre>
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

    return this.props.children
  }
}
