async function api(path, options = {}) {
    const response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || "Unbekannter Fehler.");
    }
    return data;
}

function showAuth() {
    document.getElementById("auth-section").hidden = false;
    document.getElementById("dashboard-section").hidden = true;
    document.getElementById("user-info").hidden = true;
}

function showDashboard(username) {
    document.getElementById("username").textContent = username;
    document.getElementById("auth-section").hidden = true;
    document.getElementById("dashboard-section").hidden = false;
    document.getElementById("user-info").hidden = false;
}

async function init() {
    try {
        const user = await api("/api/me");
        showDashboard(user.username);
    } catch {
        showAuth();
    }
}
const authForm = document.getElementById("auth-form");
const authMessage = document.getElementById("auth-message");

function setMessage(element, text, type) {
    element.textContent = text;
    element.className = "message " + type;
}

function getCredentials() {
    return JSON.stringify({
        username: document.getElementById("auth-username").value,
        password: document.getElementById("auth-password").value,
    });
}

authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
        const user = await api("/api/login", { method: "POST", body: getCredentials() });
        authForm.reset();
        setMessage(authMessage, "", "");
        showDashboard(user.username);
    } catch (error) {
        setMessage(authMessage, error.message, "error");
    }
});

document.getElementById("register-btn").addEventListener("click", async () => {
    if (!authForm.reportValidity()) {
        return;
    }
    try {
        await api("/api/register", { method: "POST", body: getCredentials() });
        setMessage(authMessage, "Registrierung erfolgreich. Du kannst dich jetzt einloggen.", "success");
    } catch (error) {
        setMessage(authMessage, error.message, "error");
    }
});

document.getElementById("logout-btn").addEventListener("click", async () => {
    await api("/api/logout", { method: "POST" });
    showAuth();
});
init();