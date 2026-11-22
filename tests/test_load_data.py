# tests/test_load_data.py
import pandas as pd
import pytest
from utils.data_loader import load_data
import os


# Создадим временный CSV для теста, чтобы не зависеть от основного файла
@pytest.fixture
def sample_csv(tmp_path):
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "Symbol": ["BTC", "BTC", "SHIB", "UNI"],
        "Coin_Name": ["Bitcoin", "Bitcoin", "Shiba Inu", "UNI7083"],
        "Open": [100, 105, 0, 10],
        "High": [110, 110, 0, 12],
        "Low": [90, 95, 0, 9],
        "Close": [105, 108, 0, 11],  # Нулевая цена
        "Volume": [1000, 1200, 0, 500],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_data.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)


def test_load_data_removes_zero_and_na_prices(sample_csv):
    """Проверяет, что после очистки нет цен <= 0."""
    df = load_data(sample_csv)

    # Убедимся, что строки с SHIB (цена 0) удалены
    assert len(df) == 3
    assert (df["Close"] > 0).all()
    assert (df["Open"] > 0).all()
    assert (df["Low"] > 0).all()


def test_load_data_converts_date_to_datetime(sample_csv):
    """Проверяет, что столбец Date имеет тип datetime."""
    df = load_data(sample_csv)
    assert pd.api.types.is_datetime64_any_dtype(df["Date"])


def test_load_data_renames_uni7083(sample_csv):
    """Проверяет переименование UNI7083 в UNI."""
    df = load_data(sample_csv)
    assert "UNI" in df["Coin_Name"].values
    assert "UNI7083" not in df["Coin_Name"].values
