import pandas as pd


def calculate_average_volatility(df: pd.DataFrame, window: int = 30) -> pd.Series:
    """
    Рассчитывает среднюю дневную волатильность каждой монеты
    по скользящим окнам из window наблюдений.
    """
    if window < 2:
        raise ValueError("Размер окна должен быть не меньше 2")

    # Сортируем данные по монетам и датам
    data = df.sort_values(["Coin_Name", "Date"]).copy()

    # Рассчитываем дневную доходность
    data["Daily_Return"] = data.groupby("Coin_Name")["Close"].pct_change()

    # Вычисляем стандартное отклонение доходности
    # в каждом скользящем окне
    data["Rolling_Volatility"] = data.groupby("Coin_Name")["Daily_Return"].transform(
        lambda s: s.rolling(window=window, min_periods=window).std()
    )

    # Находим среднее значение волатильности для каждой монеты
    return (
        data.groupby("Coin_Name")["Rolling_Volatility"]
        .mean()
        .sort_values(ascending=False)
    )


def calculate_max_drawdown(df: pd.DataFrame) -> pd.Series:
    """
    Рассчитывает максимальную просадку каждой монеты
    за весь доступный период наблюдения.
    """
    data = df.sort_values(["Coin_Name", "Date"]).copy()

    # Находим максимальную цену закрытия,
    # достигнутую к каждой дате
    data["Running_Max"] = data.groupby("Coin_Name")["Close"].cummax()

    # Рассчитываем падение от предыдущего максимума
    data["Drawdown"] = 1 - data["Close"] / data["Running_Max"]

    # Находим самую большую просадку для каждой монеты
    return data.groupby("Coin_Name")["Drawdown"].max().sort_values(ascending=False)
