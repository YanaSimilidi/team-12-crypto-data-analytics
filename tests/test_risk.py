import pandas as pd
import pytest

from utils.risk import calculate_average_volatility, calculate_max_drawdown


def sample_prices():
    """Создает тестовые данные для двух криптовалют."""
    data = {
        "Date": pd.to_datetime(
            ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"] * 2
        ),
        "Coin_Name": ["A"] * 4 + ["B"] * 4,
        "Close": [100, 120, 90, 110, 50, 50, 50, 50],
    }
    return pd.DataFrame(data)


def test_max_drawdown():
    """Проверяет расчет максимальной просадки на известных значениях."""
    df = sample_prices()

    result = calculate_max_drawdown(df)

    # Монета A: максимальная цена 120, минимальная после нее 90
    # Максимальная просадка: (120 - 90) / 120 = 0.25 (25%)
    assert result["A"] == pytest.approx(0.25)

    # Монета B: цена не изменялась, просадка равна нулю
    assert result["B"] == pytest.approx(0.0)


def test_average_volatility():
    """Проверяет расчет средней волатильности по скользящим окнам."""
    df = sample_prices()

    result = calculate_average_volatility(df, window=2)

    # Дневные доходности монеты A: +20%, -25%, +22.22%
    returns = pd.Series([0.20, -0.25, 110 / 90 - 1])

    # Рассчитываем стандартное отклонение для двух окон
    # и находим их среднее значение
    expected = (returns.iloc[:2].std() + returns.iloc[1:].std()) / 2

    assert result["A"] == pytest.approx(expected)

    # У монеты B цена постоянная, поэтому волатильность равна нулю
    assert result["B"] == pytest.approx(0.0)


def test_unsorted_rows_produce_same_results():
    """Проверяет, что порядок строк не влияет на результат."""
    df = sample_prices()

    # Перемешиваем строки
    shuffled_df = df.sample(frac=1, random_state=42)

    # Результаты должны совпадать независимо от порядка строк
    pd.testing.assert_series_equal(
        calculate_average_volatility(df, window=2),
        calculate_average_volatility(shuffled_df, window=2),
    )

    pd.testing.assert_series_equal(
        calculate_max_drawdown(df),
        calculate_max_drawdown(shuffled_df),
    )


def test_invalid_window():
    """Проверяет обработку некорректного размера окна волатильности."""
    df = sample_prices()

    # При размере окна меньше 2 должна возникать ошибка ValueError
    with pytest.raises(ValueError):
        calculate_average_volatility(df, window=1)
