from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any # Added imports

class SexEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other" # Added for inclusivity, can be discussed
    PREFER_NOT_TO_SAY = "Prefer not to say" # Added for inclusivity

class Client(BaseModel):
    """
    Represents a client in the SFT system.
    Stores mandatory client information.
    """
    client_id: str # Assuming a unique identifier will be needed
    full_name: str
    age: int
    sex: SexEnum
    location: str  # e.g., "Region/Country"
    height_cm: float
    weight_kg: float
    assessment_data: Optional[Dict[str, Any]] = None # For storing assessment results, e.g., {"push_ups": 10, "plank_seconds": 60}
    # email: Optional[str] = None # Consider adding email later
    # join_date: Optional[datetime] = None # Consider adding join date later

    class Config:
        use_enum_values = True # Important for ensuring enum values are used
