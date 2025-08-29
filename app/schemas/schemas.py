from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from ..models.models import MachineStatus

class MachineBase(BaseModel):
    name: str
    location: str

class MachineCreate(MachineBase):
    pass

class Machine(MachineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StatusBase(BaseModel):
    status: MachineStatus

class StatusCreate(StatusBase):
    pass

class Status(StatusBase):
    id: int
    machine_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class MachineDetail(Machine):
    current_status: Optional[Status] = None
    status_history: List[Status] = []

    class Config:
        from_attributes = True
