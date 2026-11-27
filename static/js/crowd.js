document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("crowdForm");
    const destination = document.getElementById("destination");
    const visitDate = document.getElementById("visitDate");
    const visitTime = document.getElementById("visitTime");
    const crowdMessage = document.getElementById("crowdMessage");

    const predictButton = form.querySelector(
        ".predict-button"
    );

    const resultStatus = document.querySelector(
        ".result-status"
    );

    const resultEmpty = document.querySelector(
        ".result-empty"
    );

    // Membatasi tanggal kunjungan agar tidak memilih tanggal lampau
    const today = new Date();

    const localToday = new Date(
        today.getTime() - today.getTimezoneOffset() * 60000
    ).toISOString().split("T")[0];

    visitDate.min = localToday;

    // Menghapus pesan ketika input berubah
    [destination, visitDate, visitTime].forEach(input => {
        input.addEventListener("change", function () {
            crowdMessage.textContent = "";
        });
    });

    // Menampilkan hasil prediksi
    function showResult(data) {

        resultStatus.textContent = data.crowd_level;

        resultStatus.className =
            "result-status " + data.crowd_level.toLowerCase();

        resultEmpty.innerHTML = `
            <div class="crowd-illustration">
                <span>${data.popularity_score}</span>
            </div>

            <h3>${data.crowd_level} Crowd Level</h3>

            <p>
                <strong>${data.destination}</strong>
                <br>
                ${data.visit_day}, ${data.visit_date}
                at ${data.visit_time}
            </p>

            <p>${data.description}</p>

            <h3>Popularity Score: ${data.popularity_score}/100</h3>
        `;
    }

    // Mengirim form ke Flask
    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        crowdMessage.textContent = "";

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

        // Menampilkan status loading
        predictButton.disabled = true;

        const originalText = predictButton.innerHTML;

        predictButton.innerHTML = `
            <span>Predicting...</span>
        `;

        crowdMessage.textContent =
            "Sedang menghitung prediksi keramaian...";

        try {

            const response = await fetch("/api/crowd", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    destination: destination.value,
                    visitDate: visitDate.value,
                    visitTime: visitTime.value
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.message || "Prediksi gagal dilakukan."
                );
            }

            // Menampilkan hasil
            showResult(data);

            crowdMessage.textContent =
                "Prediksi berhasil dilakukan!";

        } catch (error) {

            crowdMessage.textContent = error.message;

        } finally {

            predictButton.disabled = false;
            predictButton.innerHTML = originalText;

        }

    });

});