<template>
  <header class="border-b border-default shadow-sm">
    <nav class="container mx-auto flex items-center justify-between gap-3 py-4 px-6">
      <h1 class="text-xl font-bold" @click="$router.push('/')">Simadancing 💃</h1>

      <div class="flex items-center gap-2">
        <div v-if="auth.isImpersonating" class="flex items-center gap-2">
          <UBadge color="warning" variant="soft" class="hidden sm:inline-flex">
            Вы вошли как {{ auth.user?.username || 'пользователь' }}
          </UBadge>

          <UButton
            color="warning"
            variant="soft"
            size="sm"
            icon="i-lucide-undo-2"
            @click="stopImpersonation"
          >
            Вернуться в админку
          </UButton>
        </div>

        <!-- Slideover Menu -->
        <USlideover v-model:open="menuOpen" title="Меню" close-icon="i-lucide-x">
          <UButton
            icon="i-lucide-menu"
            color="neutral"
            variant="ghost"
          />
          <template #body>
            <UNavigationMenu
              orientation="vertical"
              :items="items"
            >
              <template #item="{ item }">
                <!-- Normal navigation item -->
                <UButton
                  v-if="item.to"
                  :icon="item.icon"
                  variant="ghost"
                  color="neutral"
                  :to="item.to"
                  class="w-full justify-start"
                >
                  {{ item.label }}
                </UButton>

                <!-- Logout special item -->
                <UButton
                  v-else-if="item.action === 'logout'"
                  :icon="item.icon"
                  variant="ghost"
                  color="error"
                  class="w-full justify-start"
                  @click="auth.logout"
                >
                  {{ item.label }}
                </UButton>
              </template>
            </UNavigationMenu>
        </template>
        </USlideover>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const toast = useAppToast()
const menuOpen = ref(false)

// Build navigation items dynamically depending on authentication
const items = computed<NavigationMenuItem[][]>(() => {
  if (auth.isAuthenticated) {
    const baseItems: NavigationMenuItem[] = [
      { label: 'Главная', icon: 'i-lucide-home', to: '/' },
      { label: 'Мои брони', icon: 'i-lucide-shopping-cart', to: '/cart' },
      { label: 'Профиль', icon: 'i-lucide-user', to: '/profile' },
    ]

    const adminItems: NavigationMenuItem[] = auth.isSuperuser
      ? [
          { label: 'Управление пользователями', icon: 'i-lucide-users', to: '/admin/users' },
          { label: 'Управление концертами', icon: 'i-lucide-music-4', to: '/admin/events' },
          { label: 'Управление бронями', icon: 'i-lucide-ticket', to: '/admin/bookings' },
        ]
      : []

    const actionItems: NavigationMenuItem[] = [
      {
        label: 'Выйти',
        icon: 'i-lucide-log-out',
        action: 'logout',
      },
    ]

    return [
      baseItems,
      ...(adminItems.length ? [adminItems] : []),
      actionItems,
    ]
  } else {
    return [[
      { label: 'Войти', icon: 'i-lucide-log-in', to: '/login' }
    ]]
  }
})

watch(() => route.fullPath, () => {
  menuOpen.value = false
})

async function stopImpersonation() {
  try {
    await auth.stopImpersonation()
    toast.add({
      title: 'Возврат в админку выполнен',
      description: 'Исходная сессия администратора восстановлена.',
      color: 'success',
    })
    menuOpen.value = false
    await router.push('/admin/users')
  } catch (error) {
    console.error('Failed to restore admin session', error)
    toast.add({
      title: 'Не удалось восстановить админскую сессию',
      description: error?.message ?? 'Пожалуйста, войдите снова.',
      color: 'error',
    })
  }
}
</script>
