from config.db import SessionLocal
from models.user import User, UserRole
from models.event import Event
from services.event_parish_registration_service import register_parish_for_event
import random

DEFAULT_EVENT_ID = 9

def seed_event_parish_registrations():
    db = SessionLocal()
    created = 0
    skipped = 0

    try:
        print(f"Seeding parish registrations for event {DEFAULT_EVENT_ID}...")

        # Ensure event exists
        event = db.query(Event).filter(Event.id == DEFAULT_EVENT_ID).first()
        if not event:
            raise Exception(f"Event with id {DEFAULT_EVENT_ID} not found")

        # Get all parish moderators
        moderators = (
            db.query(User)
            .filter(User.role == UserRole.parish_moderator)
            .all()
        )

        for moderator in moderators:
            if not moderator.parish_id:
                print(f"  [SKIP] {moderator.email} has no parish")
                skipped += 1
                continue

            try:
                # Randomize participants a bit for realism
                participants = random.randint(10, 50)

                registration = register_parish_for_event(
                    db=db,
                    current_user=moderator,
                    event_id=DEFAULT_EVENT_ID,
                    parish_id=moderator.parish_id,
                    number_of_participants=participants,
                )

                db.commit()
                db.refresh(registration)

                print(
                    f"  ✓ Parish {moderator.parish_id} registered by {moderator.email} "
                    f"({participants} participants)"
                )
                created += 1

            except Exception as e:
                db.rollback()
                print(
                    f"  [SKIP] Parish {moderator.parish_id} ({moderator.email}): {e}"
                )
                skipped += 1

        print(f"\nDone. {created} registrations created, {skipped} skipped.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding registrations: {e}")
        raise

    finally:
        db.close()
        print("Database session closed.")


if __name__ == "__main__":
    seed_event_parish_registrations()