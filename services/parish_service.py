from models.parish import Parish
from models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload


def get_parishes(db:Session):
    return db.query(Parish).options(joinedload(Parish.deanery)).all()

def get_parish_by_id(db:Session,parish_id:int):
    return db.query(Parish).filter(Parish.id == parish_id).first()

def get_parishes_by_deanery(db:Session,deanery:str):
    return db.query(Parish).filter(Parish.deanery == deanery)

def get_all_users_of_parish(db:Session,parish_id:int):
    return db.query(User).filter(User.parish_id==parish_id).all()

def get_parish_by_name(db:Session,name:str):
    return db.query(Parish).options(joinedload(Parish.deanery)).filter_by(name=name).first()

def create_parish(db:Session, name:str,deanery_id:int):
    parish = Parish(name = name,deanery_id = deanery_id)
    db.add(parish)
    db.commit()
    db.refresh(parish)
    return parish

def update_parish(db:Session,id:int,name:str,deanery_id:int):
    parish = db.query(Parish).filter(Parish.id == id).first()
    
    if parish:
        parish.name = name
        parish.deanery_id = deanery_id
        db.commit()
        db.refresh(parish)
    return parish
    
def delete_parish(db:Session,id:int):
    parish = db.query(Parish).filter(Parish.id == id).first()
   
    if parish:
        db.delete(parish)
        db.commit()
    return parish