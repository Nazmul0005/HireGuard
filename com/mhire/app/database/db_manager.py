import datetime
import logging
from typing import Dict, List, Tuple, Optional

from fastapi import HTTPException

from com.mhire.app.database.db_connection import DBConnection

logger = logging.getLogger(__name__)

class DBManager(DBConnection):
    def __init__(self):
        super().__init__()
        self.MAX_FACESET_CAPACITY = 1000

    async def save_face_token(self, face_token: str, faceset_id: str = None) -> bool:
        """Save a face token to an available faceset, create new if needed
        
        Args:
            face_token: The face token to save
            faceset_id: Optional faceset ID to use (must exist in Face++ API)
        """
        try:
            # If faceset_id is provided, use it (it should already exist in Face++ API)
            if not faceset_id:
                # Find a faceset with available capacity
                available_faceset = await self.find_available_faceset()
                
                if available_faceset:
                    faceset_id, current_count = available_faceset
                else:
                    # This should not happen as the faceset should be created in Face++ API first
                    # and then passed to this method
                    logger.error("No faceset ID provided and no available faceset found")
                    return False

            # Get existing faceset or create new one
            result = await self.collection.find_one_and_update(
                {'_id': faceset_id},
                {
                    '$setOnInsert': {
                        'created_at': datetime.datetime.now(),
                    },
                    '$push': {'face_tokens': face_token},
                    '$inc': {'count': 1}
                },
                upsert=True,
                return_document=True
            )

            return True
        except Exception as e:
            logger.error(f"Error saving face token: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save face token: {str(e)}")

    async def get_all_stored_faces(self) -> Dict[str, List[str]]:
        """Get all facesets and their tokens for verification"""
        try:
            result = {}
            cursor = self.collection.find({}, {'face_tokens': 1})
            async for doc in cursor:
                result[str(doc['_id'])] = doc.get('face_tokens', [])
            return result
        except Exception as e:
            logger.error(f"Error getting stored faces: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get stored faces: {str(e)}")

    async def get_faceset_metadata(self) -> Dict[str, Dict]:
        """Get metadata for all facesets"""
        try:
            result = {}
            cursor = self.collection.find({}, {'count': 1, 'created_at': 1})
            async for doc in cursor:
                result[str(doc['_id'])] = {
                    "count": doc.get("count", 0),
                    "created_at": doc.get("created_at")
                }
            return result
        except Exception as e:
            logger.error(f"Error getting faceset metadata: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get faceset metadata: {str(e)}")

    async def find_available_faceset(self) -> Optional[Tuple[str, int]]:
        """Find a faceset with available capacity"""
        try:
            # Find a faceset with count less than max capacity
            doc = await self.collection.find_one(
                {'count': {'$lt': self.MAX_FACESET_CAPACITY}},
                sort=[('count', 1)]  # Sort by count ascending to get the least full faceset
            )
            if doc:
                return str(doc['_id']), doc.get('count', 0)
            return None
        except Exception as e:
            logger.error(f"Error finding available faceset: {str(e)}")
            return None

    async def update_faceset_count(self, faceset_id: str, count: int) -> bool:
        """Update the face count for a faceset"""
        try:
            result = await self.collection.update_one(
                {'_id': faceset_id},
                {'$set': {'count': count}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating faceset count: {str(e)}")
            return False