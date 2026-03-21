<template>
  <UContainer class="w-full max-w-3xl py-8">
    <div class="space-y-6">
      <div class="space-y-2">
        <h1 class="text-3xl font-semibold">Личный кабинет</h1>
        <p class="text-sm text-muted">
          Здесь можно обновить данные профиля и сменить пароль без выхода из аккаунта.
        </p>
      </div>

      <UAlert
        color="neutral"
        variant="subtle"
        icon="i-lucide-info"
        title="Профиль синхронизируется с текущим аккаунтом"
        description="Если вы открыли страницу сразу после входа, данные подтянутся автоматически."
      />

      <ProfileCard />
      <PasswordChangeCard />
    </div>
  </UContainer>
</template>

<script setup lang="ts">
const auth = useAuthStore()

await useAsyncData('profile-user', async () => {
  if (!auth.user) {
    return await auth.fetchUser()
  }
  return auth.user
})
</script>
