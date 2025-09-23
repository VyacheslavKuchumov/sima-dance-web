<template>
  <header class="border-b border-gray-200 shadow-sm :dark:border-gray-700">
    <nav class="container mx-auto flex items-center justify-between py-4 px-6">
      <h1 class="text-xl font-bold">Simadancing</h1>

      <!-- Slideover Menu -->
      <USlideover title="Меню" close-icon="i-lucide-arrow-right">
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

// Build navigation items dynamically depending on authentication
const items = computed<NavigationMenuItem[][]>(() => {
  if (auth.isAuthenticated) {
    return [[
      { label: 'Главная', icon: 'i-lucide-home', to: '/' },
      { label: 'Профиль', icon: 'i-lucide-user', to: '/profile' },
      {
        label: 'Выйти',
        icon: 'i-lucide-log-out',
        action: 'logout',
      }
    ]]
  } else {
    return [[
      { label: 'Войти', icon: 'i-lucide-log-in', to: '/login' }
    ]]
  }
})
</script>