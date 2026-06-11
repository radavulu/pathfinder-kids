// Parent dashboard.
const $ = (id) => document.getElementById(id);
const SUBJECTS = ["math", "reading", "logic"];
let PALETTES = ["Ocean", "Sunset", "Meadow", "Grape", "Bubblegum", "Sky", "Mango", "Berry"];

async function loadOverview() {
  const data = await api("/api/parent/overview");
  $("dataInfo").innerHTML =
    `Database: <code>${data.data_dir}</code><br/>Source: ${data.data_dir_source}` +
    `<br/><span class="note">Kids' progress is stored in the database file shown above (./data by default).</span>`;
  const box = $("overview");
  box.innerHTML = "";
  data.children.forEach((c) => box.appendChild(kidCard(c)));
}

function kidCard(c) {
  const card = el("div", { class: "card" });
  card.style.borderTop = `6px solid ${c.theme.primary}`;
  card.appendChild(el("h2", { style: "margin-top:0" }, `${c.name} · age ${c.age}`));
  card.appendChild(el("div", {}, [
    el("span", { class: "pill" }, "⭐ " + c.stars),
    el("span", { class: "pill" }, "🔥 " + c.streak + " day streak"),
    ...c.badges.map((b) => el("span", { class: "pill" }, "🏅 " + b)),
  ]));

  // progress table
  const table = el("table", { class: "section-block" });
  table.appendChild(el("tr", {}, [
    el("th", {}, "Subject"), el("th", {}, "Level"), el("th", {}, "Skill"),
    el("th", {}, "Accuracy"), el("th", {}, "Answered"), el("th", {}, "Today"),
    el("th", {}, "Time spent"),
  ]));
  c.subjects.forEach((s) => {
    table.appendChild(el("tr", {}, [
      el("td", {}, s.label),
      el("td", {}, String(s.level)),
      el("td", {}, s.skill),
      el("td", {}, Math.round(s.accuracy * 100) + "%"),
      el("td", {}, String(s.total_answered)),
      el("td", {}, String(s.today_answered)),
      el("td", {}, `${s.minutes_spent_total}m (today ${s.minutes_spent_today}m)`),
    ]));
  });
  card.appendChild(table);

  card.appendChild(difficultyPanel(c));

  const genRow = el("div", { class: "section-block" });
  const genBtn = el("button", { class: "btn ghost", type: "button" }, `Generate new sets for ${c.name}`);
  genBtn.addEventListener("click", () => generateSets(c.id, c.name));
  genRow.appendChild(genBtn);
  card.appendChild(genRow);

  card.appendChild(resetPanel(c));

  // settings
  const det = el("details", { class: "section-block" });
  det.appendChild(el("summary", { class: "details-summary" }, "Settings"));
  det.appendChild(settingsForm(c));
  card.appendChild(det);

  // history
  const hist = el("details", { class: "section-block" });
  hist.appendChild(el("summary", { class: "details-summary" }, "Answer history"));
  const histBody = el("div", { class: "section-block" }, el("button", { class: "btn ghost", type: "button" }, "Load history"));
  histBody.querySelector("button").addEventListener("click", () => loadHistory(c.id, histBody));
  hist.appendChild(histBody);
  card.appendChild(hist);

  return card;
}

function difficultyPanel(c) {
  const box = el("div", { class: "difficulty-panel" });
  box.appendChild(el("h3", { class: "difficulty-title" }, "Difficulty (intensity)"));
  box.appendChild(el("p", { class: "note difficulty-help" },
    "Use Easier or Harder to change intensity. Today's unserved problems refresh at the new level. Kids can tap “Too hard?” after a session."));
  c.subjects.forEach((s) => {
    const row = el("div", { class: "diff-row" });
    const info = el("div", { class: "diff-info" });
    info.appendChild(el("strong", {}, s.label));
    info.appendChild(el("div", { class: "note" }, `Level ${s.level}/${s.max_level} · ${s.skill}`));
    row.appendChild(info);
    const btns = el("div", { class: "diff-btns" });
    const easier = el("button", { class: "btn ghost", type: "button" }, "Easier");
    const harder = el("button", { class: "btn ghost", type: "button" }, "Harder");
    const msg = el("span", { class: "note diff-msg" }, "");
    easier.disabled = s.level <= 1;
    harder.disabled = s.level >= s.max_level;
    easier.addEventListener("click", () => adjustLevel(c.id, s.subject, -1, msg, easier, harder, s));
    harder.addEventListener("click", () => adjustLevel(c.id, s.subject, 1, msg, easier, harder, s));
    btns.appendChild(easier);
    btns.appendChild(harder);
    btns.appendChild(msg);
    row.appendChild(btns);
    box.appendChild(row);
  });
  return box;
}

function resetPanel(c) {
  const box = el("div", { class: "reset-panel section-block" });
  box.appendChild(el("h3", { class: "difficulty-title" }, "Reset (testing)"));
  box.appendChild(el("p", { class: "note" },
    "Clears stored progress in the database and optionally generates fresh problem sets."));
  const row = el("div", { class: "btn-row" });
  const msg = el("span", { class: "note reset-msg" }, "");
  const todayBtn = el("button", { class: "btn ghost", type: "button" }, "Reset today");
  const allBtn = el("button", { class: "btn btn-danger", type: "button" }, "Full reset");
  todayBtn.addEventListener("click", () => resetChild(c.id, c.name, "today", msg));
  allBtn.addEventListener("click", () => resetChild(c.id, c.name, "all", msg));
  row.appendChild(todayBtn);
  row.appendChild(allBtn);
  row.appendChild(msg);
  box.appendChild(row);
  return box;
}

async function resetChild(childId, name, scope, msgEl) {
  const desc = scope === "today"
    ? "today's answers, sessions, and problems"
    : "ALL progress (stars, badges, history, levels) and restore default levels";
  if (!confirm(`Reset ${name}?\n\nThis will clear ${desc}.`)) return;
  msgEl.textContent = "Resetting…";
  try {
    const r = await api(`/api/parent/${childId}/reset?scope=${scope}&regenerate=true`, { method: "POST" });
    const n = r.removed;
    msgEl.textContent = scope === "today"
      ? `✓ Today cleared (${n.answers} answers, ${n.problems} problems)`
      : `✓ Full reset (${n.answers} answers, ⭐ reset, levels restored)`;
    loadOverview();
  } catch (e) {
    msgEl.textContent = "Error: " + e.message;
  }
}

async function adjustLevel(childId, subject, delta, msgEl, easierBtn, harderBtn, subj) {
  msgEl.textContent = "…";
  try {
    const r = await api(`/api/parent/${childId}/adjust-level`, {
      method: "POST",
      body: JSON.stringify({ subject, delta }),
    });
    if (!r.changed) {
      msgEl.textContent = "Already at the limit.";
    } else {
      msgEl.textContent = r.regenerated
        ? `Now: ${r.new_skill} ✓ (today's queue refreshed)`
        : `Now: ${r.new_skill} ✓`;
      subj.level = r.new_level;
      subj.skill = r.new_skill;
      easierBtn.disabled = r.new_level <= 1;
      harderBtn.disabled = r.new_level >= subj.max_level;
      loadOverview();
    }
  } catch (e) {
    msgEl.textContent = "Error: " + e.message;
  }
}

function settingsForm(c) {
  const form = el("div", { style: "margin-top:10px" });
  form.appendChild(el("label", {}, "Name"));
  const name = el("input", { value: c.name });
  form.appendChild(name);

  form.appendChild(el("label", {}, "Color theme"));
  const pal = el("select");
  PALETTES.forEach((p) => {
    const o = el("option", { value: p }, p);
    if (p === c.palette) o.setAttribute("selected", "selected");
    pal.appendChild(o);
  });
  form.appendChild(pal);

  form.appendChild(el("label", {}, "Time per subject (minutes)"));
  const tRow = el("div", { class: "row" });
  const tInputs = {};
  c.subjects.forEach((s) => {
    const wrap = el("div", {});
    wrap.appendChild(el("div", { class: "note" }, s.label));
    const inp = el("input", { type: "number", min: "1", max: "60", value: String(s.minutes) });
    tInputs[s.subject] = inp;
    wrap.appendChild(inp);
    tRow.appendChild(wrap);
  });
  form.appendChild(tRow);

  form.appendChild(el("label", {}, "Level per subject (advanced)"));
  const lRow = el("div", { class: "row" });
  const lInputs = {};
  c.subjects.forEach((s) => {
    const wrap = el("div", {});
    wrap.appendChild(el("div", { class: "note" }, s.label));
    const inp = el("input", { type: "number", min: "1", max: String(s.max_level || 20), value: String(s.level) });
    lInputs[s.subject] = inp;
    wrap.appendChild(inp);
    lRow.appendChild(wrap);
  });
  form.appendChild(lRow);

  const save = el("button", { class: "btn", style: "margin-top:12px" }, "Save settings");
  const msg = el("span", { class: "note", style: "margin-left:10px" }, "");
  save.addEventListener("click", async () => {
    const body = {
      name: name.value.trim(),
      palette: pal.value,
      time_targets: Object.fromEntries(SUBJECTS.map((s) => [s, Number(tInputs[s].value)])),
      levels: Object.fromEntries(SUBJECTS.map((s) => [s, Number(lInputs[s].value)])),
    };
    try {
      await api(`/api/parent/${c.id}/settings`, { method: "POST", body: JSON.stringify(body) });
      msg.textContent = "Saved ✓";
      loadOverview();
    } catch (e) { msg.textContent = "Error: " + e.message; }
  });
  form.appendChild(save);
  form.appendChild(msg);
  return form;
}

async function loadHistory(childId, container) {
  const data = await api(`/api/parent/${childId}/history?limit=50`);
  container.innerHTML = "";
  if (!data.history.length) {
    container.appendChild(el("p", { class: "note" }, "No answers recorded yet."));
    return;
  }
  const table = el("table");
  table.appendChild(el("tr", {}, [
    el("th", {}, "When"), el("th", {}, "Subject"), el("th", {}, "Question"),
    el("th", {}, "Their answer"), el("th", {}, "Correct?"), el("th", {}, "Right answer"),
  ]));
  data.history.forEach((h) => {
    table.appendChild(el("tr", {}, [
      el("td", {}, (h.created_at || "").replace("T", " ")),
      el("td", {}, h.subject),
      el("td", {}, h.prompt),
      el("td", {}, h.given || ""),
      el("td", { class: h.correct ? "tag-ok" : "tag-bad" }, h.correct ? "✓" : "✗"),
      el("td", {}, h.answer),
    ]));
  });
  container.appendChild(table);
}

async function generateSets(childId, childName) {
  const label = childName || "all kids";
  showGenOverlay(`Generating for ${label}…`);
  try {
    const query = childId ? `?child_id=${childId}&refresh=true` : "?refresh=true";
    const data = await api(`/api/parent/generate${query}`, { method: "POST", timeoutMs: 600000 });
    hideGenOverlay();
    renderGenResult(data, childName);
  } catch (err) {
    hideGenOverlay();
    $("genResult").textContent = "Could not generate: " + err.message;
  }
}

let genTimerId = null;
let genStartMs = 0;

function showGenOverlay(title) {
  $("genTitle").textContent = title;
  $("genStatus").textContent = "Talking to LM Studio. Math is fast; Reading & Logic take longer.";
  $("genTimer").textContent = "0:00";
  $("genOverlay").classList.remove("hidden");
  $("genAll").disabled = true;
  genStartMs = Date.now();
  clearInterval(genTimerId);
  genTimerId = setInterval(() => {
    $("genTimer").textContent = formatElapsed(Date.now() - genStartMs);
  }, 250);
}

function hideGenOverlay() {
  $("genOverlay").classList.add("hidden");
  $("genAll").disabled = false;
  clearInterval(genTimerId);
}

function renderGenResult(data, childName) {
  const lines = Object.entries(data.results).map(([cid, subs]) => {
    const parts = subs.map((s) => `${s.subject}: +${s.inserted} (${s.source})`);
    const who = childName || `Child ${cid}`;
    return `${who} — ${parts.join(", ")}`;
  });
  const elapsed = data.elapsed_seconds != null ? ` · ${data.elapsed_seconds}s` : "";
  $("genResult").innerHTML = `✓ Fresh sets for <b>${data.day}</b>${elapsed}:<br/>${lines.join("<br/>")}`;
}

async function loadLM() {
  const c = await api("/api/parent/lmstudio");
  $("lmUrl").value = c.url || "";
  $("lmModel").value = c.model || "";
}

async function loadMascot() {
  const c = await api("/api/parent/mascot");
  $("mascotName").value = c.mascot || "";
}

$("genAll").addEventListener("click", () => generateSets(null, null));
$("lmSave").addEventListener("click", async () => {
  await api("/api/parent/lmstudio", { method: "POST", body: JSON.stringify({ url: $("lmUrl").value, model: $("lmModel").value }) });
  $("lmStatus").textContent = "Saved ✓";
});
$("lmTest").addEventListener("click", async () => {
  $("lmStatus").textContent = "Testing…";
  const r = await api("/api/parent/lmstudio/test", { method: "POST" });
  if (r.ok) $("lmStatus").innerHTML = `✓ Connected. Model in use: <b>${r.model || "(auto)"}</b>. Available: ${r.models.join(", ") || "none"}`;
  else $("lmStatus").textContent = "✗ Not reachable: " + (r.error || "check that LM Studio's server is running.");
});

$("mascotSave").addEventListener("click", async () => {
  const r = await api("/api/parent/mascot", { method: "POST", body: JSON.stringify({ name: $("mascotName").value }) });
  $("mascotName").value = r.mascot;
  $("mascotStatus").textContent = "Saved ✓";
});

loadOverview().catch((e) => alert("Could not load dashboard: " + e.message));
loadLM().catch(() => {});
loadMascot().catch(() => {});
