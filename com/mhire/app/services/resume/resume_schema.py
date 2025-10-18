from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class PersonalInformation(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    summary: Optional[str] = None
    country: Optional[str] = None
    street_address: Optional[str] = None
    city_state: Optional[str] = None
    postal_code: Optional[str] = None

class Education(BaseModel):
    school_university: Optional[str] = None
    location: Optional[str] = None
    degree: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class WorkExperience(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    currently_working_here: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibility: Optional[str] = None

class JobPreferences(BaseModel):
    job_categories: Optional[str] = None
    pay_day: Optional[str] = None
    salary_range: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ResumeData(BaseModel):
    personal_information: PersonalInformation
    education: List[Education]
    work_experience: List[WorkExperience]
    job_preferences: Optional[JobPreferences] = None
    skills: List[str] = []

class ResumeUploadResponse(BaseModel):
    success: bool
    message: str
    data: Optional[ResumeData] = None
    error: Optional[str] = None