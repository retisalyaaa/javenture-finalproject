const plannerForm = document.getElementById("plannerForm");
const formMessage = document.getElementById("formMessage");

plannerForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const duration = document.getElementById("duration").value;
    const travelers = document.getElementById("travelers").value;
    const startTime = document.getElementById("startTime").value;

    const interests = document.querySelectorAll(
        'input[name="interests"]:checked'
    );

    // Validasi minat wisata
    if (interests.length === 0) {
        formMessage.textContent =
            "Please select at least one travel interest.";

        formMessage.style.color = "#c45b4b";
        return;
    }

    // Validasi jumlah orang
    if (Number(travelers) < 1 || Number(travelers) > 50) {
        formMessage.textContent =
            "Please enter a number of travelers between 1 and 50.";

        formMessage.style.color = "#c45b4b";
        return;
    }

    // Mengambil semua minat wisata yang dipilih
    const selectedInterests = Array.from(interests).map(
        interest => interest.value
    );

    // Menampilkan data input di console untuk pengecekan
    const travelPreferences = {
        duration: duration,
        travelers: travelers,
        interests: selectedInterests,
        startTime: startTime
    };

    console.log("Travel Preferences:", travelPreferences);

    formMessage.textContent =
        "Your preferences have been recorded. Itinerary generation will be available soon!";

    formMessage.style.color = "#527b4d";
});