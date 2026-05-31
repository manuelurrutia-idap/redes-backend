from pydantic import BaseModel
from typing import List, Optional
import datetime

# --- Activity ---
class ActivityBase(BaseModel):
    name: str
    duration: float = 0.0
    cost: float = 0.0

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    name: str | None = None
    duration: float | None = None
    cost: float | None = None

class Activity(ActivityBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True

# --- Dependency ---
class DependencyBase(BaseModel):
    weight: float = 1.0
    time: float = 0.0
    capacity: float = 1.0

class DependencyCreate(DependencyBase):
    from_activity_id: int
    to_activity_id: int

class DependencyUpdate(BaseModel):
    weight: float | None = None
    time: float | None = None
    capacity: float | None = None

class Dependency(DependencyBase):
    id: int
    project_id: int
    from_activity_id: int
    to_activity_id: int

    class Config:
        from_attributes = True

# --- Project ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime.datetime
    activities: List[Activity] = []
    dependencies: List[Dependency] = []

    class Config:
        from_attributes = True
