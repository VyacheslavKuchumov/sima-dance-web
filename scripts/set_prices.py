import requests

url = "http://127.0.0.1:8000/api/booking/seats/"


def get_seats(section=None, row=None):

    try:
        response = requests.get(url, params={"section": section, "row": row})
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
def update_seat_in_event(seat, new_price, new_availability):
   
    new_url = f"{url}{seat.get('id')}/"
    payload = {"price": new_price, "available": new_availability}

    try:
        response = requests.patch(new_url, json=payload)
        # Успех считается при статусах 200 или 204
        if response.status_code in (200, 204):
            print(f"Место {seat.get('section')}: {seat.get('row')}-{seat.get('number')} успешно обновлено.")
            return True
        else:
            print(f"Ошибка при обновлении места {seat.get('section')}: {seat.get('row')}-{seat.get('number')} (статус код: {response.status_code}).")
            return False
    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса на обновление: {e}")
        return False


def change_seats(section_filter, row_filter, seat_start, seat_end, new_price, new_availability):
    # Получаем все места
    seats = get_seats(section=section_filter, row=row_filter)
    if not seats:
        print("Нет данных по местам, либо произошла ошибка.")
        return
    print(f"Обновление мест в секции '{section_filter}', ряду '{row_filter}', местах с {seat_start} по {seat_end}...")
    # Фильтрация мест согласно указанным критериям
    for seat in seats:
        if (seat.get('section') == section_filter and
            seat.get('row') == row_filter and
            seat_start <= seat.get('number') <= seat_end):
            update_seat_in_event(seat, new_price, new_availability)

# БАЛКОН
section = "Балкон"
change_seats(section_filter=section, row_filter=7, seat_start=1, seat_end=26, new_price=350, new_availability="true")
change_seats(section_filter=section, row_filter=6, seat_start=1, seat_end=24, new_price=350, new_availability="true")

change_seats(section_filter=section, row_filter=5, seat_start=1, seat_end=24, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=4, seat_start=1, seat_end=24, new_price=400, new_availability="true")

change_seats(section_filter=section, row_filter=3, seat_start=1, seat_end=24, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=2, seat_start=1, seat_end=28, new_price=500, new_availability="true")

change_seats(section_filter=section, row_filter=1, seat_start=1, seat_end=28, new_price=550, new_availability="true")



# АМФИТЕАТР
section = "Амфитеатр"
change_seats(section_filter=section, row_filter=18, seat_start=1, seat_end=31, new_price=350, new_availability="true")

change_seats(section_filter=section, row_filter=17, seat_start=1, seat_end=6, new_price=350, new_availability="true")
change_seats(section_filter=section, row_filter=17, seat_start=7, seat_end=20, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=17, seat_start=21, seat_end=26, new_price=350, new_availability="true")

change_seats(section_filter=section, row_filter=16, seat_start=1, seat_end=26, new_price=400, new_availability="true")

change_seats(section_filter=section, row_filter=15, seat_start=1, seat_end=6, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=15, seat_start=7, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=15, seat_start=21, seat_end=26, new_price=400, new_availability="true")

change_seats(section_filter=section, row_filter=14, seat_start=1, seat_end=6, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=14, seat_start=7, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=14, seat_start=21, seat_end=26, new_price=400, new_availability="true")

change_seats(section_filter=section, row_filter=13, seat_start=2, seat_end=11, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=13, seat_start=16, seat_end=26, new_price=550, new_availability="true")


# ПАРТЕР
section = "Партер"
row = 12
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_availability="true")

row = 11
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_availability="true")

row = 10
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_availability="true")

row = 9
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_availability="true")

row = 8
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_availability="true")

row = 7
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_availability="true")

row = 6
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=4, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=5, seat_end=8, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=9, seat_end=16, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=17, seat_end=20, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=21, seat_end=24, new_price=400, new_availability="true")

row = 5
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=3, new_price=400, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=4, seat_end=7, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=8, seat_end=15, new_price=550, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=16, seat_end=19, new_price=500, new_availability="true")
change_seats(section_filter=section, row_filter=row, seat_start=20, seat_end=22, new_price=400, new_availability="true")

row = 4
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=22, new_price=550, new_availability="true")

row = 3
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=20, new_price=550, new_availability="true")

row = 2
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=18, new_price=550, new_availability="true")

row = 1
change_seats(section_filter=section, row_filter=row, seat_start=1, seat_end=16, new_price=550, new_availability="true")




# unavailable
section = "Балкон"
change_seats(section_filter=section, row_filter=1, seat_start=13, seat_end=21, new_price=550, new_availability="false")
change_seats(section_filter=section, row_filter=2, seat_start=15, seat_end=23, new_price=500, new_availability="false")
change_seats(section_filter=section, row_filter=3, seat_start=13, seat_end=16, new_price=500, new_availability="false")

section = "Партер"
change_seats(section_filter=section, row_filter=5, seat_start=10, seat_end=11, new_price=550, new_availability="false")
change_seats(section_filter=section, row_filter=11, seat_start=13, seat_end=16, new_price=550, new_availability="false")

section = "Партер"
change_seats(section_filter=section, row_filter=1, seat_start=9, seat_end=9, new_price=550, new_availability="false")