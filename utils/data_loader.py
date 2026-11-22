import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_data(path: str) -> pd.DataFrame:
    """
    Загружает и очищает данные о криптовалютах.
    Выполняет очистку согласно плану проекта:
    - Преобразует дату в формат datetime.
    - Удаляет строки с нулевыми или пустыми ценами.
    - Переименовывает 'UNI7083' в 'UNI'.
    """

    # Логируем начало работы
    logger.info(f"Начало загрузки данных из файла: {path}")

    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        logger.error(f"Ошибка: Файл не найден по пути {path}")
        raise  # Пробрасываем ошибку дальше, чтобы Streamlit её показал
    except Exception as e:
        logger.error(f"Ошибка при чтении CSV файла: {e}")
        raise

    # Запоминаем исходное количество строк
    initial_rows = len(df)
    logger.info(f"Данные успешно загружены. Исходное количество строк: {initial_rows}")

    # 1. Преобразование даты
    df["Date"] = pd.to_datetime(df["Date"])
    logger.debug("Столбец 'Date' преобразован в формат datetime.")

    # 2. Очистка от нулевых и пустых цен (включая проблему SHIB)
    price_columns = ["Open", "High", "Low", "Close"]
    for col in price_columns:
        rows_before_drop = len(df)

        df = df[df[col] > 0]  # Удаляет нули и NaN
        df = df.dropna(subset=[col])

        rows_dropped = rows_before_drop - len(df)
        if rows_dropped > 0:
            logger.info(
                f"Очистка: удалено {rows_dropped} строк с некорректным значением в '{col}'."
            )

    # 3. Переименование монеты
    df["Coin_Name"] = df["Coin_Name"].replace("UNI7083", "UNI")
    logger.debug("Переименование монеты UNI7083 -> UNI выполнено.")

    # Сброс индекса
    df = df.reset_index(drop=True)

    # Логируем итог
    final_rows = len(df)
    total_dropped = initial_rows - final_rows
    logger.info(
        f"Загрузка и очистка завершены. Итоговое количество строк: {final_rows}. Всего удалено: {total_dropped}."
    )

    return df
