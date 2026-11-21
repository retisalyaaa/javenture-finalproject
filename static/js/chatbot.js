
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = document.getElementById("sendButton");



function addMessage(message, sender) {

    const row = document.createElement("div");

    row.classList.add("message-row");

    if (sender === "user") {

        row.classList.add("user-row");

        const bubble = document.createElement("div");

        bubble.classList.add("message", "user-message");
        bubble.textContent = message;

        row.appendChild(bubble);

    } else {

        row.classList.add("bot-row");

        // Avatar Javenture
        const avatar = document.createElement("div");

        avatar.classList.add("bot-avatar");

        const logo = document.createElement("img");

        logo.src = "/static/img/logo-javenture.png";
        logo.alt = "Javenture";

        avatar.appendChild(logo);

        // Bubble chatbot
        const bubble = document.createElement("div");

        bubble.classList.add("message", "bot-message");
        bubble.textContent = message;

        row.appendChild(avatar);
        row.appendChild(bubble);
    }

    chatMessages.appendChild(row);

    // Otomatis tampilkan pesan terbaru
    const chatContent = document.querySelector(".chat-content");

    requestAnimationFrame(() => {

        chatContent.scrollTo({
            top: chatContent.scrollHeight,
            behavior: "smooth"
        });

    });
}



async function sendMessage(message) {

    if (!message.trim()) return;

    addMessage(message, "user");

    userInput.value = "";
    sendButton.disabled = true;

    try {

        const response = await fetch("/api/chat", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message,
                theme: "javenture"
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Terjadi kesalahan.");
        }

        addMessage(data.reply, "bot");

        console.log("Intent:", data.intent);
        console.log("Similarity:", data.score);

    } catch (error) {

        console.error("Chatbot error:", error);

        addMessage(
            "Maaf, terjadi kesalahan: " + error.message,
            "bot"
        );

    } finally {

        sendButton.disabled = false;
        userInput.focus();

    }
}


chatForm.addEventListener("submit", function(event) {

    event.preventDefault();

    sendMessage(userInput.value);

});


function sendSuggestion(message) {
    sendMessage(message);
}


// Greeting dari JSON
async function loadGreeting() {

    try {

        const response = await fetch("/api/chatbot-config");
        const data = await response.json();

        addMessage(data.greeting, "bot");

    } catch (error) {

        addMessage(
            "Halo, traveler! 👋 Aku Javenture. Ada yang ingin kamu tanyakan?",
            "bot"
        );

    }

}

loadGreeting();

async function loadSuggestions() {

    const response = await fetch("/api/chatbot-config");
    const data = await response.json();

    const container = document.getElementById("suggestions");

    container.innerHTML = "";

    data.suggestions.forEach(function(item) {

        const button = document.createElement("button");

        button.textContent = item;

        button.addEventListener("click", function() {
            sendSuggestion(item);
        });

        container.appendChild(button);

    });

}

loadSuggestions();
