# Feature: Placement & Curriculum

## Summary
Assessment of where Nivi and Nyra stand (from their actual Kumon worksheets) and the
curriculum extension made so the app matches their real level. See [[home-kumon-app]],
[[kids-and-stakeholder]].

## Status
**shipped** — placement assessed; app curriculum extended and profiles seeded at real levels.

## Source material
Kumon worksheets (dated ~May 2025) and school back-to-school packets were reviewed during
initial placement. The "grade" PDFs turned out to be **logistics packets, not report cards** — the real
signal was the Kumon work. School: W.R. Odell Primary (Cabarrus County, NC).

> **Note:** Reference PDFs (if kept) live under `docs/raw/placement/` — **not** read at runtime. Curriculum and levels are in code + wiki + DB seed.
> Placement findings live here in the wiki and in the seeded SQLite profiles.

## Findings (both ~2 years above grade level)
| Child | New grade | Math | English / Reading |
|---|---|---|---|
| **Nivi** | 3rd | Kumon **D** — long division, 3–4 digit ÷ 2-digit **with remainders** (e.g. 865÷41) | Kumon **DI** — combining sentences (but / either-or / neither-nor), comprehension, vocabulary |
| **Nyra** | 2nd | Kumon **D** — **2-digit × 2-digit multiplication** (e.g. 43×25) | Kumon **BII** — reading comprehension & key details (Flat Stanley) |

Accuracy strong on both, with a few teacher corrections on Nivi's division.

## Requirements that followed
- The app's original math ladder topped out at simple division/halves — **far too easy**.
- **Extended math ladder to L18:** ×2-digit/3-digit, 2×2 and 3×2 multiplication, division
  with remainder, long division 3-digit and 4-digit ÷ 2-digit.
- **Extended reading ladder to L9:** key details, sentence-combining (and/but/so),
  either-or/neither-nor.
- **Seeded starting levels** from the worksheets: Nyra → Math L15, Reading L7, Logic L4;
  Nivi → Math L18, Reading L9, Logic L5. All adjustable in the dashboard; adaptive leveling
  tunes from there.
- New `quotient_remainder` input + validation for long-division answers like `57R16`.

## Open questions
- Worksheets were ~1 year old (May 2025); the kids have likely progressed — real-use accuracy
  will refine levels via adaptive leveling.
- Printable PDF worksheets at these levels still offered, not yet generated.
