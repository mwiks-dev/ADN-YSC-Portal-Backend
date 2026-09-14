import re
from config.db import SessionLocal

def generate_single_parish_prefix(name: str) -> str:
    """
    Compute the prefix for a single parish name. Shared by the bulk
    `generate_parish_prefixes()` script below and by the Parish model's
    before_insert/before_update event listener (models/parish.py), so a
    single new/updated parish doesn't need the whole table scanned just
    to get its own prefix.
    """
    if not name:
        return ""

    name = name.strip()
    name = re.sub(r"\bSt\.\b", "St", name, flags=re.IGNORECASE)

    words = re.split(r"\s+", name)
    initials = "".join([w[0].upper() for w in words if w and w[0].isalpha()])

    return initials[:3]

def generate_parish_prefixes():
    """Generate and update parish prefixes in batches."""
    from models.parish import Parish  # imported inside to avoid circular issues
    from models.outstation import Outstation

    db = SessionLocal()
    try:
        print("Generating parish prefixes...")

        parishes = db.query(Parish).all()
        for parish in parishes:
            if not parish.name:
                parish.prefix = ""
                continue

            prefix = generate_single_parish_prefix(parish.name)

            #update only if not set or changed
            if parish.prefix != prefix:
                parish.prefix = prefix
                print(f"→ {parish.name}: {prefix}")

        db.commit()
        print("Parish prefixes generated successfully")

    except Exception as e:
        print(f"Error generating prefixes: {e}")
        db.rollback()
    finally:
        db.close()
        print("Database session closed. ")


if __name__ == "__main__":
    generate_parish_prefixes()
