import { useEffect, useRef, useState, useCallback } from 'react'
import { useImpulseStore } from '../store/impulseStore'
import { useBabloStore } from '../store/babloStore'
import type { WSMessage, Impulse, BabloSignal } from '../types'

interface UseWebSocketOptions {
  initDataRaw: string
  devMode?: boolean
}

interface UseWebSocketReturn {
  isConnected: boolean
  error: string | null
  reconnect: () => void
}

const WS_RECONNECT_DELAY = 3000
const WS_HEARTBEAT_INTERVAL = 30000

/**
 * Hook for managing WebSocket connection to the gateway.
 */
export function useWebSocket({ initDataRaw, devMode = false }: UseWebSocketOptions): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Store actions
  const addImpulse = useImpulseStore(state => state.addImpulse)
  const addBabloSignal = useBabloStore(state => state.addSignal)

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WSMessage = JSON.parse(event.data)

      switch (message.type) {
        case 'impulse:new':
          addImpulse(message.data as unknown as Impulse)
          break
        case 'bablo:new':
          addBabloSignal(message.data as unknown as BabloSignal)
          break
        case 'connected':
          console.log('WebSocket connected:', message.data)
          break
        case 'pong':
          // Heartbeat response received
          break
        case 'error':
          console.error('WebSocket error:', message.data)
          setError(String(message.data.error || 'Unknown error'))
          break
        default:
          console.log('Unknown message type:', message.type)
      }
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e)
    }
  }, [addImpulse, addBabloSignal])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close()
    }

    // Build WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const endpoint = devMode ? '/ws/dev' : '/ws'
    const params = devMode ? '' : `?initData=${encodeURIComponent(initDataRaw)}`
    const url = `${protocol}//${host}${endpoint}${params}`

    console.log('Connecting to WebSocket:', url.replace(initDataRaw, '[REDACTED]'))

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      setError(null)

      // Start heartbeat
      heartbeatRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping')
        }
      }, WS_HEARTBEAT_INTERVAL)
    }

    ws.onmessage = handleMessage

    ws.onerror = () => {
      console.error('WebSocket error')
      setError('Connection error')
    }

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      setIsConnected(false)

      // Clear heartbeat
      if (heartbeatRef.current) {
        clearInterval(heartbeatRef.current)
        heartbeatRef.current = null
      }

      // Attempt to reconnect unless it was a normal close
      if (event.code !== 1000 && event.code !== 4001) {
        reconnectRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...')
          connect()
        }, WS_RECONNECT_DELAY)
      } else if (event.code === 4001) {
        setError(event.reason || 'Authentication failed')
      }
    }
  }, [initDataRaw, devMode, handleMessage])

  const reconnect = useCallback(() => {
    setError(null)
    connect()
  }, [connect])

  // Connect on mount
  useEffect(() => {
    // Don't connect if we don't have initData (unless in dev mode)
    if (!devMode && !initDataRaw) {
      return
    }

    connect()

    // Cleanup on unmount
    return () => {
      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current)
      }
      if (heartbeatRef.current) {
        clearInterval(heartbeatRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted')
      }
    }
  }, [connect, devMode, initDataRaw])

  return {
    isConnected,
    error,
    reconnect,
  }
}
