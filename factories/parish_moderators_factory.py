# scripts/seed_parish_moderators.py
from config.db import SessionLocal
from models.user import User, UserRole, UserStatus
from models.parish import Parish
from passlib.context import CryptContext
from datetime import date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_PASSWORD = "Parish@1234"  # change or move to .env

def seed_parish_moderators():
    db = SessionLocal()
    created = 0
    skipped = 0

    try:
        print("Seeding parish moderators...")
        parishes = db.query(Parish).all()

        for parish in parishes:
            if not parish.name:
                print(f"  [SKIP] Parish id={parish.id} has no name")
                skipped += 1
                continue

            # Check if a moderator already exists for this parish
            existing = (
                db.query(User)
                .filter(
                    User.parish_id == parish.id,
                    User.role == UserRole.parish_moderator,
                )
                .first()
            )

            if existing:
                print(f"  [SKIP] {parish.name} already has a moderator ({existing.email})")
                skipped += 1
                continue

            # Derive a unique email and phone from the parish name
            safe_name = parish.name.lower().replace(" ", "").replace("'", "")[:20]
            email = f"mod.{safe_name}@adn.org"
            phone = f"+2547{str(parish.id).zfill(8)}"  # placeholder unique phone

            moderator = User(
                name=f"{parish.name} Moderator",
                email=email,
                phonenumber=phone,
                dateofbirth=date(2003, 1, 1),  # placeholder
                idnumber=int(f"9{str(parish.id).zfill(7)}"),  # placeholder unique ID
                baptismref=f"BREF-{parish.id}",
                password=pwd_context.hash(DEFAULT_PASSWORD),
                role=UserRole.parish_moderator,
                status=UserStatus.active_member,
                profile_pic=None,
                parish_id=parish.id,
                created_at=date.today(),
                updated_at=date.today(),
            )

            db.add(moderator)

            try:
                db.commit()
                db.refresh(moderator)
                print(f"  ✓ {parish.name}: {moderator.email} | {moderator.membership_no}")
                created += 1
            except Exception as e:
                db.rollback()
                print(f"  [ERROR] {parish.name}: {e}")
                skipped += 1

        print(f"\nDone. {created} moderators created, {skipped} skipped.")

    except Exception as e:
        print(f"Error seeding parish moderators: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        print("Database session closed.")


if __name__ == "__main__":
    seed_parish_moderators()