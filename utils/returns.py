import pandas as pd


def calculate_average_daily_returns(df: pd.DataFrame) -> pd.Series:
    """
    Рассчитывает среднюю дневную доходность для каждой монеты.

    Доходность за день = (Цена закрытия сегодня - Цена закрытия вчера) / Цена закрытия вчера
    """
    # Сортируем данные по монете и дате, чтобы pct_change работал корректно
    df_sorted = df.sort_values(by=["Coin_Name", "Date"])

    # Вычисляем дневную доходность внутри каждой группы монет
    # pct_change() автоматически обрабатывает первый день (возвращает NaN)
    daily_returns = df_sorted.groupby("Coin_Name")["Close"].pct_change()

    # Добавляем колонку с доходностью в отсортированный датафрейм
    df_sorted["Daily_Return"] = daily_returns

    # Группируем по монете и считаем среднее значение доходности
    average_returns = (
        df_sorted.groupby("Coin_Name")["Daily_Return"]
        .mean()
        .sort_values(ascending=False)
    )

    return average_returns
