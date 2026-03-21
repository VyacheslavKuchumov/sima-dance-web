import { getQuery, readBody } from 'h3'
import { callBackend } from '~~/server/utils/backend'

const BODY_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])
const PUBLIC_POST_PATHS = new Set([
  '/accounts/token',
  '/accounts/token/refresh',
  '/accounts/signup'
])

function toBackendPath(input: string | string[] | undefined) {
  if (!input) return '/'
  if (Array.isArray(input)) return `/${input.join('/')}`
  return `/${input}`
}

function normalizePath(path: string) {
  if (path.length > 1 && path.endsWith('/')) return path.slice(0, -1)
  return path
}

function ensureTrailingSlash(path: string) {
  if (path === '/') return path
  if (path.endsWith('/')) return path
  return `${path}/`
}

function isPublicRequest(method: string, path: string) {
  const normalizedPath = normalizePath(path)

  if (method === 'POST' && PUBLIC_POST_PATHS.has(normalizedPath)) {
    return true
  }

  if (method === 'GET') {
    if (normalizedPath === '/accounts/signup-groups') return true
    if (normalizedPath === '/booking/events') return true
    if (/^\/booking\/events\/\d+$/.test(normalizedPath)) return true
    if (/^\/booking\/events\/\d+\/seatmap$/.test(normalizedPath)) return true
  }

  return false
}

export default defineEventHandler(async (event) => {
  const method = (event.method || 'GET').toUpperCase() as 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  const rawPath = toBackendPath(event.context.params?.path)
  const normalizedPath = normalizePath(rawPath)
  const backendPath = ensureTrailingSlash(rawPath)
  const body = BODY_METHODS.has(method) ? await readBody(event) : undefined

  const isPublic = isPublicRequest(method, normalizedPath)

  return callBackend(event, method, backendPath, {
    body,
    query: getQuery(event),
    requireAuth: !isPublic
  })
})
