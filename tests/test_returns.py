# tests/test_returns.py
import pandas as pd
import pytest
from utils.returns import calculate_average_daily_returns


def test_calculate_returns_on_simple_data():
    """Проверяет расчет доходности на простом примере с известным ответом."""
    data = {
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"] * 2),
        "Coin_Name": ["A", "A", "A", "B", "B", "B"],
        "Close": [100, 110, 121, 200, 180, 198],  # A: +10%, +10%; B: -10%, +10%
    }
    df = pd.DataFrame(data)

    result = calculate_average_daily_returns(df)

    # Ожидаемая средняя доходность для A: (0.1 + 0.1) / 2 = 0.1
    # Ожидаемая средняя доходность для B: (-0.1 + 0.1) / 2 = 0.0
    assert result["A"] == pytest.approx(0.1)
    assert result["B"] == pytest.approx(0.0)
