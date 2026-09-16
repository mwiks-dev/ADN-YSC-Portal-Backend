from models.deanery import Deanery
from sqlalchemy.orm import Session, joinedload

def get_deaneries(db:Session):
    return db.query(Deanery).options(joinedload(Deanery)).all()

def get_deanery_by_id(db:Session, deanery_id:int):
    return db.query(Deanery).filter(Deanery.id == deanery_id).first()

def get_deaneries_by_zone(db:Session, zone:str):
    return db.query(Deanery).filter(Deanery.zone == zone)

def get_deanery_by_name(db:Session, name:str):
    return db.query(Deanery).filter(Deanery.name == name).first()

def create_deanery(db:Session, name:str, zone_id:int):
    deanery = Deanery(name=name, zone_id = zone_id)
    db.add(deanery)
    db.commit()
    db.refresh(deanery)
    return deanery

def update_deanery(db:Session,id:int,name:str,zone_id:int):
    deanery = db.query(Deanery).filter(Deanery.id == id).first()

    if deanery:
        deanery.name = name
        deanery.zone_id = zone_id
        db.commit()
        db.refresh(deanery)
    return deanery

def delete_deanery(db:Session, id:int):
    deanery = db.query(Deanery).filter(Deanery.id == id).first()
    if deanery:
        db.delete(deanery)
        db.commit()
    return deanery


def split_deanery(
    db: Session,
    deanery_id: int,
    deanery_a_name: str,
    deanery_a_zone_id: int,
    deanery_b_name: str,
    deanery_b_zone_id: int,
    parish_assignments: dict[int, str],
    delete_original: bool = False,
):
    """
    Splits an existing deanery into two brand-new deaneries (A and B).

    `parish_assignments` maps parish_id -> "A" or "B", letting the caller
    decide exactly which new deanery each existing parish should move to.
    Every parish currently in the source deanery must appear in the mapping,
    and both new deaneries must end up with at least one parish - otherwise
    it isn't really a split.

    The source deanery is only deleted if `delete_original=True` is passed
    AND nothing else (e.g. events) still references it - deaneries are kept
    around by default so historical data tied to the old deanery_id doesn't
    break.
    """
    original = (
        db.query(Deanery)
        .options(joinedload(Deanery.parishes), joinedload(Deanery.events))
        .filter(Deanery.id == deanery_id)
        .first()
    )
    if not original:
        raise ValueError(f"Deanery with id {deanery_id} not found")

    deanery_a_name = deanery_a_name.strip()
    deanery_b_name = deanery_b_name.strip()

    if not deanery_a_name or not deanery_b_name:
        raise ValueError("Both new deaneries need a name")
    if deanery_a_name.lower() == deanery_b_name.lower():
        raise ValueError("The two new deaneries must have different names")

    # A name only conflicts with a deanery that will still exist once this
    # split is done. The original row itself doesn't count as a conflict
    # when it's about to be deleted, which lets a caller "rename in place"
    # by reusing the original's name for deanery A or B.
    def name_conflicts(name: str, exclude_id: int | None) -> bool:
        existing = get_deanery_by_name(db, name)
        return bool(existing and existing.id != exclude_id)

    exclude_id = original.id if delete_original else None

    if name_conflicts(deanery_a_name, exclude_id):
        raise ValueError(f"A deanery named '{deanery_a_name}' already exists")
    if name_conflicts(deanery_b_name, exclude_id):
        raise ValueError(f"A deanery named '{deanery_b_name}' already exists")

    original_parish_ids = {p.id for p in original.parishes}
    assigned_parish_ids = set(parish_assignments.keys())

    missing = original_parish_ids - assigned_parish_ids
    if missing:
        raise ValueError(
            f"Every parish currently in this deanery must be assigned to A or B. "
            f"Missing assignment for parish id(s): {sorted(missing)}"
        )

    unknown = assigned_parish_ids - original_parish_ids
    if unknown:
        raise ValueError(
            f"These parish id(s) do not belong to deanery {deanery_id}: {sorted(unknown)}"
        )

    invalid = {pid: t for pid, t in parish_assignments.items() if t not in ("A", "B")}
    if invalid:
        raise ValueError("Each parish must be assigned to either 'A' or 'B'")

    if original_parish_ids and not any(t == "A" for t in parish_assignments.values()):
        raise ValueError("Deanery A must receive at least one parish")
    if original_parish_ids and not any(t == "B" for t in parish_assignments.values()):
        raise ValueError("Deanery B must receive at least one parish")

    # The DB has a unique index on `name`, so if a new deanery is reusing the
    # original's name, that name has to be freed up before the insert below -
    # the DB doesn't know the original is about to be deleted. Rename it out
    # of the way now; it's deleted for real further down.
    if delete_original:
        original.name = f"__deanery_split_{original.id}"
        db.flush()

    # Create the two new deaneries. Falling back to the original zone keeps
    # behaviour sane if the caller doesn't want to move the split across zones.
    deanery_a = Deanery(name=deanery_a_name, zone_id=deanery_a_zone_id or original.zone_id)
    deanery_b = Deanery(name=deanery_b_name, zone_id=deanery_b_zone_id or original.zone_id)
    db.add_all([deanery_a, deanery_b])
    db.flush()  # assigns ids + lets the prefix-generation listener run for both

    # This is the actual "connection between parishes and deanery IDs": move
    # each parish to whichever new deanery it was assigned to. This has to go
    # through the relationship collections (not just parish.deanery_id)
    # because original.parishes is still loaded in memory - if we only set
    # the raw column, SQLAlchemy still considers these parishes dependents of
    # `original` when it processes the delete below, and nulls their FK back
    # out as part of safely deleting the parent. Removing them from
    # original.parishes (and appending to the target instead) keeps the ORM's
    # view of the relationship in sync with what we're actually doing.
    for parish in list(original.parishes):
        target = parish_assignments[parish.id]
        target_deanery = deanery_a if target == "A" else deanery_b
        original.parishes.remove(parish)
        target_deanery.parishes.append(parish)

    if delete_original:
        if original.events:
            raise ValueError(
                f"Cannot delete the original deanery: {len(original.events)} event(s) "
                f"still reference it. Reassign or remove those first, or split without "
                f"deleting the original."
            )
        db.delete(original)

    db.commit()
    db.refresh(deanery_a)
    db.refresh(deanery_b)
    return deanery_a, deanery_b