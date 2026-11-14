import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Импортируем наши функции
from utils.data_loader import load_data
from utils.returns import calculate_average_daily_returns

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
    st.title("Оценка рискованности")
    st.info("Этот раздел находится в разработке. Здесь будут рассчитаны волатильность и просадки (Ксюша).")

elif choice == "«Что если бы я вложил…»":
    st.title("Что если бы я вложил…")
    st.info("Этот раздел находится в разработке. Здесь будет калькулятор инвестиций (Асмик).")

# Добавим красивый футер в самом низу страницы
st.sidebar.markdown("---")
st.sidebar.caption("Команда 12: Настя, Яна, Ксюша, Асмик")