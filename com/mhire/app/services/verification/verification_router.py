from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import logging
from typing import List

from com.mhire.app.services.verification.verification import FaceVerificationService
from com.mhire.app.services.verification.verification_schema import (
    VerificationResult, 
    HealthCheck, 
    BatchVerificationResponse, 
    APIInfo,
    BatchVerificationResult
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1",
    tags=["NID and Face Verification"]
)

# Initialize the verification service
verification_service = FaceVerificationService()


@router.post("/nid_verification")
async def verify_identity(
    
    nid_card: UploadFile = File(..., description="NID card image"),
    face_photo: UploadFile = File(..., description="Face photo for verification"),
    confidence_threshold: int = Form(75, description="Confidence threshold (50-95)")
):
    """
    Verify identity by comparing a face photo with an NID card.
    
    - **face_photo**: Upload a clear, front-facing photo of the person
    - **nid_card**: Upload a clear photo of the NID card (supports multiple photos on card)
    - **confidence_threshold**: Minimum confidence score required for a positive match (50-95)
    
    Returns verification result with confidence score and match status.
    """
    
    # Validate confidence threshold
    if not 50 <= confidence_threshold <= 95:
        return JSONResponse(
            status_code=400,
            content={"message": "Confidence threshold must be between 50 and 95"}
        )
    
    # Check if API keys are configured
    if not verification_service.api_key or not verification_service.api_secret:
        return JSONResponse(
            status_code=500,
            content={"message": "Face++ API credentials not configured"}
        )
    
    # Validate file types
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
    
    if face_photo.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"message": f"Face photo must be JPEG or PNG. Got: {face_photo.content_type}"}
        )
    
    if nid_card.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"message": f"NID card must be JPEG or PNG. Got: {nid_card.content_type}"}
        )
    
    try:
        # Read uploaded files
        face_data = await face_photo.read()
        nid_data = await nid_card.read()
        
        # Validate file sizes (max 10MB each)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(face_data) > max_size:
            return JSONResponse(
                status_code=400,
                content={"message": "Face photo file size too large (max 10MB)"}
            )
        
        if len(nid_data) > max_size:
            return JSONResponse(
                status_code=400,
                content={"message": "NID card file size too large (max 10MB)"}
            )
        
        # Process images
        logger.info("Processing face photo...")
        processed_face_data = verification_service.process_uploaded_image(face_data)
        
        if processed_face_data is None:
            return JSONResponse(
                status_code=400,
                content={"message": "Failed to process face photo"}
            )
        
        logger.info("Processing NID card...")
        processed_nid_data = verification_service.process_uploaded_image(nid_data)
        
        if processed_nid_data is None:
            return JSONResponse(
                status_code=400,
                content={"message": "Failed to process NID card"}
            )
        
        # Perform verification
        logger.info("Comparing faces...")
        result = verification_service.compare_face_with_nid(
            processed_face_data,
            processed_nid_data,
            confidence_threshold
        )
        
        # Handle error cases with clean error messages
        if not result.get('success', False):
            error_message = result.get('error', 'Verification failed')
            
            # Customize error messages for specific cases
            if "No face detected in the face photo and No face detected in the NID card" in error_message:
                return JSONResponse(
                    status_code=400,
                    content={"message": "No face found in both the photo and NID card"}
                )
            elif "No face detected in the face photo" in error_message:
                return JSONResponse(
                    status_code=400,
                    content={"message": "No face found in the photo"}
                )
            elif "No face detected in the NID card" in error_message:
                return JSONResponse(
                    status_code=400,
                    content={"message": "No face found in the NID card"}
                )
            elif "Multiple faces detected in face photo" in error_message:
                return JSONResponse(
                    status_code=400,
                    content={"message": "Multiple faces detected in face photo. Please use image with single face"}
                )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"message": error_message}
                )
        
        # Return successful result as VerificationResult model
        return VerificationResult(**result)
        
    except Exception as e:
        logger.error(f"Unexpected error during verification: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": f"An unexpected error occurred: {str(e)}"}
        )


