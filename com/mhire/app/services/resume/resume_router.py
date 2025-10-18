from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from com.mhire.app.services.resume.resume_schema import ResumeUploadResponse
from com.mhire.app.services.resume.resume import ResumeParser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Resume"])

# Initialize resume parser
resume_parser = ResumeParser()

@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_and_parse_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file (PDF, DOCX, or TXT)
    Returns structured resume data extracted using LLM
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload PDF, DOCX, or TXT files."
            )
        
        # Check file size (limit to 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum allowed size is 10MB."
            )
        
        logger.info(f"Processing resume file: {file.filename}")
        
        # Process the resume
        structured_data = resume_parser.process_resume(file_content, file.filename)
        
        logger.info("Resume processed successfully")
        
        return ResumeUploadResponse(
            success=True,
            message="Resume parsed successfully",
            data=structured_data
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return ResumeUploadResponse(
            success=False,
            message="Failed to parse resume",
            error=str(e)
        )