
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sentimentForm");
    const destination = document.getElementById("destination");
    const review = document.getElementById("review");
    const charCount = document.getElementById("charCount");
    const formMessage = document.getElementById("formMessage");

    // Menghitung jumlah karakter review
    review.addEventListener("input", function () {
        charCount.textContent = `${review.value.length}/1000`;
        formMessage.textContent = "";
    });

    // Menghapus pesan ketika destinasi diganti
    destination.addEventListener("change", function () {
        formMessage.textContent = "";
    });

    // Validasi form
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const selectedDestination = destination.value;
        const reviewText = review.value.trim();

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

        formMessage.textContent =
            "UI sudah siap! Model analisis sentimen akan diintegrasikan pada tahap berikutnya.";
    });
});
