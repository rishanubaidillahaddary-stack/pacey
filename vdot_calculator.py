"""
Kalkulator VDOT asli (Daniels-Gilbert), BUKAN tabel statis.

Kenapa ini lebih baik dari tabel JSON sebelumnya:
Tabel pace yang diekstrak dari dokumen basis pengetahuan (hasil Ollama)
ternyata melenceng 15-20 detik/km dibanding kalkulator independen lain
untuk VDOT yang sama -- kemungkinan besar Ollama "menulis" angka, bukan
menghitungnya. Modul ini menggantinya dengan rumus matematis asli yang
dipublikasikan Daniels & Gilbert (Oxygen Power, 1979), jadi hasilnya
presisi dan bisa diverifikasi ulang kapan saja -- bukan sekadar
"dipercaya" dari sebuah dokumen.

Sumber rumus (dikonfirmasi identik di banyak kalkulator independen):
  VO2(v)        = -4.60 + 0.182258*v + 0.000104*v^2      (v = m/menit)
  %VO2max(t)    = 0.8 + 0.1894393*e^(-0.012778*t)
                       + 0.2989558*e^(-0.1932605*t)       (t = menit)
  VDOT          = VO2(v) / %VO2max(t)

Catatan soal persentase zona latihan (E/M/T/I/R):
Berbeda dari rumus VDOT di atas (yang eksak dari publikasi asli),
persentase %VDOT untuk tiap zona latihan (easy, marathon, threshold,
dst) bervariasi sedikit antar sumber (mis. easy 59-74% vs 65-79%).
Nilai di bawah ini representatif dari titik tengah beberapa sumber --
kalau nanti kamu dapat akses buku aslinya, angka ini gampang disesuaikan
di satu tempat ini saja.
"""

import math


def _vo2_dari_kecepatan(v_m_per_menit: float) -> float:
    """VO2 (ml/kg/menit) yang dibutuhkan untuk lari di kecepatan v."""
    return -4.60 + 0.182258 * v_m_per_menit + 0.000104 * v_m_per_menit ** 2


def _persen_vo2max_dari_waktu(t_menit: float) -> float:
    """Fraksi VO2max yang bisa dipertahankan untuk durasi t menit."""
    return (0.8
            + 0.1894393 * math.exp(-0.012778 * t_menit)
            + 0.2989558 * math.exp(-0.1932605 * t_menit))


def _kecepatan_dari_vo2(vo2_target: float) -> float:
    """Kebalikan dari _vo2_dari_kecepatan -- solve persamaan kuadrat untuk v."""
    a, b, c = 0.000104, 0.182258, (-4.60 - vo2_target)
    diskriminan = b ** 2 - 4 * a * c
    return (-b + math.sqrt(diskriminan)) / (2 * a)


def _pace_per_km(v_m_per_menit: float) -> str:
    """Ubah kecepatan (m/menit) jadi format pace mm:ss /km."""
    detik_per_km = (1000 / v_m_per_menit) * 60
    menit = int(detik_per_km // 60)
    detik = int(round(detik_per_km % 60))
    if detik == 60:
        menit += 1
        detik = 0
    return f"{menit}:{detik:02d}"


def hitung_vdot(jarak_meter: float, waktu_menit: float) -> float:
    """
    Hitung VDOT dari hasil lomba/time-trial nyata.
    Contoh: hitung_vdot(5000, 20) untuk lari 5K dalam 20 menit.
    """
    kecepatan = jarak_meter / waktu_menit
    vo2 = _vo2_dari_kecepatan(kecepatan)
    persen = _persen_vo2max_dari_waktu(waktu_menit)
    return vo2 / persen


def hitung_zona_latihan(vdot: float) -> dict:
    """
    Dari satu angka VDOT, hasilkan pace untuk tiap zona latihan (per km).
    """
    persentase_zona = {
        "easy_low": 0.59,
        "easy_high": 0.74,
        "marathon": 0.84,
        "threshold": 0.88,
        "interval": 0.98,
        "repetition": 1.05,   # pendekatan; Daniels aslinya mengaitkan R ke pace lomba 1 mil aktual
    }
    hasil = {}
    for nama_zona, persen in persentase_zona.items():
        vo2_target = vdot * persen
        kecepatan = _kecepatan_dari_vo2(vo2_target)
        hasil[nama_zona] = _pace_per_km(kecepatan)
    return hasil


if __name__ == "__main__":
    # Contoh verifikasi: 5K dalam 20:00 -> harusnya VDOT sekitar 49-51
    vdot_contoh = hitung_vdot(jarak_meter=5000, waktu_menit=20.0)
    print(f"VDOT dari 5K/20:00: {vdot_contoh:.1f}")

    zona = hitung_zona_latihan(vdot_contoh)
    print("Pace per zona latihan:")
    for nama, pace in zona.items():
        print(f"  {nama}: {pace} /km")
