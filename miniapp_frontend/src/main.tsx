import { useEffect, useState } from 'react'
import ReactDOM from 'react-dom/client'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { TelegramProvider } from './context/TelegramContext'
import App from './App'
import './styles/index.css'

// Test levels:
// 0 = Full app (TelegramProvider + App)
// 1 = Test with webApp.ready() only
// 2 = Simple test (no Telegram SDK calls)
const TEST_LEVEL: number = 1

function TestAppWithTelegram() {
  const [status, setStatus] = useState('Initializing...')

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (webApp) {
      setStatus('Telegram SDK found, calling ready()...')
      webApp.ready()
      setStatus('webApp.ready() called successfully!')
    } else {
      setStatus('No Telegram SDK (dev mode)')
    }
  }, [])

  return (
    <div style={{
      padding: '20px',
      backgroundColor: 'var(--tg-theme-bg-color, white)',
      color: 'var(--tg-theme-text-color, black)',
      minHeight: '100vh'
    }}>
      <h1>Test Mini App (Level 1)</h1>
      <p>Status: {status}</p>
      <p>Time: {new Date().toLocaleTimeString()}</p>
    </div>
  )
}

function SimpleTestApp() {
  return (
    <div style={{
      padding: '20px',
      backgroundColor: 'var(--tg-theme-bg-color, white)',
      color: 'var(--tg-theme-text-color, black)',
      minHeight: '100vh'
    }}>
      <h1>Test Mini App (Level 2)</h1>
      <p>Simple test - no Telegram SDK calls</p>
      <p>Time: {new Date().toLocaleTimeString()}</p>
    </div>
  )
}

const root = document.getElementById('root')
if (root) {
  let component
  switch (TEST_LEVEL) {
    case 2:
      component = <SimpleTestApp />
      break
    case 1:
      component = <TestAppWithTelegram />
      break
    default:
      component = (
        <ErrorBoundary>
          <TelegramProvider>
            <App />
          </TelegramProvider>
        </ErrorBoundary>
      )
  }
  ReactDOM.createRoot(root).render(component)
}
