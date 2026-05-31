from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    activities = relationship("Activity", back_populates="project", cascade="all, delete")
    dependencies = relationship("Dependency", back_populates="project", cascade="all, delete")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    duration = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)

    project = relationship("Project", back_populates="activities")
    
    # We can fetch incoming/outgoing via Dependency queries
    outgoing_dependencies = relationship("Dependency", foreign_keys='Dependency.from_activity_id', back_populates="from_activity", cascade="all, delete")
    incoming_dependencies = relationship("Dependency", foreign_keys='Dependency.to_activity_id', back_populates="to_activity", cascade="all, delete")

class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    from_activity_id = Column(Integer, ForeignKey("activities.id"))
    to_activity_id = Column(Integer, ForeignKey("activities.id"))
    
    weight = Column(Float, default=1.0) # distance or cost
    time = Column(Float, default=0.0)
    capacity = Column(Float, default=1.0)

    project = relationship("Project", back_populates="dependencies")
    from_activity = relationship("Activity", foreign_keys=[from_activity_id], back_populates="outgoing_dependencies")
    to_activity = relationship("Activity", foreign_keys=[to_activity_id], back_populates="incoming_dependencies")
