const DEFAULT_TOAST_DURATION = 2200
const INTERNAL_TOAST_DURATION = 60_000
const toastTimers = new Map()

function getToastId(toast) {
  if (toast.id != null) return toast.id

  return [
    toast.title ?? '',
    toast.description ?? '',
    toast.color ?? 'neutral',
  ].join('::')
}

function clearToastTimer(id) {
  const timer = toastTimers.get(id)
  if (!timer) return

  clearTimeout(timer)
  toastTimers.delete(id)
}

export function useAppToast() {
  const toast = useToast()

  function scheduleRemove(id, duration) {
    if (!import.meta.client) return

    clearToastTimer(id)
    if (duration == null || duration === false || duration === Infinity) return

    const timer = window.setTimeout(() => {
      toast.remove(id)
      toastTimers.delete(id)
    }, duration)

    toastTimers.set(id, timer)
  }

  function add(input) {
    const id = getToastId(input)
    const duration = input.duration ?? DEFAULT_TOAST_DURATION
    const payload = {
      ...input,
      id,
      open: true,
      duration: INTERNAL_TOAST_DURATION,
      progress: false,
    }

    const existing = toast.toasts.value.find(item => item.id === id)

    if (existing) {
      toast.update(id, payload)
    } else {
      toast.add(payload)
    }

    scheduleRemove(id, duration)
    return { ...existing, ...payload }
  }

  function update(id, input) {
    const duration = input.duration ?? DEFAULT_TOAST_DURATION
    toast.update(id, {
      ...input,
      open: true,
      duration: INTERNAL_TOAST_DURATION,
      progress: false,
    })
    scheduleRemove(id, duration)
  }

  function remove(id) {
    clearToastTimer(id)
    toast.remove(id)
  }

  function clear() {
    for (const id of toastTimers.keys()) {
      clearToastTimer(id)
    }

    toast.clear()
  }

  return {
    ...toast,
    add,
    update,
    remove,
    clear,
  }
}
