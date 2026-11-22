# Казарян Асмик
# Программа считает долю прибыли или убытков на основе данных из CSV
from utils.data_loader import load_data


def calculate(amount, buy_price, now_price):
    coins = amount / buy_price  # Какой долей монеты владеем
    total_now = coins * now_price  # Стоимость этой доли монеты сейчас в валюте
    # Прибыль в процентах (увеличилась или упала)
    profit = (total_now - amount) / amount * 100
    # Функция выдаёт результат: стоимость доли и прибыль
    return total_now, profit


def get_price(df, coin, date):
    coin_rows = df[df["Coin_Name"] == coin]
    row = coin_rows[coin_rows["Date"] == date]
    return row["Close"].iloc[0]


if __name__ == "__main__":
    # Загружаем и очищаем таблицу с ценами (функция Насти)
    df = load_data("data/historical_crypto_data.csv")
    amount = 1000  # Кол-во вложенных денег
    buy_price = get_price(df, "BTC", "2020-01-01")  # Цена BTC на 01.01.2020 из таблицы
    now_price = get_price(
        df, "BTC", "2026-06-03"
    )  # Цена BTC на последний день в таблице

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
