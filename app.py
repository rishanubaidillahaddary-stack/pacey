"""
App utama — versi dengan password PIN, multi-bahasa, dan coach yang nyapa pakai nama.

Cara jalanin: python3 -m streamlit run app.py
"""

import json
from datetime import date, timedelta

import streamlit as st

import vdot_calculator
import schedule_generator
import db


st.set_page_config(page_title="PaceY", page_icon="👟", layout="centered")

# Init database satu kali saat app start
db.init_db()

# ─────────────────────────────────────────────
# INJECT CSS — PaceY Design System
# Font: Inter (Google Fonts)
# Style: Clean minimalis, depth effect on hover/tap
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* -- Global -- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background-color: #EEF1F7 !important;
}

/* -- Sembunyikan header & footer bawaan Streamlit -- */
#MainMenu, footer, header { visibility: hidden; }

/* -- PaceY Logo Header -- */
.pacey-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0 24px 0;
}
.pacey-logo-icon {
    background: #5B7FA6;
    color: white;
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 2px 8px rgba(91,127,166,0.25);
}
.pacey-logo-text {
    font-size: 22px;
    font-weight: 700;
    color: #2C3E5A;
    letter-spacing: -0.5px;
}
.pacey-logo-text span {
    color: #5B7FA6;
}

/* -- Cards -- */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: white;
    border-radius: 16px;
    padding: 4px;
    box-shadow: 0 2px 12px rgba(44,62,90,0.07);
}

/* -- Metric cards -- */
div[data-testid="stMetric"] {
    background: white;
    border-radius: 14px;
    padding: 16px 20px !important;
    box-shadow: 0 2px 10px rgba(44,62,90,0.08);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(44,62,90,0.13);
}
div[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #8A9BB5 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #2C3E5A !important;
}

/* -- Tombol utama -- */
.stButton > button {
    background: #5B7FA6 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    box-shadow: 0 3px 10px rgba(91,127,166,0.30) !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(91,127,166,0.38) !important;
    background: #4A6E94 !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 6px rgba(91,127,166,0.25) !important;
}

/* -- Tombol secondary (hapus profil) -- */
.stButton > button[kind="secondary"] {
    background: white !important;
    color: #8A9BB5 !important;
    border: 1.5px solid #D8E0EC !important;
    box-shadow: 0 2px 6px rgba(44,62,90,0.06) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #C0CCDC !important;
    color: #5B7FA6 !important;
    background: #F4F7FB !important;
}

/* -- Input fields -- */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 1.5px solid #D8E0EC !important;
    background: #F8FAFD !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    color: #2C3E5A !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #5B7FA6 !important;
    box-shadow: 0 0 0 3px rgba(91,127,166,0.12) !important;
}

/* -- Select box -- */
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #D8E0EC !important;
    background: #F8FAFD !important;
}

/* -- Tabs -- */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    box-shadow: 0 2px 8px rgba(44,62,90,0.07);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    color: #8A9BB5 !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #5B7FA6 !important;
    color: white !important;
}

/* -- Info / success / warning boxes -- */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
}

/* -- Dataframe / tabel -- */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(44,62,90,0.07);
}

/* -- Divider -- */
hr {
    border: none !important;
    border-top: 1.5px solid #E8EDF5 !important;
    margin: 20px 0 !important;
}

/* -- Subheader & label -- */
h2, h3 {
    color: #2C3E5A !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px !important;
}
label, .stRadio label, .stCheckbox label {
    font-family: 'Inter', sans-serif !important;
    color: #4A5E7A !important;
    font-size: 14px !important;
}

/* -- Caption -- */
.stCaption, small {
    color: #8A9BB5 !important;
    font-size: 12px !important;
}

/* -- Spinner -- */
.stSpinner > div {
    border-top-color: #5B7FA6 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TEKS UI PER BAHASA
# ─────────────────────────────────────────────
UI = {
    "id": {
        "title": "PaceY",
        "siapa": "Siapa yang mau latihan hari ini?",
        "profil_ada": "**Pilih profil yang sudah ada:**",
        "buat_baru": "**Atau buat profil baru:**",
        "username_placeholder": "contoh: rishan",
        "pin_placeholder": "PIN 6 digit",
        "btn_masuk": "🔑 Masuk",
        "btn_buat": "➕ Buat Profil",
        "err_username_kosong": "Isi username dulu.",
        "err_username_format": "Pakai huruf/angka/underscore aja.",
        "err_pin_format": "PIN harus 6 digit angka.",
        "err_pin_salah": "PIN salah.",
        "label_ganti": "(ganti)",
        "tab_hari_ini": "🏃 Hari Ini",
        "tab_pengaturan": "⚙️ Pengaturan & Kalibrasi",
        "belum_ada_jadwal": "Belum ada jadwal untuk hari ini. Buat jadwal dulu di tab **Pengaturan & Kalibrasi**.",
        "rencana_hari_ini": "Rencana Hari Ini",
        "jenis_sesi": "Jenis Sesi",
        "target_jarak": "Target Jarak",
        "fase": "Fase",
        "mgg": "mgg",
        "sudah_ditandai": "Sesi ini sudah ditandai",
        "log_sesi": "**Log sesi ini setelah dijalani:**",
        "status": "Status",
        "jarak_aktual": "Jarak aktual (km)",
        "rpe_label": "RPE (seberapa berat, 1–10)",
        "perasaan": "Perasaan",
        "ada_nyeri": "Ada nyeri/tidak nyaman?",
        "lokasi_nyeri": "Lokasi nyeri (kalau ada)",
        "catatan": "Catatan tambahan (opsional)",
        "simpan_log": "Simpan Log",
        "log_tersimpan": "Log tersimpan!",
        "jadwal_minggu": "📅 Jadwal Minggu Ini (yang belum dijalani)",
        "jadwal_kosong": "Semua jadwal minggu ini sudah dijalani, atau belum ada jadwal.",
        "riwayat": "📋 Riwayat Sesi Terakhir (sudah dijalankan)",
        "riwayat_kosong": "Belum ada sesi yang sudah dicatat. Log dulu sesi hari ini!",
        "riwayat_caption": "↑ Paling lama di atas · paling baru di bawah",
        "coach_title": "🤖 Insight dari Coach",
        "coach_btn_feedback": "Minta feedback sesi hari ini",
        "coach_btn_panduan": "Minta panduan sesi hari ini",
        "coach_spinner": "Coach lagi mikir...",
        "coach_ollama_err": "Pastikan Ollama sudah running (`ollama serve`) dan model sudah di-pull (`ollama pull llama3.2:3b`).",
        "pengaturan_judul": "Pengaturan untuk",
        "vdot_judul": "#### 1. Hitung VDOT & Pace Latihan",
        "vdot_jarak": "Jarak lomba/time-trial terakhir (km)",
        "vdot_waktu": "Waktu tempuh (menit)",
        "vdot_tersimpan": "VDOT tersimpan saat ini",
        "btn_hitung_vdot": "Hitung VDOT",
        "vdot_sukses": "VDOT kamu: {v:.1f} (tersimpan)",
        "kelayakan_judul": "#### 2. Cek Kelayakan Target",
        "kelayakan_target": "Target jarak race",
        "kelayakan_minggu": "Berapa minggu sampai hari-H",
        "btn_cek": "Cek Kelayakan",
        "kelayakan_ok": "Layak. Minimum disarankan {min} minggu — kamu punya {ada} minggu.",
        "kelayakan_kurang": "Waktu terlalu mepet. Minimum disarankan {min} minggu, kamu cuma punya {ada} minggu.",
        "kelayakan_alternatif": "Dengan {ada} minggu, target yang realistis: **{alt}**",
        "kelayakan_terlalu_pendek": "Bahkan 5K butuh waktu lebih lama dari ini. Pertimbangkan mundurkan tanggal target.",
        "fase_breakdown": "Perkiraan pembagian fase:",
        "jadwal_judul": "#### 3. Buat / Perbarui Jadwal",
        "jadwal_caption": "Ini akan menghapus jadwal lama yang BELUM dijalani. Riwayat yang sudah completed/skipped tetap aman.",
        "tujuan": "Tujuan",
        "total_minggu": "Jumlah minggu jadwal dibuat",
        "volume_awal": "Volume lari mingguan saat ini (km)",
        "hari_per_minggu": "Berapa hari/minggu bisa lari",
        "btn_generate": "Generate Jadwal",
        "jadwal_sukses": "Jadwal {n} sesi berhasil dibuat! Cek tab 'Hari Ini'.",
        "bahasa_judul": "#### 4. Bahasa / Language",
        "bahasa_label": "Pilih bahasa antarmuka & coach:",
        "bahasa_simpan": "Simpan Bahasa",
        "bahasa_sukses": "Bahasa diperbarui!",
        "password_judul": "#### 5. Ganti PIN",
        "password_baru": "PIN baru (6 digit angka)",
        "password_ulang": "Ulangi PIN baru",
        "btn_ganti_pin": "Ganti PIN",
        "pin_cocok": "PIN berhasil diperbarui!",
        "pin_tidak_cocok": "PIN tidak cocok.",
        "hapus_judul": "#### ⚠️ Hapus Profil Ini",
        "hapus_caption": "Hati-hati: ini hapus semua data dan riwayat lari untuk profil ini secara permanen.",
        "hapus_konfirmasi": "Ketik nama profil untuk konfirmasi hapus:",
        "btn_hapus": "🗑️ Hapus Profil",
        "hapus_sukses": "Profil dihapus.",
        "hapus_gagal": "Nama tidak cocok. Tulis persis nama profilnya.",
        "col_no": "No", "col_tanggal": "Tanggal", "col_sesi": "Sesi", "col_zona": "Zona",
        "col_target": "Target km", "col_aktual": "Aktual km", "col_status": "Status",
        "col_rpe": "RPE", "col_perasaan": "Perasaan", "col_fase": "Fase", "col_minggu": "Jumlah Minggu",
    },
    "en": {
        "title": "PaceY",
        "siapa": "Who's training today?",
        "profil_ada": "**Select an existing profile:**",
        "buat_baru": "**Or create a new profile:**",
        "username_placeholder": "e.g. rishan",
        "pin_placeholder": "6-digit PIN",
        "btn_masuk": "🔑 Sign In",
        "btn_buat": "➕ Create Profile",
        "err_username_kosong": "Please enter a username.",
        "err_username_format": "Use letters, numbers, or underscore only.",
        "err_pin_format": "PIN must be exactly 6 digits.",
        "err_pin_salah": "Incorrect PIN.",
        "label_ganti": "(switch)",
        "tab_hari_ini": "🏃 Today",
        "tab_pengaturan": "⚙️ Settings & Calibration",
        "belum_ada_jadwal": "No schedule for today. Create one in the **Settings & Calibration** tab.",
        "rencana_hari_ini": "Today's Plan",
        "jenis_sesi": "Session Type",
        "target_jarak": "Target Distance",
        "fase": "Phase",
        "mgg": "wk",
        "sudah_ditandai": "This session is already marked",
        "log_sesi": "**Log this session after completing it:**",
        "status": "Status",
        "jarak_aktual": "Actual distance (km)",
        "rpe_label": "RPE (how hard, 1–10)",
        "perasaan": "Feeling",
        "ada_nyeri": "Any pain or discomfort?",
        "lokasi_nyeri": "Pain location (if any)",
        "catatan": "Additional notes (optional)",
        "simpan_log": "Save Log",
        "log_tersimpan": "Log saved!",
        "jadwal_minggu": "📅 This Week's Schedule (upcoming)",
        "jadwal_kosong": "All sessions this week are done, or no schedule yet.",
        "riwayat": "📋 Recent Session History (completed/skipped)",
        "riwayat_kosong": "No sessions logged yet. Log today's session first!",
        "riwayat_caption": "↑ Oldest at top · newest at bottom",
        "coach_title": "🤖 Coach Insight",
        "coach_btn_feedback": "Get feedback on today's session",
        "coach_btn_panduan": "Get guidance for today's session",
        "coach_spinner": "Coach is thinking...",
        "coach_ollama_err": "Make sure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3.2:3b`).",
        "pengaturan_judul": "Settings for",
        "vdot_judul": "#### 1. Calculate VDOT & Training Pace",
        "vdot_jarak": "Race/time-trial distance (km)",
        "vdot_waktu": "Finish time (minutes)",
        "vdot_tersimpan": "Current saved VDOT",
        "btn_hitung_vdot": "Calculate VDOT",
        "vdot_sukses": "Your VDOT: {v:.1f} (saved)",
        "kelayakan_judul": "#### 2. Check Goal Feasibility",
        "kelayakan_target": "Target race distance",
        "kelayakan_minggu": "Weeks until race day",
        "btn_cek": "Check Feasibility",
        "kelayakan_ok": "Feasible. Minimum recommended: {min} weeks — you have {ada} weeks.",
        "kelayakan_kurang": "Too soon. Minimum recommended: {min} weeks — you only have {ada} weeks.",
        "kelayakan_alternatif": "With {ada} weeks, a realistic target is: **{alt}**",
        "kelayakan_terlalu_pendek": "Even a 5K needs more time than this. Consider pushing back your target date.",
        "fase_breakdown": "Estimated phase breakdown:",
        "jadwal_judul": "#### 3. Create / Update Schedule",
        "jadwal_caption": "This will delete unstarted scheduled sessions and replace them. Completed/skipped history is safe.",
        "tujuan": "Goal",
        "total_minggu": "Number of weeks to schedule",
        "volume_awal": "Current weekly running volume (km)",
        "hari_per_minggu": "Days per week you can run",
        "btn_generate": "Generate Schedule",
        "jadwal_sukses": "Schedule with {n} sessions created! Check the 'Today' tab.",
        "bahasa_judul": "#### 4. Language / Bahasa",
        "bahasa_label": "Select interface & coach language:",
        "bahasa_simpan": "Save Language",
        "bahasa_sukses": "Language updated!",
        "password_judul": "#### 5. Change PIN",
        "password_baru": "New PIN (6 digits)",
        "password_ulang": "Repeat new PIN",
        "btn_ganti_pin": "Change PIN",
        "pin_cocok": "PIN updated successfully!",
        "pin_tidak_cocok": "PINs do not match.",
        "hapus_judul": "#### ⚠️ Delete This Profile",
        "hapus_caption": "Warning: this permanently deletes all data and run history for this profile.",
        "hapus_konfirmasi": "Type the profile name to confirm deletion:",
        "btn_hapus": "🗑️ Delete Profile",
        "hapus_sukses": "Profile deleted.",
        "hapus_gagal": "Name doesn't match. Type the exact profile name.",
        "col_no": "No", "col_tanggal": "Date", "col_sesi": "Session", "col_zona": "Zone",
        "col_target": "Target km", "col_aktual": "Actual km", "col_status": "Status",
        "col_rpe": "RPE", "col_perasaan": "Feeling", "col_fase": "Phase", "col_minggu": "Weeks",
    },
}

LABEL_SESI = {
    "easy_run":   {"id": "🟢 Easy Run — lari santai pembangun aerobik",       "en": "🟢 Easy Run — steady aerobic builder"},
    "long_run":   {"id": "🔵 Long Run — lari panjang mingguan",               "en": "🔵 Long Run — weekly long effort"},
    "tempo":      {"id": "🟡 Tempo — lari ambang batas, cukup keras",          "en": "🟡 Tempo — threshold pace, comfortably hard"},
    "interval":   {"id": "🔴 Interval — sprint pendek berulang, intensitas tinggi", "en": "🔴 Interval — repeated fast efforts, high intensity"},
    "repetition": {"id": "🟣 Repetisi — pengulangan cepat, membangun kecepatan",    "en": "🟣 Repetition — fast reps, building speed"},
    "rest":       {"id": "⚪ Rest — hari istirahat",                           "en": "⚪ Rest — recovery day"},
}
LABEL_ZONA = {
    "E": {"id": "E (Easy/Aerobik)", "en": "E (Easy/Aerobic)"},
    "M": {"id": "M (Marathon pace)", "en": "M (Marathon pace)"},
    "T": {"id": "T (Threshold/Tempo)", "en": "T (Threshold/Tempo)"},
    "I": {"id": "I (Interval, VO2max)", "en": "I (Interval, VO2max)"},
    "R": {"id": "R (Repetisi, kecepatan)", "en": "R (Repetition, speed)"},
    None: {"id": "—", "en": "—"},
}


def t(key: str, lang: str = "id", **kwargs) -> str:
    """Ambil teks UI sesuai bahasa, dengan optional format args."""
    teks = UI.get(lang, UI["id"]).get(key, key)
    return teks.format(**kwargs) if kwargs else teks


def label_sesi(kode: str, lang: str = "id") -> str:
    return LABEL_SESI.get(kode, {}).get(lang, kode)


def label_zona(kode, lang: str = "id") -> str:
    return LABEL_ZONA.get(kode, LABEL_ZONA[None]).get(lang, "—")


# ─────────────────────────────────────────────
# KOMPONEN LOGO
# ─────────────────────────────────────────────
def render_logo(size: str = "normal"):
    """Render logo PaceY. size: 'normal' atau 'large'."""
    font_size = "28px" if size == "large" else "22px"
    icon_size = "46px" if size == "large" else "38px"
    icon_font = "24px" if size == "large" else "20px"
    st.markdown(f"""
    <div class="pacey-logo">
        <div class="pacey-logo-icon" style="width:{icon_size};height:{icon_size};font-size:{icon_font};">👟</div>
        <div class="pacey-logo-text" style="font-size:{font_size};">Pace<span>Y</span></div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LAYAR LOGIN
# ─────────────────────────────────────────────
def layar_pilih_user():
    lang = st.session_state.get("lang_login", "id")

    # Logo + pilihan bahasa
    col_logo, col_lang = st.columns([4, 1])
    with col_logo:
        render_logo("large")
        st.markdown(f"<p style='color:#8A9BB5;font-size:15px;margin-top:-12px;margin-bottom:24px;'>{t('siapa', lang)}</p>", unsafe_allow_html=True)
    with col_lang:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        pilihan_lang = st.selectbox(
            "🌐", ["🇮🇩 Indonesia", "🇬🇧 English"],
            index=0 if lang == "id" else 1,
            label_visibility="collapsed", key="login_lang_select"
        )
        lang_baru = "id" if "Indonesia" in pilihan_lang else "en"
        if lang_baru != lang:
            st.session_state["lang_login"] = lang_baru
            st.rerun()

    daftar = db.daftar_username()
    col_kiri, col_kanan = st.columns([2, 1])

    with col_kiri:
        if daftar:
            st.markdown(f"<p style='font-weight:600;color:#2C3E5A;font-size:13px;margin-bottom:6px;'>{t('profil_ada', lang).replace('**','')}</p>", unsafe_allow_html=True)
            pilihan = st.selectbox(
                "👤", daftar,
                format_func=lambda u: f"👤 {u.capitalize()}",
                label_visibility="collapsed", key="pilih_user"
            )
            pin_masuk = st.text_input(
                t("pin_placeholder", lang),
                type="password", max_chars=6,
                placeholder=t("pin_placeholder", lang),
                label_visibility="collapsed", key="pin_masuk"
            )
            if st.button(t("btn_masuk", lang), use_container_width=True):
                if not pin_masuk.isdigit() or len(pin_masuk) != 6:
                    st.warning(t("err_pin_format", lang))
                elif not db.cek_password(pilihan, pin_masuk):
                    st.error(t("err_pin_salah", lang))
                else:
                    bahasa_user = db.ambil_bahasa(pilihan)
                    st.session_state["username"] = pilihan
                    st.session_state["lang"] = bahasa_user
                    st.rerun()

    with col_kanan:
        st.markdown(f"<p style='font-weight:600;color:#2C3E5A;font-size:13px;margin-bottom:6px;'>{t('buat_baru', lang).replace('**','')}</p>", unsafe_allow_html=True)
        nama_baru = st.text_input(
            "username", placeholder=t("username_placeholder", lang),
            label_visibility="collapsed", key="input_nama_baru"
        )
        pin_baru = st.text_input(
            "pin", type="password", max_chars=6,
            placeholder=t("pin_placeholder", lang),
            label_visibility="collapsed", key="input_pin_baru"
        )
        if st.button(t("btn_buat", lang), use_container_width=True):
            nama_baru = nama_baru.strip().lower()
            if not nama_baru:
                st.warning(t("err_username_kosong", lang))
            elif not nama_baru.replace("_", "").isalnum():
                st.warning(t("err_username_format", lang))
            elif not pin_baru.isdigit() or len(pin_baru) != 6:
                st.warning(t("err_pin_format", lang))
            else:
                db.set_password(nama_baru, pin_baru)
                db.simpan_bahasa(nama_baru, lang)
                st.session_state["username"] = nama_baru
                st.session_state["lang"] = lang
                st.rerun()


# ─────────────────────────────────────────────
# CEK LOGIN
# ─────────────────────────────────────────────
if "username" not in st.session_state:
    layar_pilih_user()
    st.stop()

USERNAME = st.session_state["username"]
LANG = st.session_state.get("lang", db.ambil_bahasa(USERNAME))

# Load VDOT dari DB kalau session_state kosong
if "vdot" not in st.session_state:
    vdot_tersimpan = db.ambil_setting(USERNAME, "vdot")
    if vdot_tersimpan:
        st.session_state["vdot"] = float(vdot_tersimpan)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_judul, col_user = st.columns([4, 1])
with col_judul:
    render_logo()
with col_user:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button(f"👤 {USERNAME.capitalize()} {t('label_ganti', LANG)}", use_container_width=True):
        for k in ["username", "lang", "vdot"]:
            st.session_state.pop(k, None)
        st.rerun()

with open("periodization_rules.json") as f:
    rules = json.load(f)

tab_hari_ini, tab_pengaturan = st.tabs([t("tab_hari_ini", LANG), t("tab_pengaturan", LANG)])


# ====================================================================
# TAB 1: HARI INI
# ====================================================================
with tab_hari_ini:
    hari_ini_str = str(date.today())
    sesi_hari_ini = db.ambil_sesi_by_tanggal(USERNAME, hari_ini_str)

    if sesi_hari_ini is None:
        st.info(t("belum_ada_jadwal", LANG))
    else:
        st.subheader(f"{t('rencana_hari_ini', LANG)} — {hari_ini_str}")
        col1, col2, col3 = st.columns(3)
        col1.metric(t("jenis_sesi", LANG), label_sesi(sesi_hari_ini["session_type"], LANG).split("—")[0].strip())
        col2.metric(t("target_jarak", LANG), f"{sesi_hari_ini['planned_distance_km']} km")
        col3.metric(t("fase", LANG), f"{sesi_hari_ini['phase']} ({t('mgg', LANG)} {sesi_hari_ini['week_number']})")

        st.caption(label_sesi(sesi_hari_ini["session_type"], LANG))

        if sesi_hari_ini["status"] != "scheduled":
            st.success(f"{t('sudah_ditandai', LANG)}: **{sesi_hari_ini['status']}**")
        else:
            st.divider()
            st.markdown(t("log_sesi", LANG))
            with st.form("log_form"):
                status = st.radio(t("status", LANG), ["completed", "skipped"])
                jarak_aktual = st.number_input(
                    t("jarak_aktual", LANG), min_value=0.0,
                    value=float(sesi_hari_ini["planned_distance_km"] or 0.0), step=0.5
                )
                rpe = st.slider(t("rpe_label", LANG), 1, 10, 5)
                feeling = st.select_slider(t("perasaan", LANG), options=["easy", "moderate", "hard", "very_hard"])
                ada_nyeri = st.checkbox(t("ada_nyeri", LANG))
                lokasi_nyeri = st.text_input(t("lokasi_nyeri", LANG)) if ada_nyeri else None
                catatan = st.text_area(t("catatan", LANG))
                submitted = st.form_submit_button(t("simpan_log", LANG))

                if submitted:
                    db.catat_hasil_sesi(
                        USERNAME, sesi_hari_ini["id"], status=status, jarak_aktual=jarak_aktual,
                        rpe=rpe, feeling=feeling, ada_nyeri=ada_nyeri,
                        lokasi_nyeri=lokasi_nyeri, catatan=catatan
                    )
                    st.success(t("log_tersimpan", LANG))
                    st.rerun()

    st.divider()

    # ── JADWAL MINGGU INI (scheduled) ──
    st.subheader(t("jadwal_minggu", LANG))
    senin = date.today() - timedelta(days=date.today().weekday())
    minggu = date.today() + timedelta(days=6 - date.today().weekday())
    jadwal_minggu = db.ambil_jadwal_minggu_ini(USERNAME, str(senin), str(minggu))
    if jadwal_minggu:
        tampil = [
            {
                t("col_no", LANG): i + 1,
                t("col_tanggal", LANG): s["scheduled_date"],
                t("col_sesi", LANG): label_sesi(s["session_type"], LANG),
                t("col_zona", LANG): label_zona(s["zone"], LANG),
                t("col_target", LANG): s["planned_distance_km"],
            }
            for i, s in enumerate(jadwal_minggu)
        ]
        st.dataframe(tampil, hide_index=True, use_container_width=True)
    else:
        st.info(t("jadwal_kosong", LANG))

    st.divider()

    # ── RIWAYAT (completed/skipped) ──
    st.subheader(t("riwayat", LANG))
    riwayat = db.ambil_sesi_terakhir_logged(USERNAME, 10)
    if riwayat:
        riwayat_asc = list(reversed(riwayat))
        tampil_riwayat = [
            {
                t("col_no", LANG): i + 1,
                t("col_tanggal", LANG): r["scheduled_date"],
                t("col_sesi", LANG): label_sesi(r["session_type"], LANG),
                t("col_target", LANG): r["planned_distance_km"],
                t("col_aktual", LANG): r["actual_distance_km"],
                t("col_status", LANG): r["status"],
                t("col_rpe", LANG): r["rpe"],
                t("col_perasaan", LANG): r["feeling"],
            }
            for i, r in enumerate(riwayat_asc)
        ]
        st.dataframe(tampil_riwayat, hide_index=True, use_container_width=True)
        st.caption(t("riwayat_caption", LANG))
    else:
        st.info(t("riwayat_kosong", LANG))

    # ── COACHING INSIGHT ──
    st.divider()
    st.subheader(t("coach_title", LANG))

    def _bangun_fakta_lengkap() -> dict:
        fakta = {}
        if sesi_hari_ini:
            fakta["jadwal_hari_ini"] = {
                "tanggal": sesi_hari_ini["scheduled_date"],
                "jenis_sesi": sesi_hari_ini["session_type"],
                "zona": sesi_hari_ini.get("zone"),
                "target_km": sesi_hari_ini["planned_distance_km"],
                "fase": sesi_hari_ini.get("phase"),
                "minggu_ke": sesi_hari_ini.get("week_number"),
                "status": sesi_hari_ini["status"],
            }
            if sesi_hari_ini["status"] != "scheduled":
                fakta["jadwal_hari_ini"].update({
                    "aktual_km": sesi_hari_ini.get("actual_distance_km"),
                    "rpe": sesi_hari_ini.get("rpe"),
                    "perasaan": sesi_hari_ini.get("feeling"),
                    "ada_nyeri": bool(sesi_hari_ini.get("has_pain")),
                    "catatan": sesi_hari_ini.get("notes"),
                })
        else:
            fakta["jadwal_hari_ini"] = None

        fakta["riwayat_7_sesi_terakhir"] = [
            {
                "tanggal": r["scheduled_date"],
                "jenis": r["session_type"],
                "target_km": r["planned_distance_km"],
                "aktual_km": r["actual_distance_km"],
                "status": r["status"],
                "rpe": r["rpe"],
                "perasaan": r["feeling"],
            }
            for r in riwayat[:7]
        ]
        fakta["statistik"] = {
            "total_sesi_tercatat": len(riwayat),
            "rasio_skip_persen": round(db.hitung_rasio_skip(USERNAME) * 100, 1),
        }
        vdot = st.session_state.get("vdot")
        if vdot:
            zona_pace = vdot_calculator.hitung_zona_latihan(vdot)
            fakta["vdot_dan_pace"] = {
                "vdot": round(vdot, 1),
                "pace_easy_low": zona_pace["easy_low"],
                "pace_easy_high": zona_pace["easy_high"],
                "pace_marathon": zona_pace["marathon"],
                "pace_threshold": zona_pace["threshold"],
                "pace_interval": zona_pace["interval"],
                "pace_repetition": zona_pace["repetition"],
                "catatan": "pace dalam format mm:ss per km",
            }
        return fakta

    def _catatan_coach() -> str:
        if sesi_hari_ini is None:
            if LANG == "en":
                return "The runner has no schedule for today. Remind them to generate a schedule first."
            return "Pelari belum punya jadwal hari ini. Ingatkan untuk generate jadwal dulu."
        elif sesi_hari_ini["status"] == "scheduled":
            if LANG == "en":
                return (
                    "The runner has NOT logged today's session yet (status: 'scheduled'). "
                    "Explain in detail what they should do today: session type, distance, and the right pace "
                    "based on their zone and VDOT. Motivate them to get started."
                )
            return (
                "Pelari BELUM log sesi hari ini (status masih 'scheduled'). "
                "Jelaskan sesi yang harus dijalani hari ini secara detail: jenis sesi, "
                "berapa km, dan pace yang tepat sesuai zona dan VDOT yang ada. "
                "Motivasi mereka untuk segera mulai."
            )
        elif sesi_hari_ini["status"] == "skipped":
            if LANG == "en":
                return (
                    "The runner SKIPPED today's session. Give supportive, non-judgmental feedback. "
                    "Remind them that rest is sometimes needed, but consistency matters for long-term progress."
                )
            return (
                "Pelari MEN-SKIP sesi hari ini. Berikan feedback yang suportif, "
                "jangan menghakimi. Ingatkan bahwa istirahat kadang perlu, "
                "tapi konsistensi penting untuk progres jangka panjang."
            )
        else:
            if LANG == "en":
                return (
                    "The runner completed today's session. Give feedback based on actual vs target distance, "
                    "RPE, and how they felt."
                )
            return (
                "Pelari sudah menyelesaikan sesi hari ini. Berikan feedback "
                "berdasarkan data aktual vs target, RPE, dan perasaan yang dilaporkan."
            )

    tombol_label = t("coach_btn_feedback" if sesi_hari_ini else "coach_btn_panduan", LANG)
    if st.button(tombol_label):
        try:
            from ollama_coach_bridge import minta_penjelasan_coach
            fakta = _bangun_fakta_lengkap()
            with st.spinner(t("coach_spinner", LANG)):
                insight = minta_penjelasan_coach(
                    fakta,
                    catatan_singkat=_catatan_coach(),
                    username=USERNAME,
                    bahasa=LANG,
                )
            st.info(insight)
        except Exception as e:
            st.warning(f"Ollama error: `{e}`\n\n{t('coach_ollama_err', LANG)}")


# ====================================================================
# TAB 2: PENGATURAN
# ====================================================================
with tab_pengaturan:
    st.subheader(f"{t('pengaturan_judul', LANG)}: 👤 {USERNAME.capitalize()}")

    # ── VDOT ──
    st.markdown(t("vdot_judul", LANG))
    col1, col2 = st.columns(2)
    with col1:
        jarak_km = st.number_input(t("vdot_jarak", LANG), min_value=1.0, value=5.0, step=0.5)
    with col2:
        waktu_menit = st.number_input(t("vdot_waktu", LANG), min_value=1.0, value=25.0, step=0.5)

    vdot_terkini = st.session_state.get("vdot", None)
    if vdot_terkini:
        st.caption(f"{t('vdot_tersimpan', LANG)}: **{vdot_terkini:.1f}**")
    if st.button(t("btn_hitung_vdot", LANG)):
        vdot_terkini = vdot_calculator.hitung_vdot(jarak_km * 1000, waktu_menit)
        st.session_state["vdot"] = vdot_terkini
        db.simpan_setting(USERNAME, "vdot", str(vdot_terkini))
        zona = vdot_calculator.hitung_zona_latihan(vdot_terkini)
        st.success(t("vdot_sukses", LANG, v=vdot_terkini))
        zona_tampil = [{"No": i+1, "Zona": nama, "Pace /km": pace} for i, (nama, pace) in enumerate(zona.items())]
        st.dataframe(zona_tampil, hide_index=True)

    st.divider()

    # ── KELAYAKAN ──
    st.markdown(t("kelayakan_judul", LANG))
    jarak_target = st.selectbox(t("kelayakan_target", LANG), ["5k", "10k", "half_marathon", "marathon"])
    minggu_tersedia = st.number_input(t("kelayakan_minggu", LANG), min_value=1, value=24)

    if st.button(t("btn_cek", LANG)):
        minimum = rules["guardrail_kelayakan_target"][f"minimal_minggu_dari_nol_ke_{jarak_target}"]
        if minggu_tersedia >= minimum:
            st.success(t("kelayakan_ok", LANG, min=minimum, ada=minggu_tersedia))
            breakdown = schedule_generator.ringkasan_fase(int(minggu_tersedia), "race")
            fase_tampil = [{"No": i+1, t("col_fase", LANG): f, t("col_minggu", LANG): w} for i, (f, w) in enumerate(breakdown.items())]
            st.write(t("fase_breakdown", LANG))
            st.dataframe(fase_tampil, hide_index=True)
        else:
            st.warning(t("kelayakan_kurang", LANG, min=minimum, ada=minggu_tersedia))
            urutan = ["5k", "10k", "half_marathon", "marathon"]
            alternatif = [j for j in urutan if rules["guardrail_kelayakan_target"][f"minimal_minggu_dari_nol_ke_{j}"] <= minggu_tersedia]
            if alternatif:
                st.info(t("kelayakan_alternatif", LANG, ada=minggu_tersedia, alt=alternatif[-1]))
            else:
                st.info(t("kelayakan_terlalu_pendek", LANG))

    st.divider()

    # ── GENERATE JADWAL ──
    st.markdown(t("jadwal_judul", LANG))
    st.caption(t("jadwal_caption", LANG))
    tujuan_opts = {"race": "race", "maintenance": "maintenance"}
    tujuan = st.radio(t("tujuan", LANG), list(tujuan_opts.keys()))
    total_minggu_jadwal = st.number_input(t("total_minggu", LANG), min_value=1, value=12)
    volume_awal = st.number_input(t("volume_awal", LANG), min_value=0.0, value=15.0, step=1.0)
    hari_per_minggu = st.selectbox(t("hari_per_minggu", LANG), [3, 4, 5, 6, 7], index=1)

    if st.button(t("btn_generate", LANG)):
        db.hapus_jadwal_belum_dijalani(USERNAME, str(date.today()))
        jadwal_baru = schedule_generator.generate_jadwal(
            tanggal_mulai=date.today(),
            total_minggu=int(total_minggu_jadwal),
            tujuan=tujuan,
            volume_awal_km=volume_awal,
            hari_per_minggu=hari_per_minggu,
        )
        db.simpan_jadwal(USERNAME, jadwal_baru)
        st.success(t("jadwal_sukses", LANG, n=len(jadwal_baru)))

    st.divider()

    # ── PILIHAN BAHASA ──
    st.markdown(t("bahasa_judul", LANG))
    st.caption(t("bahasa_label", LANG))
    lang_options = ["🇮🇩 Indonesia", "🇬🇧 English"]
    lang_idx = 0 if LANG == "id" else 1
    lang_pilihan = st.radio("🌐", lang_options, index=lang_idx, label_visibility="collapsed", horizontal=True)
    lang_baru = "id" if "Indonesia" in lang_pilihan else "en"
    if st.button(t("bahasa_simpan", LANG)):
        db.simpan_bahasa(USERNAME, lang_baru)
        st.session_state["lang"] = lang_baru
        st.success(t("bahasa_sukses", LANG))
        st.rerun()

    st.divider()

    # ── GANTI PIN ──
    st.markdown(t("password_judul", LANG))
    pin_baru_1 = st.text_input(t("password_baru", LANG), type="password", max_chars=6, key="pin1")
    pin_baru_2 = st.text_input(t("password_ulang", LANG), type="password", max_chars=6, key="pin2")
    if st.button(t("btn_ganti_pin", LANG)):
        if not pin_baru_1.isdigit() or len(pin_baru_1) != 6:
            st.warning(t("err_pin_format", LANG))
        elif pin_baru_1 != pin_baru_2:
            st.error(t("pin_tidak_cocok", LANG))
        else:
            db.set_password(USERNAME, pin_baru_1)
            st.success(t("pin_cocok", LANG))

    st.divider()

    # ── HAPUS PROFIL ──
    st.markdown(t("hapus_judul", LANG))
    st.caption(t("hapus_caption", LANG))
    konfirmasi = st.text_input(t("hapus_konfirmasi", LANG), placeholder=USERNAME)
    if st.button(t("btn_hapus", LANG), type="secondary"):
        if konfirmasi.strip().lower() == USERNAME:
            import os
            db_file = f"running_{USERNAME}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
            for k in ["username", "lang", "vdot"]:
                st.session_state.pop(k, None)
            st.success(t("hapus_sukses", LANG))
            st.rerun()
        else:
            st.error(t("hapus_gagal", LANG))
