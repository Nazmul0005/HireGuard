from pydantic import BaseModel
from typing import Optional, List

class FaceVerificationMatch(BaseModel):
    confidence: float
    face_token: str

class VerificationResponse(BaseModel):
    status: str
    message: str
    confidence: Optional[float] = None
    face_token: Optional[str] = None
    is_duplicate: bool = False
    matches: Optional[List[FaceVerificationMatch]] = None

class ErrorResponse(BaseModel):
    """Standard error response model"""
    status_code: int
    detail: str
    error_type: Optional[str] = None  # For categorizing errors
    timestamp: Optional[str] = None    # For error tracking
