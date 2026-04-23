import sqlite3
import hashlib
from datetime import datetime

def create_connection():
    """Veritabanı bağlantısı oluşturur ve WAL modunu aktif eder."""
    conn = sqlite3.connect('parking.db')
    conn.execute("PRAGMA journal_mode=WAL") 
    conn.row_factory = sqlite3.Row # Verileri sözlük gibi çekmemizi sağlar
    return conn

def setup_database():
    conn = create_connection()
    cursor = conn.cursor()

    # 1. Vehicles Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Parking Sessions Tablosu (CALC-01 desteğiyle)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            slot_id TEXT,
            entry_time DATETIME NOT NULL,
            exit_time DATETIME,
            fee REAL DEFAULT 0.0,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (vehicle_id)
        )
    ''')

    # 3. Slot Status Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS slot_status (
            slot_id TEXT PRIMARY KEY,
            is_occupied INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Admins Tablosu (Güvenlik Kararı 3.4 gereği)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Veritabanı yapısı %100 hazır!")

# --- IS MANTIGI FONKSIYONLARI ---

def add_vehicle_entry(vehicle_id, slot_id):
    """Aracı kaydeder, oturum başlatır ve slotu günceller."""
    conn = create_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute("INSERT OR IGNORE INTO vehicles (vehicle_id) VALUES (?)", (vehicle_id,))
        cursor.execute("INSERT INTO parking_sessions (vehicle_id, slot_id, entry_time) VALUES (?, ?, ?)", 
                       (vehicle_id, slot_id, now))
        cursor.execute("UPDATE slot_status SET is_occupied = 1, last_updated = ? WHERE slot_id = ?", (now, slot_id))
        conn.commit()
    finally:
        conn.close()

def add_vehicle_exit(vehicle_id, slot_id):
    """Ücreti hesaplar, oturumu kapatır ve slotu boşaltır."""
    conn = create_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # En son aktif oturumu bul
    cursor.execute("""SELECT entry_time, session_id FROM parking_sessions 
                      WHERE vehicle_id = ? AND exit_time IS NULL""", (vehicle_id,))
    row = cursor.fetchone()
    
    if row:
        entry_time_str = row['entry_time']
        fee = calculate_fee(entry_time_str, now_str)
        
        # Oturumu ve slotu güncelle
        cursor.execute("UPDATE parking_sessions SET exit_time = ?, fee = ? WHERE session_id = ?", 
                       (now_str, fee, row['session_id']))
        cursor.execute("UPDATE slot_status SET is_occupied = 0, last_updated = ? WHERE slot_id = ?", (now_str, slot_id))
        conn.commit()
        conn.close()
        return fee
    conn.close()
    return 0

def calculate_fee(entry_time_str, exit_time_str):
    fmt = '%Y-%m-%d %H:%M:%S'
    entry = datetime.strptime(entry_time_str, fmt)
    exit_ = datetime.strptime(exit_time_str, fmt)
    hours = (exit_ - entry).total_seconds() / 3600
    
    if hours <= 1: return 50.0 # SDD 3.6 Tablo 8'e göre güncellendi
    elif hours <= 3: return 100.0
    elif hours <= 6: return 160.0
    else: return 200.0

def get_live_status():
    """Furkan'ın arayüzü için anlık doluluk verisi döner."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM slot_status")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    setup_database()
    # İlk çalıştırmada slotları tanımlayalım (Örn: 10 slot)
    conn = create_connection()
    for i in range(1, 11):
        conn.execute("INSERT OR IGNORE INTO slot_status (slot_id) VALUES (?)", (f"Slot-{i}",))
    conn.commit()
    conn.close()