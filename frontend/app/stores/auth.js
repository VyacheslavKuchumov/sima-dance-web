
function parseTokenPayload(token) {
  try {
    const payload = token.split('.')[1]
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const decoded =
      typeof atob === 'function'
        ? atob(normalized)
        : Buffer.from(normalized, 'base64').toString('utf8')
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

function getTokenExpiryMs(token) {
  const payload = parseTokenPayload(token)
  const expSeconds = Number(payload?.exp)
  if (!Number.isFinite(expSeconds)) return 0
  return expSeconds * 1000
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null,
    refreshToken: null,
    user: null,
    userId: null,
  }),
  getters: {
    isAuthenticated: (state) => {
      if (!state.accessToken) return false
      const expiryMs = getTokenExpiryMs(state.accessToken)
      if (!expiryMs) return false
      return Date.now() < expiryMs
    },
  },
  persist: true,  // requires @pinia/plugin-persistedstate
  actions: {
    authHeader() {
      if (!this.accessToken) return {}
      return { Authorization: `Bearer ${this.accessToken}` }
    },

    hydrateFromToken() {
      if (!this.accessToken) {
        this.userId = null
        this.user = null
        return
      }

      const payload = parseTokenPayload(this.accessToken)
      const parsedId = Number(payload?.user_id)
      this.userId = Number.isFinite(parsedId) && parsedId > 0 ? parsedId : null

      if (!this.isAuthenticated) {
        void this.ensureAccessToken()
      }
    },

    async ensureAccessToken() {
      if (!this.accessToken) return false

      const expiryMs = getTokenExpiryMs(this.accessToken)
      if (!expiryMs) return this.refreshAccessToken()
      if (Date.now() < expiryMs - 30_000) return true

      return this.refreshAccessToken()
    },

    async login({ username, password }) {
      const res = await $fetch('/api/backend/accounts/token/', {
        method: 'POST',
        body: { username, password },
      })
      this.accessToken = res.access
      this.refreshToken = res.refresh
      this.hydrateFromToken()
      await this.fetchUser()
    },
    async signup({ username, password }) {
      await $fetch('/api/backend/accounts/signup/', {
        method: 'POST',
        body: {
          username, password
        },
      })
      // auto-login after register
      await this.login({ username, password })
    },
    async refreshAccessToken() {
      if (!this.refreshToken) return false

      try {
        const res = await $fetch('/api/backend/accounts/token/refresh/', {
          method: 'POST',
          body: { refresh: this.refreshToken },
        })
        this.accessToken = res.access
        if (res.refresh) this.refreshToken = res.refresh
        this.hydrateFromToken()
        return true
      } catch (err) {
        console.error('Refresh token failed', err)
        this.logout(false)
        return false
      }
    },
    async fetchUser() {
      const ok = await this.ensureAccessToken()
      if (!ok) return null

      this.user = await $fetch('/api/backend/accounts/me/', {
        headers: this.authHeader()
      })
      this.userId = Number(this.user?.id) || this.userId
      return this.user
    },
    logout(redirect = true) {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      this.userId = null
      if (redirect) {
        const router = useRouter()
        router.push('/login')
      }
    }
  }
})
