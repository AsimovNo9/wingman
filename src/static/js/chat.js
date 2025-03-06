const socket = io();
const room = "user1-user2"; // Define room based on users

const db = new Dexie("ChatDB");
db.version(1).stores({ messages: "++id, room, user, msg" });

function saveMessage(room, user, msg) {
    db.messages.add({ room, user, msg, timestamp: new Date() });
}

function loadMessages(room) {
    db.messages.where("room").equals(room).toArray().then(messages => {
        messages.forEach(m => displayMessage(m.user, m.msg));
    });
}

function displayMessage(user, msg) {
    let chatBox = document.getElementById("chat-box");
    let messageDiv = document.createElement("div");
    let messageContent = document.createElement("div");
    
    messageDiv.className = `message-wrapper ${user === "Me" ? "message-self" : "message-other"}`;
    messageContent.className = "message-content";
    messageContent.innerText = msg;
    
    if (user !== "Me" && user !== "System") {
        let userLabel = document.createElement("div");
        userLabel.className = "message-user";
        userLabel.innerText = user;
        messageDiv.appendChild(userLabel);
    }
    
    messageDiv.appendChild(messageContent);
    
    if (user === "System") {
        messageDiv.className = "message-system";
        messageContent.className = "message-system-content";
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}


socket.emit("join", { room });

socket.on("message", (data) => {
    displayMessage(data.user, data.msg);
    saveMessage(room, data.user, data.msg);
});

function sendMessage() {
    let msgInput = document.getElementById("msg");
    let msg = msgInput.value.trim();
    if(msg){
        socket.emit("message",{room, msg});
        displayMessage("Me", msg);
        saveMessage(room, "Me", msg);
        msgInput.value="";
    }
}

document.getElementById("msg").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

loadMessages(room)