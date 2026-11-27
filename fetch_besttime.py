
import os
import requests
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("BESTTIME_PRIVATE_KEY")
PUBLIC_KEY = os.getenv("BESTTIME_PUBLIC_KEY")

BASE_URL = "https://besttime.app/api/v1"

# Destinasi yang akan diambil datanya

destinasi = {
    "Malioboro": "Jalan Malioboro, Yogyakarta, Indonesia",
    "Candi Prambanan": "Prambanan Temple, Sleman, Yogyakarta, Indonesia",
    "Obelix Sea View": "Obelix Sea View, Bantul, Yogyakarta, Indonesia",
    "Gembira Loka": "Gembira Loka Zoo, Yogyakarta, Indonesia",
    "Taman Pintar": "Taman Pintar Yogyakarta, Indonesia",
    "Bukit Bintang": "Bukit Bintang, Patuk, Gunungkidul, Yogyakarta, Indonesia",
    "Taman Sari": "Taman Sari, Yogyakarta, Indonesia",
    "Keraton Yogyakarta": "Keraton Ngayogyakarta Hadiningrat, Yogyakarta, Indonesia",
    "Hutan Pinus": "Hutan Pinus Mangunan, Bantul, Yogyakarta, Indonesia",
    "HeHa Ocean View": "HeHa Ocean View, Gunungkidul, Yogyakarta, Indonesia"
}


def ambil_forecast(nama, alamat):

    print(f"\nMengambil forecast: {nama}")

    # 1. Membuat forecast baru menggunakan Private Key
    url_forecast = f"{BASE_URL}/forecasts"

    params_forecast = {
        "api_key_private": PRIVATE_KEY,
        "venue_name": nama,
        "venue_address": alamat
    }

    response = requests.post(
        url_forecast,
        params=params_forecast,
        timeout=60
    )

    data_forecast = response.json()

    if data_forecast.get("status") != "OK":
        print("Forecast gagal!")

        print("Pesan:", data_forecast.get("message"))

        venue_info = data_forecast.get("venue_info", {})

        print("Tempat ditemukan:", venue_info.get("venue_name"))
        print("Venue ID:", venue_info.get("venue_id"))

        print("Kode error:",
            data_forecast.get("resolution_info", {}).get("code"))

        return []

    # 2. Mengambil ID tempat dari hasil forecast
    venue_info = data_forecast["venue_info"]
    venue_id = venue_info["venue_id"]

    print("Tempat ditemukan:", venue_info["venue_name"])
    print("Venue ID:", venue_id)

    # 3. Mengambil data popular time menggunakan Public Key
    url_week = f"{BASE_URL}/forecasts/week/raw2"

    params_week = {
        "api_key_public": PUBLIC_KEY,
        "venue_id": venue_id
    }

    response_week = requests.get(
        url_week,
        params=params_week,
        timeout=60
    )

    data_week = response_week.json()

    if data_week.get("status") != "OK":
        print("Gagal mengambil data:", data_week)
        return []

    # 4. Mengubah data mingguan menjadi baris per jam
    hasil = []

    week_raw = data_week["analysis"]["week_raw"]

    for hari_data in week_raw:

        hari = hari_data["day_int"]
        data_jam = hari_data["day_raw"]

        for index, skor in enumerate(data_jam):

            # BestTime memulai hari dari pukul 06.00
            jam = (6 + index) % 24

            # Jam 00.00-05.00 masuk ke hari berikutnya
            hari_asli = (hari + (1 if index >= 18 else 0)) % 7

            hasil.append({
                "nama_wisata": nama,
                "hari": hari_asli,
                "jam": jam,
                "popularity_score": skor
            })

    return hasil

# 5. Mengambil data destinasi
semua_data = []

for nama, alamat in destinasi.items():

    data = ambil_forecast(nama, alamat)
    semua_data.extend(data)

# 6. Menyimpan data ke CSV
if semua_data:

    df = pd.DataFrame(semua_data)

    os.makedirs("data", exist_ok=True)

    df.to_csv(
        "data/crowd_raw.csv",
        index=False
    )

    print("\nBerhasil menyimpan data!")
    print(df.head(10))
    print("\nTotal data:", len(df))

else:
    print("\nBelum ada data yang berhasil diambil.")