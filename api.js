const BASE = "";  // same origin

function getToken() {
  return localStorage.getItem("token");
}

function getUser() {
  try { return JSON.parse(localStorage.getItem("user")); } catch { return null; }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/login.html";
}

function requireAuth() {
  if (!getToken()) window.location.href = "/login.html";
}

function requireAdmin() {
  requireAuth();
  const u = getUser();
  if (!u || u.role !== "admin") window.location.href = "/classes.html";
}

async function api(method, path, body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  const token = getToken();
  if (token) opts.headers["Authorization"] = `Bearer ${token}`;
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(BASE + path, opts);
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function showAlert(container, msg, type = "error") {
  const el = document.querySelector(container);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
  setTimeout(() => { el.innerHTML = ""; }, 4000);
}

function formatDate(dt) {
  return new Date(dt).toLocaleString("en-IN", {
    dateStyle: "medium", timeStyle: "short"
  });
}

function categoryBadge(cat) {
  const map = { yoga: "badge-yoga", hiit: "badge-hiit", strength: "badge-strength" };
  const cls = map[cat?.toLowerCase()] || "badge-default";
  return `<span class="badge ${cls}">${cat}</span>`;
}

function setNavUser() {
  const u = getUser();
  if (!u) return;
  const nameEl = document.getElementById("nav-username");
  if (nameEl) nameEl.textContent = u.name;
  const adminLinks = document.querySelectorAll(".admin-only");
  adminLinks.forEach(el => el.style.display = u.role === "admin" ? "" : "none");
}
