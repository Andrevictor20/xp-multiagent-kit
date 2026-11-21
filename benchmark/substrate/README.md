# Substrate Repository

A small, dependency-free Python project used as the controlled repository under work
for the XP kit benchmark. Both arms (with and without the kit) start from an identical
copy of this tree at a pinned commit.

Layout:

- `app/parser.py` — integer and ISO date parsing.
- `app/pricing.py` — line items and order totals.
- `app/service.py` — in-memory task registry.
- `tests/` — `unittest` suite (22 tests) that is green at the base commit.

Run the suite with:

```bash
python3 -m unittest discover -s tests -q
```
