import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Импортируем наши функции
from utils.data_loader import load_data
from utils.returns import calculate_average_daily_returns
from utils.risk import calculate_average_volatility, calculate_max_drawdown

# Настройка страницы
st.set_page_config(
    page_title="Анализ криптовалют",
    layout="wide"
)

# --- Боковое меню ---
st.sidebar.title("Навигация по проекту")
st.sidebar.markdown("Выберите интересующий раздел анализа:")

menu_options = [
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
if choice == "Сравнение доходности":
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
    st.info("Этот раздел находится в разработке. Здесь будет график сравнения двух выбранных монет (Яна).")


elif choice == "Оценка рискованности":
    st.title("Оценка рискованности криптовалют")

    st.markdown("""
    **Средняя волатильность** показывает, насколько сильно
    колеблется дневная доходность криптовалюты.

    **Максимальная просадка** показывает наибольшее падение
    цены от предыдущего максимума за период наблюдения.
    """)

    # Выбор периода расчёта волатильности
    window = st.selectbox(
        "Окно волатильности (наблюдений)",
        [7, 30, 90],
        index=1
    )

    # Расчёт показателей
    volatility = calculate_average_volatility(df, window) * 100
    drawdown = calculate_max_drawdown(df) * 100

    # Объединяем результаты в одну таблицу
    risk_table = (
        pd.DataFrame({
            "Средняя волатильность (%)": volatility,
            "Максимальная просадка (%)": drawdown,
        })
        .rename_axis("Монета")
        .reset_index()
        .sort_values(
            "Средняя волатильность (%)",
            ascending=False
        )
    )

    # График волатильности
    st.subheader("Средняя дневная волатильность")

    fig_volatility = px.bar(
        risk_table,
        x="Монета",
        y="Средняя волатильность (%)",
        color="Средняя волатильность (%)",
        color_continuous_scale="OrRd",
        title=f"Средняя волатильность (окно {window} дней)"
    )

    fig_volatility.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_volatility, width="stretch")

    # График максимальных просадок
    st.subheader("Максимальная просадка")

    fig_drawdown = px.bar(
        risk_table.sort_values(
            "Максимальная просадка (%)",
            ascending=False
        ),
        x="Монета",
        y="Максимальная просадка (%)",
        color="Максимальная просадка (%)",
        color_continuous_scale="Reds",
        title="Максимальная просадка по монетам"
    )

    fig_drawdown.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_drawdown, width="stretch")

    # Таблица с результатами
    st.subheader("Таблица показателей рискованности")

    st.dataframe(
        risk_table.style.format({
            "Средняя волатильность (%)": "{:.2f}%",
            "Максимальная просадка (%)": "{:.2f}%"
        }),
        width="stretch",
        hide_index=True
    )


elif choice == "«Что если бы я вложил…»":
    st.title("Что если бы я вложил…")
    st.info("Этот раздел находится в разработке. Здесь будет калькулятор инвестиций (Асмик).")

# Добавим красивый футер в самом низу страницы
st.sidebar.markdown("---")
st.sidebar.caption("Команда 12: Настя, Яна, Ксюша, Асмик")