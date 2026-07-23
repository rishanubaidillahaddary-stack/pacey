"""
Coach bridge — versi Groq API.
Model: llama3-8b-8192
"""

import os
import json
import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"


def minta_penjelasan_coach(
    fakta_terkomputasi: dict,
    catatan_singkat: str = "",
    username: str = "kamu",
    bahasa: str = "id",
) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY belum diset." if bahasa == "id" else "GROQ_API_KEY not set."

    nama = username.capitalize()

    # Ringkas fakta supaya tidak melebihi token limit
    fakta_ringkas = {
        "jadwal_hari_ini": fakta_terkomputasi.get("jadwal_hari_ini"),
        "statistik": fakta_terkomputasi.get("statistik"),
        "vdot_dan_pace": fakta_terkomputasi.get("vdot_dan_pace"),
        "riwayat_singkat": fakta_terkomputasi.get("riwayat_7_sesi_terakhir", [])[:3],
    }

    if bahasa == "en":
        system = "You are a friendly running coach. Give short, motivating feedback based only on the data provided. Do not invent numbers."
        user = f"""Runner's name: {nama}

Data:
{json.dumps(fakta_ringkas, ensure_ascii=False)}

Instruction: {catatan_singkat}

Write 3-4 sentences of personalized coaching feedback in English. Use {nama}'s name once."""
    else:
        system = "Kamu adalah pelatih lari yang ramah. Berikan feedback singkat dan memotivasi berdasarkan data yang diberikan saja. Jangan mengarang angka."
        user = f"""Nama pelari: {nama}

Data:
{json.dumps(fakta_ringkas, ensure_ascii=False)}

Instruksi: {catatan_singkat}

Tulis 3-4 kalimat feedback coaching dalam bahasa Indonesia. Gunakan nama {nama} sekali."""

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": 200,
                "temperature": 0.5,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "Tidak bisa konek ke Groq." if bahasa == "id" else "Cannot connect to Groq."
    except requests.exceptions.Timeout:
        return "Groq timeout, coba lagi." if bahasa == "id" else "Groq timed out, try again."
    except Exception as e:
        return f"Error: {e}"
