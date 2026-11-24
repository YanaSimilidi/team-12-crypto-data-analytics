import pandas as pd


def filter_dates(df: pd.DataFrame, start, end) -> pd.DataFrame:
    """Отбирает записи за выбранный включительный интервал дат"""
    start_date = pd.Timestamp(start)
    end_date = pd.Timestamp(end)
    if start_date > end_date:
        raise ValueError("Начало периода должно быть не позже конца")

    return df.loc[df["Date"].between(start_date, end_date)].copy()


def aggregate_price_volume(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """Группирует цену закрытия и объём торгов одной монеты.
    Для каждого дня, недели или месяца берёт последнюю цену закрытия
    и суммирует торговый объём за соответствующий интервал """
    frequencies = {"День": "D", "Неделя": "W-SUN", "Месяц": "MS"}
    if frequency not in frequencies:
        raise ValueError("Неизвестный шаг группировки")

    columns = ["Date", "Close", "Volume"]
    if df.empty:
        return pd.DataFrame(columns=columns)
    if df["Coin_Name"].nunique() != 1:
        raise ValueError("Для графика выберите одну монету")

    by_date = df.sort_values("Date").set_index("Date")
    grouped = by_date.resample(frequencies[frequency]).agg(
        Close=("Close", "last"),
        Volume=("Volume", lambda values: values.sum(min_count=1)),
    )
    return grouped.dropna(subset=["Close"]).reset_index()[columns]


def monthly_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Рассчитывает помесячное изменение последней цены закрытия"""
    columns = ["Year", "Month", "Return_Pct"]
    if df.empty:
        return pd.DataFrame(columns=columns)
    if df["Coin_Name"].nunique() != 1:
        raise ValueError("Для помесячного анализа выберите одну монету")

    month_close = (
        df.sort_values("Date")
        .set_index("Date")["Close"]
        .resample("MS")
        .last()
    )
    # Доходность первого месяца не рассчитываем: нет предыдущей цены.
    # Пропуски между месяцами не подменяем нулевым изменением.
    returns = month_close.pct_change(fill_method=None).dropna().mul(100)
    return pd.DataFrame({
        "Year": returns.index.year,
        "Month": returns.index.month,
        "Return_Pct": returns.to_numpy(),
    })[columns]


def build_price_volume_figure(df: pd.DataFrame, coin: str):
    """Строит линию цены закрытия и столбцы объёма с общей осью дат"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    if df.empty:
        raise ValueError("Нет данных для построения графика")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.70, 0.30],
        vertical_spacing=0.07,
        subplot_titles=(f"Цена {coin}", "Объём торгов"),
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="lines",
            name="Цена закрытия",
            line=dict(color="#3B82F6"),
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Volume"],
            name="Volume",
            marker_color="#94A3B8",
        ),
        row=2, col=1,
    )
    fig.update_layout(
        title=f"Цена и торговая активность — {coin}",
        height=670,
        showlegend=False,
        hovermode="x unified",
        margin=dict(l=25, r=20, t=90, b=40),
    )
    fig.update_yaxes(title_text="Цена (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Объем торгов", row=2, col=1)
    fig.update_xaxes(title_text="Дата", row=2, col=1)
    return fig
