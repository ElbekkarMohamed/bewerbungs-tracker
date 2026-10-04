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
    loadDashboard();
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

const STATUS_LABELS = {
    applied: "Beworben",
    interview: "Gespräch",
    offer: "Zusage",
    rejected: "Absage",
};

function formatDate(isoDate) {
    return isoDate.split("-").reverse().join(".");
}

function createStat(label, value) {
    const div = document.createElement("div");
    div.className = "stat";
    const strong = document.createElement("strong");
    strong.textContent = value;
    div.append(strong, label);
    return div;
}

async function loadStats() {
    const stats = await api("/api/stats");
    const container = document.getElementById("stats");
    container.innerHTML = "";
    container.append(createStat("Gesamt", stats.total));
    for (const [status, label] of Object.entries(STATUS_LABELS)) {
        container.append(createStat(label, stats.by_status[status]));
    }
}

function createRow(application) {
    const row = document.createElement("tr");
    const values = [
        application.company,
        application.position,
        formatDate(application.applied_on),
        STATUS_LABELS[application.status],
        application.notes || "",
    ];
    for (const value of values) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
    }
    return row;
}

async function loadApplications() {
    const filter = document.getElementById("filter").value;
    const path = filter ? `/api/applications?status=${filter}` : "/api/applications";
    const applications = await api(path);

    const tbody = document.getElementById("applications-body");
    tbody.innerHTML = "";
    if (applications.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 6;
        cell.textContent = "Noch keine Bewerbungen.";
        row.append(cell);
        tbody.append(row);
        return;
    }
    for (const application of applications) {
        tbody.append(createRow(application));
    }
}

async function loadDashboard() {
    await loadStats();
    await loadApplications();
}

document.getElementById("filter").addEventListener("change", loadApplications);


const applicationForm = document.getElementById("application-form");
const formMessage = document.getElementById("form-message");

applicationForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = JSON.stringify({
        company: document.getElementById("company").value,
        position: document.getElementById("position").value,
        applied_on: document.getElementById("applied-on").value,
        status: document.getElementById("status").value,
        notes: document.getElementById("notes").value,
    });
    try {
        await api("/api/applications", { method: "POST", body });
        applicationForm.reset();
        setMessage(formMessage, "Bewerbung gespeichert.", "success");
        loadDashboard();
    } catch (error) {
        setMessage(formMessage, error.message, "error");
    }
});


init();