from utils.invest import calculate


# Проверяет функцию: правильно ли она считает деньги и прибыль
def test_calculate():
    # Пример: вложили 100, монета стоила 10, сейчас стоит 20
    total_now, profit = calculate(100, 10, 20)
    # Ожидаем, что денег станет 200, прибыль будет 100%
    assert total_now == 200
    assert profit == 100


# Проверяет, что функция правильно считает убыток
def test_loss():
    # Пример: вложили 100, монета стоила 20, сейчас стоит 10
    total_now, profit = calculate(100, 20, 10)
    # Ожидаем, что денег станет 50, убыток будет -50%
    assert total_now == 50
    assert profit == -50