import pandas as pd
import pytest

from utils.risk import (
    calculate_daily_volatility,
    calculate_max_drawdown,
    select_custom_period,
    get_risk_top5,
)


def sample_prices():
    # A меняется в цене, B остаётся постоянной
    return pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"] * 2),
        "Coin_Name": ["A"] * 4 + ["B"] * 4,
        "Close": [100, 120, 90, 110, 50, 50, 50, 50],
    })


def test_daily_volatility():
    """Проверяет волатильность на заранее известных изменениях цены"""
    result = calculate_daily_volatility(sample_prices())
    # Доходности A: +20%, -25%, +22.22%; используем std(ddof=1).
    expected = pd.Series([0.20, -0.25, 110 / 90 - 1]).std()
    assert result["A"] == pytest.approx(expected)
    assert result["B"] == pytest.approx(0.0)


def test_volatility_ignores_missing_days():
    """Пропуск календарного дня не должен считаться дневной доходностью"""
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-04", "2024-01-05"]),
        "Coin_Name": ["A"] * 4,
        "Close": [100, 110, 200, 180],
    })
    result = calculate_daily_volatility(df)
    # Учитываются только +10% (01→02) и -10% (04→05)
    assert result["A"] == pytest.approx(pd.Series([0.1, -0.1]).std())


def test_max_drawdown():
    """Проверяет наибольшее падение от предыдущего максимума"""
    result = calculate_max_drawdown(sample_prices())
    assert result["A"] == pytest.approx(0.25)  # 120 → 90
    assert result["B"] == pytest.approx(0.0)


def test_select_custom_period():
    """Проверяет исключение неполных монет и общие даты сравнения"""
    df = pd.DataFrame({
        "Date": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04",  # A
            "2024-01-01", "2024-01-03", "2024-01-04",               # B
            "2024-01-02", "2024-01-03", "2024-01-04",               # C — нет начала
        ]),
        "Coin_Name": ["A"] * 4 + ["B"] * 3 + ["C"] * 3,
        "Close": [100] * 10,
    })
    result, start, end, excluded = select_custom_period(df, "2024-01-01", "2024-01-04")
    assert (start, end) == (pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-04"))
    assert excluded == ["C"]
    assert set(result["Coin_Name"]) == {"A", "B"}
    assert set(result["Date"]) == set(pd.to_datetime([
        "2024-01-01", "2024-01-03", "2024-01-04"
    ]))
    assert all(group["Date"].nunique() == 3 for _, group in result.groupby("Coin_Name"))


def test_select_custom_period_invalid_dates():
    """Дата начала не может совпадать с датой окончания или быть позже неё"""
    with pytest.raises(ValueError):
        select_custom_period(sample_prices(), "2024-01-04", "2024-01-01")


def test_get_risk_top5():
    """Проверяет все четыре рейтинга и исключение пропусков"""
    table = pd.DataFrame({
        "Монета": list("ABCDEFG"),
        "Дневная волатильность (%)": [1, 2, 3, 4, 5, 6, float("nan")],
        "Максимальная просадка (%)": [70, 60, 50, 40, 30, 20, 10],
    })
    top = get_risk_top5(table)
    assert top["Топ-5 монет с наименьшей волатильностью"]["Монета"].tolist() == list("ABCDE")
    assert top["Топ-5 монет с наибольшей волатильностью"]["Монета"].tolist() == list("FEDCB")
    assert top["Топ-5 монет с наименьшей просадкой"]["Монета"].tolist() == list("GFEDC")
    assert top["Топ-5 монет с наибольшей просадкой"]["Монета"].tolist() == list("ABCDE")
