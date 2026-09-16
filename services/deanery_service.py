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
):
    """
    Splits an existing deanery into two.

    Deanery "A" REUSES the original deanery's primary key: it's the same
    row, just renamed and/or re-zoned in place. Anything elsewhere in the
    database that references the original deanery_id (events, historical
    records, reports, etc.) automatically keeps pointing at a valid,
    correct deanery - no reassignment, no dangling foreign keys, and no
    leftover "retired" deanery row hanging around.

    Deanery "B" is a genuinely new row.

    `parish_assignments` maps parish_id -> "A" or "B", letting the caller
    decide exactly which of the two resulting deaneries each existing
    parish ends up under. Every parish currently in the source deanery must
    appear in the mapping, and both sides must end up with at least one
    parish - otherwise it isn't really a split.

    Either side can be moved to a different zone by passing a zone_id that
    differs from the original deanery's zone; omitting a zone_id (None)
    keeps that side in the original zone.
    """
    original = (
        db.query(Deanery)
        .options(joinedload(Deanery.parishes))
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

    # Name-uniqueness checks must exclude the original row itself, since
    # deanery A is allowed to keep (or only slightly change) the original's
    # own name.
    existing_a = get_deanery_by_name(db, deanery_a_name)
    if existing_a and existing_a.id != original.id:
        raise ValueError(f"A deanery named '{deanery_a_name}' already exists")
    existing_b = get_deanery_by_name(db, deanery_b_name)
    if existing_b and existing_b.id != original.id:
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

    # Deanery B: a brand new row. Can live in a different zone than the
    # original deanery did.
    deanery_b = Deanery(name=deanery_b_name, zone_id=deanery_b_zone_id or original.zone_id)
    db.add(deanery_b)
    db.flush()  # assigns its id + lets the prefix-generation listener run

    # Deanery A: the ORIGINAL row, renamed/re-zoned in place. Its id never
    # changes, so every existing foreign-key reference to it stays valid
    # with no extra work.
    original.name = deanery_a_name
    original.zone_id = deanery_a_zone_id or original.zone_id

    # Only parishes moving to B need their deanery_id updated - parishes
    # staying on A are already pointing at `original.id`, which is unchanged.
    for parish in original.parishes:
        if parish_assignments[parish.id] == "B":
            parish.deanery_id = deanery_b.id

    db.commit()
    db.refresh(original)
    db.refresh(deanery_b)
    return original, deanery_b