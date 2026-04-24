import re
from sqlalchemy import text
from config.db import SessionLocal
from models.deanery import Deanery
from models.zone import Zone


def _generate_deanery_prefix_candidates(zone_letter: str, deanery_name: str):
    clean_name = deanery_name.strip().upper().replace("DEANERY", "").strip()
    words = [re.sub(r"[^A-Z]", "", w) for w in clean_name.split()]
    words = [w for w in words if w]

    seen = set()

    def _candidate(suffix):
        if len(suffix) == 3:
            val = f"{zone_letter}-{suffix}"
            if val not in seen:
                seen.add(val)
                return val
        return None

    initials = "".join(w[0] for w in words)
    all_letters = "".join(words)

    # Strategy 1: sliding window across initials
    for i in range(len(initials) - 2):
        c = _candidate(initials[i:i+3])
        if c: yield c

    if len(initials) >= 3:
        c = _candidate(initials[:3])
        if c: yield c

    # Strategy 2: sliding window within each word
    for word in words:
        for i in range(len(word) - 2):
            c = _candidate(word[i:i+3])
            if c: yield c

    # Strategy 3: sliding window across all letters
    for i in range(len(all_letters) - 2):
        c = _candidate(all_letters[i:i+3])
        if c: yield c

    # Strategy 4: cross-word combos (1 + 2)
    for i in range(len(words) - 1):
        for a in words[i]:
            for j in range(len(words[i+1]) - 1):
                c = _candidate(a + words[i+1][j:j+2])
                if c: yield c

    # Strategy 5: cross-word combos (2 + 1)
    for i in range(len(words) - 1):
        for j in range(len(words[i]) - 1):
            for b in words[i+1]:
                c = _candidate(words[i][j:j+2] + b)
                if c: yield c


def generate_deanery_prefixes():
    db = SessionLocal()
    updated = 0
    try:
        print("Generating deanery prefixes...")

        # Step 1: Wipe ALL prefixes atomically with raw SQL in its own commit
        # This avoids SQLAlchemy's executemany batching the NULLs row-by-row
        db.execute(text("UPDATE deaneries SET prefix = NULL"))
        db.commit()
        print("  Cleared existing prefixes.")

        # Step 2: Fetch deaneries (plain objects, no ORM tracking of prefix)
        deaneries = db.query(Deanery).join(Zone).all()
        assigned_prefixes = {}

        for deanery in deaneries:
            if not deanery.zone or not deanery.name:
                print(f"  [SKIP] Deanery id={deanery.id} — missing zone or name")
                continue

            zone_letter = deanery.zone.name.strip().split()[-1][-1].upper()

            prefix = None
            for candidate in _generate_deanery_prefix_candidates(zone_letter, deanery.name):
                if candidate not in assigned_prefixes:
                    prefix = candidate
                    break

            if not prefix:
                raise ValueError(
                    f"Could not find a unique prefix for '{deanery.name}' "
                    f"(zone={zone_letter}). All letter candidates exhausted."
                )

            # Step 3: Update each row individually with raw SQL
            # This avoids executemany which MySQL evaluates row-by-row
            # and triggers the unique constraint before all updates land
            db.execute(
                text("UPDATE deaneries SET prefix = :prefix WHERE id = :id"),
                {"prefix": prefix, "id": deanery.id}
            )
            db.commit()  # commit each row immediately so the next row can safely check uniqueness

            assigned_prefixes[prefix] = deanery.name
            updated += 1
            print(f"  → {deanery.name}: {prefix}")

        print(f"Deanery prefixes done. ({updated} updated)")
        return updated

    except Exception as e:
        print(f"Error generating deanery prefixes: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        print("Database session closed.")


if __name__ == "__main__":
    generate_deanery_prefixes()