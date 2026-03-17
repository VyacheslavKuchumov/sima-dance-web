export default defineNuxtPlugin(() => {
  const maybeLocalStorage = (globalThis as any).localStorage

  if (!maybeLocalStorage || typeof maybeLocalStorage.getItem !== 'function') {
    const store = new Map<string, string>()

    ;(globalThis as any).localStorage = {
      getItem(key: string) {
        return store.has(key) ? store.get(key)! : null
      },
      setItem(key: string, value: string) {
        store.set(key, String(value))
      },
      removeItem(key: string) {
        store.delete(key)
      },
      clear() {
        store.clear()
      },
      key(index: number) {
        return Array.from(store.keys())[index] ?? null
      },
      get length() {
        return store.size
      }
    }
  }
})
