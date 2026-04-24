def generate_membership_no(db, parish_id):
    from models import User, Parish
    from sqlalchemy import func
    from sqlalchemy.orm import joinedload

    parish = (
        db.query(Parish)
        .options(joinedload(Parish.deanery))  
        .filter(Parish.id == parish_id)
        .first()
    )

    if not parish:
        raise ValueError(f"Parish with id={parish_id} not found")
    if not parish.deanery:
        raise ValueError(f"Parish '{parish.name}' has no associated deanery")

    deanery_prefix = (parish.deanery.prefix or "").strip()
    parish_prefix = (parish.prefix or "").strip()

    if not deanery_prefix or not parish_prefix:
        raise ValueError(
            f"Missing prefix — deanery_prefix='{deanery_prefix}', parish_prefix='{parish_prefix}'"
        )

    prefix_pattern = f"{deanery_prefix}-{parish_prefix}-%"

    last_user = (
        db.query(User)
        .filter(
            User.parish_id == parish_id,
            User.membership_no.like(prefix_pattern),
        )
        .order_by(User.membership_no.desc())  
        .with_for_update()                  
        .first()
    )

    if last_user and last_user.membership_no:
        try:
            last_seq = int(last_user.membership_no.split("-")[-1])
        except ValueError:
            last_seq = 0
    else:
        last_seq = 0

    new_seq = str(last_seq + 1).zfill(4)
    return f"{deanery_prefix}-{parish_prefix}-{new_seq}"