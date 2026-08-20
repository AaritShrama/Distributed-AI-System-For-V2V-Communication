from fastapi import FastAPI, Depends, HTTPException
from backend.app.schemas.semantic_message import SemanticMessage
from backend.app.websocket.handlers import router as websocket_router
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.event import Event
from backend.app.models.vehicle import Vehicle
from backend.app.schemas.vehicle import VehicleCreate, VehicleResponse



app = FastAPI(
    title="Ditributed AI System Backend",
    version="0.1.0"
)

app.include_router(websocket_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "av-backend" 
    }

@app.post("/events")
async def recieve_event(message : SemanticMessage, db : Session = Depends(get_db)):
    event = Event(
        vehicle_id=message.vehicle_id,
        event_type=message.event_type,
        object_type=message.object_type,
        confidence=message.confidence,
        risk_level=message.risk_level,
        latitude=message.position.latitude,
        longitude=message.position.longitude,
        description=message.description,
        recommendation=message.recommendation,
        timestamp=message.timestamp
        )
    db.add(event)
    db.commit()
    db.refresh(event)    
    
    return {
        "status": "recieved",
        "event_id": event.id ,
        "message": message
    }

@app.post("/vehicles", response_model=VehicleResponse)
async def register_vehicle(
    vehicle_data:VehicleCreate,
    db: Session = Depends(get_db)
    ):

    existing_vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.vehicle_id == vehicle_data.vehicle_id)
        .first()
    )

    if existing_vehicle:
        raise HTTPException(
            status_code=409,
            detail="Vehicle already registered"
        )
    
    vehicle = Vehicle(
        vehicle_id=vehicle_data.vehicle_id,
        status="offline"
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle

@app.get("/vehicles", response_model=list[VehicleResponse])
async def get_vehicles(
    db: Session = Depends(get_db)
):
    vehicles = db.query(Vehicle).all()

    return vehicles


@app.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleResponse
)
async def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.vehicle_id == vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    return vehicle







