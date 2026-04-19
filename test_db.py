from database import calculate_fee

def test_calculate_fee():
    # 1 saatlik giriş: 20 TL olmalı
    assert calculate_fee("2026-04-19 10:00:00", "2026-04-19 11:00:00") == 20.0
    # 5 saatlik giriş: 60 TL olmalı
    assert calculate_fee("2026-04-19 10:00:00", "2026-04-19 15:00:00") == 60.0