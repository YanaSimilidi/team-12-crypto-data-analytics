import pandas as pd
import logging

# Создаем логгер
logger = logging.getLogger(__name__)

#Пишем функцию для сравнения двух монет
def compare_coins(
    df: pd.DataFrame, 
    coin1: str, 
    coin2: str, 
    start_date: str, 
    end_date: str
) -> tuple[pd.DataFrame, float]:
    """Сравнивает две монеты, приводя их цены к 100
    на первый день"""

    logger.info(f"Запущено сравнение {coin1} и {coin2} с {start_date} по {end_date}")
    
    # Фильтруем данные по датам и выбранным монетам
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    df_filtered = df[
        mask & (df['Coin_Name'].isin([coin1, coin2]))
    ]
    
    # Делаем сводную таблицу, где колонки - это монеты, а строки - даты
    pivot = df_filtered.pivot(
        index='Date', 
        columns='Coin_Name', 
        values='Close'
    )
    
    # Проверяем, что обе монеты есть в данных за этот период
    if coin1 not in pivot.columns or coin2 not in pivot.columns:
        # Логируем ошибку
        logger.error(f"Не найдены данные для {coin1} или {coin2} в выбранном периоде")
        raise ValueError(
            "Одна из монет не найдена в выбранном периоде"
        )
        
    # Нормируем (делим на первую цену и умножаем на 100)
    normalized = (pivot / pivot.iloc[0]) * 100

    # Считаем корреляцию дневных изменений
    # .pct_change() считает процент изменения от дня к дню
    daily_changes = normalized.pct_change().dropna()
    correlation = daily_changes[coin1].corr(daily_changes[coin2])
    
    logger.info(f"Сравнение {coin1} и {coin2} успешно завершено. Корреляция: {correlation:.2f}")
    
    return normalized, correlation