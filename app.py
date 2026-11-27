
"""Aplikasi utama Javenture."""

import json
import os
import re
import joblib
import pandas as pd

from pathlib import Path
from chatbot_engine import ChatbotEngine, load_theme
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

app = Flask(__name__)

# Memuat model analisis sentimen
MODEL_PATH = ROOT / "models" / "model_sentiment.pkl"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model sentiment tidak ditemukan. "
        "Pastikan model_sentiment.pkl berada di folder model."
    )

sentiment_model = joblib.load(MODEL_PATH)

# Memuat model prediksi keramaian
CROWD_MODEL_PATH = ROOT / "models" / "model_crowd.pkl"

if not CROWD_MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model crowd tidak ditemukan. "
        "Pastikan model_crowd.pkl berada di folder models."
    )

crowd_model = joblib.load(CROWD_MODEL_PATH)

# Mengambil daftar destinasi yang dikenal model
crowd_destinations = (
    crowd_model
    .named_steps["preprocessing"]
    .named_transformers_["destinasi"]
    .categories_[0]
    .tolist()
)

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
    destinations = sorted(
        tempat["nama"].dropna().astype(str).unique().tolist()
    )

    return render_template(
        "sentiment.html",
        destinations=destinations
    )

# MEMBERSIHKAN TEKS REVIEW
def clean_sentiment_text(text):
    text = text.lower()

    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# API ANALISIS SENTIMEN
@app.route("/api/sentiment", methods=["POST"])
def predict_sentiment():

    data = request.get_json(silent=True) or {}

    review = str(data.get("review", "")).strip()
    destination = str(data.get("destination", "")).strip()

    # Validasi input
    if not destination or not review:
        return jsonify({
            "success": False,
            "message": "Destinasi dan review wajib diisi."
        }), 400

    if len(review) < 10:
        return jsonify({
            "success": False,
            "message": "Review minimal 10 karakter."
        }), 400

    if len(review) > 1000:
        return jsonify({
            "success": False,
            "message": "Review maksimal 1000 karakter."
        }), 400

    # Memastikan destinasi tersedia
    daftar_destinasi = tempat["nama"].dropna().astype(str).unique()

    if destination not in daftar_destinasi:
        return jsonify({
            "success": False,
            "message": "Destinasi tidak ditemukan."
        }), 400

    try:
        # Preprocessing
        cleaned_review = clean_sentiment_text(review)

        # Prediksi sentimen
        prediction = sentiment_model.predict([cleaned_review])[0]

        # Mengambil probabilitas setiap kelas
        probabilities = sentiment_model.predict_proba(
            [cleaned_review]
        )[0]

        classes = sentiment_model.named_steps[
            "classifier"
        ].classes_

        scores = {
            label: round(float(score) * 100, 2)
            for label, score in zip(classes, probabilities)
        }

        return jsonify({
            "success": True,
            "destination": destination,
            "review": review,
            "sentiment": prediction,
            "probability": scores[prediction],
            "scores": scores
        })

    except Exception as error:
        app.logger.exception("Gagal melakukan analisis sentimen")

        return jsonify({
            "success": False,
            "message": "Terjadi kesalahan saat menganalisis review."
        }), 500

# HALAMAN PREDIKSI KERAMAIAN
@app.route("/crowd")
def crowd():
    return render_template(
        "crowd.html",
        destinations=crowd_destinations
    )


# API PREDIKSI KERAMAIAN
@app.route("/api/crowd", methods=["POST"])
def predict_crowd():

    data = request.get_json(silent=True) or {}

    destination = str(data.get("destination", "")).strip()
    visit_date = str(data.get("visitDate", "")).strip()
    visit_time = str(data.get("visitTime", "")).strip()

    # Validasi input
    if not destination or not visit_date or not visit_time:
        return jsonify({
            "success": False,
            "message": "Destinasi, tanggal, dan jam wajib diisi."
        }), 400

    if destination not in crowd_destinations:
        return jsonify({
            "success": False,
            "message": "Destinasi tidak tersedia dalam model."
        }), 400

    try:
        # Mengubah tanggal menjadi objek date
        tanggal = datetime.strptime(
            visit_date, "%Y-%m-%d"
        ).date()

        # Mengubah jam menjadi angka
        jam = datetime.strptime(
            visit_time, "%H:%M"
        ).hour

        # Mengambil kode hari: Senin = 0, Minggu = 6
        hari = tanggal.weekday()

        # Menentukan apakah tanggal termasuk weekend
        is_weekend = int(hari in [5, 6])

        # Menyiapkan input sesuai fitur training
        input_data = pd.DataFrame([{
            "nama_wisata": destination,
            "hari": hari,
            "jam": jam,
            "is_weekend": is_weekend
        }])

        # Melakukan prediksi
        prediction = float(
            crowd_model.predict(input_data)[0]
        )

        prediction = max(0, min(100, prediction))
        prediction = round(prediction, 2)

        # Mengelompokkan tingkat keramaian
        if prediction <= 30:
            level = "Low"
            description = "Keramaian relatif rendah. Waktu ini berpotensi lebih nyaman untuk berkunjung."

        elif prediction <= 60:
            level = "Medium"
            description = "Keramaian tergolong sedang. Pertimbangkan waktu kunjunganmu."

        else:
            level = "High"
            description = "Keramaian relatif tinggi. Bersiaplah menghadapi kondisi yang lebih ramai."

        return jsonify({
            "success": True,
            "destination": destination,
            "visit_date": visit_date,
            "visit_day": tanggal.strftime("%A"),
            "visit_time": visit_time,
            "popularity_score": prediction,
            "crowd_level": level,
            "description": description
        })

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Format tanggal atau jam tidak valid."
        }), 400

    except Exception:
        app.logger.exception("Gagal melakukan prediksi keramaian")

        return jsonify({
            "success": False,
            "message": "Terjadi kesalahan saat melakukan prediksi."
        }), 500


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