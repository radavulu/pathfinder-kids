"""Hybrid answer validation.

- numeric  -> exact local check with normalization (0.5 == 1/2 == "1 / 2").
- multiple_choice -> local exact match against the correct option (index or text).
- short    -> LM Studio judge (in lmstudio.py); this module provides a lenient fallback.
"""
from __future__ import annotations

import re
from fractions import Fraction

_NUM_CLEAN = re.compile(r"[\s$,]")


def normalize_numeric(value: str) -> float | None:
    if value is None:
        return None
    s = _NUM_CLEAN.sub("", str(value)).strip()
    if not s:
        return None
    try:
        if "/" in s:
            return float(Fraction(s))
        return float(s)
    except (ValueError, ZeroDivisionError):
        return None


def check_numeric(given: str, answer: str, tol: float = 1e-6) -> bool:
    g = normalize_numeric(given)
    a = normalize_numeric(answer)
    if g is None or a is None:
        # Fall back to trimmed string compare if either side isn't numeric.
        return str(given).strip().lower() == str(answer).strip().lower()
    return abs(g - a) <= tol


def _norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def check_multiple_choice(given: str, answer: str, options: list[str] | None) -> bool:
    given_n = _norm_text(given)
    answer_n = _norm_text(answer)
    if given_n == answer_n:
        return True
    # Allow answering by index ("2" or "B") when options are known.
    if options:
        # numeric index (1-based or 0-based)
        if given_n.isdigit():
            idx = int(given_n)
            for i in (idx, idx - 1):
                if 0 <= i < len(options) and _norm_text(options[i]) == answer_n:
                    return True
        # letter index A/B/C/D
        if len(given_n) == 1 and given_n.isalpha():
            i = ord(given_n) - ord("a")
            if 0 <= i < len(options) and _norm_text(options[i]) == answer_n:
                return True
    return False


def check_quotient_remainder(given: str, answer: str) -> bool:
    """Compare 'quotient R remainder' answers, tolerant of spaces/case (e.g. '35 r 16' == '35R16')."""
    def norm(s: str) -> str:
        return re.sub(r"\s+", "", str(s)).upper().replace("REMAINDER", "R")
    return norm(given) == norm(answer)


def check_short_fallback(given: str, answer: str) -> bool:
    """Spelling-lenient fallback when the model judge is unavailable."""
    g, a = _norm_text(given), _norm_text(answer)
    if not g:
        return False
    if g == a:
        return True
    # accept if the kid's answer contains the key answer or vice versa (short answers only)
    return a in g or g in a
