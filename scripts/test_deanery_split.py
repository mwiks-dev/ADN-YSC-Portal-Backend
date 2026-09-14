"""
Standalone local test for the deanery-split changes.

Runs against a throwaway SQLite database (no Docker, no MySQL, nothing to
clean up afterwards) so you can sanity-check the logic in isolation before
touching your real dev database.

USAGE
-----
1. Copy this file into the root of your ADN-YSC-Portal-Backend repo
   (same folder as main.py), after applying the patch.
2. Make sure your .env has a DATABASE_URL set (any value works - this
   script overrides it with SQLite before importing anything DB-related),
   plus SECRET_KEY and ALGORITHM, since config/db.py and utils/auth_utils.py
   read those at import time.
3. Run:  python test_deanery_split.py
4. Read the printed output - each check prints PASS/FAIL.

This does NOT touch your real database - it points DATABASE_URL at
sqlite:///:memory: before any app modules are imported.
"""

import os
import sys

# Force an isolated in-memory DB before config.db (or anything importing it)
# gets loaded. Must happen before any `from config...` or `from models...`
# import below.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("SECRET_KEY", "test-secret-not-used")
os.environ.setdefault("ALGORITHM", "HS256")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# If this script lives inside scripts/, also add the repo root (one level
# up) to sys.path, since config/, models/, services/ etc. are all
# top-level packages relative to the repo root, not to scripts/.
_here = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_here) == "scripts":
    sys.path.insert(0, os.path.dirname(_here))

# config/db.py passes MySQL-only connection-pool kwargs (pool_size,
# max_overflow, ...) into create_engine(). SQLite's pool implementation
# doesn't accept those, so strip them when the URL is sqlite - this only
# affects this test script, config/db.py itself is untouched.
import sqlalchemy

_original_create_engine = sqlalchemy.create_engine


def _sqlite_safe_create_engine(url, **kwargs):
    if str(url).startswith("sqlite"):
        for unsupported in (
            "pool_size", "max_overflow", "pool_timeout",
            "pool_recycle", "pool_pre_ping",
        ):
            kwargs.pop(unsupported, None)
    return _original_create_engine(url, **kwargs)


sqlalchemy.create_engine = _sqlite_safe_create_engine

failures = []


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        failures.append(label)


def main():
    from config.db import Base, engine, SessionLocal
    # Import every model so SQLAlchemy registers all relationships before
    # create_all runs - mirrors what scripts/seed_deaneries_parishes.py does.
    import models.zone
    import models.deanery
    import models.parish
    import models.user
    import models.outstation
    import models.event

    Base.metadata.create_all(bind=engine)

    from models.zone import Zone
    from services.deanery_service import (
        create_deanery,
        split_deanery,
        get_deanery_by_id,
    )
    from services.parish_service import create_parish, get_parishes_by_deanery
    from scripts.generate_parish_prefixes import generate_single_parish_prefix

    db = SessionLocal()

    # --- Setup: one zone, one deanery, four parishes ---
    zone = Zone(name="ZONE A")
    db.add(zone)
    db.commit()
    db.refresh(zone)

    deanery = create_deanery(db, "MANGU DEANERY", zone.id)

    p1 = create_parish(db, "St. Teresa Gachege", deanery.id)
    p2 = create_parish(db, "St. Anne Mataara", deanery.id)
    p3 = create_parish(db, "St. Peter Nyamangara", deanery.id)
    p4 = create_parish(db, "St. John the Baptist Mangu", deanery.id)

    print("\n--- Fix 1: parish prefix generation no longer crashes ---")
    check(
        "generate_single_parish_prefix computes a 3-letter prefix directly",
        generate_single_parish_prefix("St. Anne Mataara") == "SAM",
    )
    check(
        "Newly created parish got an auto-filled prefix (no TypeError)",
        p2.prefix == "SAM",
    )

    print("\n--- Fix 2: deaneryParishes / get_parishes_by_deanery ---")
    parishes_in_deanery = get_parishes_by_deanery(db, deanery.id)
    check(
        "get_parishes_by_deanery returns all 4 seeded parishes",
        len(parishes_in_deanery) == 4,
    )
    check(
        "Results are actual Parish rows filtered by deanery_id",
        {p.id for p in parishes_in_deanery} == {p1.id, p2.id, p3.id, p4.id},
    )

    print("\n--- New feature: split_deanery guard rails ---")

    # Missing assignment
    try:
        split_deanery(
            db, deanery.id, "MANGU EAST DEANERY", zone.id,
            "MANGU WEST DEANERY", zone.id,
            {p1.id: "A", p2.id: "B", p3.id: "A"},  # p4 missing on purpose
        )
        check("Rejects a split that leaves a parish unassigned", False)
    except ValueError:
        check("Rejects a split that leaves a parish unassigned", True)

    # Everything on one side
    try:
        split_deanery(
            db, deanery.id, "MANGU EAST DEANERY", zone.id,
            "MANGU WEST DEANERY", zone.id,
            {p1.id: "A", p2.id: "A", p3.id: "A", p4.id: "A"},
        )
        check("Rejects a split where side B ends up empty", False)
    except ValueError:
        check("Rejects a split where side B ends up empty", True)

    print("\n--- New feature: split_deanery actually splits ---")
    deanery_a, deanery_b = split_deanery(
        db, deanery.id, "MANGU EAST DEANERY", zone.id,
        "MANGU WEST DEANERY", zone.id,
        {p1.id: "A", p2.id: "A", p3.id: "B", p4.id: "B"},
    )

    a_parish_ids = {p.id for p in get_parishes_by_deanery(db, deanery_a.id)}
    b_parish_ids = {p.id for p in get_parishes_by_deanery(db, deanery_b.id)}

    check("Deanery A got exactly the 2 parishes it was assigned", a_parish_ids == {p1.id, p2.id})
    check("Deanery B got exactly the 2 parishes it was assigned", b_parish_ids == {p3.id, p4.id})
    check("Original deanery still exists (delete_original defaults to False)",
          get_deanery_by_id(db, deanery.id) is not None)
    check("Original deanery now has 0 parishes left",
          len(get_parishes_by_deanery(db, deanery.id)) == 0)

    # Duplicate name guard
    try:
        split_deanery(db, deanery_a.id, "MANGU WEST DEANERY", zone.id, "SOMETHING ELSE", zone.id, {})
        check("Rejects reusing an existing deanery name", False)
    except ValueError:
        check("Rejects reusing an existing deanery name", True)

    print("\n" + "=" * 50)
    if failures:
        print(f"{len(failures)} check(s) FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")


if __name__ == "__main__":
    main()