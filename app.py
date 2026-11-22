# Импорт необходимых библиотек
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import logging

# Импорт функций
from utils.data_loader import load_data
from utils.returns import calculate_average_daily_returns
from utils.risk import calculate_average_volatility, calculate_max_drawdown
from utils.compare import compare_coins

# Настройка логирования, чтобы записывать действия программы в файл и выводить в консоль
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

# Отображение бокового меню
st.sidebar.title("Навигация по проекту")
st.sidebar.markdown("Выберите интересующий раздел анализа:")

menu_options = [
    "Сравнение доходности",
    "Сравнение двух монет",
    "Оценка рискованности",
    "«Что если бы я вложил…»"
]

choice = st.sidebar.radio("Разделы", menu_options)

# Загрузка данных
# Использование кэширования, чтобы данные не загружались заново при каждом клике в меню
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

# Отображение выбранного пункта
if choice == "Сравнение доходности":
    st.title("Сравнение доходности криптовалют")
    st.markdown("""
    На этом графике показана **средняя дневная доходность** каждой монеты за весь период наблюдений. 
    Доходность рассчитывается как процентное изменение цены закрытия по сравнению с предыдущим днем.
    """)

    st.markdown("###  Настройки анализа")
    col_date, col_slider = st.columns([2, 1]) 
    
    with col_date:
        min_date = df['Date'].min().to_pydatetime()
        max_date = df['Date'].max().to_pydatetime()
        date_range = st.date_input(
            "Выберите период:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            st.warning("Пожалуйста, выберите конечную дату периода.")
            st.stop()

    with col_slider:
        top_n = st.slider("Сколько монет показать?", min_value=5, max_value=24, value=10)
    
    st.markdown("---")
    
    # Фильтруем данные
    df_filtered = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    
    if df_filtered.empty:
        st.warning("За выбранный период данные отсутствуют. Попробуйте изменить даты.")
    else:
        avg_returns = calculate_average_daily_returns(df_filtered)
        
        if avg_returns.empty:
             st.warning("Недостаточно данных для расчета доходности за этот период.")
        else:
            avg_returns_pct = avg_returns * 100
            sorted_returns = avg_returns_pct.sort_values(ascending=False).reset_index()
            sorted_returns.columns = ['Монета', 'Средняя доходность (%)']

            # Метрики (Карточки)
            best_coin = sorted_returns.iloc[0]
            worst_coin = sorted_returns.iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                # Карточка для лидера
                st.metric(
                    label=" Лидер по доходности", 
                    value=best_coin['Монета'], 
                    delta=f"{best_coin['Средняя доходность (%)']:.3f}% в день",
                    delta_color="normal" # Зеленый цвет для роста
                )
            with col2:
                # Карточка для аутсайдера
                st.metric(
                    label=" Аутсайдер", 
                    value=worst_coin['Монета'], 
                    delta=f"{worst_coin['Средняя доходность (%)']:.3f}% в день",
                    delta_color="inverse"
                )
            with col3:
                # Общая информация
                st.metric(
                    label=" Дней в анализе",
                    value=f"{len(df_filtered['Date'].unique())} дн.",
                    delta="Выбранный период"
                )

            st.markdown("---")

            df_to_plot = sorted_returns.head(top_n)

            # Два графика в ряд (Столбчатый и Boxplot)
            tab1, tab2 = st.tabs([" Средняя доходность", " Разброс доходности (волатильность)"])
            
            with tab1:
                fig_bar = px.bar(
                    df_to_plot,
                    x='Монета',
                    y='Средняя доходность (%)',
                    color='Средняя доходность (%)',
                    color_continuous_scale='RdYlGn', 
                    title=f"Топ-{top_n} монет по средней доходности"
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, width='stretch')
                
            with tab2:
                st.info("Этот график показывает, насколько сильно цена монеты отклонялась от среднего значения. Широкий «ящик» означает высокий риск (волатильность).")
                
                # Расчет дневной доходности для боксплота
                df_filtered_returns = df_filtered.copy()
                df_filtered_returns['Daily_Return'] = df_filtered_returns.sort_values('Date').groupby('Coin_Name')['Close'].pct_change() * 100
                
                # Вывод только топ-N монет
                top_coins = df_to_plot['Монета'].tolist()
                df_filtered_returns = df_filtered_returns[df_filtered_returns['Coin_Name'].isin(top_coins)]
                
                fig_box = px.box(
                    df_filtered_returns,
                    x='Coin_Name',
                    y='Daily_Return',
                    color='Coin_Name',
                    title="Распределение дневной доходности",
                    labels={'Coin_Name': 'Монета', 'Daily_Return': 'Дневная доходность (%)'}
                )
                fig_box.update_layout(xaxis_tickangle=-45, showlegend=False)
                st.plotly_chart(fig_box, width='stretch')

            st.markdown("---")

            # Кнопка скачивания и таблица
            col_table, col_download = st.columns([3, 1])
            
            with col_table:
                st.subheader("Таблица показателей")
            with col_download:
                # Кнопка для скачивания
                csv = sorted_returns.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=" Скачать в CSV",
                    data=csv,
                    file_name='crypto_returns.csv',
                    mime='text/csv',
                )

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