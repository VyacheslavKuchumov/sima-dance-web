import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuthStore()

  // Skip check for public pages
  const publicPages = ['/login', '/signup']
  if (publicPages.includes(to.path)) {
    return
  }

  // Redirect if not logged in
  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }
})