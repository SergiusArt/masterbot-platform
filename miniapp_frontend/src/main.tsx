import ReactDOM from 'react-dom/client'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { TelegramProvider } from './context/TelegramContext'
import App from './App'
import './styles/index.css'

const root = document.getElementById('root')
if (root) {
  ReactDOM.createRoot(root).render(
    <ErrorBoundary>
      <TelegramProvider>
        <App />
      </TelegramProvider>
    </ErrorBoundary>
  )
}
