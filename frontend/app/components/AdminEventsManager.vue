<template>
  <div class="space-y-6">
    <UCard class="w-full">
      <template #header>
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div class="space-y-1">
            <h1 class="text-2xl font-semibold">Управление концертами</h1>
            <p class="text-sm text-gray-500">
              Создавайте новые события, редактируйте карточки концертов и управляйте архивом.
            </p>
          </div>

          <div class="flex w-full flex-col gap-2 sm:flex-row lg:w-auto">
            <UInput
              v-model="search"
              class="w-full sm:min-w-80"
              placeholder="Поиск по названию или дате"
            />

            <UButton
              color="neutral"
              variant="outline"
              :loading="loading"
              @click="loadEvents"
            >
              Обновить
            </UButton>

            <UButton color="primary" @click="openCreate">
              Новый концерт
            </UButton>
          </div>
        </div>
      </template>

      <UProgress v-if="loading" animation="swing" />

      <div v-else class="space-y-4">
        <UAlert
          v-if="!filteredEvents.length"
          color="neutral"
          variant="subtle"
          title="События не найдены"
          description="Измените фильтр или добавьте новое событие."
        />

        <article
          v-for="event in filteredEvents"
          :key="event.id"
          class="rounded-2xl border border-gray-200 p-4"
        >
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div class="space-y-2">
              <div class="flex flex-wrap items-center gap-2">
                <h2 class="text-lg font-semibold">{{ event.title }}</h2>
                <UBadge :color="event.archived ? 'neutral' : 'success'" variant="subtle">
                  {{ event.archived ? 'В архиве' : 'Активен' }}
                </UBadge>
              </div>

              <div class="space-y-1 text-sm text-gray-600">
                <p><span class="font-medium text-gray-900">Дата:</span> {{ formatDate(event.starts_at) }}</p>
                <p><span class="font-medium text-gray-900">Изображение:</span> {{ event.img_url || 'Стандартное изображение карточки' }}</p>
              </div>
            </div>

            <div class="flex flex-col gap-2 sm:flex-row lg:flex-col">
              <UButton
                color="primary"
                variant="outline"
                :to="`/seats/${event.id}`"
              >
                Открыть схему
              </UButton>

              <UButton
                color="neutral"
                @click="openEdit(event)"
              >
                Редактировать
              </UButton>
            </div>
          </div>
        </article>
      </div>
    </UCard>

    <UModal v-model:open="modalOpen" :title="editingEventId ? 'Редактировать концерт' : 'Новый концерт'">
      <template #body>
        <form class="space-y-4" @submit.prevent="saveEvent">
          <UFormField label="Название" required>
            <UInput
              v-model="form.title"
              class="w-full"
              placeholder="Например, Весенний концерт"
              :disabled="saving"
            />
          </UFormField>

          <UFormField label="Дата" required>
            <UInput
              v-model="form.starts_at"
              class="w-full"
              type="date"
              :disabled="saving"
            />
          </UFormField>

          <UFormField label="Ссылка на изображение">
            <UInput
              v-model="form.img_url"
              class="w-full"
              placeholder="https://..."
              :disabled="saving"
            />
          </UFormField>

          <label class="flex items-center gap-3 rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-700">
            <input
              v-model="form.archived"
              type="checkbox"
              :disabled="saving"
            >
            Скрыть концерт в архив
          </label>
        </form>
      </template>

      <template #footer>
        <UButton
          color="neutral"
          variant="outline"
          :disabled="saving"
          @click="closeModal"
        >
          Закрыть
        </UButton>

        <UButton
          color="primary"
          :loading="saving"
          @click="saveEvent"
        >
          {{ editingEventId ? 'Сохранить изменения' : 'Создать концерт' }}
        </UButton>
      </template>
    </UModal>
  </div>
</template>

<script setup>
const { request } = useAdminApi()
const toast = useAppToast()
const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const modalOpen = ref(false)
const editingEventId = ref(null)
const search = ref('')
const events = ref([])

const form = reactive({
  title: '',
  starts_at: '',
  img_url: '',
  archived: false,
})

const filteredEvents = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return events.value

  return events.value.filter((event) => {
    const haystack = [event.title, event.starts_at]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(query)
  })
})

function formatDate(value) {
  if (!value) return '—'

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(new Date(value))
}

function resetForm() {
  form.title = ''
  form.starts_at = ''
  form.img_url = ''
  form.archived = false
}

function clearEditQuery() {
  if (!route.query.edit) return

  const query = { ...route.query }
  delete query.edit
  void router.replace({ query })
}

function openCreate() {
  editingEventId.value = null
  resetForm()
  modalOpen.value = true
  clearEditQuery()
}

function openEdit(event, syncQuery = true) {
  editingEventId.value = event.id
  form.title = event.title ?? ''
  form.starts_at = event.starts_at ?? ''
  form.img_url = event.img_url ?? ''
  form.archived = Boolean(event.archived)
  modalOpen.value = true

  if (syncQuery) {
    void router.replace({
      query: {
        ...route.query,
        edit: String(event.id),
      },
    })
  }
}

function closeModal() {
  modalOpen.value = false
  editingEventId.value = null
  resetForm()
  clearEditQuery()
}

async function loadEvents() {
  loading.value = true

  try {
    const response = await request('/api/backend/booking/events/')
    events.value = Array.isArray(response) ? response : response?.results ?? []
  } catch (error) {
    console.error('Failed to load admin events', error)
    toast.add({
      title: 'Не удалось загрузить концерты',
      description: error?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    loading.value = false
  }
}

async function saveEvent() {
  if (!form.title.trim() || !form.starts_at) {
    toast.add({
      title: 'Заполните обязательные поля',
      description: 'Название и дата концерта обязательны.',
      color: 'warning',
    })
    return
  }

  saving.value = true

  try {
    const isEditing = Boolean(editingEventId.value)
    const payload = {
      title: form.title.trim(),
      starts_at: form.starts_at,
      img_url: form.img_url.trim(),
      archived: Boolean(form.archived),
    }

    if (editingEventId.value) {
      await request(`/api/backend/booking/events/${editingEventId.value}/`, {
        method: 'PATCH',
        body: payload,
      })
    } else {
      await request('/api/backend/booking/events/', {
        method: 'POST',
        body: payload,
      })
    }

    await loadEvents()
    closeModal()
    toast.add({
      title: isEditing ? 'Концерт обновлен' : 'Концерт создан',
      description: 'Изменения сохранены.',
      color: 'success',
    })
  } catch (error) {
    console.error('Failed to save event', error)
    toast.add({
      title: 'Не удалось сохранить концерт',
      description: error?.message ?? 'Проверьте данные и повторите попытку.',
      color: 'error',
    })
  } finally {
    saving.value = false
  }
}

watch(
  [events, () => route.query.edit],
  ([loadedEvents, editId]) => {
    if (!editId) return

    const event = loadedEvents.find((item) => String(item.id) === String(editId))
    if (!event) return
    if (modalOpen.value && editingEventId.value === event.id) return

    openEdit(event, false)
  },
  { immediate: true },
)

onMounted(() => {
  void loadEvents()
})
</script>
