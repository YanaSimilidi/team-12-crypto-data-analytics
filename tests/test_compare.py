import pytest
import pandas as pd
from utils.compare import compare_coins

@pytest.fixture
def mock_df():
    """Создаем маленькую таблицу для теста"""
    data = {
        'Date': pd.to_datetime([
            '2023-01-01', '2023-01-02', '2023-01-03', 
            '2023-01-01', '2023-01-02', '2023-01-03'
        ]),
        'Coin_Name': ['BTC', 'BTC', 'BTC', 'ETH', 'ETH', 'ETH'],
        'Close': [100, 110, 120, 50, 50, 25] 
        # BTC вырос на 20%, ETH упал на 50%
    }
    return pd.DataFrame(data)

def test_compare_normalization(mock_df):
    """Проверяем, что цены правильно приводятся к 100"""
    result, corr = compare_coins(
        mock_df, 'BTC', 'ETH', 
        pd.to_datetime('2023-01-01'), 
        pd.to_datetime('2023-01-03')
    )
    
    # В первый день обе монеты должны стоить ровно 100
    assert result['BTC'].iloc[0] == 100
    assert result['ETH'].iloc[0] == 100
    
    # BTC вырос до 120, ETH упал до 50
    assert result['BTC'].iloc[2] == 120
    assert result['ETH'].iloc[2] == 50

def test_compare_missing_coin(mock_df):
    """Проверяем, что если монеты нет, выдается ошибка"""
    with pytest.raises(ValueError, match="Одна из монет не найдена в выбранном периоде"):
        compare_coins(
            mock_df, 'BTC', 'DOGE', 
            pd.to_datetime('2023-01-01'), 
            pd.to_datetime('2023-01-03')
        )

def test_compare_correlation(mock_df):
    """Проверяем, что корреляция считается"""
    result, corr = compare_coins(
        mock_df, 'BTC', 'ETH', 
        pd.to_datetime('2023-01-01'), 
        pd.to_datetime('2023-01-03')
    )
    # Проверяем, что корреляция вернулась в виде числа от -1 до 1
    assert -1 <= corr <= 1