import requests


# Функция для получения информации обо всех местах мероприятия по event_uid.
def get_event_seats(event_uid):
    """
    Получает список мест для заданного мероприятия.

    Аргументы:
      event_uid (str): Идентификатор мероприятия.

    Возвращает:
      list: Список словарей с информацией о местах или пустой список при ошибке.
    """
    url = f"https://simadancing.ru/api/seats_in_events/{event_uid}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # вызывает исключение при ошибочном статусе запроса
    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []

    try:
        seats = response.json()
        return seats
    except ValueError:
        print("Ошибка: не удалось распарсить JSON-ответ")
        return []


# Функция для обновления конкретного места посредством PUT-запроса.
def update_seat_in_event(seat_in_event_id, new_price, new_status):
    """
    Обновляет цену и статус для заданного места.

    Аргументы:
      seat_in_event_id (int): Идентификатор записи в таблице SeatInEvent.
      new_price (int или float): Новая цена.
      new_status (str): Новый статус (например, 'available', 'booked', и т.п.).

    Возвращает:
      bool: True, если обновление прошло успешно, иначе False.
    """
    url = f"https://simadancing.ru/api/seats_in_events/{seat_in_event_id}"
    payload = {"price": new_price, "status": new_status}

    try:
        response = requests.put(url, json=payload)
        # Успех считается при статусах 200 или 204
        if response.status_code in (200, 204):
            print(f"Место с ID {seat_in_event_id} успешно обновлено.")
            return True
        else:
            print(f"Ошибка при обновлении места с ID {seat_in_event_id} (статус код: {response.status_code}).")
            return False
    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса на обновление: {e}")
        return False


def change_seats(section_filter, row_filter, seat_start, seat_end, new_price, new_status):
    # ID мероприятия, по которому будет осуществлен запрос
    event_uid = "6c92a6e3-1b59-4845-9e75-68cd03cf0f38"

    # Получение списка мест с API (контекст модели SeatInEvent)
    seats = get_event_seats(event_uid)
    if not seats:
        print("Нет данных по местам, либо произошла ошибка.")
        return

    # Вывод списка мест для ознакомления
    print("Список мест мероприятия:")
    for seat in seats:
        # Предполагается, что каждый словарь включает ключи:
        # 'seat_in_event_id', 'section', 'row', 'number', 'price', 'status'
        print(f"ID: {seat.get('seat_in_event_id')}, Секция: {seat.get('seat').get('section')}, "
              f"Ряд: {seat.get('seat').get('row')}, Номер: {seat.get('seat').get('number')}, "
              f"Цена: {seat.get('price')}, Статус: {seat.get('status')}")

    # # Получаем от пользователя фильтры для выбора мест
    # section_filter = input("Введите секцию для фильтрации: ").strip()
    # row_filter = input("Введите ряд для фильтрации: ").strip()
    # seat_start = input("Введите начальный номер места (целое число): ").strip()
    # seat_end = input("Введите конечный номер места (целое число): ").strip()
    # new_price_input = input("Введите новое значение цены: ").strip()
    # new_status = input("Введите новый статус для выбранных мест: ").strip()



    # Фильтрация мест согласно указанным критериям
    for seat in seats:
        # Если номер места отсутствует или его нельзя преобразовать в число, пропускаем
        try:
            seat_number = int(seat.get('seat').get('number'))
        except (ValueError, TypeError):
            continue

        if (seat.get('seat').get('section') == section_filter and
                seat.get('seat').get('row') == row_filter and
                seat_start <= seat_number <= seat_end):

            # Получаем идентификатор записи для обновления
            seat_id = seat.get('seat_in_event_id')
            if seat_id is not None:
                update_seat_in_event(seat_id, new_price, new_status)
            else:
                print("Отсутствует идентификатор для данного места. Обновление невозможно.")



# БАЛКОН
section = "Балкон"
change_seats(section_filter=section, row_filter="7", seat_start=1, seat_end=26, new_price=350, new_status="available")
change_seats(section_filter=section, row_filter="6", seat_start=1, seat_end=24, new_price=350, new_status="available")

change_seats(section_filter=section, row_filter="5", seat_start=1, seat_end=24, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter="4", seat_start=1, seat_end=24, new_price=400, new_status="available")

change_seats(section_filter=section, row_filter="3", seat_start=1, seat_end=24, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter="2", seat_start=1, seat_end=28, new_price=500, new_status="available")

change_seats(section_filter=section, row_filter="1", seat_start=1, seat_end=28, new_price=550, new_status="available")



# АМФИТЕАТР
section = "Амфитеатр"
change_seats(section_filter=section, row_filter="18", seat_start=1, seat_end=31, new_price=350, new_status="available")

change_seats(section_filter=section, row_filter="17", seat_start=1, seat_end=6, new_price=350, new_status="available")
change_seats(section_filter=section, row_filter="17", seat_start=7, seat_end=20, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter="17", seat_start=21, seat_end=26, new_price=350, new_status="available")

change_seats(section_filter=section, row_filter="16", seat_start=1, seat_end=26, new_price=400, new_status="available")

change_seats(section_filter=section, row_filter="15", seat_start=1, seat_end=6, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter="15", seat_start=7, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter="15", seat_start=21, seat_end=26, new_price=400, new_status="available")

change_seats(section_filter=section, row_filter="14", seat_start=1, seat_end=6, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter="14", seat_start=7, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter="14", seat_start=21, seat_end=26, new_price=400, new_status="available")

change_seats(section_filter=section, row_filter="13", seat_start=2, seat_end=11, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter="13", seat_start=16, seat_end=26, new_price=550, new_status="available")


# ПАРТЕР
section = "Партер"
row = "12"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_status="available")

row = "11"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_status="available")

row = "10"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_status="available")

row = "9"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_status="available")

row = "8"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_status="available")

row = "7"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_status="available")

row = "6"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_status="available")

row = "5"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=3, new_price=400, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=4, seat_end=7, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=8, seat_end=15, new_price=550, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=16, seat_end=19, new_price=500, new_status="available")
change_seats(section_filter=section, row_filter=row, seat_start=20, seat_end=22, new_price=400, new_status="available")

row = "4"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=22, new_price=550, new_status="available")

row = "3"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=20, new_price=550, new_status="available")

row = "2"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=18, new_price=550, new_status="available")

row = "1"
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=16, new_price=550, new_status="available")




# unavailable
section = "Балкон"
change_seats(section_filter=section, row_filter="1", seat_start=13, seat_end=21, new_price=550, new_status="unavailable")
change_seats(section_filter=section, row_filter="2", seat_start=15, seat_end=23, new_price=500, new_status="unavailable")
change_seats(section_filter=section, row_filter="3", seat_start=13, seat_end=16, new_price=500, new_status="unavailable")

section = "Партер"
change_seats(section_filter=section, row_filter="5", seat_start=10, seat_end=11, new_price=550, new_status="unavailable")
change_seats(section_filter=section, row_filter="11", seat_start=13, seat_end=16, new_price=550, new_status="unavailable")

section = "Партер"
change_seats(section_filter=section, row_filter="1", seat_start=9, seat_end=9, new_price=550, new_status="unavailable")