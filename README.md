# 🌿 Javenture — Explore Jogja, Your Way!

## 1. Deskripsi Singkat

**Javenture** merupakan aplikasi web pariwisata berbasis Flask yang dirancang untuk membantu pengguna menjelajahi destinasi wisata di Yogyakarta. Aplikasi ini mengintegrasikan pengolahan data, Machine Learning, sistem rekomendasi, dan chatbot untuk memberikan informasi serta membantu pengguna merencanakan perjalanan wisata dengan lebih mudah.

## 2. Fitur Javenture

| Fitur | Deskripsi |
|---|---|
| **Tourism Dashboard** | Menampilkan informasi destinasi wisata populer dan persebaran lokasi wisata di Yogyakarta melalui visualisasi data. |
| **Sentiment Analysis** | Menganalisis ulasan wisatawan untuk mengklasifikasikan sentimen positif, negatif, dan netral menggunakan TF-IDF dan Logistic Regression. |
| **Crowd Prediction** | Memperkirakan tingkat popularitas atau keramaian destinasi berdasarkan hari dan jam kunjungan menggunakan Random Forest Regressor. |
| **Travel Planner** | Memberikan rekomendasi destinasi berdasarkan minat dan anggaran pengguna, serta menyusun urutan perjalanan menggunakan Nearest Neighbor dan perhitungan jarak Haversine. |
| **Javenture Assistant** | Chatbot untuk membantu pengguna mendapatkan informasi wisata menggunakan pendekatan Rule-Based dan Information Retrieval. |

## 3. Struktur Folder

```text
javenture-finalproject/
│
├── data/                   # Dataset pariwisata
├── models/                 # Model Machine Learning
├── notebooks/              # Notebook preprocessing dan training
├── scripts/                # Script pengolahan data
├── static/                 # CSS, JavaScript, dan gambar
├── templates/              # HTML templates
├── theme/                  # File pendukung tampilan
│
├── app.py                  # Main Flask application
├── chatbot_engine.py       # Chatbot processing engine
├── fetch_besttime.py       # Pengambilan data popularitas
├── requirements.txt        # Daftar dependencies
└── README.md
```

## 4. Data Source

Javenture menggunakan beberapa sumber data untuk mendukung pengembangan fitur:

- **Dataset Destinasi Wisata:** Dataset publik yang berisi informasi destinasi wisata di Yogyakarta, seperti nama tempat, kategori, rating, harga tiket, koordinat, jumlah penilaian, dan deskripsi.
- **Dataset Ulasan Wisata:** Dataset ulasan wisata yang digunakan untuk preprocessing dan pelatihan model analisis sentimen.
- **Data Popular Times:** Data historis popularitas destinasi yang dikumpulkan menggunakan BestTime API untuk pengembangan model prediksi keramaian.

## 5. Setup dan Instalasi

1. Clone repository:

```bash
git clone https://github.com/retisalyaaa/javenture-finalproject.git
```

2. Masuk ke direktori project:

```bash
cd javenture-finalproject
```

3. Buat virtual environment:

```bash
python -m venv venv
```

4. Aktifkan virtual environment:

**Windows:**

```powershell
.\venv\Scripts\Activate.ps1
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Jalankan aplikasi:

```bash
python app.py
```

7. Buka aplikasi melalui browser:

```text
http://127.0.0.1:5000
```

## 6. 👩‍💻 Developer

**Retisalya**

Mahasiswa Teknologi Informasi yang tertarik pada pengembangan aplikasi web, pengolahan data, dan teknologi digital.

🔗 GitHub: [@retisalyaaa](https://github.com/retisalyaaa)

---

⭐ Jika project ini menarik, jangan lupa berikan star pada repository ini!
