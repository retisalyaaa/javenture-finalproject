"""Aplikasi dashboard utama Javenture."""
from pathlib import Path
import pandas as pd
from flask import Flask, jsonify, render_template

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
app = Flask(__name__)


def baca_csv(nama_file):
    """Membaca file CSV dari folder data."""
    lokasi = DATA / nama_file
    if not lokasi.exists():
        raise FileNotFoundError(
            f"{nama_file} belum tersedia. Jalankan: python scripts/00_import_kaggle.py"
        )
    return pd.read_csv(lokasi)


# Data dibaca sekali ketika aplikasi dijalankan.
tempat = baca_csv("tempat.csv")
rating = baca_csv("rating_interactions.csv")
pengguna = baca_csv("users_kaggle.csv")


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/dashboard")
def data_dashboard():
    """Mengirim ringkasan dan data visualisasi ke halaman dashboard."""
    ringkasan = {
        "total_destinasi": int(tempat["place_id"].nunique()),
        "total_kategori": int(tempat["kategori"].nunique()),
        "rata_rating": round(float(tempat["rating_tempat"].mean()), 2),
        "total_penilaian": int(len(rating)),
        "total_pengguna": int(pengguna["User_Id"].nunique()),
    }

    # Destinasi populer dihitung dari jumlah rating pada dataset Kaggle.
    populer = tempat.nlargest(10, "jumlah_penilaian")[[
        "nama", "jumlah_penilaian", "rating_tempat"
    ]]

    kategori = (
        tempat.groupby("kategori").size()
        .sort_values(ascending=False)
        .rename_axis("kategori").reset_index(name="jumlah")
    )

    sebaran_rating = (
        tempat.assign(kelompok_rating=pd.cut(
            tempat["rating_tempat"],
            bins=[0, 3, 3.5, 4, 4.5, 5.01],
            labels=["≤ 3,0", "3,1–3,5", "3,6–4,0", "4,1–4,5", "4,6–5,0"]
        ))
        .groupby("kelompok_rating", observed=False).size()
        .rename_axis("rentang").reset_index(name="jumlah")
    )

    kolom_peta = tempat[[
        "nama", "kategori", "latitude", "longitude", "rating_tempat", "harga_tiket"
    ]].copy()

    return jsonify({
        "ringkasan": ringkasan,
        "populer": populer.to_dict(orient="records"),
        "kategori": kategori.to_dict(orient="records"),
        "rating": sebaran_rating.to_dict(orient="records"),
        "peta": kolom_peta.to_dict(orient="records"),
    })


if __name__ == "__main__":
    app.run(debug=True)
