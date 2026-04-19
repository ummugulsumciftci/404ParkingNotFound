import sqlite3
from datetime import datetime

def create_connection():
    """Veritabanı bağlantısı oluşturur ve WAL modunu aktif eder."""
    # SRS 1.3.5: Veri bütünlüğü için WAL modu etkinleştirilmelidir[cite: 379].
    conn = sqlite3.connect('parking.db')
    conn.execute("PRAGMA journal_mode=WAL") 
    return conn

def setup_database():
    conn = create_connection()
    cursor = conn.cursor()

    # 1. Vehicles Tablosu: Araçların genel bilgilerini tutar[cite: 374].
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            plate_text TEXT
        )
    ''')

    # 2. Parking Sessions Tablosu: Giriş-çıkış ve ücretleri tutar[cite: 375].
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            entry_time DATETIME NOT NULL,
            exit_time DATETIME,
            fee REAL DEFAULT 0.0,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (vehicle_id)
        )
    ''')

    # 3. Slot Status Tablosu: Park yerlerinin anlık durumunu tutar[cite: 377].
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS slot_status (
            slot_id TEXT PRIMARY KEY,
            is_occupied INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Veritabanı ve tablolar başarıyla oluşturuldu!")

if __name__ == "__main__":
    setup_database()
def add_vehicle_entry(vehicle_id, entry_time):
    """Yeni bir araç girişi kaydeder[cite: 303]."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Önce aracı genel listeye ekle veya güncelle
        cursor.execute("INSERT OR IGNORE INTO vehicles (vehicle_id) VALUES (?)", (vehicle_id,))
        # Giriş oturumu oluştur
        cursor.execute("INSERT INTO parking_sessions (vehicle_id, entry_time) VALUES (?, ?)", 
                       (vehicle_id, entry_time))
        conn.commit()
    except Exception as e:
        print(f"Giriş kaydı hatası: {e}") # SRS 1.8.9: Hata günlüğü tutulmalı[cite: 489].
    finally:
        conn.close()

def update_slot(slot_id, is_occupied):
    """Park yerinin doluluk durumunu günceller[cite: 308]."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE slot_status SET is_occupied = ?, last_updated = CURRENT_TIMESTAMP WHERE slot_id = ?", 
                   (is_occupied, slot_id))
    conn.commit()
    conn.close()
def calculate_fee(entry_time_str, exit_time_str):
    """Süreye bağlı ücret hesaplar[cite: 312]."""
    fmt = '%Y-%m-%d %H:%M:%S'
    entry = datetime.strptime(entry_time_str, fmt)
    exit_ = datetime.strptime(exit_time_str, fmt)
    
    duration = exit_ - entry
    hours = duration.total_seconds() / 3600
    
    # Basit ücret tarifesi [cite: 314]
    if hours <= 1: return 20.0
    elif hours <= 3: return 40.0
    elif hours <= 6: return 60.0
    else: return 100.0
import hashlib

def hash_password(password):
    """Şifreyi güvenli bir şekilde hashler."""
    return hashlib.sha256(password.encode()).hexdigest()