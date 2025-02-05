from pydantic import BaseModel, UUID4, EmailStr

class Case(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    username: str

class UserCaseResponse(BaseModel):
    id: UUID4
    patient_id: str
    prediction: str
    
class CaseRequest(BaseModel):
    case_no: str
