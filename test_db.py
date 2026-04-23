from database import calculate_fee

def test_calculate_fee_tiers():
    """Yeni ücret tarifesi (Tablo 8) test senaryoları."""
    
    # 1. Senaryo: 0-1 Saat Arası (50 TL)
    # 45 dakikalık kalış
    assert calculate_fee("2026-04-23 10:00:00", "2026-04-23 10:45:00") == 50.0
    
    # 2. Senaryo: Tam 1. saat sınırı (50 TL)
    assert calculate_fee("2026-04-23 10:00:00", "2026-04-23 11:00:00") == 50.0
    
    # 3. Senaryo: 1-3 Saat Arası (100 TL)
    # 2.5 saatlik kalış
    assert calculate_fee("2026-04-23 10:00:00", "2026-04-23 12:30:00") == 100.0
    
    # 4. Senaryo: 3-6 Saat Arası (160 TL)
    # 5 saatlik kalış
    assert calculate_fee("2026-04-23 10:00:00", "2026-04-23 15:00:00") == 160.0
    
    # 5. Senaryo: 6 Saat Üzeri (200 TL)
    # 10 saatlik kalış
    assert calculate_fee("2026-04-23 10:00:00", "2026-04-23 20:00:00") == 200.0

def test_calculate_fee_day_cross():
    """Gün devredince (gece yarısı) ücretin doğru hesaplanması."""
    # 23:00'de girdi, ertesi gün 01:00'de çıktı (2 saat = 100 TL)
    assert calculate_fee("2026-04-23 23:00:00", "2026-04-24 01:00:00") == 100.0