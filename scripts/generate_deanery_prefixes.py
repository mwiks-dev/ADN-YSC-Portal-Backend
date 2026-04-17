from config.db import SessionLocal
from models.zone import Zone
from models.deanery import Deanery
from models.parish import Parish
from models.outstation import Outstation
from models.user import User

def generate_deanery_prefixes():
    db = SessionLocal()
    try:
        print("Generating deanery prefixes...")

        deaneries = db.query(Deanery).join(Zone).all()

        for deanery in deaneries:
            if not deanery.zone or not deanery.name:
                continue

            # Extract Zone Letter (A, B, C, D)
            zone_letter = deanery.zone.name.strip().split()[-1][-1].upper()  # e.g. "ZONE A" → "A"

            # Take the first 3 letters of the deanery name (ignoring case)
            deanery_initials = deanery.name.strip().replace("DEANERY", "").strip().upper()[:3]

            # Combine
            prefix = f"{zone_letter}-{deanery_initials}"

            # Update only if not set or changed
            if deanery.prefix != prefix:
                deanery.prefix = prefix
                print(f"→ {deanery.name}: {prefix}")

        db.commit()
        print("Deanery prefixes generated successfully!")

    except Exception as e:
        print(f"Error generating prefixes: {e}")
        db.rollback()
    finally:
        db.close()
        print("Database session closed.")


if __name__ == "__main__":
    generate_deanery_prefixes()

