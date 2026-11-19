<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-4">
        <h2 class="text-xl font-semibold">Потенциальная выручка за все доступные места</h2>
        <UButton :loading="loading" variant="outline" @click="load">Пересчитать</UButton>
      </div>
    </template>
    <p class="mb-4 text-sm text-muted">Общий зал для одного концерта. Включены забронированные места; места с отключённой доступностью исключены.</p>
    <UAlert v-if="error" color="error" :title="error" />
    <template v-else-if="report">
      <div class="grid gap-4 sm:grid-cols-3">
        <div v-for="section in report.sections" :key="section.section">
          <h3 class="font-semibold">{{ section.section }}</h3>
          <p>{{ section.seats_count }} мест — {{ money(section.total) }}</p>
          <p v-if="section.unpriced_count" class="text-sm text-warning">Без цены: {{ section.unpriced_count }} (учтены как 0 ₽)</p>
        </div>
      </div>
      <p class="mt-4 text-lg font-semibold">Итого: {{ money(report.total) }}</p>
      <p class="mt-2 text-sm text-muted">Расчёт сохранён: {{ new Date(report.sections[0].calculated_at).toLocaleString('ru-RU') }}</p>
    </template>
  </UCard>
</template>

<script setup>
const { request } = useAdminApi()
const report = ref(null)
const loading = ref(false)
const error = ref('')
const money = value => new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(Number(value))

async function load() {
  loading.value = true
  error.value = ''
  try {
    report.value = await request('/api/backend/booking/revenue/')
  } catch {
    error.value = 'Не удалось рассчитать выручку. Попробуйте ещё раз.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
