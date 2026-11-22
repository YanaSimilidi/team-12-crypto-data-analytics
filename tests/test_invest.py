from utils.invest import calculate


# Проверяет функциюцию: правильно ли она считает деньги и прибыль
def test_calculate():
    # Пример: вложили 100, монета стоила 10, сейчас стоит 20
    total_now, profit = calculate(100, 10, 20)
    # Ожидаем, что денег станет 200, прибыль будет 100%
    assert total_now == 200
    assert profit == 100
