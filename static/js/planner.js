const plannerForm = document.getElementById("plannerForm");
const formMessage = document.getElementById("formMessage");
const receiptPrinter = document.getElementById("receiptPrinter");

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
            "Please enter between 1 and 50 travelers.";

        formMessage.style.color = "#c45b4b";
        return;
    }

    // Mengambil preferensi perjalanan
    const selectedInterests = Array.from(interests).map(
        interest => interest.value
    );

    const travelPreferences = {
        duration: duration,
        travelers: travelers,
        interests: selectedInterests,
        startTime: startTime
    };

    console.log("Travel Preferences:", travelPreferences);

    // Pesan berhasil
    formMessage.textContent =
        "Your travel preferences have been submitted!";

    formMessage.style.color = "#527b4d";

    // Mengulang animasi jika tombol ditekan kembali
    receiptPrinter.classList.remove("printing");

    // Memulai animasi struk keluar dari printer
    setTimeout(function () {
        receiptPrinter.classList.add("printing");

        document.getElementById("itinerary-result").scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);
});