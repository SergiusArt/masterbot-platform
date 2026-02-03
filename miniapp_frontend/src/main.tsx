import ReactDOM from 'react-dom/client'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { TelegramProvider } from './context/TelegramContext'
import App from './App'
import './styles/index.css'

// Simple test mode - set to true to test without complex components
const TEST_MODE = true

function TestApp() {
  return (
    <div style={{
      padding: '20px',
      backgroundColor: 'var(--tg-theme-bg-color, white)',
      color: 'var(--tg-theme-text-color, black)',
      minHeight: '100vh'
    }}>
      <h1>Test Mini App</h1>
      <p>If you see this, React is working!</p>
      <p>Time: {new Date().toLocaleTimeString()}</p>
    </div>
  )
}

const root = document.getElementById('root')
if (root) {
  ReactDOM.createRoot(root).render(
    TEST_MODE ? (
      <TestApp />
    ) : (
      <ErrorBoundary>
        <TelegramProvider>
          <App />
        </TelegramProvider>
      </ErrorBoundary>
    )
  )
}
