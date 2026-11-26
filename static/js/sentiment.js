document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("sentimentForm");
    const destination = document.getElementById("destination");
    const review = document.getElementById("review");
    const charCount = document.getElementById("charCount");
    const formMessage = document.getElementById("formMessage");
    const resultSection = document.getElementById("resultSection");

    const analyzeButton = form.querySelector(
        ".analyze-button"
    );

    // Menyimpan hasil analisis selama halaman dibuka
    let history = [];

    // Menghitung karakter review
    review.addEventListener("input", function () {

        charCount.textContent =
            `${review.value.length}/1000`;

        formMessage.textContent = "";

    });


    // Menghapus pesan ketika destinasi diganti
    destination.addEventListener("change", function () {

        formMessage.textContent = "";

    });


    // Mengirim review ke Flask
    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        const selectedDestination = destination.value;
        const reviewText = review.value.trim();

        // Validasi
        if (!selectedDestination) {

            formMessage.textContent =
                "Silakan pilih destinasi wisata terlebih dahulu.";

            destination.focus();
            return;
        }

        if (reviewText.length < 10) {

            formMessage.textContent =
                "Ulasan terlalu singkat. Tulis minimal 10 karakter.";

            review.focus();
            return;
        }

        // Status loading
        analyzeButton.disabled = true;

        analyzeButton.querySelector("span:first-child").textContent =
            "Analyzing...";

        formMessage.textContent =
            "Sedang menganalisis review kamu...";

        try {

            const response = await fetch("/api/sentiment", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    destination: selectedDestination,
                    review: reviewText
                })

            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message || "Analisis gagal dilakukan."
                );
            }

            // Menampilkan hasil
            displayResult(result);

            // Menyimpan riwayat sesi
            history.unshift(result);

            updateOverview();
            updateHistory();

            formMessage.textContent =
                "Review berhasil dianalisis!";

        } catch (error) {

            formMessage.textContent = error.message;

        } finally {

            analyzeButton.disabled = false;

            analyzeButton.querySelector("span:first-child").textContent =
                "Analyze Sentiment";

        }

    });


    // Menampilkan hasil analisis
    function displayResult(data) {

        const emptyResult = resultSection.querySelector(
            ".result-empty"
        );

        if (emptyResult) {
            emptyResult.remove();
        }

        let resultCard = document.getElementById(
            "sentimentResultCard"
        );

        if (!resultCard) {

            resultCard = document.createElement("div");

            resultCard.id = "sentimentResultCard";
            resultCard.className = "result-empty";

            resultSection.appendChild(resultCard);

        }

        const sentimentInfo = {

            positive: {
                label: "Positive",
                emoji: "😊",
                color: "#249B62",
                description:
                    "Review menunjukkan pengalaman yang cenderung positif."
            },

            neutral: {
                label: "Neutral",
                emoji: "😐",
                color: "#C58A24",
                description:
                    "Review menunjukkan pengalaman yang cenderung netral."
            },

            negative: {
                label: "Negative",
                emoji: "😞",
                color: "#D9534F",
                description:
                    "Review menunjukkan pengalaman yang cenderung negatif."
            }

        };

        const info = sentimentInfo[data.sentiment];

        if (!info) {
            throw new Error("Label sentimen tidak dikenali.");
        }

        resultCard.style.display = "block";
        resultCard.style.textAlign = "left";
        resultCard.style.padding = "28px";
        resultCard.style.borderRadius = "18px";
        resultCard.style.background = "#ffffff";
        resultCard.style.border = "1px solid #e5e7eb";

        resultCard.innerHTML = `
            <div style="text-align:center;">

                <div style="font-size:45px;">
                    ${info.emoji}
                </div>

                <p style="margin-bottom:8px;">
                    Sentiment Result
                </p>

                <h2 style="
                    color:${info.color};
                    font-size:30px;
                    margin:0;
                ">
                    ${info.label}
                </h2>

                <p style="margin-top:10px;">
                    ${info.description}
                </p>

            </div>

            <hr style="
                border:0;
                border-top:1px solid #e5e7eb;
                margin:22px 0;
            ">

            <p>
                <strong>Destination:</strong>
                <span id="resultDestination"></span>
            </p>

            <p>
                <strong>Your Review:</strong>
            </p>

            <p id="resultReview"></p>

            <div style="
                background:#f0f7f2;
                padding:16px;
                border-radius:12px;
                margin-top:20px;
            ">

                <strong>Prediction Probability</strong>

                <h3 style="
                    color:${info.color};
                    margin:8px 0;
                ">
                    ${data.probability}%
                </h3>

                <p style="
                    font-size:12px;
                    color:#64748b;
                    margin:0;
                ">
                    Probabilitas yang diberikan model untuk kelas prediksi,
                    bukan jaminan kebenaran hasil.
                </p>

            </div>

        `;

        document.getElementById(
            "resultDestination"
        ).textContent = data.destination;

        document.getElementById(
            "resultReview"
        ).textContent = data.review;

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    }


    // Memperbarui ringkasan sentimen
    function updateOverview() {

        const total = history.length;

        const counts = {
            positive: 0,
            neutral: 0,
            negative: 0
        };

        history.forEach(function (item) {
            counts[item.sentiment]++;
        });

        Object.keys(counts).forEach(function (sentiment) {

            const card = document.querySelector(
                `.sentiment-card.${sentiment}`
            );

            if (!card) return;

            const percentage = total
                ? ((counts[sentiment] / total) * 100).toFixed(1)
                : 0;

            card.querySelector("h3").textContent =
                `${percentage}%`;

            card.querySelector("p").textContent =
                `${counts[sentiment]} dari ${total} analisis sesi ini`;

        });

        const note = document.querySelector(".overview-note");

        if (note) {
            note.textContent =
                "*Ringkasan berdasarkan analisis selama halaman ini dibuka.";
        }

    }


    // Memperbarui riwayat analisis
    function updateHistory() {

        const historyCard = document.querySelector(".history-card");

        const emptyHistory = historyCard.querySelector(
            ".history-empty"
        );

        if (emptyHistory) {
            emptyHistory.remove();
        }

        let historyList = document.getElementById(
            "sentimentHistoryList"
        );

        if (!historyList) {

            historyList = document.createElement("div");

            historyList.id = "sentimentHistoryList";

            historyCard.appendChild(historyList);

        }

        historyList.innerHTML = "";

        history.forEach(function (item) {

            const colors = {
                positive: "#249B62",
                neutral: "#C58A24",
                negative: "#D9534F"
            };

            const historyItem = document.createElement("div");

            historyItem.style.padding = "18px";
            historyItem.style.marginBottom = "12px";
            historyItem.style.border = "1px solid #e5e7eb";
            historyItem.style.borderRadius = "12px";

            const title = document.createElement("h4");
            title.textContent = item.destination;

            const label = document.createElement("strong");
            label.textContent = item.sentiment.toUpperCase();
            label.style.color = colors[item.sentiment];

            const text = document.createElement("p");
            text.textContent = item.review;

            historyItem.append(title, label, text);

            historyList.appendChild(historyItem);

        });

    }

});