from pydantic import BaseModel, ConfigDict
from typing import Optional

class CrimeCriminalLinkBase(BaseModel):
    crime_id: str
    criminal_id: str
    role: str = "ACCUSED"
    notes: Optional[str] = None

class CrimeCriminalLinkCreate(CrimeCriminalLinkBase):
    pass

class CrimeCriminalLinkUpdate(BaseModel):
    role: Optional[str] = None
    notes: Optional[str] = None

class CrimeCriminalLinkResponse(CrimeCriminalLinkBase):
    ROWID: str
    linked_by_officer_id: Optional[str] = None
    linked_at: Optional[str] = None
    CREATEDTIME: str
    MODIFIEDTIME: str

    model_config = ConfigDict(from_attributes=True)
