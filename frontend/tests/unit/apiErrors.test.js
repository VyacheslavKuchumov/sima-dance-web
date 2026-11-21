import { test } from 'node:test'
import assert from 'node:assert/strict'
import { getApiErrorMessage } from '../../app/utils/apiErrors.js'

test('explains invalid usernames and duplicate logins from Django', () => {
  assert.match(getApiErrorMessage({ status: 400, data: { username: ['Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'] } }), /Логин:.*Пробелы в логине недопустимы/)
  assert.match(getApiErrorMessage({ status: 400, data: { username: ['A user with that username already exists.'] } }), /логин уже занят/)
})

test('keeps multiple field errors, including nested Nuxt proxy data', () => {
  const error = { data: { statusCode: 400, data: { username: ['This field is required.'], full_name: ['This field may not be blank.'] } } }
  assert.equal(getApiErrorMessage(error), 'Логин: Заполните это поле. Ваше ФИО: Поле не должно быть пустым.')
})

test('passes translated proxy messages and Russian application errors through', () => {
  assert.equal(getApiErrorMessage({ status: 400, data: { data: { message: 'Логин: Этот логин уже занят.' } } }), 'Логин: Этот логин уже занят.')
  assert.equal(getApiErrorMessage(new Error('Нужна авторизация администратора.')), 'Нужна авторизация администратора.')
})

test('explains bad credentials, expired sessions and booking conflicts', () => {
  assert.equal(getApiErrorMessage({ status: 401, data: { detail: 'No active account found with the given credentials' } }), 'Неверный логин или пароль.')
  assert.match(getApiErrorMessage({ status: 401 }), /Сессия истекла/)
  assert.match(getApiErrorMessage({ status: 409, data: { detail: 'Seat already booked: 12' } }), /место уже занято/)
  assert.match(getApiErrorMessage({ status: 400, data: { detail: 'Hold expired for booking: 12' } }), /удержания места истекло/)
})

test('hides technical errors and server internals', () => {
  assert.match(getApiErrorMessage({ status: 500, data: { detail: 'Ошибка SQL: секрет' } }), /временно недоступен/)
  assert.equal(getApiErrorMessage({ status: 400, message: '[POST] /api/backend/accounts/signup/: 400', data: '<html>Bad Request</html>' }), 'Проверьте введённые данные и повторите попытку.')
  assert.equal(getApiErrorMessage(new Error('Unexpected internal failure'), 'Не удалось обновить профиль.'), 'Не удалось обновить профиль.')
})

test('explains connection failures and rate limiting', () => {
  assert.match(getApiErrorMessage(new TypeError('Failed to fetch')), /Проверьте интернет/)
  assert.match(getApiErrorMessage({ status: 429 }), /Слишком много попыток/)
})
