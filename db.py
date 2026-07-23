"""
Modul database — versi PostgreSQL (Supabase) untuk deploy cloud.
Pakai psycopg2 sebagai driver. Connection string diambil dari
environment variable DATABASE_URL (diset di Streamlit Cloud secrets).
"""

import os
import hashlib
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


def dapatkan_koneksi():
    """Koneksi ke PostgreSQL via DATABASE_URL dari environment."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL belum diset di environment/secrets.")
    conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
    return conn


def init_db():
    """Buat semua tabel kalau belum ada. Dipanggil sekali saat app start."""
    conn = dapatkan_koneksi()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            scheduled_date TEXT NOT NULL,
            session_type TEXT NOT NULL,
            zone TEXT,
            planned_distance_km REAL,
            status TEXT DEFAULT 'scheduled',
            actual_distance_km REAL,
            rpe INTEGER,
            feeling TEXT,
            has_pain INTEGER DEFAULT 0,
            pain_location TEXT,
            notes TEXT,
            phase TEXT,
            week_number INTEGER,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (username, key)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# ── SETTINGS ──

def simpan_setting(username: str, key: str, value: str):
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO user_settings (username, key, value, updated_at)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT (username, key)
           DO UPDATE SET value=EXCLUDED.value, updated_at=EXCLUDED.updated_at""",
        (username, key, value, datetime.now().isoformat())
    )
    conn.commit()
    cur.close()
    conn.close()


def ambil_setting(username: str, key: str, default=None):
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        "SELECT value FROM user_settings WHERE username=%s AND key=%s",
        (username, key)
    )
    baris = cur.fetchone()
    cur.close()
    conn.close()
    return baris["value"] if baris else default


# ── PASSWORD ──

def _hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def set_password(username: str, pin: str):
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO users (username, password_hash, created_at)
           VALUES (%s, %s, %s)
           ON CONFLICT (username)
           DO UPDATE SET password_hash=EXCLUDED.password_hash""",
        (username, _hash_pin(pin), datetime.now().isoformat())
    )
    conn.commit()
    cur.close()
    conn.close()


def cek_password(username: str, pin: str) -> bool:
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username=%s", (username,))
    baris = cur.fetchone()
    cur.close()
    conn.close()
    if not baris:
        return False
    return baris["password_hash"] == _hash_pin(pin)


def punya_password(username: str) -> bool:
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username=%s", (username,))
    ada = cur.fetchone() is not None
    cur.close()
    conn.close()
    return ada


# ── BAHASA ──

def ambil_bahasa(username: str) -> str:
    return ambil_setting(username, "bahasa", default="id")


def simpan_bahasa(username: str, kode: str):
    simpan_setting(username, "bahasa", kode)


# ── USERS ──

def daftar_username() -> list:
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users ORDER BY username")
    hasil = [r["username"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return hasil


# ── SESSIONS ──

def simpan_jadwal(username: str, daftar_sesi: list):
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    for sesi in daftar_sesi:
        cur.execute(
            """INSERT INTO sessions
               (username, scheduled_date, session_type, zone, planned_distance_km,
                status, created_at, phase, week_number)
               VALUES (%s, %s, %s, %s, %s, 'scheduled', %s, %s, %s)""",
            (username, sesi["tanggal"], sesi["jenis"], sesi["zona"], sesi["jarak_km"],
             datetime.now().isoformat(), sesi["fase"], sesi["minggu_ke"])
        )
    conn.commit()
    cur.close()
    conn.close()


def hapus_jadwal_belum_dijalani(username: str, dari_tanggal: str):
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM sessions WHERE username=%s AND status='scheduled' AND scheduled_date>=%s",
        (username, dari_tanggal)
    )
    conn.commit()
    cur.close()
    conn.close()


def catat_hasil_sesi(username: str, id_sesi: int, status: str, jarak_aktual: float = None,
                      rpe: int = None, feeling: str = None, ada_nyeri: bool = False,
                      lokasi_nyeri: str = None, catatan: str = None):
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        """UPDATE sessions SET
             status=%s, actual_distance_km=%s, rpe=%s, feeling=%s,
             has_pain=%s, pain_location=%s, notes=%s
           WHERE id=%s AND username=%s""",
        (status, jarak_aktual, rpe, feeling, int(ada_nyeri),
         lokasi_nyeri, catatan, id_sesi, username)
    )
    conn.commit()
    cur.close()
    conn.close()


def ambil_sesi_by_tanggal(username: str, tanggal: str):
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM sessions WHERE username=%s AND scheduled_date=%s ORDER BY id DESC LIMIT 1",
        (username, tanggal)
    )
    baris = cur.fetchone()
    cur.close()
    conn.close()
    return dict(baris) if baris else None


def ambil_jadwal_minggu_ini(username: str, tanggal_senin: str, tanggal_minggu: str) -> list:
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM sessions
           WHERE username=%s AND scheduled_date BETWEEN %s AND %s AND status='scheduled'
           ORDER BY scheduled_date""",
        (username, tanggal_senin, tanggal_minggu)
    )
    hasil = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return hasil


def ambil_sesi_terakhir_logged(username: str, jumlah: int = 10) -> list:
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM sessions
           WHERE username=%s AND status IN ('completed', 'skipped')
           ORDER BY scheduled_date DESC LIMIT %s""",
        (username, jumlah)
    )
    hasil = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return hasil


def hitung_rasio_skip(username: str, jumlah_minggu_terakhir: int = 2) -> float:
    conn = dapatkan_koneksi()
    cur = conn.cursor()
    cur.execute(
        """SELECT status FROM sessions
           WHERE username=%s AND status IN ('completed', 'skipped')
           ORDER BY scheduled_date DESC LIMIT %s""",
        (username, jumlah_minggu_terakhir * 7)
    )
    baris = cur.fetchall()
    cur.close()
    conn.close()
    if not baris:
        return 0.0
    total = len(baris)
    di_skip = sum(1 for b in baris if b["status"] == "skipped")
    return di_skip / total
