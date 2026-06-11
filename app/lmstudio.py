"""LM Studio client (OpenAI-compatible) for generating and judging content."""
from __future__ import annotations

import json
import re

from . import db, curriculum

TIMEOUT = 30  # quick calls: models list, test connection
GENERATE_TIMEOUT = 120  # per chunk when creating problems
GENERATE_CHUNK = 5  # problems per LM request (smaller = faster first response)

_SESSION = None


def _client():
    """A requests session that ignores environment proxies.

    LM Studio runs locally (localhost), so its traffic must go DIRECT. On machines
    with a corporate proxy (e.g. an iboss PAC pointing everything at 127.0.0.1:8009),
    honoring HTTP(S)_PROXY would wrongly route the local call through the proxy and fail.
    trust_env=False bypasses that for these local calls only.
    """
    global _SESSION
    if _SESSION is None:
        import requests
        s = requests.Session()
        s.trust_env = False
        _SESSION = s
    return _SESSION


class LMStudioError(RuntimeError):
    pass


def get_config() -> tuple[str, str]:
    url = (db.get_setting("lmstudio_url") or "http://localhost:1234/v1").rstrip("/")
    model = db.get_setting("lmstudio_model") or ""
    return url, model


def list_models(url: str | None = None) -> list[str]:
    if url is None:
        url, _ = get_config()
    resp = _client().get(f"{url}/models", timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return [m.get("id") for m in data if m.get("id")]


def resolve_model(url: str, model: str) -> str:
    if model:
        return model
    models = list_models(url)
    if not models:
        raise LMStudioError("No model is loaded in LM Studio.")
    return models[0]


def test_connection() -> dict:
    url, model = get_config()
    try:
        models = list_models(url)
        chosen = model or (models[0] if models else None)
        return {"ok": bool(models), "url": url, "models": models, "model": chosen}
    except Exception as exc:  # noqa: BLE001 - surfaced to the parent dashboard
        return {"ok": False, "url": url, "error": str(exc)}


def _chat(messages: list[dict], temperature: float = 0.7, max_tokens: int = 1200, *, timeout: float | None = None) -> str:
    url, model = get_config()
    model = resolve_model(url, model)
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    resp = _client().post(
        f"{url}/chat/completions",
        json=payload,
        timeout=timeout if timeout is not None else TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


_JSON_BLOCK = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _extract_json(text: str):
    text = text.strip()
    m = _JSON_BLOCK.search(text)
    if m:
        text = m.group(1).strip()
    # Grab the outermost array or object.
    for opener, closer in (("[", "]"), ("{", "}")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    return json.loads(text)  # last resort, may raise


def _valid_problem(item: dict, input_type: str) -> bool:
    if not all(k in item for k in ("prompt", "answer", "explanation", "hint")):
        return False
    if input_type == "multiple_choice":
        opts = item.get("options")
        if not isinstance(opts, list) or len(opts) < 2:
            return False
        ans = str(item["answer"]).strip()
        norm_opts = [str(o).strip() for o in opts]
        if ans not in norm_opts:
            # Model often paraphrases the answer — snap to the closest option text.
            ans_l = ans.lower()
            for o in norm_opts:
                if o.lower() == ans_l or ans_l in o.lower() or o.lower() in ans_l:
                    item["answer"] = o
                    return True
            return False
    return True


def _generate_chunk(subject: str, level: int, count: int, skill: str, guide: str) -> list[dict]:
    """Ask LM Studio for up to `count` problems in one request."""
    meta = curriculum.SUBJECTS[subject]
    input_type = meta["input"]
    shape = (
        '{"prompt": "...", "type": "multiple_choice", "options": ["A","B","C","D"], '
        '"answer": "<exactly one of options>", "explanation": "...", "hint": "..."}'
        if input_type == "multiple_choice"
        else '{"prompt": "...", "type": "numeric", "answer": "<number only>", '
        '"explanation": "...", "hint": "..."}'
    )
    system = (
        "You are a friendly tutor creating practice problems for a 6-9 year old child. "
        "Use simple, warm, age-appropriate language. Keep each problem self-contained "
        "(include any short reading passage inside the prompt). "
        "Explanations must be kind and clear (1-2 short sentences). "
        "Hints must nudge without giving the answer (1 short sentence). "
        "Respond with ONLY a JSON array, no extra text."
    )
    user = (
        f"Create {count} '{meta['label']}' problems at skill level: {skill}. "
        f"Content guidance: {guide}. "
        f"Each item must be a JSON object exactly like: {shape}. "
        f"Return a JSON array of {count} such objects."
    )
    last_err: Exception | None = None
    for attempt in range(2):
        try:
            raw = _chat(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.8 if attempt == 0 else 0.4,
                max_tokens=min(4000, 350 * count + 200),
                timeout=GENERATE_TIMEOUT,
            )
            data = _extract_json(raw)
            if isinstance(data, dict):
                data = [data]
            problems = []
            for item in data:
                if not isinstance(item, dict) or not _valid_problem(item, input_type):
                    continue
                problems.append(
                    {
                        "prompt": str(item["prompt"]).strip(),
                        "type": input_type,
                        "options": [str(o).strip() for o in item.get("options", [])] or None,
                        "answer": str(item["answer"]).strip(),
                        "explanation": str(item["explanation"]).strip(),
                        "hint": str(item["hint"]).strip(),
                        "skill": skill,
                        "source": "lmstudio",
                    }
                )
            if problems:
                return problems
            last_err = LMStudioError("Model returned no valid problems.")
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise LMStudioError(str(last_err) if last_err else "Generation failed.")


def generate_problems(subject: str, level: int, count: int) -> list[dict]:
    """Ask LM Studio for `count` problems in small chunks. Raises on total failure."""
    skill = curriculum.skill_for(subject, level)
    guide = curriculum.guide_for(subject, level)
    problems: list[dict] = []
    seen_prompts: set[str] = set()
    remaining = count
    while remaining > 0 and len(problems) < count:
        chunk = min(GENERATE_CHUNK, count - len(problems))
        batch = _generate_chunk(subject, level, chunk, skill, guide)
        added = 0
        for p in batch:
            if p["prompt"] in seen_prompts:
                continue
            seen_prompts.add(p["prompt"])
            problems.append(p)
            added += 1
            if len(problems) >= count:
                break
        if added == 0:
            break
        remaining = count - len(problems)
    if problems:
        return problems[:count]
    raise LMStudioError("Generation failed.")


def judge_short(prompt: str, expected: str, given: str) -> tuple[bool, str]:
    """Judge a free-text answer. Returns (correct, kid_friendly_explanation)."""
    system = (
        "You grade a young child's answer kindly and leniently (ignore spelling/case). "
        'Respond ONLY as JSON: {"correct": true/false, "explanation": "..."}.'
    )
    user = (
        f"Question: {prompt}\nExpected answer: {expected}\nChild's answer: {given}\n"
        "Is the child's answer correct? Give a short, warm explanation."
    )
    raw = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=200,
    )
    data = _extract_json(raw)
    return bool(data.get("correct")), str(data.get("explanation", "")).strip()
