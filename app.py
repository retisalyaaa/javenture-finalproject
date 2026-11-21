
"""Aplikasi utama Javenture."""

import json
import os
import pandas as pd

from pathlib import Path
from chatbot_engine import ChatbotEngine, load_theme
from pathlib import Path
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

app = Flask(__name__)

# Memuat konfigurasi chatbot Javenture
BASE_DIR = Path(__file__).resolve().parent

CHATBOT_FILE = BASE_DIR / "theme" / "faq.json"

chatbot_data = load_theme(CHATBOT_FILE)

chatbot_engine = ChatbotEngine(chatbot_data)

# Membaca dataset.
def baca_csv(nama_file):
    lokasi = DATA / nama_file

    if not lokasi.exists():
        raise FileNotFoundError(
            f"{nama_file} belum tersedia. "
            "Jalankan scripts/00_import_kaggle.py terlebih dahulu."
        )

    return pd.read_csv(lokasi)

tempat = baca_csv("tempat.csv")
rating = baca_csv("rating_interactions.csv")
pengguna = baca_csv("users_kaggle.csv")


# Foto destinasi berdasarkan nama atau kategori.
FOTO_DESTINASI = {
    "tamansari water castle":
        "https://commons.wikimedia.org/wiki/Special:FilePath/Taman%20Sari%2C%20Yogyakarta.jpg",

    "budaya dan sejarah":
        "https://commons.wikimedia.org/wiki/Special:FilePath/Yogyakarta%20Indonesia%20Prambanan-temple-complex-05.jpg",

    "alam":
        "https://commons.wikimedia.org/wiki/Special:FilePath/Bukit%20Bintang%20Yogyakarta.jpg",

    "pantai":
        "https://commons.wikimedia.org/wiki/Special:FilePath/Perahu%20di%20Pantai%20Drini.jpg",
}

# HALAMAN DASHBOARD
@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/dashboard")
def data_dashboard():
    """Mengirim rekomendasi destinasi dan data peta."""

    # Urutkan destinasi berdasarkan jumlah penilaian.
    populer = tempat.nlargest(
        10, "jumlah_penilaian"
    ).copy()

    daftar_populer = []

    for _, baris in populer.iterrows():
        kategori = str(baris["kategori"]).lower()
        nama = str(baris["nama"]).lower()

        # Cari foto berdasarkan nama destinasi.
        foto = FOTO_DESTINASI.get(nama)

        # Jika tidak ada, gunakan foto berdasarkan kategori.
        if not foto:
            foto = FOTO_DESTINASI.get(
                kategori,
                "/static/img/hero-jogja.png"
            )

        daftar_populer.append({
            "nama": baris["nama"],
            "kategori": baris["kategori"],
            "rating_tempat": float(baris["rating_tempat"]),
            "jumlah_penilaian": int(baris["jumlah_penilaian"]),
            "foto": foto
        })

    # Siapkan data koordinat untuk peta.
    kolom_peta = tempat[[
        "nama",
        "kategori",
        "latitude",
        "longitude",
        "rating_tempat"
    ]].copy()

    kolom_peta = kolom_peta.where(
        pd.notna(kolom_peta), None
    )

    return jsonify({
        "populer": daftar_populer,
        "peta": kolom_peta.to_dict(orient="records")
    })


# HALAMAN ANALISIS SENTIMEN
@app.route("/sentiment")
def sentiment():
    return render_template("sentiment.html")


# HALAMAN PREDIKSI KERAMAIAN
@app.route("/crowd")
def crowd():
    return render_template("crowd.html")


# HALAMAN PERENCANAAN TRAVELING
@app.route("/planner")
def planner():
    return render_template("planner.html")


# Halaman chatbot
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():

    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "error": "Pesan tidak boleh kosong."
        }), 400

    if len(message) > 500:
        return jsonify({
            "error": "Pesan maksimal 500 karakter."
        }), 400

    result = chatbot_engine.reply(message)

    return jsonify(result)

@app.route("/api/chatbot-config")
def chatbot_config():

    return jsonify({
        "greeting": chatbot_data["greeting"],
        "suggestions": chatbot_data["suggestions"],
        "bot_name": chatbot_data["bot_name"],
        "avatar": chatbot_data["avatar"]
    })


if __name__ == "__main__":
    app.run(debug=True)