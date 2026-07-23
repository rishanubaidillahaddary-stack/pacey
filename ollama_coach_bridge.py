"""
Coach bridge — versi Groq API (menggantikan Ollama lokal).
Model: llama3-8b-8192 (gratis di Groq, lebih pintar dari llama3.2:3b lokal).
API key diambil dari environment variable GROQ_API_KEY.
"""

import os
import json
import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

GLOSARIUM_SESI = {
    "easy_run": {
        "id": "lari santai/pelan untuk membangun daya tahan aerobik tanpa kelelahan berlebih",
        "en": "easy/slow run to build aerobic endurance without excessive fatigue",
    },
    "long_run": {
        "id": "lari terjauh dalam seminggu, pace tetap santai, melatih daya tahan jangka panjang",
        "en": "the longest run of the week at an easy pace, building long-term endurance",
    },
    "tempo": {
        "id": "lari di ambang batas (threshold) — terasa 'nyaman tapi berat', melatih tubuh membuang asam laktat lebih efisien",
        "en": "threshold run — 'comfortably hard' effort, training the body to clear lactate efficiently",
    },
    "interval": {
        "id": "lari cepat berulang dengan jeda istirahat, melatih kapasitas jantung-paru (VO2max)",
        "en": "repeated fast efforts with rest intervals, training cardiovascular capacity (VO2max)",
    },
    "repetition": {
        "id": "lari sangat cepat jarak pendek dengan istirahat penuh, melatih kecepatan & ekonomi lari",
        "en": "very fast short efforts with full recovery, training speed and running economy",
    },
    "rest": {
        "id": "hari istirahat penuh, bagian penting dari pemulihan tubuh",
        "en": "full rest day, an essential part of recovery",
    },
}


def _muat_glosarium_fase() -> dict:
    try:
        with open("periodization_rules.json") as f:
            rules = json.load(f)
        hasil = {}
        for grup in ("race_goal_periodization", "maintenance_goal_periodization"):
            for fase in rules[grup]["phases"]:
                hasil[fase["name"]] = fase["fokus"]
        return hasil
    except (FileNotFoundError, KeyError):
        return {}


def _kumpulkan_konteks_relevan(fakta: dict, bahasa: str = "id") -> str:
    teks_fakta = json.dumps(fakta, ensure_ascii=False).lower()
    glosarium_fase = _muat_glosarium_fase()
    baris = []

    for istilah, definisi_dict in GLOSARIUM_SESI.items():
        if istilah in teks_fakta:
            definisi = definisi_dict.get(bahasa, definisi_dict["id"])
            label = "Session" if bahasa == "en" else "Sesi"
            baris.append(f"- {label} '{istilah}': {definisi}")

    for fase, definisi in glosarium_fase.items():
        if fase in teks_fakta:
            label = "Phase" if bahasa == "en" else "Fase"
            baris.append(f"- {label} '{fase}': {definisi}")

    if not baris:
        return ""

    header = (
        "TERMS IN THE DATA (use these definitions only):"
        if bahasa == "en"
        else "ISTILAH YANG MUNCUL DI DATA (pakai definisi ini saja):"
    )
    return header + "\n" + "\n".join(baris)


def minta_penjelasan_coach(
    fakta_terkomputasi: dict,
    catatan_singkat: str = "",
    username: str = "kamu",
    bahasa: str = "id",
) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "(GROQ_API_KEY belum diset di secrets.)" if bahasa == "id" else "(GROQ_API_KEY not set in secrets.)"

    konteks = _kumpulkan_konteks_relevan(fakta_terkomputasi, bahasa)
    nama = username.capitalize()

    if bahasa == "en":
        prompt = f"""You are a friendly and supportive running coach assistant speaking to a recreational runner named {nama}.

COMPUTED FACTS (do not change or add numbers):
{json.dumps(fakta_terkomputasi, ensure_ascii=False, indent=2)}

{konteks}

{catatan_singkat}

Give a short insight (max 4-5 sentences) in natural, motivating English. Address {nama} by name at least once. Only use pace/distance numbers already in the data."""
    else:
        prompt = f"""Kamu adalah asisten pelatih lari yang ramah dan suportif, berbicara kepada pelari bernama {nama}.

FAKTA YANG SUDAH DIHITUNG (jangan diubah atau tambah angka baru):
{json.dumps(fakta_terkomputasi, ensure_ascii=False, indent=2)}

{konteks}

{catatan_singkat}

Berikan insight singkat (maksimal 4-5 kalimat) dalam bahasa Indonesia yang natural dan memotivasi. Sapa {nama} dengan namanya minimal sekali. Jangan sebut angka pace/jarak selain yang sudah ada di data."""

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.4,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "(Tidak bisa konek ke Groq API.)" if bahasa == "id" else "(Cannot connect to Groq API.)"
    except requests.exceptions.Timeout:
        return "(Groq API timeout — coba lagi.)" if bahasa == "id" else "(Groq API timed out — try again.)"
    except Exception as e:
        return f"(Error: {e})"
