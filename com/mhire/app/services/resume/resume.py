from openai import OpenAI
import json
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
from typing import Dict, Any
from com.mhire.app.config.config import Config
from com.mhire.app.services.resume.resume_schema import ResumeData, PersonalInformation, Education, WorkExperience, JobPreferences

class ResumeParser:
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.model_name2 = self.config.model_name2 or "gpt-3.5-turbo"

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()
            pdf_document.close()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

    def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text based on file extension"""
        if filename.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_content)
        elif filename.lower().endswith('.txt'):
            return file_content.decode('utf-8')
        else:
            raise Exception("Unsupported file format. Please upload PDF, DOCX, or TXT files.")

    def create_extraction_prompt(self, cv_text: str) -> str:
        """Create a prompt for LLM to extract structured data"""
        prompt = f"""
        Extract the following information from the CV/Resume text below and return it as a JSON object with this exact structure:

        {{
            "personal_information": {{
                "name": "Full name",
                "phone_number": "Phone number",
                "email": "Email address",
                "gender": "Gender",
                "date_of_birth": "Date of birth in dd/mm/yyyy format",
                "summary": "Professional summary or objective",
                "country": "Country",
                "street_address": "Street address",
                "city_state": "City and State",
                "postal_code": "Postal code"
            }},
            "education": [
                {{
                    "school_university": "Institution name",
                    "location": "Location",
                    "degree": "Degree/qualification",
                    "start_date": "Start date in dd/mm/yyyy format",
                    "end_date": "End date in dd/mm/yyyy format"
                }}
            ],
            "work_experience": [
                {{
                    "job_title": "Job title",
                    "company_name": "Company name",
                    "location": "Location",
                    "currently_working_here": true/false,
                    "start_date": "Start date in dd/mm/yyyy format",
                    "end_date": "End date in dd/mm/yyyy format or null if currently working",
                    "responsibility": "Job responsibilities and achievements"
                }}
            ],
            "job_preferences": {{
                "job_categories": "Preferred job categories",
                "pay_day": "Payment frequency preference",
                "salary_range": "Expected salary range",
                "start_date": "Preferred start date",
                "end_date": "Contract end date if applicable"
            }},
            "skills": ["skill1", "skill2", "skill3"]
        }}

        Rules:
        1. If information is not available, use null for that field
        2. For boolean fields, use true/false
        3. Extract all education entries and work experiences as separate objects in their respective arrays
        4. For skills, extract both technical and soft skills as a list
        5. Ensure all dates are in dd/mm/yyyy format
        6. Return only valid JSON, no additional text

        CV/Resume Text:
        {cv_text}
        """
        return prompt

    def parse_with_llm(self, cv_text: str) -> Dict[Any, Any]:
        """Use LLM to parse CV text and extract structured data"""
        try:
            prompt = self.create_extraction_prompt(cv_text)
            
            response = self.client.chat.completions.create(
                model=self.model_name2,
                messages=[
                    {"role": "system", "content": "You are an expert CV/Resume parser. Extract information accurately and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            try:
                json_data = json.loads(content)
                return json_data
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_content = content[start_idx:end_idx]
                    return json.loads(json_content)
                else:
                    raise Exception("Could not extract valid JSON from LLM response")
                    
        except Exception as e:
            raise Exception(f"Error parsing CV with LLM: {str(e)}")

    def validate_and_structure_data(self, parsed_data: Dict[Any, Any]) -> ResumeData:
        """Validate and structure the parsed data into Pydantic models"""
        try:
            # Create PersonalInformation object
            personal_info_data = parsed_data.get('personal_information', {})
            personal_info = PersonalInformation(**personal_info_data)
            
            # Create Education objects
            education_list = []
            for edu_data in parsed_data.get('education', []):
                education_list.append(Education(**edu_data))
            
            # Create WorkExperience objects
            work_experience_list = []
            for work_data in parsed_data.get('work_experience', []):
                work_experience_list.append(WorkExperience(**work_data))
            
            # Create JobPreferences object
            job_pref_data = parsed_data.get('job_preferences', {})
            job_preferences = JobPreferences(**job_pref_data) if job_pref_data else None
            
            # Get skills
            skills = parsed_data.get('skills', [])
            
            # Create final ResumeData object
            resume_data = ResumeData(
                personal_information=personal_info,
                education=education_list,
                work_experience=work_experience_list,
                job_preferences=job_preferences,
                skills=skills
            )
            
            return resume_data
            
        except Exception as e:
            raise Exception(f"Error validating and structuring data: {str(e)}")

    def process_resume(self, file_content: bytes, filename: str) -> ResumeData:
        """Main method to process resume file and return structured data"""
        # Extract text from file
        cv_text = self.extract_text_from_file(file_content, filename)
        
        # Parse with LLM
        parsed_data = self.parse_with_llm(cv_text)
        
        # Validate and structure data
        structured_data = self.validate_and_structure_data(parsed_data)
        
        return structured_data