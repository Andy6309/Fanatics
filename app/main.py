from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

# Import database and models
from .db.database import engine, get_db
from .models import models
from .schemas import schemas

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fanatics Collectibles Machine Monitoring")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# API Endpoints
@app.post("/api/machines", response_model=schemas.Machine)
def create_machine(machine: schemas.MachineCreate, db: Session = Depends(get_db)):
    db_machine = models.Machine(**machine.model_dump())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

@app.post("/api/machines/{machine_id}/status", response_model=schemas.Status)
def log_status(
    machine_id: int, status: schemas.StatusCreate, db: Session = Depends(get_db)
):
    # Check if machine exists
    db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Create status log
    db_status = models.StatusLog(machine_id=machine_id, **status.model_dump())
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

@app.get("/api/machines", response_model=List[schemas.Machine])
def list_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    machines = db.query(models.Machine).offset(skip).limit(limit).all()
    return machines

@app.get("/api/machines/{machine_id}", response_model=schemas.MachineDetail)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    # Get machine
    db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Get status history (last 5)
    status_history = (
        db.query(models.StatusLog)
        .filter(models.StatusLog.machine_id == machine_id)
        .order_by(models.StatusLog.timestamp.desc())
        .limit(5)
        .all()
    )
    
    # Get current status (most recent)
    current_status = status_history[0] if status_history else None
    
    # Create response
    machine_detail = schemas.MachineDetail(
        **db_machine.__dict__,
        current_status=current_status,
        status_history=status_history
    )
    return machine_detail

# Web Interface
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    machines = db.query(models.Machine).all()
    return templates.TemplateResponse("index.html", {"request": request, "machines": machines})

@app.get("/machines/{machine_id}", response_class=HTMLResponse)
async def machine_detail(request: Request, machine_id: int, db: Session = Depends(get_db)):
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Get status history for the chart
    status_history = (
        db.query(models.StatusLog)
        .filter(models.StatusLog.machine_id == machine_id)
        .order_by(models.StatusLog.timestamp.asc())
        .all()
    )
    
    # Prepare data for the chart
    chart_data = {
        'labels': [s.timestamp.strftime('%Y-%m-%d %H:%M:%S') for s in status_history],
        'statuses': [s.status.value for s in status_history]
    }
    
    return templates.TemplateResponse(
        "machine_detail.html", 
        {
            "request": request, 
            "machine": machine,
            "status_history": status_history[:5],  # Last 5 status updates for the list
            "chart_data": chart_data
        }
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
