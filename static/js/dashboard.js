
const gambarDefault = "/static/img/hero-jogja.png";

// Mengambil data dashboard dari Flask.
async function muatDashboard() {
    try {
        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("Data dashboard gagal dimuat.");
        }

        const data = await response.json();

        tampilkanDestinasi(data.populer);
        tampilkanPeta(data.peta);

    } catch (error) {
        console.error(error);

        document.getElementById("pesanError").textContent =
            "Data destinasi belum berhasil dimuat. Silakan refresh halaman.";
    }
}


// Menampilkan kartu rekomendasi destinasi.
function tampilkanDestinasi(destinasi) {
    const container = document.getElementById("destinationList");

    container.innerHTML = "";

    destinasi.forEach((tempat, index) => {
        const kartu = document.createElement("article");

        kartu.className = "destination-card";

        const foto = tempat.foto || gambarDefault;
        const peringkat = index + 1;

        kartu.innerHTML = `
            <div class="destination-image">
                <img
                    src="${escapeHTML(foto)}"
                    alt="${escapeHTML(tempat.nama)}"
                    loading="lazy"
                    onerror="this.onerror=null; this.src='${gambarDefault}'"
                >

                <span class="rank-badge ${peringkat === 1 ? "first" : ""}">
                    ${peringkat}
                </span>
            </div>

            <div class="destination-info">
                <span class="destination-category">
                    ${escapeHTML(tempat.kategori)}
                </span>

                <h3>${escapeHTML(tempat.nama)}</h3>

                <div class="destination-meta">
                    <span class="destination-rating">
                        ★ ${Number(tempat.rating_tempat).toFixed(1)}
                    </span>

                    <span>
                        ${Number(tempat.jumlah_penilaian).toLocaleString("id-ID")}
                        penilaian
                    </span>
                </div>

                <div class="destination-count">
                    Popular destination in Yogyakarta
                </div>
            </div>
        `;

        container.appendChild(kartu);
    });
}


// Menghindari karakter HTML dari data masuk ke dalam markup.
function escapeHTML(nilai) {
    return String(nilai ?? "").replace(/[&<>"']/g, karakter => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[karakter]);
}


// Menampilkan peta persebaran wisata.
function tampilkanPeta(destinasi) {
    const peta = L.map("map").setView([-7.7956, 110.3695], 10);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(peta);

    destinasi.forEach(tempat => {
        const lat = Number(tempat.latitude);
        const lon = Number(tempat.longitude);

        if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
            return;
        }

        if (lat < -9 || lat > -6 || lon < 108 || lon > 112) {
            return;
        }

        const popup = `
            <b>${escapeHTML(tempat.nama)}</b><br>
            Kategori: ${escapeHTML(tempat.kategori)}<br>
            Rating: ${Number(tempat.rating_tempat).toFixed(1)}
        `;

        L.marker([lat, lon])
            .addTo(peta)
            .bindPopup(popup);
    });
}


// Jalankan setelah halaman selesai dimuat.
document.addEventListener("DOMContentLoaded", muatDashboard);
