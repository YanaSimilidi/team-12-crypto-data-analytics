import pandas as pd
import plotly.express as px
import streamlit as st

from utils.overview import (
    aggregate_price_volume,
    build_price_volume_figure,
    filter_dates,
    monthly_returns,
)


MONTH_NAMES = {
    1: "Янв", 2: "Фев", 3: "Мар", 4: "Апр", 5: "Май", 6: "Июн",
    7: "Июл", 8: "Авг", 9: "Сен", 10: "Окт", 11: "Ноя", 12: "Дек",
}


def show_overview(df: pd.DataFrame) -> None:
    """Отображает страницу с фильтрами, графиками и сводками по CSV"""
    st.title("Обзор данных о криптовалютах")

    first = df["Date"].min()
    last = df["Date"].max()
    m1, m2, m3 = st.columns(3)
    m1.metric("Криптовалют в датасете", f"{df['Coin_Name'].nunique()}")
    m2.metric("Первая дата", first.strftime("%d.%m.%Y"))
    m3.metric("Последняя дата", last.strftime("%d.%m.%Y"))

    st.subheader("Период анализа")
    left, right = st.columns(2)
    with left:
        selected_start = st.date_input(
            "Начало периода", value=first.date(),
            min_value=first.date(), max_value=last.date(),
            key="overview_start",
        )
    with right:
        selected_end = st.date_input(
            "Конец периода", value=last.date(),
            min_value=first.date(), max_value=last.date(),
            key="overview_end",
        )

    start_date = pd.Timestamp(selected_start)
    end_date = pd.Timestamp(selected_end)
    if start_date > end_date:
        st.warning("Дата начала периода должна быть не позже даты окончания")
        return

    period_df = filter_dates(df, start_date, end_date)
    if period_df.empty:
        st.warning("За выбранный период нет наблюдений")
        return

    available_coins = sorted(period_df["Coin_Name"].unique().tolist())

    tab_price, tab_monthly = st.tabs([
        "Цены и объёмы", "Помесячная доходность",
    ])

    with tab_price:
        coin = st.selectbox(
            "Криптовалюта", available_coins,
            index=available_coins.index("BTC") if "BTC" in available_coins else 0,
            key="overview_detail_coin",
        )
        coin_df = period_df.loc[
            period_df["Coin_Name"] == coin
        ].sort_values("Date")
        if len(coin_df) < 2:
            st.info("Для построения динамики нужны минимум две даты")
        else:
            scale = st.selectbox(
                "Группировка цен и объёма", ["День", "Неделя", "Месяц"],
                index=2 if (end_date - start_date).days > 120 else 0,
                key="overview_volume_scale",
            )
            # Сохраняем график цены закрытия и объёма на общей оси дат
            grouped = aggregate_price_volume(coin_df, scale)
            fig = build_price_volume_figure(grouped, coin)
            st.plotly_chart(fig, width="stretch")

            start_price = coin_df["Close"].iloc[0]
            end_price = coin_df["Close"].iloc[-1]
            change = (end_price / start_price - 1) * 100
            p1, p2, p3 = st.columns(3)
            p1.metric("Цена в начале выборки, $", f"{start_price:,.6g}")
            p2.metric("Цена в конце выборки, $", f"{end_price:,.6g}")
            p3.metric("Изменение цены", f"{change:+.2f}%")

    with tab_monthly:
        coin = st.selectbox(
            "Криптовалюта для помесячного анализа", available_coins,
            index=available_coins.index("BTC") if "BTC" in available_coins else 0,
            key="overview_monthly_coin",
        )
        monthly_df = monthly_returns(
            period_df.loc[period_df["Coin_Name"] == coin]
        )
        if monthly_df.empty:
            st.info("Нужно минимум два месяца данных для помесячной доходности")
        else:
            heat = monthly_df.pivot(
                index="Year", columns="Month", values="Return_Pct"
            )
            heat = heat.reindex(columns=list(range(1, 13)))
            fig_heat = px.imshow(
                heat,
                x=[MONTH_NAMES[m] for m in heat.columns],
                y=[str(y) for y in heat.index],
                color_continuous_scale="RdYlGn",
                color_continuous_midpoint=0,
                labels={"x": "Месяц", "y": "Год", "color": "Доходность (%)"},
                title=f"Помесячное изменение цены закрытия {coin} (%)",
                aspect="auto",
            )
            fig_heat.update_traces(
                hovertemplate="Год: %{y}<br>Месяц: %{x}<br>Доходность: %{z:.2f}%<extra></extra>"
            )
            st.plotly_chart(fig_heat, width="stretch")
