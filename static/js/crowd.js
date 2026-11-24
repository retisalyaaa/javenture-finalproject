
document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("crowdForm");
    const destination = document.getElementById("destination");
    const visitDate = document.getElementById("visitDate");
    const visitTime = document.getElementById("visitTime");
    const crowdMessage = document.getElementById("crowdMessage");

    // Membatasi tanggal kunjungan agar tidak memilih tanggal lampau
    const today = new Date();
    const localToday = new Date(
        today.getTime() - today.getTimezoneOffset() * 60000
    ).toISOString().split("T")[0];

    visitDate.min = localToday;

    // Menghapus pesan ketika pengguna mengubah input
    destination.addEventListener("change", function () {
        crowdMessage.textContent = "";
    });

    visitDate.addEventListener("change", function () {
        crowdMessage.textContent = "";
    });

    visitTime.addEventListener("change", function () {
        crowdMessage.textContent = "";
    });

    // Validasi form prediksi
    form.addEventListener("submit", function (event) {

        event.preventDefault();

        if (!destination.value) {
            crowdMessage.textContent =
                "Silakan pilih destinasi wisata terlebih dahulu.";
            destination.focus();
            return;
        }

        if (!visitDate.value) {
            crowdMessage.textContent =
                "Silakan tentukan tanggal kunjungan.";
            visitDate.focus();
            return;
        }

        if (!visitTime.value) {
            crowdMessage.textContent =
                "Silakan pilih jam kunjungan.";
            visitTime.focus();
            return;
        }

        crowdMessage.textContent =
            "Form berhasil divalidasi! Model prediksi kepadatan akan diintegrasikan pada tahap berikutnya.";

    });

});