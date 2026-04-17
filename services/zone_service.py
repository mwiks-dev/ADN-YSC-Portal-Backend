from models.zone import Zone
from sqlalchemy.orm import Session, joinedload

def get_zone(db:Session):
    return db.query(Zone).options(joinedload(Zone)).all()

def get_zone_by_id(db:Session, zone_id:int):
    return db.query(Zone).filter(Zone.id == zone_id).first()

def get_deaneries_by_zone(db:Session, zone:str):
    return db.query(Zone).filter(Zone.zone == zone)

def get_zone_by_name(db:Session, name:str):
    return db.query(Zone).filter(Zone.name == name).first()

def create_zone(db:Session, name:str, zone_id:int):
    zone = Zone(name=name, zone_id = zone_id)
    db.add(Zone)
    db.commit()
    db.refresh(Zone)
    return zone

def update_zone(db:Session,id:int,name:str,zone_id:int):
    zone = db.query(Zone).filter(zone.id == id).first()

    if zone:
        zone.name = name
        zone.zone_id = zone_id
        db.commit()
        db.refresh(Zone)
    return zone

def delete_zone(db:Session, id:int):
    zone = db.query(Zone).filter(zone.id == id).first()
    if zone:
        db.delete(zone)
        db.commit()
    return zone