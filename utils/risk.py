import pandas as pd


def calculate_daily_volatility(df: pd.DataFrame) -> pd.Series:
    """Дневная волатильность каждой монеты за переданный период.
    Стандартное отклонение изменений цены закрытия между соседними
    календарными днями (доли единицы: 0.05 = 5%). Если между датами
    пропущен день, многодневное изменение не считается дневным.
    """
    data = df.sort_values(["Coin_Name", "Date"]).copy()
    data["Date"] = pd.to_datetime(data["Date"])
    by_coin = data.groupby("Coin_Name")
    previous_date = by_coin["Date"].shift(1)
    data["Daily_Return"] = by_coin["Close"].pct_change()
    consecutive_days = (data["Date"] - previous_date).dt.days == 1
    data.loc[~consecutive_days, "Daily_Return"] = float("nan")
    return (
        data.groupby("Coin_Name")["Daily_Return"]
        .std()
        .sort_values(ascending=False)
    )


def select_custom_period(df: pd.DataFrame, start_date, end_date):
    """Отбор по заданным датам с одинаковыми датами для всех монет.
    Использует первую и последнюю *доступные* даты внутри выбранного
    интервала. В сравнение попадают монеты, имеющие цену на обеих
    границах. Даты остальных наблюдений пересекаются между монетами.
    Возвращает (данные, фактическое начало, фактический конец, исключенные).
    """
    start = pd.Timestamp(start_date).normalize()
    end = pd.Timestamp(end_date).normalize()
    if start >= end:
        raise ValueError("Начало периода должно быть раньше окончания")
    if df.empty:
        return df.copy(), start, end, []

    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"]).dt.normalize()
    period_data = data.loc[data["Date"].between(start, end)].copy()
    if period_data.empty:
        return period_data, start, end, sorted(data["Coin_Name"].unique())

    actual_start = period_data["Date"].min()
    actual_end = period_data["Date"].max()
    coverage = period_data.groupby("Coin_Name")["Date"].agg(["min", "max"])
    eligible = coverage.index[
        (coverage["min"] == actual_start) &
        (coverage["max"] == actual_end)
    ]
    excluded = sorted(set(data["Coin_Name"]) - set(eligible))
    period_data = period_data.loc[period_data["Coin_Name"].isin(eligible)].copy()

    if not period_data.empty:
        counts = period_data.groupby("Date")["Coin_Name"].nunique()
        common_dates = counts.loc[counts == len(eligible)].index
        period_data = period_data.loc[period_data["Date"].isin(common_dates)].copy()

    return period_data, actual_start, actual_end, excluded


def calculate_max_drawdown(df: pd.DataFrame) -> pd.Series:
    """
    Максимальная просадка по цене закрытия за переданный период.
    Возвращаем наибольшее падение для каждой монеты в долях.
    """
    data = df.sort_values(["Coin_Name", "Date"]).copy()
    data["Running_Max"] = data.groupby("Coin_Name")["Close"].cummax()
    data["Drawdown"] = 1 - data["Close"] / data["Running_Max"]
    return data.groupby("Coin_Name")["Drawdown"].max().sort_values(ascending=False)


def get_risk_top5(risk_table: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Формирует четыре рейтинга монет по показателям рискованности.
    """
    volatility_col = "Дневная волатильность (%)"
    drawdown_col = "Максимальная просадка (%)"
    required = ["Монета", volatility_col, drawdown_col]

    missing = [column for column in required if column not in risk_table.columns]
    if missing:
        raise ValueError("В таблице отсутствуют столбцы: " + ", ".join(missing))

    valid_volatility = risk_table.dropna(subset=[volatility_col])
    valid_drawdown = risk_table.dropna(subset=[drawdown_col])

    return {
        "Топ-5 монет с наименьшей волатильностью": (
            valid_volatility.nsmallest(5, volatility_col)[["Монета", volatility_col]].copy()
        ),
        "Топ-5 монет с наименьшей просадкой": (
            valid_drawdown.nsmallest(5, drawdown_col)[["Монета", drawdown_col]].copy()
        ),
        "Топ-5 монет с наибольшей волатильностью": (
            valid_volatility.nlargest(5, volatility_col)[["Монета", volatility_col]].copy()
        ),
        "Топ-5 монет с наибольшей просадкой": (
            valid_drawdown.nlargest(5, drawdown_col)[["Монета", drawdown_col]].copy()
        ),
    }
