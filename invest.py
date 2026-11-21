# Казарян Асмик
# Программа считает долю прибыли или убытков в зависимости
# от кол-ва вложенных средств


def calculate(amount, buy_price, now_price):
    coins = amount / buy_price  # Какой долей монеты владеем
    total_now = coins * now_price  # Стоимость этой доли монеты сейчас в валюте
    # Прибыль в процентах (увеличилась или упала)
    profit = (total_now - amount) / amount * 100
    # Функция выдаёт результат: стоимость доли и прибыль
    return total_now, profit


amount = 1000  # Кол-во вложенных денег
buy_price = 7200.17  # Стоимость монеты на 2020 год
now_price = 66260.43  # Цена одной монеты ейчас

# Запустили ф-цию calculate с тремя числами и сложили результаты
# в total_now, profit
total_now, profit = calculate(amount, buy_price, now_price)

if profit >= 0:
    print(
        f"Вложив {amount}$, "
        f"сейчас у вас было бы {round(total_now, 2)}$. "
        f"Прибыль (+{round(profit, 2)}%) "
    )
else:
    print(
        f"Вложив {amount}$, "
        f"сейчас у вас было бы {round(total_now, 2)}$. "
        f"Убыток ({round(profit, 2)}%) "
    )
