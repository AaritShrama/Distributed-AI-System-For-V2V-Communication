from fastapi import FastAPI, Depends
from backend.app.schemas.semantic_message import SemanticMessage
from backend.app.websocket.handlers import router as websocket_router
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.event import Event


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
