"""Offline problem bank used when LM Studio is unreachable or for deterministic math."""
from __future__ import annotations

import random

from . import curriculum


def _math_starter(level: int, rng: random.Random) -> dict:
    level = curriculum.clamp_level("math", level)

    def mk(prompt, answer, explanation, hint):
        return {
            "prompt": prompt,
            "type": "numeric",
            "options": None,
            "answer": str(answer),
            "explanation": explanation,
            "hint": hint,
        }

    if level == 1:
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        return mk(f"{a} + {b} = ?", a + b, f"Count up: {a} and {b} more makes {a+b}.", "Try counting on your fingers.")
    if level == 2:
        a = rng.randint(2, 10)
        b = rng.randint(1, a)
        return mk(f"{a} - {b} = ?", a - b, f"Start at {a} and count back {b} to get {a-b}.", "Count backwards from the big number.")
    if level == 3:
        a, b = rng.randint(5, 14), rng.randint(1, 6)
        return mk(f"{a} + {b} = ?", a + b, f"{a} plus {b} is {a+b}.", "Start at the bigger number and count up.")
    if level == 4:
        a = rng.randint(11, 20)
        b = rng.randint(1, 9)
        return mk(f"{a} - {b} = ?", a - b, f"{a} take away {b} leaves {a-b}.", "Count back from the bigger number.")
    if level == 5:
        a, b = rng.randint(10, 50), rng.randint(10, 40)
        a -= a % 10
        b -= b % 10
        return mk(f"{a} + {b} = ?", a + b, f"Add the tens: {a} + {b} = {a+b}.", "Add the tens, then the ones.")
    if level == 6:
        a, b = rng.randint(15, 89), rng.randint(15, 89)
        return mk(f"{a} + {b} = ?", a + b, f"{a} + {b} = {a+b}. Don't forget to carry!", "Add the ones first, carry if over 9.")
    if level == 7:
        a = rng.choice([2, 5, 10])
        b = rng.randint(1, 9)
        return mk(f"{a} × {b} = ?", a * b, f"{a} groups of {b} is {a*b}.", f"Count by {a}s, {b} times.")
    if level == 8:
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        return mk(f"{a} × {b} = ?", a * b, f"{a} times {b} is {a*b}.", "Think of equal groups.")
    if level == 9:
        a, b = rng.randint(1, 10), rng.randint(1, 10)
        return mk(f"{a} × {b} = ?", a * b, f"{a} times {b} is {a*b}.", "Use a times-table you know.")
    if level == 10:
        b = rng.randint(2, 9)
        q = rng.randint(2, 9)
        a = b * q
        return mk(f"{a} ÷ {b} = ?", q, f"{a} shared into {b} groups gives {q} each.", "Which number times the divisor makes the total?")

    def mkqr(prompt, q, r, explanation, hint):
        return {
            "prompt": prompt,
            "type": "quotient_remainder",
            "options": None,
            "answer": f"{q}R{r}",
            "explanation": explanation,
            "hint": hint,
        }

    if level == 11:
        base = rng.choice([4, 8, 12, 16, 20])
        if rng.random() < 0.5:
            return mk(f"What is half of {base}?", base // 2, f"Half of {base} is {base//2}.", "Split it into two equal parts.")
        return mk(f"What is a quarter of {base}?", base // 4, f"A quarter of {base} is {base//4}.", "Split it into four equal parts.")
    if level == 12:
        a, b = rng.randint(25, 99), rng.randint(3, 9)
        return mk(f"{a} × {b} = ?", a * b, f"{a} × {b} = {a*b}.", "Multiply the ones, then the tens, and add.")
    if level == 13:
        a, b = rng.randint(200, 999), rng.randint(3, 9)
        return mk(f"{a} × {b} = ?", a * b, f"{a} × {b} = {a*b}.", "Multiply each digit by the ones, carrying as you go.")
    if level == 14:
        a, b = rng.randint(21, 99), rng.randint(12, 99)
        return mk(f"{a} × {b} = ?", a * b, f"{a} × {b} = {a*b}.", "Multiply by the ones, then the tens, then add the two rows.")
    if level == 15:
        a, b = rng.randint(150, 999), rng.randint(12, 99)
        return mk(f"{a} × {b} = ?", a * b, f"{a} × {b} = {a*b}.", "Two rows: times the ones, then times the tens, then add.")
    if level == 16:
        d = rng.randint(4, 9)
        q = rng.randint(30, 180)
        r = rng.randint(1, d - 1)
        dividend = d * q + r
        return mkqr(f"{dividend} ÷ {d} = ?", q, r, f"{dividend} ÷ {d} = {q} remainder {r}.", f"How many {d}s fit, and what is left over?")
    if level == 17:
        d = rng.randint(15, 49)
        q = rng.randint(12, 45)
        r = rng.randint(1, d - 1)
        dividend = d * q + r
        return mkqr(f"{dividend} ÷ {d} = ?", q, r, f"{dividend} ÷ {d} = {q} remainder {r}.", f"Estimate how many {d}s fit; the leftover is the remainder.")
    d = rng.randint(35, 99)
    q = rng.randint(70, 150)
    r = rng.randint(1, d - 1)
    dividend = d * q + r
    return mkqr(f"{dividend} ÷ {d} = ?", q, r, f"{dividend} ÷ {d} = {q} remainder {r}.", "Work left to right; bring down each digit and find the remainder.")


_READING_BANK: dict[int, list[dict]] = {
    1: [
        {"prompt": "Which word names an animal?", "options": ["cat", "cup", "car", "can"], "answer": "cat",
         "explanation": "A cat is an animal; the others are not.", "hint": "Which one says meow?"},
        {"prompt": "Which word rhymes with 'sun'?", "options": ["run", "sit", "top", "bag"], "answer": "run",
         "explanation": "'Run' and 'sun' end with the same sound.", "hint": "Say each word out loud."},
    ],
    2: [
        {"prompt": "The dog ran to the park. Where did the dog go?", "options": ["the park", "the shop", "the school", "the zoo"],
         "answer": "the park", "explanation": "The sentence says the dog ran to the park.", "hint": "Look for the place word."},
    ],
    3: [
        {"prompt": "Mia has a red ball. She kicks it to Sam. Who gets the ball?",
         "options": ["Sam", "Mia", "the dog", "nobody"], "answer": "Sam",
         "explanation": "Mia kicks the ball to Sam, so Sam gets it.", "hint": "Who did Mia kick it to?"},
    ],
    4: [
        {"prompt": "Ben planted seeds. He watered them every day. Soon little green plants grew. What is this about?",
         "options": ["growing plants", "cooking food", "a car trip", "a rainy day"], "answer": "growing plants",
         "explanation": "Ben planted and watered seeds and plants grew — it's about growing plants.", "hint": "What did Ben grow?"},
    ],
    5: [
        {"prompt": "The puppy was tiny. What does 'tiny' mean?", "options": ["very small", "very big", "very loud", "very fast"],
         "answer": "very small", "explanation": "'Tiny' means very small.", "hint": "Think about a baby puppy's size."},
    ],
    6: [
        {"prompt": "Anya put on her boots and grabbed an umbrella before going out. What was the weather probably like?",
         "options": ["rainy", "sunny and hot", "snowy with no clouds", "very windy and dry"], "answer": "rainy",
         "explanation": "Boots and an umbrella suggest it was rainy.", "hint": "Why use an umbrella?"},
    ],
    7: [
        {"prompt": "Maya planted a seed in a small pot. She watered it every morning. After two weeks, a tiny green leaf appeared. Which statement matches the story?",
         "options": ["Maya watered it every morning", "The seed never grew", "Maya forgot the pot", "A flower bloomed that day"],
         "answer": "Maya watered it every morning", "explanation": "The story says she watered it every morning.", "hint": "Look for the sentence about her daily routine."},
        {"prompt": "Leo built a fort out of pillows. His sister helped him add a roof made of a blanket. They read books inside it. Which statement matches?",
         "options": ["His sister helped add a roof", "Leo built it from boxes", "They slept outside", "Leo read alone"],
         "answer": "His sister helped add a roof", "explanation": "The passage says his sister helped add the blanket roof.", "hint": "Who helped, and with what?"},
    ],
    8: [
        {"prompt": "Pick the best word to join: 'It started to rain. We went inside.'", "options": ["so", "but", "or", "nor"],
         "answer": "so", "explanation": "'So' shows the rain caused them to go inside.", "hint": "One thing made the other happen."},
        {"prompt": "Pick the best word to join: 'He studied hard. He still felt nervous.'", "options": ["but", "so", "and", "or"],
         "answer": "but", "explanation": "'But' shows a contrast between studying and still feeling nervous.", "hint": "The two parts go in opposite directions."},
    ],
    9: [
        {"prompt": "Choose the word: '___ Sam nor his brothers can swim.'", "options": ["Neither", "Either", "Both", "And"],
         "answer": "Neither", "explanation": "'Neither … nor' is the matching pair.", "hint": "Which word pairs with 'nor'?"},
        {"prompt": "Choose the word: 'You can have either tea ___ juice.'", "options": ["or", "nor", "and", "but"],
         "answer": "or", "explanation": "'Either … or' is the matching pair.", "hint": "Which word pairs with 'either'?"},
    ],
}

_LOGIC_BANK: dict[int, list[dict]] = {
    1: [
        {"prompt": "What comes next? 🔵 🟡 🔵 🟡 ___", "options": ["🔵", "🟡", "🟢", "🔴"], "answer": "🔵",
         "explanation": "The pattern goes blue, yellow, repeating — next is blue.", "hint": "Say the colors in order."},
    ],
    2: [
        {"prompt": "Which one does NOT belong? apple, banana, carrot, grape", "options": ["carrot", "apple", "banana", "grape"],
         "answer": "carrot", "explanation": "Carrot is a vegetable; the rest are fruits.", "hint": "Three are fruits."},
    ],
    3: [
        {"prompt": "What number comes next? 2, 4, 6, 8, ___", "options": ["10", "9", "12", "7"], "answer": "10",
         "explanation": "The numbers go up by 2 each time, so next is 10.", "hint": "How much does it jump each time?"},
    ],
    4: [
        {"prompt": "Which one is a thing you wear?", "options": ["hat", "spoon", "chair", "lamp"], "answer": "hat",
         "explanation": "A hat is something you wear.", "hint": "Which goes on your body?"},
    ],
    5: [
        {"prompt": "Tom has 3 apples and gets 2 more. How many apples now?", "options": ["5", "4", "6", "1"], "answer": "5",
         "explanation": "3 apples plus 2 more is 5.", "hint": "Add the two numbers."},
    ],
    6: [
        {"prompt": "There are 4 birds. 2 fly away, then 1 comes back. How many birds now?",
         "options": ["3", "2", "4", "5"], "answer": "3", "explanation": "4 minus 2 is 2, plus 1 is 3.", "hint": "Do it one step at a time."},
    ],
}


def _starter_problem(subject: str, level: int, rng: random.Random) -> dict:
    if subject == "math":
        p = _math_starter(level, rng)
    else:
        bank = _READING_BANK if subject == "reading" else _LOGIC_BANK
        level = curriculum.clamp_level(subject, level)
        pool = None
        for lv in range(level, 0, -1):
            if bank.get(lv):
                pool = bank[lv]
                break
        if not pool:
            pool = next(iter(bank.values()))
        item = dict(rng.choice(pool))
        p = {
            "prompt": item["prompt"],
            "type": "multiple_choice",
            "options": list(item["options"]),
            "answer": item["answer"],
            "explanation": item["explanation"],
            "hint": item["hint"],
        }
    p["skill"] = curriculum.skill_for(subject, level)
    p["source"] = "starter"
    return p


def starter_batch(subject: str, level: int, count: int, seed: int) -> list[dict]:
    """Build a batch of offline starter problems for one subject/level."""
    rng = random.Random(seed)
    out: list[dict] = []
    seen_prompts: set[str] = set()
    tries = 0
    while len(out) < count and tries < count * 6:
        tries += 1
        p = _starter_problem(subject, level, rng)
        if subject == "math" and p["prompt"] in seen_prompts:
            continue
        seen_prompts.add(p["prompt"])
        out.append(p)
    return out
