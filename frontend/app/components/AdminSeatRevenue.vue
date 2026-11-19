<template>
  <UCard>
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-4">
        <h1 class="text-2xl font-semibold">Подсчёт выручки</h1>
        <UButton :loading="loading" variant="outline" @click="load">Обновить</UButton>
      </div>
    </template>
    <div class="space-y-5">
      <p class="text-sm text-muted">Потенциальная выручка от продажи всех доступных мест на один концерт, включая уже забронированные. Недоступные места исключены. Данные обновляются раз в минуту.</p>
      <label v-if="report?.events.length" class="block space-y-2">
        <span class="font-semibold">Концерт</span>
        <select v-model="eventId" class="block w-full rounded-lg border border-default bg-default p-2" :disabled="loading" @change="load">
          <option v-for="event in report.events" :key="event.id" :value="String(event.id)">
            {{ event.title }} — {{ event.starts_at }}
          </option>
        </select>
      </label>
      <UAlert v-if="error" color="error" :title="error" />
      <UProgress v-if="loading && !report" animation="swing" />
      <template v-if="report">
        <UAlert v-if="!report.event_id" color="neutral" title="Концертов пока нет" description="Потенциальная выручка рассчитана по залу. Для просмотра бронирований создайте концерт." />
        <div class="grid gap-4 sm:grid-cols-3">
          <div v-for="section in report.sections" :key="section.section" class="space-y-2 rounded-xl border border-default p-4">
            <h2 class="text-lg font-semibold">{{ section.section }}</h2>
            <p class="text-xl font-semibold">{{ money(section.total) }}</p>
            <p>Всего доступных мест: {{ section.seats_count }}</p>
            <p>Забронировано: <strong>{{ section.reserved_count }}</strong></p>
            <p class="text-sm text-muted">Удержано: {{ section.held_count }} · Подтверждено: {{ section.confirmed_count }}</p>
            <p>Свободно: {{ section.free_count }}</p>
            <p v-if="section.unpriced_count" class="text-sm text-warning">Без цены: {{ section.unpriced_count }} (учтены как 0 ₽)</p>
          </div>
        </div>
        <div class="space-y-2">
          <p class="text-lg font-semibold">Общая потенциальная выручка: {{ money(report.total) }}</p>
          <p>Забронировано: {{ report.reserved_count }} из {{ report.seats_count }} · Свободно: {{ report.free_count }}</p>
          <p class="text-sm text-muted">Расчёт сохранён: {{ new Date(report.sections[0].calculated_at).toLocaleString('ru-RU') }}</p>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
const { request } = useAdminApi()
const report = ref(null)
const eventId = ref('')
const loading = ref(false)
const error = ref('')
let refreshTimer
const money = value => new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(Number(value))

async function load() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    const query = eventId.value ? { event_id: eventId.value } : {}
    report.value = await request('/api/backend/booking/revenue/', { query })
    eventId.value = report.value.event_id ? String(report.value.event_id) : ''
  } catch {
    error.value = 'Не удалось обновить расчёт. Повторим через минуту или нажмите «Обновить».'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
  refreshTimer = setInterval(load, 60_000)
})
onBeforeUnmount(() => clearInterval(refreshTimer))
</script>
