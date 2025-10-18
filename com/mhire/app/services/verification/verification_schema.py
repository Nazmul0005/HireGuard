from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class VerificationResult(BaseModel):
    """Schema for face verification result."""
    success: bool
    match: bool
    confidence: float
    threshold_used: int
    message: str
    additional_info: Optional[Dict[str, Any]] = None
    face1_quality: Optional[Dict[str, Any]] = None
    face2_quality: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str
    message: str


class BatchVerificationResult(BaseModel):
    """Schema for batch verification result."""
    success: bool
    match: bool
    confidence: float
    threshold_used: int
    message: str
    additional_info: Optional[Dict[str, Any]] = None
    face1_quality: Optional[Dict[str, Any]] = None
    face2_quality: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    pair_index: int
    face_filename: str
    nid_filename: str


class BatchVerificationResponse(BaseModel):
    """Schema for batch verification response."""
    results: List[BatchVerificationResult]
    total_pairs: int


class APIInfo(BaseModel):
    """Schema for API information response."""
    api_name: str
    version: str
    description: str
    features: List[str]
    supported_formats: List[str]
    max_file_size: str
    confidence_threshold_range: str
    endpoints: Dict[str, str]


class OCRValidationResult(BaseModel):
    """Schema for OCR validation result."""
    is_valid_nid: bool
    confidence: float
    indicators_found: int
    found_indicators: List[str]
    extracted_text: str
    total_text_length: int
    error: Optional[str] = None


class PhotoValidationResult(BaseModel):
    """Schema for photo validation result."""
    is_valid_photo: bool
    confidence: float
    face_ratio: float
    characteristics: Dict[str, bool]
    faces_detected: int
    blur_level: float
    error: Optional[str] = None