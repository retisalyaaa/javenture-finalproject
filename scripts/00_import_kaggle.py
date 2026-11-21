"""Membersihkan dan menggabungkan dataset Kaggle untuk dashboard Javenture."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "kaggle"
DATA = ROOT / "data"


def perbaiki_koordinat(nilai, jenis):
    """Mengubah koordinat dengan titik berlebih menjadi format desimal."""
    teks = str(nilai).strip()
    tanda = -1 if teks.startswith("-") else 1
    angka = "".join(re.findall(r"\d", teks))
    batas = 1 if jenis == "latitude" else 3

    if not angka:
        return None
    if len(angka) <= batas:
        return tanda * float(angka)
    return tanda * float(angka[:batas] + "." + angka[batas:])


def main():
    tempat = pd.read_csv(RAW / "tourism_jogja.csv")
    rating = pd.read_csv(RAW / "tourism_rating.csv")
    pengguna = pd.read_csv(RAW / "user.csv")

    # Bersihkan koordinat dan pastikan nilainya masuk akal.
    tempat["latitude"] = tempat["latitude"].apply(
        lambda x: perbaiki_koordinat(x, "latitude")
    )
    tempat["longitude"] = tempat["longitude"].apply(
        lambda x: perbaiki_koordinat(x, "longitude")
    )

    valid = (
        tempat["latitude"].between(-9, -6)
        & tempat["longitude"].between(108, 112)
    )
    if not valid.all():
        raise ValueError("Ada koordinat yang tidak valid. Periksa dataset sumber.")

    # Hitung banyaknya penilaian pengguna untuk setiap destinasi.
    jumlah_penilaian = rating.groupby("Place_Id").size()
    tempat["jumlah_penilaian"] = (
        tempat["place_id"].map(jumlah_penilaian).fillna(0).astype(int)
    )

    # Samakan nama kolom agar mudah digunakan di Flask.
    data_tempat = tempat.rename(columns={
        "name": "nama",
        "type": "kategori",
        "rating": "rating_tempat",
        "htm": "harga_tiket",
        "description": "deskripsi",
    })[[
        "place_id", "nama", "kategori", "rating_tempat", "harga_tiket",
        "latitude", "longitude", "jumlah_penilaian", "deskripsi"
    ]]

    # Gabungkan rating pengguna dengan nama destinasi dan profil pengguna.
    data_rating = rating.merge(
        tempat[["place_id", "name"]],
        left_on="Place_Id", right_on="place_id", how="left"
    ).merge(pengguna, on="User_Id", how="left")
    data_rating = data_rating.rename(columns={
        "name": "nama_tempat",
        "Place_Ratings": "rating_pengguna",
        "Location": "lokasi_pengguna",
        "Age": "usia_pengguna",
    })[[
        "User_Id", "Place_Id", "nama_tempat", "rating_pengguna",
        "lokasi_pengguna", "usia_pengguna"
    ]]

    DATA.mkdir(exist_ok=True)
    data_tempat.to_csv(DATA / "tempat.csv", index=False, encoding="utf-8-sig")
    data_rating.to_csv(DATA / "rating_interactions.csv", index=False, encoding="utf-8-sig")
    pengguna.to_csv(DATA / "users_kaggle.csv", index=False, encoding="utf-8-sig")

    print("Preprocessing selesai.")
    print(f"Destinasi : {len(data_tempat)}")
    print(f"Pengguna  : {len(pengguna)}")
    print(f"Penilaian : {len(data_rating)}")
    print("File tersimpan di folder data/")


if __name__ == "__main__":
    main()
