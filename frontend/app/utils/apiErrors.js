const fields = {
  username: 'Логин', password: 'Пароль', group: 'Группа',
  full_name: 'Ваше ФИО', child_full_name: 'ФИО ребёнка',
  current_password: 'Текущий пароль', new_password: 'Новый пароль',
  email: 'Электронная почта', event_id: 'Событие', seat_id: 'Место',
  user_id: 'Пользователь', name: 'Название', price: 'Цена',
}

function translate(message) {
  if (typeof message !== 'string') return ''
  const text = message.trim()
  if (/^[А-Яа-яЁё]/u.test(text) && !/https?:\/\/|Traceback|<[^>]+>/.test(text)) return text
  if (/user with that username already exists/i.test(text)) return 'Этот логин уже занят. Выберите другой или войдите в свой аккаунт.'
  if (/enter a valid username/i.test(text)) return 'Используйте буквы, цифры и символы @ . + - _. Пробелы в логине недопустимы.'
  if (/no active account found|unable to log in with provided credentials/i.test(text)) return 'Неверный логин или пароль.'
  if (/authentication credentials|token.*(?:invalid|expired)|given token not valid/i.test(text)) return 'Сессия истекла. Пожалуйста, войдите снова.'
  if (/this field is required/i.test(text)) return 'Заполните это поле.'
  if (/may not be (?:blank|null)/i.test(text)) return 'Поле не должно быть пустым.'
  if (/ensure this field has no more than (\d+) characters/i.test(text)) return `Введите не более ${text.match(/no more than (\d+)/i)[1]} символов.`
  if (/ensure this field has at least (\d+) characters/i.test(text)) return `Введите не менее ${text.match(/at least (\d+)/i)[1]} символов.`
  if (/invalid pk|object does not exist/i.test(text)) return 'Выбранное значение больше недоступно. Обновите страницу и выберите снова.'
  if (/valid integer|valid number/i.test(text)) return 'Введите корректное число.'
  if (/valid email/i.test(text)) return 'Введите корректный адрес электронной почты.'
  if (/password is too common/i.test(text)) return 'Выберите менее распространённый пароль.'
  if (/password is entirely numeric/i.test(text)) return 'Пароль не должен состоять только из цифр.'
  if (/password is too short/i.test(text)) return 'Пароль слишком короткий. Используйте не менее 8 символов.'
  if (/seat already booked|seat.*(?:held|reserved)|seat is not available/i.test(text)) return 'Это место уже занято. Выберите другое.'
  if (/hold.*expired/i.test(text)) return 'Время удержания места истекло. Выберите место заново.'
  if (/booking not in held state|only held bookings/i.test(text)) return 'Эту бронь уже нельзя подтвердить. Обновите список бронирований.'
  if (/not found/i.test(text)) return 'Запись не найдена. Обновите страницу.'
  if (/permission|not allowed/i.test(text)) return 'У вас нет прав для этого действия.'
  return ''
}

function validationMessages(payload) {
  if (typeof payload === 'string') return [translate(payload)].filter(Boolean)
  if (Array.isArray(payload)) return payload.flatMap(validationMessages)
  if (!payload || typeof payload !== 'object') return []
  return Object.entries(payload).flatMap(([key, value]) => {
    if (['statusCode', 'statusMessage', 'stack', 'url', 'code'].includes(key)) return []
    const messages = validationMessages(value)
    return fields[key] ? messages.map(message => `${fields[key]}: ${message}`) : messages
  })
}

/** Accept both DRF responses and errors wrapped by the Nuxt API proxy. */
export function getApiErrorMessage(error, fallback = 'Не удалось выполнить действие. Попробуйте ещё раз.') {
  const status = Number(error?.statusCode || error?.status || error?.response?.status || error?.data?.statusCode)
  if (status >= 500) return 'Сервис временно недоступен. Попробуйте через несколько минут.'
  const payload = error?.data ?? error?.response?._data
  const messages = validationMessages(payload)
  if (messages.length) return [...new Set(messages)].join(' ')
  const message = translate(error?.message) || translate(payload?.statusMessage)
  if (message) return message
  if (status === 401) return 'Сессия истекла. Пожалуйста, войдите снова.'
  if (status === 403) return 'У вас нет прав для этого действия.'
  if (status === 404) return 'Запись не найдена. Обновите страницу.'
  if (status === 409) return 'Данные уже изменились. Обновите страницу и повторите попытку.'
  if (status === 429) return 'Слишком много попыток. Подождите немного и попробуйте снова.'
  if (status === 400 || status === 422) return 'Проверьте введённые данные и повторите попытку.'
  if (/fetch|network|timeout|abort/i.test(error?.message ?? '')) return 'Не удалось связаться с сервером. Проверьте интернет и попробуйте ещё раз.'
  return fallback
}
