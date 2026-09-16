import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.db import SessionLocal
import models.zone
import models.deanery
import models.parish

from models.deanery import Deanery
from models.zone import Zone
from models.parish import Parish
from scripts.generate_parish_prefixes import generate_single_parish_prefix


def backfill_deanery_prefixes(db):
    changed = []
    deaneries = db.query(Deanery).all()
    for deanery in deaneries:
        if not deanery.zone_id:
            print(f"  SKIP deanery id={deanery.id} '{deanery.name}': no zone assigned")
            continue

        zone = db.query(Zone).filter(Zone.id == deanery.zone_id).first()
        if not zone:
            print(f"  SKIP deanery id={deanery.id} '{deanery.name}': zone_id points to a missing zone")
            continue

        zone_letter = zone.name.strip().split()[-1][-1].upper()
        deanery_initials = deanery.name.strip().replace("DEANERY", "").strip().upper()[:3]
        new_prefix = f"{zone_letter}-{deanery_initials}"

        if deanery.prefix != new_prefix:
            changed.append((deanery.id, deanery.name, deanery.prefix, new_prefix))
            deanery.prefix = new_prefix

    return changed


def backfill_parish_prefixes(db):
    changed = []
    parishes = db.query(Parish).all()
    for parish in parishes:
        if not parish.name:
            continue
        new_prefix = generate_single_parish_prefix(parish.name)
        if parish.prefix != new_prefix:
            changed.append((parish.id, parish.name, parish.prefix, new_prefix))
            parish.prefix = new_prefix

    return changed


def main():
    db = SessionLocal()
    try:
        print("=== Backfilling deanery prefixes ===")
        deanery_changes = backfill_deanery_prefixes(db)
        for id_, name, old, new in deanery_changes:
            print(f"  Deanery id={id_} '{name}': '{old}' -> '{new}'")
        print(f"{len(deanery_changes)} deanery row(s) will be updated.\n")

        print("=== Backfilling parish prefixes ===")
        parish_changes = backfill_parish_prefixes(db)
        for id_, name, old, new in parish_changes:
            print(f"  Parish id={id_} '{name}': '{old}' -> '{new}'")
        print(f"{len(parish_changes)} parish row(s) will be updated.\n")

        # Check for prefix collisions BEFORE committing, so you see them
        # instead of finding out via a failed registration.
        print("=== Checking for duplicate membership-number prefixes within each deanery ===")
        all_parishes = db.query(Parish).all()
        by_deanery = {}
        for p in all_parishes:
            by_deanery.setdefault(p.deanery_id, []).append(p)

        collisions_found = False
        for deanery_id, parishes in by_deanery.items():
            seen = {}
            for p in parishes:
                combo = p.prefix
                if combo in seen:
                    collisions_found = True
                    print(
                        f"  COLLISION in deanery_id={deanery_id}: parish '{seen[combo]}' "
                        f"and parish '{p.name}' both compute prefix '{combo}'"
                    )
                seen[combo] = p.name

        if not collisions_found:
            print("  No collisions found.")
        else:
            print(
                "\n  NOTE: these parishes will safely interleave into one shared "
                "membership-number sequence after the membership_utils.py fix - "
                "this is informational, not blocking."
            )

        confirm = input("\nCommit these changes to the database? [y/N]: ").strip().lower()
        if confirm == "y":
            db.commit()
            print("Committed.")
        else:
            db.rollback()
            print("Rolled back - no changes were made.")

    except Exception:
        db.rollback()
        print("An error occurred - rolled back, no changes were made.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()