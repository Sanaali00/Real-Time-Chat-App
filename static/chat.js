let socket;

function connectWebSocket() {
    const username = document.getElementById("username").value.trim();
    if (!username) {
        alert("Please enter a username.");
        return;
    }

    socket = new WebSocket(`ws://${window.location.host}/ws/${username}`);

      socket.onopen = function () {
        document.getElementById("sendButton").disabled = false; // Enable the Send button
        document.getElementById("message").disabled = false; // Enable message input
    };
    socket.onmessage = function (event) {
        displayMessage(event.data);
    };

    socket.onclose = function () {
        appendMessageToChat("🔴 You have left the chat.");
        document.getElementById("sendButton").disabled = true;
    };
}

function sendMessage() {
    const messageInput = document.getElementById("message");
    const message = messageInput.value.trim();

    if (message && socket) {
        const username = document.getElementById("username").value;
        const messageData = JSON.stringify({ user: username, message: message });

        socket.send(messageData);
        messageInput.value = "";
    }
}

function displayMessage(message) {
    try {
        let messageData = JSON.parse(message);
        let user = messageData.user;
        let text = messageData.message;
        let status = messageData.status || "";

        let formattedMessage = `<strong>${user}:</strong> ${text}`;
        if (status === "join") {
            formattedMessage = `✅ <strong>${user}</strong> joined the chat!`;
        } else if (status === "leave") {
            formattedMessage = `❌ <strong>${user}</strong> left the chat!`;
        }

        appendMessageToChat(formattedMessage);
    } catch (error) {
        console.error("Error parsing message:", error);
        appendMessageToChat(message);
    }
}

function appendMessageToChat(message) {
    const chatBox = document.getElementById("chatBox");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("p-2", "bg-secondary", "text-white", "rounded", "mb-1");
    messageDiv.innerHTML = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function disconnectWebSocket() {
    if (socket) {
        socket.close();
        alert("You have left the chat.");
        location.reload();
    }
}
