// ── API helpers ────────────────────────────────────────────────────────────

const API_BASE = "";

function getToken() {
  return localStorage.getItem("dentai_token");
}

function getUser() {
  const raw = localStorage.getItem("dentai_user");
  return raw ? JSON.parse(raw) : null;
}

function setAuth(token, user) {
  localStorage.setItem("dentai_token", token);
  localStorage.setItem("dentai_user", JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem("dentai_token");
  localStorage.removeItem("dentai_user");
}

function authHeaders(extra = {}) {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken()}`,
    ...extra,
  };
}

async function apiFetch(path, options = {}) {
  const resp = await fetch(API_BASE + path, {
    headers: authHeaders(),
    ...options,
  });
  if (resp.status === 401) {
    clearAuth();
    window.location.href = "/login";
    return;
  }
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.detail || "Request failed");
  return data;
}

// ── Auth ───────────────────────────────────────────────────────────────────

async function login(email, password) {
  const resp = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.detail || "Login failed");
  setAuth(data.access_token, data.user);
  return data.user;
}

async function register(fullName, email, password, role) {
  const resp = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name: fullName, email, password, role }),
  });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.detail || "Registration failed");
  return data;
}

function logout() {
  clearAuth();
  window.location.href = "/";
}

// ── UI Utilities ────────────────────────────────────────────────────────────

function showAlert(containerId, message, type = "info") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  setTimeout(() => { if (el) el.innerHTML = ""; }, 5000);
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.innerHTML = loading
    ? `<span class="spinner"></span> Loading...`
    : btn.dataset.label || btn.innerHTML;
}

function requireAuth(requiredRole = null) {
  const user = getUser();
  const token = getToken();
  if (!user || !token) {
    window.location.href = "/login";
    return null;
  }
  if (requiredRole && user.role !== requiredRole) {
    window.location.href = user.role === "faculty" ? "/faculty" : "/student";
    return null;
  }
  return user;
}

function setUserUI(user) {
  document.querySelectorAll(".user-name").forEach(el => el.textContent = user.full_name);
  document.querySelectorAll(".user-role").forEach(el => el.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1));
  document.querySelectorAll(".user-avatar").forEach(el => {
    el.textContent = user.full_name.charAt(0).toUpperCase();
  });
}

function initPage(requiredRole = null) {
  const user = requireAuth(requiredRole);
  if (user) setUserUI(user);
  return user;
}

// ── Notes & Bookmarks ───────────────────────────────────────────────────────

async function saveNote(title, content, topic = "") {
  return apiFetch("/api/notes/create", {
    method: "POST",
    body: JSON.stringify({ title, content, topic }),
  });
}

async function addBookmark(topic, description = "", urlOrRef = "") {
  return apiFetch("/api/notes/bookmark", {
    method: "POST",
    body: JSON.stringify({ topic, description, url_or_ref: urlOrRef }),
  });
}

// ── Expose globals ──────────────────────────────────────────────────────────
window.DentAI = {
  login, register, logout, apiFetch, getToken, getUser, showAlert,
  setLoading, requireAuth, setUserUI, initPage, saveNote, addBookmark,
};
