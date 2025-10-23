import re
from config.db import SessionLocal


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

            # Normalize name: remove extra spaces and periods after 'St.'
            name = parish.name.strip()
            name = re.sub(r"\bSt\.\b", "St", name, flags=re.IGNORECASE)

            # Split into words and take the first letter of each
            words = re.split(r"\s+", name)
            initials = "".join(
                [w[0].upper() for w in words if w and w[0].isalpha()]
            )

            prefix = initials[:3]

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
