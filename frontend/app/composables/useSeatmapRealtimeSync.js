const LOCAL_BACKEND_PORT = 8000

function normalizeBaseUrl(baseUrl) {
  const normalized = new URL(baseUrl)

  if (normalized.protocol === 'http:') {
    normalized.protocol = 'ws:'
  } else if (normalized.protocol === 'https:') {
    normalized.protocol = 'wss:'
  }

  return normalized
}

function resolveSeatmapBaseUrl() {
  const config = useRuntimeConfig()
  const configuredBase = config.public?.backendWsUrl?.trim()

  if (configuredBase) {
    return configuredBase
  }

  if (!import.meta.client) {
    return ''
  }

  const { protocol, hostname } = window.location

  if (
    hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname === '0.0.0.0' ||
    hostname.endsWith('.localhost')
  ) {
    return `${protocol}//${hostname}:${LOCAL_BACKEND_PORT}`
  }

  if (hostname.startsWith('api.') || hostname.startsWith('backend.')) {
    return `${protocol}//${hostname}`
  }

  return `${protocol}//api.${hostname}`
}

function buildSeatmapSocketUrl(eventId) {
  const baseUrl = resolveSeatmapBaseUrl()
  if (!baseUrl) return ''

  const url = normalizeBaseUrl(baseUrl)
  url.pathname = `/ws/booking/events/${eventId}/seatmap/`
  url.search = ''
  url.hash = ''

  return url.toString()
}

export function useSeatmapRealtimeSync({ eventId, onMessage } = {}) {
  const connectionState = ref('idle')
  const socket = shallowRef(null)
  const reconnectTimer = ref(null)
  const reconnectAttempt = ref(0)
  const resolvedEventId = computed(() => {
    const value = unref(eventId)
    return value == null || value === '' ? null : String(value)
  })

  let stopRequested = false
  let connectionToken = 0

  function clearReconnectTimer() {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
  }

  function closeSocket() {
    connectionToken += 1

    const currentSocket = socket.value
    socket.value = null

    if (!currentSocket) return

    if (
      currentSocket.readyState === WebSocket.CONNECTING ||
      currentSocket.readyState === WebSocket.OPEN
    ) {
      currentSocket.close(1000, 'seatmap sync reset')
    }
  }

  function scheduleReconnect() {
    if (stopRequested || !import.meta.client || !resolvedEventId.value) return

    clearReconnectTimer()
    connectionState.value = 'reconnecting'

    const delay = Math.min(15_000, 1_000 * (2 ** reconnectAttempt.value))
    reconnectAttempt.value += 1
    reconnectTimer.value = window.setTimeout(() => {
      connect()
    }, delay)
  }

  function stop() {
    stopRequested = true
    clearReconnectTimer()
    closeSocket()
    connectionState.value = 'closed'
  }

  function connect() {
    if (!import.meta.client) return
    if (typeof WebSocket === 'undefined') {
      connectionState.value = 'unsupported'
      return
    }

    const nextEventId = resolvedEventId.value
    if (!nextEventId) {
      stop()
      return
    }

    stopRequested = false
    clearReconnectTimer()
    closeSocket()

    const socketUrl = buildSeatmapSocketUrl(nextEventId)
    if (!socketUrl) {
      connectionState.value = 'unsupported'
      return
    }

    connectionState.value = 'connecting'
    const currentToken = connectionToken
    const nextSocket = new WebSocket(socketUrl)
    socket.value = nextSocket

    nextSocket.onopen = () => {
      if (currentToken !== connectionToken || socket.value !== nextSocket) return
      reconnectAttempt.value = 0
      connectionState.value = 'connected'
    }

    nextSocket.onmessage = async (event) => {
      if (currentToken !== connectionToken || socket.value !== nextSocket) return

      let payload
      try {
        payload = JSON.parse(event.data)
      } catch (error) {
        console.warn('Seatmap websocket sent invalid JSON', error)
        return
      }

      if (payload?.event_id == null || String(payload.event_id) !== nextEventId) {
        return
      }

      if (payload.type !== 'seatmap.change') {
        return
      }

      try {
        await onMessage?.(payload, nextSocket)
      } catch (error) {
        console.error('Seatmap websocket message handler failed', error)
      }
    }

    nextSocket.onerror = () => {
      if (currentToken !== connectionToken || socket.value !== nextSocket) return
      nextSocket.close()
    }

    nextSocket.onclose = () => {
      if (currentToken !== connectionToken || socket.value !== nextSocket) return

      socket.value = null

      if (stopRequested) {
        connectionState.value = 'closed'
        return
      }

      scheduleReconnect()
    }
  }

  watch(resolvedEventId, () => {
    connect()
  }, { immediate: true })

  onUnmounted(() => {
    stop()
  })

  return {
    connectionState,
    connect,
    stop,
    socket,
  }
}
