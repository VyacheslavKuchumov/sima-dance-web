export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()

  auth.hydrateFromToken()

  const ok = await auth.ensureAccessToken()
  if (!ok) {
    return navigateTo('/login')
  }

  if (!auth.user) {
    try {
      await auth.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user for superuser middleware', error)
      return navigateTo('/login')
    }
  }

  if (!auth.isSuperuser) {
    return navigateTo('/')
  }
})
