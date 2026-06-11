// Shared helpers for Home Kumon.

function formatElapsed(ms) {
  const sec = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

async function api(path, opts = {}) {
  const timeoutMs = opts.timeoutMs ?? apiTimeoutFor(path);
  const { timeoutMs: _ignored, ...fetchOpts } = opts;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...fetchOpts,
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        detail = (await res.json()).detail || detail;
      } catch (_err) {
        /* non-JSON error body */
      }
      throw new Error(detail);
    }
    return res.json();
  } catch (err) {
    if (err.name === "AbortError") {
      const mins = Math.round(timeoutMs / 60000);
      throw new Error(
        `Request timed out after ${mins || 1} min — LM Studio may still be working. ` +
        "Wait a moment, then try again or use Generate new sets from the parent dashboard first.",
      );
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

/** Long-running routes need more time than quick dashboard reads. */
function apiTimeoutFor(path) {
  if (path.includes("/api/parent/generate") || path.includes("/reset")) return 900000; // 15 min
  if (path.includes("/adjust-level")) return 300000; // 5 min (may regenerate sets)
  if (path.includes("/api/kid/") && path.includes("/next")) return 180000; // 3 min first fetch
  return 30000;
}

function applyTheme(theme) {
  if (!theme) return;
  const r = document.documentElement.style;
  r.setProperty("--primary", theme.primary);
  r.setProperty("--accent", theme.accent);
  r.setProperty("--bg", theme.bg);
}

function qs(name) {
  return new URLSearchParams(location.search).get(name);
}

function el(tag, props = {}, children = []) {
  const e = document.createElement(tag);
  Object.entries(props).forEach(([k, v]) => {
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  });
  (Array.isArray(children) ? children : [children]).forEach((c) => {
    if (c == null) return;
    e.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  });
  return e;
}

// A cheerful star mascot ("Sparky"). mood: happy | cheer | think | sad
function mascotSVG(mood = "happy", color = "#FFC940") {
  const eyes = mood === "think"
    ? '<circle cx="38" cy="46" r="4"/><circle cx="62" cy="46" r="4"/>'
    : '<circle cx="38" cy="44" r="5"/><circle cx="62" cy="44" r="5"/>';
  let mouth;
  if (mood === "sad") mouth = '<path d="M38 64 Q50 56 62 64" stroke="#5a3d00" stroke-width="4" fill="none" stroke-linecap="round"/>';
  else if (mood === "cheer") mouth = '<path d="M36 58 Q50 76 64 58" stroke="#5a3d00" stroke-width="5" fill="#fff"/>';
  else mouth = '<path d="M38 58 Q50 70 62 58" stroke="#5a3d00" stroke-width="4" fill="none" stroke-linecap="round"/>';
  return `<svg class="mascot" viewBox="0 0 100 100" fill="${color}" stroke="#e0a900" stroke-width="2">
    <path d="M50 6 L61 38 L95 38 L67 58 L78 92 L50 71 L22 92 L33 58 L5 38 L39 38 Z"/>
    <g fill="#5a3d00" stroke="none">${eyes}</g>${mouth}
  </svg>`;
}

function confettiBurst(n = 90) {
  let layer = document.getElementById("confetti");
  if (!layer) { layer = el("div", { id: "confetti" }); document.body.appendChild(layer); }
  const colors = ["#FF7B54", "#2E8BC0", "#43A047", "#EC407A", "#F4A100", "#8E44AD"];
  for (let i = 0; i < n; i++) {
    const bit = el("div", { class: "confetti-bit" });
    bit.style.left = Math.random() * 100 + "vw";
    bit.style.background = colors[i % colors.length];
    bit.style.animationDuration = 2 + Math.random() * 2 + "s";
    bit.style.animationDelay = Math.random() * 0.6 + "s";
    layer.appendChild(bit);
    setTimeout(() => bit.remove(), 4500);
  }
}

function initials(name) {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
