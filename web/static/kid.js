// Kid session flow.
const childId = qs("child");
let today = null;
let cur = null;            // current problem
let attempt = 1;
let typed = "";
let sub = null;           // current subject key
let secs = 0;
let startMs = 0;          // wall-clock start of the current subject session
let timerId = null;
let timeUp = false;
let busy = false;
let sessionStats = { done: 0, correct: 0, wrong: 0 };

const $ = (id) => document.getElementById(id);

function setSessionLayout(active) {
  document.querySelector(".wrap")?.classList.toggle("session-active", active);
}

function resetSessionStats() {
  sessionStats = { done: 0, correct: 0, wrong: 0 };
  renderSessionStats();
}

function renderSessionStats() {
  $("statDone").textContent = sessionStats.done;
  $("statCorrect").textContent = sessionStats.correct;
  $("statWrong").textContent = sessionStats.wrong;
}

function recordAnswer(outcome) {
  sessionStats.done += 1;
  if (outcome === "correct") sessionStats.correct += 1;
  else sessionStats.wrong += 1;
  renderSessionStats();
}

function showCoach(kind, label, body, extra) {
  const panel = $("coachPanel");
  const extraEl = $("coachExtra");
  panel.classList.remove("hidden", "coach-ok", "coach-hint", "coach-bad");
  panel.classList.add(`coach-${kind}`);
  $("coachLabel").textContent = label;
  $("coachBody").textContent = body;
  if (extra) {
    extraEl.textContent = extra;
    extraEl.classList.remove("hidden");
  } else {
    extraEl.textContent = "";
    extraEl.classList.add("hidden");
  }
}

function hideCoach() {
  $("coachPanel").classList.add("hidden");
  $("coachExtra").classList.add("hidden");
}

async function loadToday() {
  setSessionLayout(false);
  today = await api(`/api/kid/${childId}/today`);
  applyTheme(today.child.theme);
  $("mascot").innerHTML = mascotSVG("happy");
  $("kidName").textContent = today.child.name;
  $("stars").textContent = today.child.stars;
  $("streak").textContent = today.child.streak;
  const box = $("subjects");
  box.innerHTML = "";
  today.subjects.forEach((s) => {
    const tile = el("div", { class: "card subject-tile" });
    tile.appendChild(el("div", { class: "ico" }, s.icon));
    tile.appendChild(el("div", { class: "meta" }, [
      el("h3", {}, `${s.label}  ·  Level ${s.level}`),
      el("small", {}, s.skill),
      el("div", {}, el("small", {}, `🎯 ${s.minutes} min · done today: ${s.answered}`)),
    ]));
    tile.appendChild(el("div", {}, "▶"));
    tile.addEventListener("click", () => startSubject(s));
    box.appendChild(tile);
  });
  show("todayView");
}

function show(view) {
  ["todayView", "sessionView", "celebrateView"].forEach((v) => $(v).classList.toggle("hidden", v !== view));
  setSessionLayout(view === "sessionView");
}

function startSubject(s) {
  sub = s.subject;
  secs = s.minutes * 60;
  startMs = Date.now();
  timeUp = false;
  resetSessionStats();
  hideCoach();
  $("timer").classList.remove("low");
  show("sessionView");
  startTimer();
  loadNext();
}

function startTimer() {
  clearInterval(timerId);
  renderTimer();
  timerId = setInterval(() => {
    secs--;
    renderTimer();
    if (secs <= 0) { clearInterval(timerId); timeUp = true; }
  }, 1000);
}

function renderTimer() {
  const m = Math.max(0, Math.floor(secs / 60));
  const s = Math.max(0, secs % 60);
  $("timer").textContent = `${m}:${String(s).padStart(2, "0")}`;
  $("timer").classList.toggle("low", secs <= 30);
}

async function loadNext() {
  if (timeUp) return endSession();
  hideCoach();
  attempt = 1; typed = "";
  try {
    cur = await api(`/api/kid/${childId}/next?subject=${sub}`);
  } catch (e) {
    $("problem").textContent = "All done for now! 🎉";
    return setTimeout(endSession, 1200);
  }
  $("skillTag").textContent = cur.skill;
  $("problem").textContent = cur.prompt;
  renderAnswerArea();
}

function renderAnswerArea() {
  const area = $("answerArea");
  area.innerHTML = "";
  if (cur.type === "multiple_choice") {
    const grid = el("div", { class: "options" });
    cur.options.forEach((opt) => {
      const b = el("button", { class: "opt" }, opt);
      b.addEventListener("click", () => submit(opt, b));
      grid.appendChild(b);
    });
    area.appendChild(grid);
  } else {
    const isQR = cur.type === "quotient_remainder";
    if (isQR) {
      area.appendChild(el("div", { class: "note", style: "text-align:center;margin-bottom:6px" },
        "Type the quotient, then R, then the remainder (e.g. 35R16)"));
    }
    const boxEl = el("div", { class: "answer-box", id: "typed" }, "·");
    area.appendChild(boxEl);
    const pad = el("div", { class: "keypad" });
    const keys = isQR
      ? ["1","2","3","4","5","6","7","8","9","R","0","⌫"]
      : ["1","2","3","4","5","6","7","8","9","⌫","0","C"];
    keys.forEach((k) => {
      const b = el("button", { class: "key" }, k);
      b.addEventListener("click", () => press(k));
      pad.appendChild(b);
    });
    area.appendChild(pad);
    const check = el("button", { class: "btn big", style: "display:block;margin:14px auto 0" }, "Check ✓");
    check.addEventListener("click", () => { if (typed !== "") submit(typed, null); });
    area.appendChild(check);
  }
}

function press(k) {
  if (k === "C") typed = "";
  else if (k === "⌫") typed = typed.slice(0, -1);
  else if (typed.length < 8) typed += k;
  const t = $("typed"); if (t) t.textContent = typed || "·";
}

async function submit(answer, btn) {
  if (busy) return;
  busy = true;
  try {
    const r = await api(`/api/kid/${childId}/answer`, {
      method: "POST",
      body: JSON.stringify({ problem_id: cur.problem_id, answer, attempt }),
    });
    handleResult(r, btn);
  } catch (e) {
    showCoach("bad", "Oops", e.message);
  } finally {
    busy = false;
  }
}

function handleResult(r, btn) {
  if (r.correct) {
    if (btn) btn.classList.add("correct");
    recordAnswer("correct");
    showCoach("ok", "Great job!", r.praise || "Correct!", null);
    $("mascot").innerHTML = mascotSVG("cheer");
    if (typeof r.stars === "number") $("stars").textContent = r.stars;
    confettiBurst(28);
    if (r.new_badges && r.new_badges.length) {
      showCoach("ok", "Great job!", r.praise || "Correct!", "🏅 New badge: " + r.new_badges.join(", "));
    }
    setTimeout(loadNext, 1100);
    return;
  }
  if (!r.reveal) {
    if (btn) { btn.classList.add("wrong"); btn.disabled = true; }
    const hintText = r.hint || r.nudge || "Try again!";
    showCoach("hint", "💡 Hint", hintText, "You get one more try!");
    $("mascot").innerHTML = mascotSVG("think");
    attempt = 2;
    if (cur.type !== "multiple_choice") { typed = ""; const t = $("typed"); if (t) t.textContent = "·"; }
    return;
  }
  if (btn) btn.classList.add("wrong");
  recordAnswer("wrong");
  showCoach(
    "bad",
    "Let's learn",
    "The answer is: " + (r.correct_answer || ""),
    r.explanation || "",
  );
  $("mascot").innerHTML = mascotSVG("happy");
  if (typeof r.stars === "number") $("stars").textContent = r.stars;
  setTimeout(loadNext, 2200);
}

async function endSession() {
  clearInterval(timerId);
  setSessionLayout(false);
  const elapsed = startMs ? Math.round((Date.now() - startMs) / 1000) : 0;
  const r = await api(`/api/kid/${childId}/finish?subject=${sub}&seconds=${elapsed}`, { method: "POST" });
  $("celebMascot").innerHTML = mascotSVG("cheer");
  const pct = Math.round((r.accuracy || 0) * 100);
  $("celebTitle").textContent = r.leveled_up ? "Level up! 🚀" : "Great work! 🎉";
  let body = r.total
    ? `You answered ${r.total} (${sessionStats.correct} right, ${sessionStats.wrong} to learn from) — ${pct}% correct.`
    : "Come back soon for more!";
  if (r.leveled_up) body += ` You moved up to "${r.new_skill}"!`;
  $("celebBody").textContent = body;
  const badges = $("celebBadges"); badges.innerHTML = "";
  (r.badges || []).forEach((b) => badges.appendChild(el("span", { class: "badge" }, "🏅 " + b)));
  const easierBtn = $("easierBtn");
  easierBtn.classList.remove("hidden");
  easierBtn.textContent = "Too hard? Make it easier next time";
  easierBtn.onclick = async () => {
    easierBtn.disabled = true;
    try {
      const adj = await api(`/api/kid/${childId}/adjust-level?subject=${sub}&delta=-1`, { method: "POST" });
      if (adj.changed) {
        easierBtn.textContent = adj.regenerated
          ? `Next time will be easier: ${adj.new_skill} ✓ (new problems ready)`
          : `Next time will be easier: ${adj.new_skill} ✓`;
      } else {
        easierBtn.textContent = "You're already at the easiest level here!";
      }
    } catch (e) {
      easierBtn.textContent = "Could not change — ask a parent";
      easierBtn.disabled = false;
    }
  };
  confettiBurst(140);
  show("celebrateView");
}

$("doneBtn").addEventListener("click", () => { if (!busy) endSession(); });
$("backBtn").addEventListener("click", loadToday);

if (!childId) location.href = "/";
loadToday().catch((e) => alert("Could not load: " + e.message));
