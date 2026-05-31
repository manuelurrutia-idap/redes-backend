from sqlalchemy.orm import Session
import models, schemas

# Project
def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project

# Activity
def get_activities(db: Session, project_id: int):
    return db.query(models.Activity).filter(models.Activity.project_id == project_id).all()

def create_activity(db: Session, activity: schemas.ActivityCreate, project_id: int):
    db_activity = models.Activity(**activity.model_dump(), project_id=project_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def delete_activity(db: Session, activity_id: int):
    db_act = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if db_act:
        db.delete(db_act)
        db.commit()
    return db_act

def update_activity(db: Session, activity_id: int, activity_update: schemas.ActivityUpdate):
    db_act = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if db_act:
        update_data = activity_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_act, key, value)
        db.commit()
        db.refresh(db_act)
    return db_act

# Dependency
def get_dependencies(db: Session, project_id: int):
    return db.query(models.Dependency).filter(models.Dependency.project_id == project_id).all()

def create_dependency(db: Session, dependency: schemas.DependencyCreate, project_id: int):
    db_dependency = models.Dependency(**dependency.model_dump(), project_id=project_id)
    db.add(db_dependency)
    db.commit()
    db.refresh(db_dependency)
    return db_dependency

def delete_dependency(db: Session, dependency_id: int):
    db_dep = db.query(models.Dependency).filter(models.Dependency.id == dependency_id).first()
    if db_dep:
        db.delete(db_dep)
        db.commit()
    return db_dep

def update_dependency(db: Session, dependency_id: int, dependency_update: schemas.DependencyUpdate):
    db_dep = db.query(models.Dependency).filter(models.Dependency.id == dependency_id).first()
    if db_dep:
        update_data = dependency_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dep, key, value)
        db.commit()
        db.refresh(db_dep)
    return db_dep
