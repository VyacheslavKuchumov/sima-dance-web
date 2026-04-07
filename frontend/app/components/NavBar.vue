<template>
  <header class="border-b border-default shadow-sm">
    <nav class="container mx-auto flex items-center justify-between py-4 px-6">
      <h1 class="text-xl font-bold" @click="$router.push('/')">Simadancing 💃</h1>

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
    </nav>
  </header>
</template>

<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const auth = useAuthStore()
const route = useRoute()
const menuOpen = ref(false)

// Build navigation items dynamically depending on authentication
const items = computed<NavigationMenuItem[][]>(() => {
  if (auth.isAuthenticated) {
    const baseItems: NavigationMenuItem[] = [
      { label: 'Главная', icon: 'i-lucide-home', to: '/' },
      { label: 'Корзина', icon: 'i-lucide-shopping-cart', to: '/cart' },
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
</script>
