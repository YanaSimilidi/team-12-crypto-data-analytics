import pandas as pd
import logging

logger = logging.getLogger(__name__)


def calculate_average_daily_returns(df: pd.DataFrame) -> pd.Series:
    """
    Рассчитывает среднюю дневную доходность для каждой монеты.

    Доходность за день = (Цена закрытия сегодня - Цена закрытия вчера) / Цена закрытия вчера
    """

    # Логируем начало работы и размер входных данных
    logger.info(f"Начало расчёта доходности. Строк на входе: {len(df)}")

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

    # Логируем результат: сколько монет получилось и какая оказалась лучшей
    if not average_returns.empty:
        best_coin = average_returns.index[0]
        best_return = average_returns.iloc[0]
        logger.info(
            f"Расчёт доходности завершён. Обработано монет: {len(average_returns)}. "
            f"Лидер: {best_coin} ({best_return:.4%})"
        )
    else:
        logger.warning("Расчёт доходности не дал результатов (пустой DataFrame).")

    return average_returns
