import requests
import json
from PIL import Image
import io
import logging
from typing import Optional, Tuple, Dict, Any
from com.mhire.app.config.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize config
config = Config()
API_KEY = config.api_key
API_SECRET = config.api_secret


class FaceVerificationService:
    """Service class for face verification operations using Face++ API."""
    
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.compare_url = 'https://api-us.faceplusplus.com/facepp/v3/compare'
        self.detect_url = 'https://api-us.faceplusplus.com/facepp/v3/detect'
        self.ocr_url = 'https://api-us.faceplusplus.com/imagepp/v1/recognizetext'
    
    def resize_image_if_needed(self, image_data: bytes, max_size_mb: int = 2, max_dimension: int = 2048) -> bytes:
        """
        Resize image if it's too large for Face++ API.
        
        Face++ Image Requirements:
        - File size: <= 2MB
        - Min dimension: 48px (shorter side)
        - Max dimension: 4096px (longer side)
        - Recommended max: 2048px × 2048px for best performance
        
        Args:
            image_data (bytes): Image data
            max_size_mb (int): Maximum file size in MB (default: 2)
            max_dimension (int): Maximum width/height in pixels (default: 2048)
        
        Returns:
            bytes: Resized and optimized image data
        """
        try:
            # Load image
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            width, height = img.size
            original_size_mb = len(image_data) / (1024 * 1024)
            logger.info(f"Original image: {width}x{height}, {original_size_mb:.2f} MB")
            
            # Check and resize dimensions if needed
            min_dimension = 48
            
            # Check if image is too large
            if width > max_dimension or height > max_dimension:
                logger.info(f"Image too large, resizing to max {max_dimension}px...")
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                width, height = img.size
                logger.info(f"Resized to: {width}x{height}")
            
            # Check if image is too small
            if min(width, height) < min_dimension:
                logger.warning(f"Image too small, needs to be at least {min_dimension}px on shorter side")
                scale = min_dimension / min(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width, height = img.size
                logger.info(f"Upscaled to: {width}x{height}")
            
            # Now compress to meet file size requirements
            quality = 90
            output = io.BytesIO()
            
            # Try different quality levels
            while quality > 20:
                output.seek(0)
                output.truncate()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                size_mb = output.tell() / (1024 * 1024)
                
                if size_mb <= max_size_mb:
                    logger.info(f"Final image: {width}x{height}, {size_mb:.2f} MB (quality: {quality})")
                    output.seek(0)
                    return output.getvalue()
                
                quality -= 5
            
            # If still too large after quality reduction, resize further
            logger.info("Still too large after quality reduction, reducing dimensions...")
            scale = 0.8
            
            while scale > 0.3:  # Don't reduce below 30% of current size
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                # Don't go below minimum dimension
                if min(new_width, new_height) < min_dimension:
                    break
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                output.seek(0)
                output.truncate()
                img_resized.save(output, format='JPEG', quality=85, optimize=True)
                size_mb = output.tell() / (1024 * 1024)
                
                if size_mb <= max_size_mb:
                    logger.info(f"Final image: {new_width}x{new_height}, {size_mb:.2f} MB")
                    output.seek(0)
                    return output.getvalue()
                
                scale -= 0.1
            
            # Last resort - use current image with lowest acceptable quality
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=70, optimize=True)
            size_mb = output.tell() / (1024 * 1024)
            logger.info(f"Final image (last resort): {width}x{height}, {size_mb:.2f} MB (quality: 70)")
            output.seek(0)
            return output.getvalue()
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return image_data  # Return original data as fallback
    
    def get_largest_face(self, faces_list: list) -> Optional[dict]:
        """
        Get the largest face from a list of detected faces.
        This helps handle NID cards with multiple photos of the same person.
        
        Args:
            faces_list (list): List of face objects from Face++ API
        
        Returns:
            dict: The largest face object
        """
        if not faces_list:
            return None
        
        largest_face = None
        max_area = 0
        
        for face in faces_list:
            # Calculate face area using face rectangle
            face_rect = face.get('face_rectangle', {})
            width = face_rect.get('width', 0)
            height = face_rect.get('height', 0)
            area = width * height
            
            if area > max_area:
                max_area = area
                largest_face = face
        
        return largest_face
    
    def compare_face_with_nid(self, face_image_data: bytes, nid_image_data: bytes, confidence_threshold: int = 80) -> dict:
        """
        Compare a face photo with an NID card photo to verify identity match.
        Now handles multiple faces in NID cards by selecting the largest face.
        
        Args:
            face_image_data (bytes): Face image data
            nid_image_data (bytes): NID image data
            confidence_threshold (int): Minimum confidence score for a match (default: 80)
        
        Returns:
            dict: Result containing match status, confidence score, and details
        """
        
        try:
            # Process both images to meet Face++ requirements
            logger.info("Processing face image...")
            processed_face = self.resize_image_if_needed(face_image_data)
            
            logger.info("Processing NID image...")
            processed_nid = self.resize_image_if_needed(nid_image_data)
            
            # Prepare files for API
            files = {
                'image_file1': ('face.jpg', processed_face, 'image/jpeg'),
                'image_file2': ('nid.jpg', processed_nid, 'image/jpeg')
            }
            
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret
            }
            
            # Make the API request
            logger.info("Sending comparison request to Face++ API...")
            response = requests.post(self.compare_url, files=files, data=data)
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing images: {str(e)}",
                'match': False,
                'confidence': 0
            }
        
        # Check if the API call was successful
        if response.status_code != 200:
            return {
                'success': False,
                'error': f"API request failed with status code {response.status_code}: {response.text}",
                'match': False,
                'confidence': 0
            }
        
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            return {
                'success': False,
                'error': "Unable to parse API response",
                'match': False,
                'confidence': 0
            }
        
        # Check for API errors
        if 'error_message' in result:
            return {
                'success': False,
                'error': f"Face++ API Error: {result['error_message']}",
                'match': False,
                'confidence': 0
            }
        
        # Check both images first, collect all face detection errors
        errors = []
        
        if 'faces1' not in result or len(result['faces1']) == 0:
            errors.append("No face detected in the face photo")
        
        if 'faces2' not in result or len(result['faces2']) == 0:
            errors.append("No face detected in the NID card")
        
        # If there are face detection errors, return combined message
        if errors:
            return {
                'success': False,
                'error': " and ".join(errors),
                'match': False,
                'confidence': 0
            }
        
        # Handle multiple faces in face photo (should still be single)
        if len(result['faces1']) > 1:
            return {
                'success': False,
                'error': "Multiple faces detected in face photo. Please use image with single face.",
                'match': False,
                'confidence': 0
            }
        
        # Handle multiple faces in NID card (select the largest one)
        selected_nid_face = None
        multiple_faces_info = {}
        
        if len(result['faces2']) > 1:
            logger.info(f"Multiple faces detected in NID card ({len(result['faces2'])} faces). Selecting the largest face...")
            selected_nid_face = self.get_largest_face(result['faces2'])
            
            if selected_nid_face:
                # Get face rectangle info for logging
                face_rect = selected_nid_face.get('face_rectangle', {})
                logger.info(f"Selected main face with dimensions: {face_rect.get('width', 'unknown')}x{face_rect.get('height', 'unknown')} pixels")
                multiple_faces_info = {
                    'selected_face_dimensions': f"{face_rect.get('width', 'unknown')}x{face_rect.get('height', 'unknown')}"
                }
            else:
                return {
                    'success': False,
                    'error': "Could not select appropriate face from NID card",
                    'match': False,
                    'confidence': 0
                }
        else:
            selected_nid_face = result['faces2'][0]
        
        # Get confidence score
        confidence = result.get('confidence', 0)
        
        # Determine if it's a match based on threshold
        is_match = confidence >= confidence_threshold
        
        # Prepare additional info
        additional_info = {
            'faces_in_face_photo': len(result['faces1']),
            'faces_in_nid_card': len(result['faces2']),
            'used_largest_nid_face': len(result['faces2']) > 1,
            **multiple_faces_info
        }
        
        logger.info(f"Comparison complete - Match: {is_match}, Confidence: {confidence}%")
        
        return {
            'success': True,
            'match': is_match,
            'confidence': confidence,
            'threshold_used': confidence_threshold,
            'face1_quality': result['faces1'][0].get('face_quality', {}),
            'face2_quality': selected_nid_face.get('face_quality', {}),
            'additional_info': additional_info,
            'message': f"{'Match' if is_match else 'No match'} - Confidence: {confidence}%"
        }
    
    def validate_nid_document_with_ocr(self, image_data: bytes) -> dict:
        """
        Validate if the uploaded image is actually an NID card using Face++ OCR API.
        
        Args:
            image_data (bytes): Image data to validate
        
        Returns:
            dict: Validation result with OCR text and document indicators
        """
        try:
            # Process image to meet Face++ requirements
            processed_image = self.resize_image_if_needed(image_data)
            
            files = {
                'image_file': ('nid.jpg', processed_image, 'image/jpeg')
            }
            
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret
            }
            
            logger.info("Sending OCR request to Face++ API...")
            response = requests.post(self.ocr_url, files=files, data=data)
            
            if response.status_code != 200:
                return {
                    'is_valid_nid': False,
                    'error': f"OCR API request failed: {response.status_code}",
                    'confidence': 0
                }
            
            result = response.json()
            
            if 'error_message' in result:
                return {
                    'is_valid_nid': False,
                    'error': f"OCR API Error: {result['error_message']}",
                    'confidence': 0
                }
            
            # Extract text from OCR result
            extracted_text = ""
            if 'result' in result and 'text' in result['result']:
                for text_item in result['result']['text']:
                    extracted_text += text_item.get('value', '') + " "
            
            extracted_text = extracted_text.lower().strip()
            
            # Define NID/document indicators (common terms found in official documents)
            nid_indicators = [
                'national', 'identity', 'card', 'government', 'republic', 'bangladesh',
                'citizen', 'birth', 'date', 'father', 'mother', 'address', 'signature',
                'id', 'no', 'serial', 'issue', 'expire', 'valid', 'official', 'ministry',
                'department', 'registration', 'voter', 'passport', 'license', 'authority'
            ]
            
            # Count how many indicators are found
            indicators_found = 0
            found_indicators = []
            
            for indicator in nid_indicators:
                if indicator in extracted_text:
                    indicators_found += 1
                    found_indicators.append(indicator)
            
            # Calculate confidence based on indicators found
            confidence = min((indicators_found / len(nid_indicators)) * 100, 100)
            
            # Consider it a valid NID if we find at least 2 indicators
            is_valid_nid = indicators_found >= 2
            
            logger.info(f"OCR validation complete - Valid NID: {is_valid_nid}, Indicators found: {indicators_found}")
            
            return {
                'is_valid_nid': is_valid_nid,
                'confidence': confidence,
                'indicators_found': indicators_found,
                'found_indicators': found_indicators,
                'extracted_text': extracted_text[:200],  # First 200 chars for debugging
                'total_text_length': len(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"Error in OCR validation: {str(e)}")
            return {
                'is_valid_nid': False,
                'error': f"OCR validation failed: {str(e)}",
                'confidence': 0
            }
    
    def validate_face_photo_characteristics(self, image_data: bytes) -> dict:
        """
        Validate if the uploaded image has characteristics of a regular photo (not a document).
        
        Args:
            image_data (bytes): Image data to validate
        
        Returns:
            dict: Validation result with photo characteristics
        """
        try:
            # Process image to meet Face++ requirements
            processed_image = self.resize_image_if_needed(image_data)
            
            files = {
                'image_file': ('photo.jpg', processed_image, 'image/jpeg')
            }
            
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'return_attributes': 'blur,eyestatus,emotion,beauty,headpose'
            }
            
            logger.info("Sending face detection request to Face++ API...")
            response = requests.post(self.detect_url, files=files, data=data)
            
            if response.status_code != 200:
                return {
                    'is_valid_photo': False,
                    'error': f"Face detection API failed: {response.status_code}",
                    'confidence': 0
                }
            
            result = response.json()
            
            if 'error_message' in result:
                return {
                    'is_valid_photo': False,
                    'error': f"Face detection error: {result['error_message']}",
                    'confidence': 0
                }
            
            if 'faces' not in result or len(result['faces']) == 0:
                return {
                    'is_valid_photo': False,
                    'error': "No face detected in photo",
                    'confidence': 0
                }
            
            # Analyze the first (and should be only) face
            face = result['faces'][0]
            face_rect = face.get('face_rectangle', {})
            attributes = face.get('attributes', {})
            
            # Calculate face-to-image ratio (photos typically have larger face ratios)
            image_width = result.get('image_width', 1)
            image_height = result.get('image_height', 1)
            face_width = face_rect.get('width', 0)
            face_height = face_rect.get('height', 0)
            
            face_area = face_width * face_height
            image_area = image_width * image_height
            face_ratio = (face_area / image_area) * 100 if image_area > 0 else 0
            
            # Photo characteristics scoring
            photo_score = 0
            characteristics = {}
            
            # 1. Face size ratio (photos typically have larger faces)
            if face_ratio > 5:  # Face takes up more than 5% of image
                photo_score += 25
                characteristics['good_face_ratio'] = True
            else:
                characteristics['good_face_ratio'] = False
            
            # 2. Blur analysis (photos can have some blur, documents are usually sharp)
            blur_info = attributes.get('blur', {})
            blur_level = blur_info.get('blurness', {}).get('value', 0)
            if 0 < blur_level < 50:  # Some natural blur is okay for photos
                photo_score += 20
                characteristics['natural_blur'] = True
            else:
                characteristics['natural_blur'] = False
            
            # 3. Head pose (photos often have slight angles)
            headpose = attributes.get('headpose', {})
            yaw = abs(headpose.get('yaw_angle', 0))
            pitch = abs(headpose.get('pitch_angle', 0))
            roll = abs(headpose.get('roll_angle', 0))
            
            if yaw < 30 and pitch < 30 and roll < 30:  # Natural pose variations
                photo_score += 25
                characteristics['natural_pose'] = True
            else:
                characteristics['natural_pose'] = False
            
            # 4. Multiple faces check (documents might have multiple photos)
            if len(result['faces']) == 1:
                photo_score += 30
                characteristics['single_face'] = True
            else:
                characteristics['single_face'] = False
            
            is_valid_photo = photo_score >= 50  # At least 50% confidence
            
            logger.info(f"Photo validation complete - Valid photo: {is_valid_photo}, Score: {photo_score}")
            
            return {
                'is_valid_photo': is_valid_photo,
                'confidence': photo_score,
                'face_ratio': face_ratio,
                'characteristics': characteristics,
                'faces_detected': len(result['faces']),
                'blur_level': blur_level
            }
            
        except Exception as e:
            logger.error(f"Error in photo validation: {str(e)}")
            return {
                'is_valid_photo': False,
                'error': f"Photo validation failed: {str(e)}",
                'confidence': 0
            }
    
    def process_uploaded_image(self, image_data: bytes) -> Optional[bytes]:
        """Process uploaded image and return optimized data."""
        try:
            # Process the image to meet Face++ requirements
            processed_data = self.resize_image_if_needed(image_data)
            return processed_data
        except Exception as e:
            logger.error(f"Error processing uploaded image: {str(e)}")
            return None