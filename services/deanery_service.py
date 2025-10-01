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