
import json
import random
import re
import csv
from pathlib import Path
from difflib import SequenceMatcher


THRESHOLD = 0.45

NORMALISASI = {
    "gmn": "bagaimana",
    "gimana": "bagaimana",
    "gmna": "bagaimana",
    "brp": "berapa",
    "ga": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
    "tdk": "tidak",
    "udh": "sudah",
    "udah": "sudah",
    "utk": "untuk",
    "dgn": "dengan",
    "yg": "yang",
    "bs": "bisa",
    "makasi": "makasih"
}

STOPWORDS = {
    "yang", "di", "ke", "dari", "itu", "ini", "dong",
    "deh", "ya", "sih", "aku", "saya", "kamu", "apa",
    "aja", "nih", "tuh", "dan", "atau", "untuk",
    "dengan", "kalau"
}


def load_theme(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def preprocess(text):
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    tokens = []

    for word in text.split():
        word = NORMALISASI.get(word, word)

        for token in word.split():
            if token and token not in STOPWORDS:
                tokens.append(token)

    return tokens


def similarity(a, b):
    if not a or not b:
        return 0.0

    set_a = set(a)
    set_b = set(b)

    same = len(set_a & set_b)
    jaccard = same / len(set_a | set_b)

    fuzzy = SequenceMatcher(
        None, " ".join(a), " ".join(b)
    ).ratio()

    coverage = same / len(set_b)

    return (
        0.4 * jaccard +
        0.3 * fuzzy +
        0.3 * coverage
    )


def angka(nilai):
    try:
        return float(nilai)
    except (ValueError, TypeError):
        return 0


def rupiah(nilai):
    return "Rp{:,.0f}".format(nilai).replace(",", ".")


def normalisasi_nama(teks):
    return " ".join(preprocess(teks))


class ChatbotEngine:

    def __init__(self, theme, threshold=THRESHOLD):
        self.theme = theme
        self.threshold = threshold

        self.patterns = []
        self.responses = {}

        for intent in theme["intents"]:
            tag = intent["tag"]
            self.responses[tag] = intent["responses"]

            for pattern in intent["patterns"]:
                self.patterns.append((
                    tag,
                    preprocess(pattern)
                ))

        # MEMBACA DATASET DESTINASI
        lokasi_file = (
            Path(__file__).resolve().parent
            / "data"
            / "tempat.csv"
        )

        self.destinasi = []

        try:
            with open(
                lokasi_file,
                "r",
                encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)
                self.destinasi = list(reader)

        except FileNotFoundError:
            print("Dataset tempat.csv tidak ditemukan:", lokasi_file)

    def classify(self, message):
        tokens = preprocess(message)

        best_score = 0
        best_tag = None

        for tag, pattern_tokens in self.patterns:
            score = similarity(tokens, pattern_tokens)

            if score > best_score:
                best_score = score
                best_tag = tag

        if best_score >= self.threshold:
            return best_tag, round(best_score, 2)

        return None, round(best_score, 2)

    # MENCARI DESTINASI BERDASARKAN NAMA
    def cari_destinasi(self, message):
        pertanyaan = normalisasi_nama(message)

        hasil_terbaik = None
        skor_terbaik = 0

        for tempat in self.destinasi:
            nama = normalisasi_nama(tempat["nama"])

            if nama and nama in pertanyaan:
                return tempat

            skor = SequenceMatcher(
                None, pertanyaan, nama
            ).ratio()

            if skor > skor_terbaik:
                skor_terbaik = skor
                hasil_terbaik = tempat

        if skor_terbaik >= 0.72:
            return hasil_terbaik

        return None

    # MENCARI HARGA TIKET
    def informasi_harga(self, tempat):
        harga = angka(tempat.get("harga_tiket"))

        if harga <= 0:
            return (
                f"Untuk harga tiket {tempat['nama']}, "
                "informasinya belum tersedia di dataset Javenture. "
                "Sebaiknya cek informasi resmi destinasi tersebut ya!"
            )

        return (
            f"Harga tiket {tempat['nama']} berdasarkan dataset "
            f"Javenture adalah **{rupiah(harga)} per orang**. "
            "Harga ini merupakan data dataset dan bisa berbeda "
            "dengan harga terbaru di lokasi wisata ya!"
        )

    # REKOMENDASI DESTINASI
    def rekomendasi(self, kategori=None, murah=False, estetik=False):
        hasil = []

        kata_estetik = [
            "foto", "pemandangan", "indah", "bukit",
            "spot", "panorama", "alam", "cantik",
            "instagram", "perbukitan"
        ]

        for tempat in self.destinasi:
            if kategori:
                if tempat["kategori"].lower() != kategori.lower():
                    continue

            rating = angka(tempat.get("rating_tempat"))
            harga = angka(tempat.get("harga_tiket"))

            if rating <= 0:
                continue

            if murah and (harga <= 0 or harga > 10000):
                continue

            if estetik:
                deskripsi = (
                    tempat.get("deskripsi", "").lower()
                )

                if not any(
                    kata in deskripsi for kata in kata_estetik
                ):
                    continue

            hasil.append(tempat)

        hasil.sort(
            key=lambda x: angka(x.get("rating_tempat")),
            reverse=True
        )

        return hasil[:5]

    # FORMAT HASIL REKOMENDASI
    def format_rekomendasi(self, hasil, judul):
        if not hasil:
            return (
                "Maaf, aku belum menemukan destinasi yang "
                "sesuai di dataset Javenture. 😅"
            )

        jawaban = [judul, ""]

        for nomor, tempat in enumerate(hasil, start=1):
            nama = tempat["nama"]
            rating = angka(tempat.get("rating_tempat"))
            harga = angka(tempat.get("harga_tiket"))

            info_harga = (
                rupiah(harga)
                if harga > 0
                else "Belum tersedia"
            )

            jawaban.append(
                f"{nomor}. **{nama}**\n"
                f"   Rating: {rating:.1f}/5\n"
                f"   Tiket: {info_harga}"
            )

        jawaban.append(
            "\nSemoga membantu menemukan destinasi "
            "favoritmu! 💚"
        )

        return "\n\n".join(jawaban)

    # MENANGANI PERTANYAAN BERDASARKAN DATASET
    def jawab_dataset(self, message):
        teks = message.lower()

        # PERTANYAAN HARGA TIKET
        if any(kata in teks for kata in [
            "harga", "tiket", "biaya masuk",
            "tiket masuk", "berapa"
        ]):
            tempat = self.cari_destinasi(message)

            if tempat:
                return self.informasi_harga(tempat)

        # PERTANYAAN DETAIL DESTINASI
        if any(kata in teks for kata in [
            "ceritakan", "jelaskan", "tentang",
            "deskripsi", "informasi"
        ]):
            tempat = self.cari_destinasi(message)

            if tempat:
                return (
                    f"**{tempat['nama']}** merupakan destinasi "
                    f"wisata kategori {tempat['kategori']} di "
                    "Yogyakarta.\n\n"
                    f"{tempat.get('deskripsi', '')}\n\n"
                    f"Rating: {angka(tempat.get('rating_tempat')):.1f}/5\n"
                    f"Harga tiket: "
                    f"{rupiah(angka(tempat.get('harga_tiket')))}"
                    if angka(tempat.get("harga_tiket")) > 0
                    else
                    f"**{tempat['nama']}** merupakan destinasi "
                    f"wisata kategori {tempat['kategori']} di "
                    f"Yogyakarta.\n\n{tempat.get('deskripsi', '')}\n\n"
                    f"Rating: {angka(tempat.get('rating_tempat')):.1f}/5\n"
                    "Harga tiket belum tersedia di dataset."
                )

        # REKOMENDASI WISATA
        if any(kata in teks for kata in [
            "rekomendasi", "wisata", "tempat bagus",
            "tempat menarik", "destinasi", "liburan"
        ]):
            kategori = None

            if any(kata in teks for kata in [
                "pantai", "laut", "pesisir"
            ]):
                kategori = "Pantai"

            elif any(kata in teks for kata in [
                "alam", "hutan", "gunung", "air terjun",
                "bukit", "pemandangan"
            ]):
                kategori = "Alam"

            elif any(kata in teks for kata in [
                "sejarah", "budaya", "candi", "keraton"
            ]):
                kategori = "Budaya Dan Sejarah"

            elif "museum" in teks:
                kategori = "Museum"

            elif any(kata in teks for kata in [
                "kuliner", "makanan"
            ]):
                kategori = "Kuliner"

            elif any(kata in teks for kata in [
                "buatan", "keluarga", "wahana"
            ]):
                kategori = "Buatan"

            murah = any(kata in teks for kata in [
                "murah", "hemat", "terjangkau"
            ])

            estetik = any(kata in teks for kata in [
                "estetik", "aesthetic", "foto",
                "instagramable", "instagram"
            ])

            hasil = self.rekomendasi(
                kategori=kategori,
                murah=murah,
                estetik=estetik
            )

            if kategori:
                judul = (
                    f"Ini rekomendasi wisata kategori "
                    f"{kategori} berdasarkan dataset Javenture:"
                )
            elif murah:
                judul = (
                    "Ini beberapa destinasi dengan tiket "
                    "maksimal Rp10.000 berdasarkan dataset:"
                )
            else:
                judul = (
                    "Ini beberapa rekomendasi destinasi "
                    "wisata Yogyakarta berdasarkan rating:"
                )

            if estetik:
                judul = (
                    "Ini beberapa destinasi dengan deskripsi "
                    "yang cocok untuk menikmati pemandangan "
                    "dan berburu foto:"
                )

            return self.format_rekomendasi(hasil, judul)

        return None

    def reply(self, message):
        # COBA JAWAB DARI DATASET TERLEBIH DAHULU
        jawaban_dataset = self.jawab_dataset(message)

        if jawaban_dataset:
            return {
                "reply": jawaban_dataset,
                "intent": "informasi_dataset",
                "score": 1.0
            }

        # JIKA BUKAN PERTANYAAN DATASET, GUNAKAN FAQ JSON
        tag, score = self.classify(message)

        if tag is None:
            answers = self.theme["fallback"]
        else:
            answers = self.responses[tag]

        return {
            "reply": random.choice(answers),
            "intent": tag,
            "score": score
        }
