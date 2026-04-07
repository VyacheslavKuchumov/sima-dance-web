export function useAdminApi() {
  const auth = useAuthStore()

  async function request(path, options = {}) {
    const ok = await auth.ensureAccessToken()
    if (!ok) {
      throw new Error('Нужна авторизация администратора.')
    }

    return await $fetch(path, {
      ...options,
      headers: {
        ...(options.headers ?? {}),
        ...auth.authHeader(),
      },
    })
  }

  return {
    request,
  }
}
