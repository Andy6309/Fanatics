from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.database import Base
import enum

class MachineStatus(str, enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    status_history = relationship("StatusLog", back_populates="machine", cascade="all, delete-orphan")

class StatusLog(Base):
    __tablename__ = "status_logs"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    status = Column(Enum(MachineStatus))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    machine = relationship("Machine", back_populates="status_history")
