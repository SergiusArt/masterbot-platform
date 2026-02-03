import React from 'react'
import ReactDOM from 'react-dom/client'
import { TelegramProvider } from './context/TelegramContext'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TelegramProvider>
      <App />
    </TelegramProvider>
  </React.StrictMode>,
)
