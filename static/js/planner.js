
const plannerForm = document.getElementById("plannerForm");
const formMessage = document.getElementById("formMessage");
const receiptPrinter = document.getElementById("receiptPrinter");


// FORMAT RUPIAH
function formatRupiah(angka) {
    return new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0
    }).format(angka);
}


// MENCEGAH TEKS DATA DIBACA SEBAGAI HTML
function escapeHTML(teks) {
    return String(teks ?? "").replace(/[&<>"']/g, function (karakter) {
        const karakterHTML = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return karakterHTML[karakter];
    });
}


// MEMBUAT TAMPILAN ITINERARY
function tampilkanItinerary(data) {
    const receiptContent = document.querySelector(".receipt-content");

    let isiReceipt = `
        <p class="receipt-brand">JAVENTURE</p>
        <p class="receipt-subtitle">YOUR PERSONAL TRAVEL PLAN</p>

        <div class="receipt-divider"></div>

        <h3>TRAVEL ITINERARY</h3>
        <p class="receipt-center">YOGYAKARTA, INDONESIA</p>

        <div class="receipt-divider"></div>

        <div class="receipt-info">
            <div>
                <span>TRIP DURATION</span>
                <strong>${data.duration} DAYS</strong>
            </div>

            <div>
                <span>TRAVELERS</span>
                <strong>${data.travelers} PEOPLE</strong>
            </div>

            <div>
                <span>STARTING TIME</span>
                <strong>${data.start_time}</strong>
            </div>

            <div>
                <span>TOTAL DESTINATIONS</span>
                <strong>${data.destination_count} PLACES</strong>
            </div>
        </div>

        <div class="receipt-divider"></div>

        <p class="receipt-section-title">YOUR DESTINATIONS</p>
    `;

    // TAMPILKAN JADWAL SETIAP HARI
    data.days.forEach(function (hari) {
        isiReceipt += `
            <div class="receipt-divider"></div>

            <p class="receipt-section-title">
                DAY ${String(hari.day).padStart(2, "0")}
                — ${hari.destinations} DESTINATIONS
            </p>
        `;

        hari.schedule.forEach(function (item) {

            // JADWAL PERJALANAN ANTAR DESTINASI
            if (item.type === "travel") {
                isiReceipt += `
                    <div class="receipt-item">
                        <div class="receipt-time">
                            ${item.start} - ${item.end}
                        </div>

                        <strong>TRAVEL TO NEXT DESTINATION</strong>

                        <span>
                            Estimated ${item.duration} minutes
                            · ${item.distance} km
                        </span>
                    </div>
                `;
            }

            // JADWAL KUNJUNGAN DESTINASI
            if (item.type === "visit") {
                const destinasi = item.destination;

                isiReceipt += `
                    <div class="receipt-item">
                        <div class="receipt-time">
                            ${item.start} - ${item.end}
                        </div>

                        <strong>
                            ${escapeHTML(destinasi.nama)}
                        </strong>

                        <span>
                            ${escapeHTML(destinasi.kategori)}
                        </span>

                        <p>
                            ${escapeHTML(destinasi.deskripsi)}
                        </p>

                        <p>
                            Rating: ${destinasi.rating.toFixed(1)} / 5
                            <br>
                            Ticket: ${formatRupiah(destinasi.harga_tiket)}
                            / person
                            <br>
                            Estimated visit: ${item.duration} minutes
                        </p>
                    </div>
                `;
            }
        });
    });

    // RINGKASAN BIAYA
    isiReceipt += `
        <div class="receipt-divider"></div>

        <div class="receipt-total">
            <span>TOTAL TICKET BUDGET</span>
            <strong>${formatRupiah(data.ticket_budget)}</strong>
        </div>

        <div class="receipt-total">
            <span>TOTAL TICKET COST</span>
            <strong>${formatRupiah(data.total_ticket_cost)}</strong>
        </div>

        <div class="receipt-total">
            <span>REMAINING BUDGET</span>
            <strong>${formatRupiah(data.remaining_budget)}</strong>
        </div>

        <div class="receipt-divider"></div>

        <p class="receipt-thanks">HAPPY JOURNEY!</p>

        <p class="receipt-footer">
            Discover the beauty of Yogyakarta with Javenture.
        </p>

        <div class="receipt-barcode">
            || ||| || |||| | ||| || |||| ||
        </div>

        <p class="receipt-id">
            JAV-TRIP-${new Date().getFullYear()}-001
        </p>
    `;

    receiptContent.innerHTML = isiReceipt;
}


// KIRIM PREFERENSI DAN BUAT ITINERARY
plannerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const duration = document.getElementById("duration").value;
    const travelers = document.getElementById("travelers").value;
    const startTime = document.getElementById("startTime").value;
    const ticketBudget = document.getElementById("ticketBudget").value;
    const destinationCount = document.getElementById("destinationCount").value;

    const interests = document.querySelectorAll(
        'input[name="interests"]:checked'
    );

    if (interests.length === 0) {
        formMessage.textContent =
            "Please select at least one travel interest.";

        formMessage.style.color = "#c45b4b";
        return;
    }

    if (Number(travelers) < 1 || Number(travelers) > 50) {
        formMessage.textContent =
            "Please enter between 1 and 50 travelers.";

        formMessage.style.color = "#c45b4b";
        return;
    }

    if (Number(ticketBudget) < 1) {
        formMessage.textContent =
            "Please enter a valid ticket budget.";

        formMessage.style.color = "#c45b4b";
        return;
    }

    if (Number(destinationCount) < 1 || Number(destinationCount) > 15) {
        formMessage.textContent =
            "Please choose between 1 and 15 destinations.";

        formMessage.style.color = "#c45b4b";
        return;
    }

    const selectedInterests = Array.from(interests).map(
        interest => interest.value
    );

    const travelPreferences = {
        duration: duration,
        travelers: travelers,
        startTime: startTime,
        interests: selectedInterests,
        ticketBudget: ticketBudget,
        destinationCount: destinationCount
    };

    formMessage.textContent = "Creating your travel itinerary...";
    formMessage.style.color = "#527b4d";

    const submitButton = plannerForm.querySelector(
        ".generate-button"
    );

    submitButton.disabled = true;

    try {
        const response = await fetch(
            "/api/planner/recommendations",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(travelPreferences)
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Failed to generate itinerary."
            );
        }

        tampilkanItinerary(data);

        formMessage.textContent =
            "Your personalized itinerary is ready!";

        formMessage.style.color = "#527b4d";

        receiptPrinter.classList.remove("printing");

        setTimeout(function () {
            receiptPrinter.classList.add("printing");

            document.getElementById("itinerary-result").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }, 100);

    } catch (error) {
        formMessage.textContent = error.message;
        formMessage.style.color = "#c45b4b";

    } finally {
        submitButton.disabled = false;
    }
});
