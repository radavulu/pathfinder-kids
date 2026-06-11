"""Subject definitions and per-subject level ladders.

Levels are 1-indexed. Each entry has a short `skill` (kid-facing-ish) and a `guide`
string used to steer LM Studio generation. Everything here is tunable; adaptive
leveling moves a child up the ladder, never down (per design).
"""
from __future__ import annotations

# Input/answer style per subject (drives the kid UI and validation path).
SUBJECTS = {
    "math": {"label": "Math", "input": "numeric", "icon": "🔢"},
    "reading": {"label": "Reading", "input": "multiple_choice", "icon": "📖"},
    "logic": {"label": "Logic", "input": "multiple_choice", "icon": "🧩"},
}

LADDERS: dict[str, list[dict]] = {
    "math": [
        {"skill": "Adding within 10", "guide": "single-digit addition, sums up to 10"},
        {"skill": "Subtracting within 10", "guide": "single-digit subtraction, no negatives, within 10"},
        {"skill": "Adding within 20", "guide": "addition with sums up to 20"},
        {"skill": "Subtracting within 20", "guide": "subtraction within 20, no negatives"},
        {"skill": "Add & subtract within 100 (no regrouping)", "guide": "2-digit add/subtract without carrying or borrowing"},
        {"skill": "Add & subtract within 100 (regrouping)", "guide": "2-digit add/subtract with carrying/borrowing"},
        {"skill": "Beginning multiplication (×2, ×5, ×10)", "guide": "multiplication facts for 2, 5, and 10 only"},
        {"skill": "Multiplication facts to ×5", "guide": "multiplication tables 1-5"},
        {"skill": "Multiplication facts to ×10", "guide": "multiplication tables 1-10"},
        {"skill": "Simple division", "guide": "division facts that are the inverse of the ×1-10 tables, whole results only"},
        {"skill": "Halves & quarters (intro fractions)", "guide": "identify 1/2 and 1/4 of small even numbers; answer as a whole number"},
        {"skill": "Multiply 2-digit × 1-digit", "guide": "a 2-digit number times a 1-digit number, with carrying"},
        {"skill": "Multiply 3-digit × 1-digit", "guide": "a 3-digit number times a 1-digit number, with carrying"},
        {"skill": "Multiply 2-digit × 2-digit", "guide": "two 2-digit numbers, standard algorithm"},
        {"skill": "Multiply 3-digit × 2-digit", "guide": "a 3-digit number times a 2-digit number"},
        {"skill": "Divide by 1-digit (with remainder)", "guide": "2-3 digit number ÷ 1-digit, answer as quotient and remainder"},
        {"skill": "Long division: 3-digit ÷ 2-digit (remainder)", "guide": "3-digit ÷ 2-digit divisor, answer as quotient and remainder"},
        {"skill": "Long division: 4-digit ÷ 2-digit (remainder)", "guide": "4-digit ÷ 2-digit divisor, answer as quotient and remainder"},
    ],
    "reading": [
        {"skill": "Letter sounds & sight words", "guide": "pick the word that matches a sound or simple meaning; very short words"},
        {"skill": "One-sentence comprehension", "guide": "a single simple sentence, then a who/what/where question with 4 choices"},
        {"skill": "Two-sentence comprehension", "guide": "two short sentences, then a comprehension question with 4 choices"},
        {"skill": "Short passage — main idea", "guide": "a 3-4 sentence passage, ask the main idea, 4 choices"},
        {"skill": "Vocabulary in context", "guide": "a sentence using a slightly tricky word; ask its meaning, 4 choices"},
        {"skill": "Inference", "guide": "a 3-4 sentence passage; ask a question whose answer is implied, not stated, 4 choices"},
        {"skill": "Key details in a passage", "guide": "a 4-6 sentence passage; ask which statement matches the passage, 4 choices"},
        {"skill": "Combining sentences (and / but / so)", "guide": "show two short sentences; ask which conjunction best joins them (and/but/so), 4 choices"},
        {"skill": "Either-or / neither-nor", "guide": "a sentence with a blank; ask which correlative conjunction fits (either/or, neither/nor), 4 choices"},
    ],
    "logic": [
        {"skill": "Patterns — what comes next", "guide": "a short shape/color/number pattern; ask what comes next, 4 choices"},
        {"skill": "Odd one out", "guide": "four items, one does not belong; ask which, 4 choices"},
        {"skill": "Number sequences", "guide": "a simple number sequence (e.g. +2, +3, doubling); ask the next number, 4 choices"},
        {"skill": "Sorting & categories", "guide": "group items by a rule; ask which item fits a category, 4 choices"},
        {"skill": "One-step word puzzles", "guide": "a one-step logic word problem; 4 choices"},
        {"skill": "Two-step reasoning", "guide": "a two-step deduction or word problem; 4 choices"},
    ],
}

# Starting levels (1-indexed) for a 7-year-old baseline. Age 8+ gets +1 tier via start_level().
START_LEVEL_AGE7 = {"math": 3, "reading": 2, "logic": 2}

# Named profiles seeded on first run, with starting levels derived from the kids'
# actual Kumon worksheets (May 2025). Adjustable later in the parent dashboard.
#   Nyra (3rd grade): Kumon D math → 3×2 multiplication; reading = key details.
#   Nivi (4th grade): Kumon D math = long division 4-digit / 2-digit; English = sentence combining.
NAMED_PROFILES = [
    {"name": "Nyra", "age": 8, "seed_index": 0,
     "levels": {"math": 15, "reading": 7, "logic": 4}},
    {"name": "Nivi", "age": 9, "seed_index": 1,
     "levels": {"math": 18, "reading": 9, "logic": 5}},
]


def start_level(subject: str, age: int) -> int:
    base = START_LEVEL_AGE7.get(subject, 1)
    bump = 1 if age >= 8 else 0
    return clamp_level(subject, base + bump)


def clamp_level(subject: str, level: int) -> int:
    n = len(LADDERS[subject])
    return max(1, min(level, n))


def skill_for(subject: str, level: int) -> str:
    level = clamp_level(subject, level)
    return LADDERS[subject][level - 1]["skill"]


def guide_for(subject: str, level: int) -> str:
    level = clamp_level(subject, level)
    return LADDERS[subject][level - 1]["guide"]
