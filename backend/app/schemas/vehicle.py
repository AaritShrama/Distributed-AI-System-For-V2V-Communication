from datetime import datetime
from pydantic import BaseModel

class VehicleCreate(BaseModel):
    vehicle_id:str

class VehicleResponse(BaseModel):
    id: int
    vehicle_id: str
    status: str
    last_seen: datetime | None=None
    model_config= {"from_attributes":True}

