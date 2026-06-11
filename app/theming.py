"""Derive a stable color theme for a child from their name.

Each child's whole UI is themed from one primary color so the two profiles feel
distinct. Placeholder names ("Kid 1"/"Kid 2") are nudged to opposite ends of the
palette so they don't collide before the parent renames them.
"""
from __future__ import annotations

import hashlib

# Curated kid-friendly palettes: (name, primary, accent, soft background).
PALETTES = [
    {"name": "Ocean", "primary": "#2E8BC0", "accent": "#145DA0", "bg": "#EAF4FB"},
    {"name": "Sunset", "primary": "#FF7B54", "accent": "#E14D2A", "bg": "#FFF1EC"},
    {"name": "Meadow", "primary": "#43A047", "accent": "#2E7D32", "bg": "#ECF7ED"},
    {"name": "Grape", "primary": "#8E44AD", "accent": "#6C3483", "bg": "#F5ECFA"},
    {"name": "Bubblegum", "primary": "#EC407A", "accent": "#C2185B", "bg": "#FDECF3"},
    {"name": "Sky", "primary": "#00A0B0", "accent": "#007684", "bg": "#E6F7F9"},
    {"name": "Mango", "primary": "#F4A100", "accent": "#C98200", "bg": "#FFF6E5"},
    {"name": "Berry", "primary": "#6D4C9F", "accent": "#513876", "bg": "#F0ECF8"},
]


def _hash_index(name: str, offset: int = 0) -> int:
    h = hashlib.sha256(name.strip().lower().encode("utf-8")).hexdigest()
    return (int(h[:8], 16) + offset) % len(PALETTES)


def theme_for(name: str, seed_index: int = 0) -> dict:
    """Return a palette dict for a child.

    seed_index spreads the two seeded profiles apart (0 -> Ocean-ish, 1 -> opposite half).
    """
    if name.strip().lower() in ("kid 1", "kid 2", "child 1", "child 2"):
        idx = 0 if seed_index == 0 else len(PALETTES) // 2  # Ocean vs Bubblegum
    else:
        idx = _hash_index(name, offset=seed_index * (len(PALETTES) // 2))
    return PALETTES[idx]
