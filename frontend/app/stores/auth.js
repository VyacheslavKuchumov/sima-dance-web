
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
    signupGroups: [],
    impersonationSession: null,
  }),
  getters: {
    isAuthenticated: (state) => {
      if (!state.accessToken) return false
      const expiryMs = getTokenExpiryMs(state.accessToken)
      if (!expiryMs) return false
      return Date.now() < expiryMs
    },
    isSuperuser: (state) => Boolean(state.user?.is_superuser),
    isImpersonating: (state) => Boolean(state.impersonationSession?.refreshToken),
  },
  persist: true,  // requires @pinia/plugin-persistedstate
  actions: {
    applySession({ accessToken = null, refreshToken = null, user = null, userId = null } = {}) {
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      this.user = user
      this.userId = userId
    },

    captureSession() {
      return {
        accessToken: this.accessToken,
        refreshToken: this.refreshToken,
        user: this.user,
        userId: this.userId,
      }
    },

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
      this.impersonationSession = null
      this.applySession({
        accessToken: res.access,
        refreshToken: res.refresh,
      })
      this.hydrateFromToken()
      await this.fetchUser()
    },
    async fetchSignupGroups({ force = false } = {}) {
      if (this.signupGroups.length && !force) return this.signupGroups

      const groups = await $fetch('/api/backend/accounts/signup-groups/')
      this.signupGroups = Array.isArray(groups) ? groups : []
      return this.signupGroups
    },
    async signup({ username, password, group, full_name, child_full_name }) {
      await $fetch('/api/backend/accounts/signup/', {
        method: 'POST',
        body: {
          username,
          password,
          group,
          full_name,
          child_full_name,
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

        if (this.restoreOriginalSession()) {
          return this.ensureAccessToken()
        }

        this.logout(false)
        return false
      }
    },
    async fetchUser() {
      const ok = await this.ensureAccessToken()
      if (!ok) return null

      this.user = await $fetch('/api/backend/accounts/me/', {
        headers: this.authHeader(),
      })
      this.userId = Number(this.user?.id) || this.userId
      return this.user
    },
    restoreOriginalSession() {
      if (!this.impersonationSession) return false

      const originalSession = this.impersonationSession
      this.impersonationSession = null
      this.applySession(originalSession)
      this.hydrateFromToken()

      return true
    },
    async impersonateUser(userId) {
      const ok = await this.ensureAccessToken()
      if (!ok) {
        throw new Error('Нужна активная сессия администратора.')
      }

      const originalSession = this.captureSession()
      const res = await $fetch('/api/backend/accounts/admin/impersonate/', {
        method: 'POST',
        body: { user_id: userId },
        headers: this.authHeader(),
      })

      if (!this.impersonationSession) {
        this.impersonationSession = originalSession
      }

      this.applySession({
        accessToken: res.access,
        refreshToken: res.refresh,
        user: res.user ?? null,
        userId: Number(res.user?.id) || null,
      })
      this.hydrateFromToken()

      if (!this.user) {
        const loadedUser = await this.fetchUser()
        if (!loadedUser) {
          throw new Error('Не удалось завершить вход за пользователя.')
        }
      }

      return this.user
    },
    async stopImpersonation() {
      const restored = this.restoreOriginalSession()
      if (!restored) return false

      const restoredUser = await this.fetchUser()
      if (!restoredUser) {
        throw new Error('Не удалось восстановить исходную сессию.')
      }

      return true
    },
    async updateProfile(payload) {
      const ok = await this.ensureAccessToken()
      if (!ok) return null

      this.user = await $fetch('/api/backend/accounts/me/', {
        method: 'PATCH',
        body: payload,
        headers: this.authHeader(),
      })
      this.userId = Number(this.user?.id) || this.userId
      return this.user
    },
    async changePassword(payload) {
      const ok = await this.ensureAccessToken()
      if (!ok) return false

      await $fetch('/api/backend/accounts/change-password/', {
        method: 'POST',
        body: payload,
        headers: this.authHeader(),
      })
      return true
    },
    logout(redirect = true) {
      this.applySession()
      this.signupGroups = []
      this.impersonationSession = null
      if (redirect) {
        const router = useRouter()
        router.push('/login')
      }
    }
  }
})
