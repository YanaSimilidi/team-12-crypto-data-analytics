import streamlit as st
import pandas as pd
import plotly.express as px
import os
import logging

# Импортируем наши функции
from utils.data_loader import load_data
from utils.returns import calculate_average_daily_returns
from utils.compare import compare_coins
from views.overview import show_overview
from utils.risk import (
    calculate_daily_volatility,
    calculate_max_drawdown,
    select_custom_period,
    get_risk_top5,
)

# Настраиваем логи чтобы записывать действия программы в файл и выводить в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Настройка страницы
st.set_page_config(
    page_title="Анализ криптовалют",
    layout="wide"
)

# --- Боковое меню ---
st.sidebar.title("Навигация по проекту")
st.sidebar.markdown("Выберите интересующий раздел анализа:")

menu_options = [
    "Обзор данных",
    "Сравнение доходности",
    "Сравнение двух монет",
    "Оценка рискованности",
    "«Что если бы я вложил…»"
]

choice = st.sidebar.radio("Разделы", menu_options)

# --- Загрузка данных ---
# Используем кэширование, чтобы данные не загружались заново при каждом клике в меню
@st.cache_data
def get_cached_data(file_path):
    if not os.path.exists(file_path):
        return None
    return load_data(file_path)

DATA_PATH = "data/historical_crypto_data.csv"
df = get_cached_data(DATA_PATH)

if df is None:
    st.error(f"Файл с данными не найден по пути: `{DATA_PATH}`. Пожалуйста, убедитесь, что он лежит в папке data.")
    st.stop() # Останавливаем выполнение, если нет данных

# --- Отображение выбранного пункта ---
if choice == "Обзор данных":
    show_overview(df)

elif choice == "Сравнение доходности":
    st.title("Сравнение доходности криптовалют")
    st.markdown("""
    На этом графике показана **средняя дневная доходность** каждой монеты за весь период наблюдений. 
    Доходность рассчитывается как процентное изменение цены закрытия по сравнению с предыдущим днем.
    """)
    
    # Считаем доходность
    avg_returns = calculate_average_daily_returns(df)
    
    # Переводим в проценты для удобства отображения
    avg_returns_pct = avg_returns * 100
    
    # Сортируем по убыванию
    sorted_returns = avg_returns_pct.sort_values(ascending=False).reset_index()
    sorted_returns.columns = ['Монета', 'Средняя доходность (%)']

    # Строим интерактивный график
    fig = px.bar(
        sorted_returns,
        x='Монета',
        y='Средняя доходность (%)',
        color='Средняя доходность (%)',
        color_continuous_scale='RdYlGn', # Красный для убытков, зеленый для прибыли
        title="Средняя дневная доходность по монетам"
    )
    fig.update_layout(xaxis_tickangle=-45)
    
    st.plotly_chart(fig, width='stretch')
    st.dataframe(
        sorted_returns.style.format({'Средняя доходность (%)': '{:.4f}%'}),
        width='stretch'
    )   

elif choice == "Сравнение двух монет":
    st.title("Сравнение двух монет")
    st.markdown("""
    Выберите две монеты и период. График покажет, как изменилась бы стоимость 
    **100$**, вложенных в каждую из них в первый день выбранного периода.
    """)
    
    # Выбор монет
    coins = sorted(df['Coin_Name'].unique())
    col1, col2 = st.columns(2)
    coin1 = col1.selectbox("Первая монета", coins, index=0)
    # По умолчанию выбираем вторую монету, чтобы они не совпадали
    default_idx = 1 if len(coins) > 1 else 0
    coin2 = col2.selectbox("Вторая монета", coins, index=default_idx) 
    
    # Выбор дат
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input("Начало периода", min_date)
    end_date = col_d2.date_input("Конец периода", max_date)
    
    if st.button("Построить график"):
        try:
            # Вызываем функцию сравнения
            result, corr = compare_coins(
                df, coin1, coin2, 
                pd.to_datetime(start_date), 
                pd.to_datetime(end_date)
            )
            
            # Считаем рост за период
            growth1 = result[coin1].iloc[-1] - 100
            growth2 = result[coin2].iloc[-1] - 100
            
            # Подготавливаем данные для Plotly (нужно перевести в "длинный" формат)
            # Сейчас result имеет колонки [coin1, coin2] и индекс Date
            plot_df = result.reset_index().melt(
                id_vars='Date', 
                var_name='Монета', 
                value_name='Стоимость 100$'
            )
            
            # Строим интерактивный график
            fig = px.line(
                plot_df, 
                x='Date', 
                y='Стоимость 100$', 
                color='Монета',
                title=f'Сравнение {coin1} и {coin2} (база 100)',
                markers=True # Добавляем точки на линиях
            )
            fig.update_layout(hovermode="x unified")
            
            st.plotly_chart(fig, width='stretch')
            
            # Выводим результаты
            st.markdown("### Результат анализа")
            
            # Подписи с процентами
            m1, m2 = st.columns(2)
            m1.metric(
                label=f"Изменение {coin1} за период", 
                value=f"{growth1:.1f}%"
            )
            m2.metric(
                label=f"Изменение {coin2} за период", 
                value=f"{growth2:.1f}%"
            )
            
            # Вывод корреляции
            st.write(f"**Коэффициент корреляции:** {corr:.2f}")
            
            if corr >= 0.7:
                st.success("Монеты движутся почти синхронно.")
            elif corr >= 0.3:
                st.info("У монет есть умеренная связь.")
            elif corr >= -0.3:
                st.warning("Монеты движутся независимо друг от друга.")
            else:
                st.error("Монеты движутся в противоположных направлениях.")
                
        except Exception as e:
            st.error(f"Ошибка: {e}")


elif choice == "Оценка рискованности":
    st.title("Оценка рискованности криптовалют")

    min_date = pd.Timestamp(df["Date"].min()).date()
    max_date = pd.Timestamp(df["Date"].max()).date()

    last_common_date = pd.Timestamp(
        df.groupby("Coin_Name")["Date"].max().min()
    )
    default_year = last_common_date.year - 1
    default_start = pd.Timestamp(default_year, 1, 1).date()
    default_end = pd.Timestamp(default_year, 12, 31).date()
    if not (min_date <= default_start < default_end <= max_date):
        default_start, default_end = min_date, max_date

    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input(
            "Начало периода",
            value=default_start,
            min_value=min_date,
            max_value=max_date,
            key="risk_start_date",
        )
    with col_end:
        end_date = st.date_input(
            "Конец периода",
            value=default_end,
            min_value=min_date,
            max_value=max_date,
            key="risk_end_date",
        )

    if start_date >= end_date:
        st.warning("Дата начала должна быть раньше даты окончания периода")
        st.stop()

    risk_df, actual_start, actual_end, excluded = select_custom_period(
        df, start_date, end_date
    )
    if risk_df.empty or risk_df["Date"].nunique() < 3:
        st.warning(
            "Недостаточно общих дат для расчёта показателей. "
            "Выберите более длинный период."
        )
        st.stop()

    if excluded:
        with st.expander(
            f"Почему не включены некоторые монеты ({len(excluded)})?"
        ):
            st.write(
                "Для сопоставимого расчёта оставлены монеты, у которых "
                "имеются цены на обеих фактических границах выбранного периода. "
                "Не включены: " + ", ".join(excluded) + "."
            )

    volatility = calculate_daily_volatility(risk_df) * 100
    drawdown = calculate_max_drawdown(risk_df) * 100
    risk_table = (
        pd.DataFrame({
            "Дневная волатильность (%)": volatility,
            "Максимальная просадка (%)": drawdown,
        })
        .rename_axis("Монета")
        .reset_index()
        .dropna(subset=["Дневная волатильность (%)", "Максимальная просадка (%)"])
        .sort_values("Дневная волатильность (%)", ascending=False)
    )
    if risk_table.empty:
        st.warning("Недостаточно последовательных дневных данных для расчёта волатильности")
        st.stop()

    fig_volatility = px.bar(
        risk_table,
        x="Монета",
        y="Дневная волатильность (%)",
        color="Дневная волатильность (%)",
        color_continuous_scale="OrRd",
        title="Дневная волатильность за выбранный период",
    )
    fig_volatility.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_volatility, width="stretch")

    fig_drawdown = px.bar(
        risk_table.sort_values("Максимальная просадка (%)", ascending=False),
        x="Монета",
        y="Максимальная просадка (%)",
        color="Максимальная просадка (%)",
        color_continuous_scale="Reds",
        title="Максимальная просадка за выбранный период",
    )
    fig_drawdown.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_drawdown, width="stretch")

    st.subheader("Таблица показателей рискованности")
    st.dataframe(
        risk_table.style.format({
            "Дневная волатильность (%)": "{:.2f}%",
            "Максимальная просадка (%)": "{:.2f}%",
        }),
        width="stretch",
        hide_index=True,
    )

    top5 = get_risk_top5(risk_table)
    st.subheader("Топ-5 криптовалют по показателям рискованности")

    left, right = st.columns(2)
    with left:
        st.markdown("**Наименьшая волатильность**")
        st.dataframe(
            top5["Топ-5 монет с наименьшей волатильностью"].style.format({
                "Дневная волатильность (%)": "{:.2f}%"
            }),
            hide_index=True, width="stretch",
        )
    with right:
        st.markdown("**Наибольшая волатильность**")
        st.dataframe(
            top5["Топ-5 монет с наибольшей волатильностью"].style.format({
                "Дневная волатильность (%)": "{:.2f}%"
            }),
            hide_index=True, width="stretch",
        )

    left, right = st.columns(2)
    with left:
        st.markdown("**Наименьшая максимальная просадка**")
        st.dataframe(
            top5["Топ-5 монет с наименьшей просадкой"].style.format({
                "Максимальная просадка (%)": "{:.2f}%"
            }),
            hide_index=True, width="stretch",
        )
    with right:
        st.markdown("**Наибольшая максимальная просадка**")
        st.dataframe(
            top5["Топ-5 монет с наибольшей просадкой"].style.format({
                "Максимальная просадка (%)": "{:.2f}%"
            }),
            hide_index=True, width="stretch",
        )

elif choice == "«Что если бы я вложил…»":
    st.title("Что если бы я вложил…")
    st.info("Этот раздел находится в разработке. Здесь будет калькулятор инвестиций (Асмик).")

# Добавим красивый футер в самом низу страницы
st.sidebar.markdown("---")
st.sidebar.caption("Команда: Настя, Яна, Ксюша, Асмик")