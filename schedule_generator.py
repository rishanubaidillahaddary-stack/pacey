"""
Schedule generator -- fitur INTI aplikasi.

Sebelum ini, app cuma punya 3 alat berdiri sendiri (kalkulator VDOT, cek
kelayakan, form log bebas). Modul ini yang nyatuin semuanya jadi output
konkret: jadwal harian nyata, tersimpan sebagai sesi 'scheduled' di
database -- bukan cuma dibuat pas lagi nge-log.

Prinsip volume yang dipakai (bukan pendapat pribadi, praktik umum coaching):
- Kenaikan volume mingguan dibatasi ~8%/minggu (versi konservatif dari
  "aturan 10%" yang umum dipakai, walau di sains olahraga sendiri masih
  diperdebatkan seberapa ketat aturan ini)
- Cutback week (turun ~25%) tiap minggu ke-4, biar tubuh sempat pulih
  sebelum lanjut naik -- pola "3 minggu naik, 1 minggu turun" ini lazim
  dipakai coach (termasuk kerangka yang dipakai Pfitzinger, Hansons, dkk)
- Taper 2 tahap: minggu taper pertama ~70% dari volume puncak, minggu
  taper berikutnya ~50%
"""

import json
from datetime import date, timedelta


NAMA_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# Index hari (0=Senin..6=Minggu) yang dipakai lari, per jumlah hari/minggu.
# Hari terakhir di tiap list SELALU dianggap long run day.
POLA_HARI_LARI = {
    3: [1, 3, 5],              # Selasa, Kamis, Sabtu(long run)
    4: [1, 2, 4, 5],           # Selasa, Rabu, Jumat, Sabtu(long run)
    5: [1, 2, 3, 4, 5],        # Selasa-Jumat, Sabtu(long run)
    6: [0, 1, 2, 3, 4, 5],     # Senin-Sabtu(long run)
    7: [0, 1, 2, 3, 4, 5, 6],  # tiap hari, Minggu(long run)
}


def _load_rules():
    with open("periodization_rules.json") as f:
        return json.load(f)


def _jadwal_fase_per_minggu(total_minggu: int, tujuan: str, rules: dict) -> list:
    """Hasilkan list nama fase untuk tiap minggu, mis. ['base','base','build',...]."""
    key = "race_goal_periodization" if tujuan == "race" else "maintenance_goal_periodization"
    fase_list = rules[key]["phases"]

    hasil = []
    sisa = total_minggu
    for i, fase in enumerate(fase_list):
        if i == len(fase_list) - 1:
            jumlah = sisa  # fase terakhir ambil semua sisa (hindari minggu hilang akibat pembulatan)
        else:
            jumlah = max(1, round(fase["pct_of_total_weeks"] * total_minggu))
            jumlah = min(jumlah, sisa)
        hasil.extend([fase["name"]] * jumlah)
        sisa -= jumlah
        if sisa <= 0:
            break
    return hasil[:total_minggu]


def _progresi_volume(jadwal_fase: list, volume_awal_km: float) -> list:
    """
    Hitung target volume (km) tiap minggu, mengikuti fase & aturan cutback/taper.

    Kunci perbaikan: `baseline` adalah garis tren yang TERUS naik tiap minggu
    (kecuali taper), sedangkan cutback cuma mendiskon OUTPUT minggu itu --
    tidak menurunkan baseline yang dipakai minggu berikutnya. Kalau cutback
    ikut menurunkan baseline, hasilnya progres malah stagnan/turun tiap
    siklus 4 minggu -- persis bug yang kejadian di versi awal modul ini.
    """
    volumes = []
    baseline = volume_awal_km
    puncak = volume_awal_km
    for i, fase in enumerate(jadwal_fase):
        if fase == "taper":
            urutan_taper = jadwal_fase[:i + 1].count("taper")
            v = puncak * (0.70 if urutan_taper == 1 else 0.50)
        elif fase == "base_rotation":
            v = volume_awal_km * (0.80 if (i + 1) % 4 == 0 else 1.0)
        else:
            if i > 0:
                baseline = min(baseline * 1.08, volume_awal_km * 1.6)  # baseline naik terus, dibatasi 1.6x
            v = baseline * 0.75 if (i + 1) % 4 == 0 else baseline
            puncak = max(puncak, v)
        volumes.append(round(v, 1))
    return volumes


def _sesi_untuk_minggu(tanggal_senin: date, fase: str, volume_km: float, hari_per_minggu: int) -> list:
    """Hasilkan 7 sesi harian (Senin-Minggu) untuk satu minggu tertentu."""
    pola = POLA_HARI_LARI.get(hari_per_minggu, POLA_HARI_LARI[4])
    hari_long_run = pola[-1]
    hari_quality = pola[1] if len(pola) >= 3 and fase in ("build", "peak") else None

    ada_quality = hari_quality is not None
    km_long_run = round(volume_km * 0.28, 1)
    km_quality = round(volume_km * 0.15, 1) if ada_quality else 0.0
    sisa_km = max(volume_km - km_long_run - km_quality, 0)
    jumlah_hari_easy = len(pola) - 1 - (1 if ada_quality else 0)
    km_per_easy = round(sisa_km / jumlah_hari_easy, 1) if jumlah_hari_easy > 0 else 0.0

    sesi_minggu_ini = []
    for offset in range(7):
        tanggal = tanggal_senin + timedelta(days=offset)
        if offset not in pola:
            sesi_minggu_ini.append({
                "tanggal": str(tanggal), "jenis": "rest", "zona": None, "jarak_km": 0.0
            })
        elif offset == hari_long_run:
            sesi_minggu_ini.append({
                "tanggal": str(tanggal), "jenis": "long_run", "zona": "E", "jarak_km": km_long_run
            })
        elif offset == hari_quality:
            jenis_quality = "tempo" if fase == "build" else "interval"
            zona_quality = "T" if fase == "build" else "I"
            sesi_minggu_ini.append({
                "tanggal": str(tanggal), "jenis": jenis_quality, "zona": zona_quality, "jarak_km": km_quality
            })
        else:
            sesi_minggu_ini.append({
                "tanggal": str(tanggal), "jenis": "easy_run", "zona": "E", "jarak_km": km_per_easy
            })
    return sesi_minggu_ini


def ringkasan_fase(total_minggu: int, tujuan: str) -> dict:
    """
    Preview breakdown fase tanpa perlu generate jadwal penuh -- dipakai
    di halaman kelayakan target, biar hasilnya bukan cuma layak/tidak,
    tapi juga 'kalau layak, begini kira-kira pembagian fasenya'.
    """
    rules = _load_rules()
    jadwal_fase = _jadwal_fase_per_minggu(total_minggu, tujuan, rules)
    ringkasan = {}
    for fase in jadwal_fase:
        ringkasan[fase] = ringkasan.get(fase, 0) + 1
    return ringkasan


def generate_jadwal(tanggal_mulai: date, total_minggu: int, tujuan: str,
                     volume_awal_km: float, hari_per_minggu: int) -> list:
    """
    Fungsi utama. Hasilkan jadwal lengkap dari tanggal_mulai sampai total_minggu
    ke depan. Return: list flat berisi semua sesi harian (dict), siap disimpan ke DB.
    """
    rules = _load_rules()
    jadwal_fase = _jadwal_fase_per_minggu(total_minggu, tujuan, rules)
    volumes = _progresi_volume(jadwal_fase, volume_awal_km)

    # Mundurkan tanggal_mulai ke Senin terdekat sebelumnya, biar tiap minggu rapi Senin-Minggu
    tanggal_senin_pertama = tanggal_mulai - timedelta(days=tanggal_mulai.weekday())

    semua_sesi = []
    for minggu_ke in range(total_minggu):
        tanggal_senin = tanggal_senin_pertama + timedelta(weeks=minggu_ke)
        sesi_minggu = _sesi_untuk_minggu(
            tanggal_senin, jadwal_fase[minggu_ke], volumes[minggu_ke], hari_per_minggu
        )
        for sesi in sesi_minggu:
            sesi["fase"] = jadwal_fase[minggu_ke]
            sesi["minggu_ke"] = minggu_ke + 1
        semua_sesi.extend(sesi_minggu)

    # Buang sesi yang tanggalnya sebelum tanggal_mulai asli (dari sisa hari di minggu pertama)
    return [s for s in semua_sesi if s["tanggal"] >= str(tanggal_mulai)]


if __name__ == "__main__":
    # Contoh: mulai hari ini, target 10K dalam 12 minggu, volume awal 15 km/minggu, lari 4x/minggu
    jadwal = generate_jadwal(
        tanggal_mulai=date.today(),
        total_minggu=12,
        tujuan="race",
        volume_awal_km=15.0,
        hari_per_minggu=4,
    )
    print(f"Total sesi dihasilkan: {len(jadwal)}")
    print("\n8 sesi pertama:")
    for s in jadwal[:8]:
        print(f"  Minggu {s['minggu_ke']} ({s['fase']:>8}) {s['tanggal']} - {s['jenis']:<10} {s['zona'] or '-':<3} {s['jarak_km']} km")
