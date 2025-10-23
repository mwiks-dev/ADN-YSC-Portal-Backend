def generate_membership_no(db, parish_id):
    from models import User, Parish

    # Get parish and related deanery
    parish = db.query(Parish).get(parish_id)
    if not parish or not parish.deanery:
        raise ValueError("Parish or Deanery missing for membership number generation")

    deanery_prefix = parish.deanery.prefix or ""
    parish_prefix = parish.prefix or ""

    # Get the highest current sequence for this parish safely
    last_user = (
        db.query(User)
        .filter(User.parish_id == parish_id)
        .order_by(User.id.desc())  # Fastest to get last inserted
        .first()
    )

    # Extract sequence from last membership number if it exists
    if last_user and last_user.membership_no:
        try:
            last_seq = int(last_user.membership_no.split("-")[-1])
        except ValueError:
            last_seq = 0
    else:
        last_seq = 0

    new_seq = str(last_seq + 1).zfill(4)
    return f"{deanery_prefix}-{parish_prefix}-{new_seq}"
