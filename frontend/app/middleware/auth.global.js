import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  auth.hydrateFromToken()
  await auth.ensureAccessToken()

  const publicPages = ['/login', '/signup']
  const isPublicPage = publicPages.includes(to.path)

  if (!auth.isAuthenticated && !isPublicPage) {
    return navigateTo('/login')
  }

  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchUser()
    } catch (error) {
      console.error('Failed to fetch current user in global middleware', error)
    }
  }

  if (auth.isAuthenticated && isPublicPage) {
    return navigateTo('/')
  }
})
