import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    """
    Загружает и очищает данные о криптовалютах.
    Выполняет очистку согласно плану проекта:
    - Преобразует дату в формат datetime.
    - Удаляет строки с нулевыми или пустыми ценами.
    - Переименовывает 'UNI7083' в 'UNI'.
    """
    df = pd.read_csv(path)

    # 1. Преобразование даты
    df["Date"] = pd.to_datetime(df["Date"])

    # 2. Очистка от нулевых и пустых цен (включая проблему SHIB)
    # Оставляем только строки, где все ключевые цены > 0 и не пустые
    price_columns = ["Open", "High", "Low", "Close"]
    for col in price_columns:
        df = df[df[col] > 0]  # Это также удалит NaN, так как NaN > 0 -> False
        df = df.dropna(subset=[col])

    # 3. Переименование монеты
    df["Coin_Name"] = df["Coin_Name"].replace("UNI7083", "UNI")

    # Опционально: можно сбросить индекс после удаления строк
    df = df.reset_index(drop=True)

    return df
