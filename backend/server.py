from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import io
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import re
import time

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'passport_photos_db')]

# Google Drive configuration with service account
GOOGLE_FOLDER_ID = os.environ.get('GOOGLE_FOLDER_ID', '')
SERVICE_ACCOUNT_KEY_PATH = os.environ.get('SERVICE_ACCOUNT_KEY_PATH', '')

# Initialize Google Drive service with service account
GOOGLE_DRIVE_SERVICE = None
if SERVICE_ACCOUNT_KEY_PATH and Path(SERVICE_ACCOUNT_KEY_PATH).exists():
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES)
        GOOGLE_DRIVE_SERVICE = build('drive', 'v3', credentials=credentials)
        logger.info("✓ Google Drive service account initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google Drive service: {str(e)}")
        GOOGLE_DRIVE_SERVICE = None
else:
    logger.warning("Google Drive service account not configured")

# Create uploads directory for local storage
UPLOADS_DIR = ROOT_DIR / 'uploads'
UPLOADS_DIR.mkdir(exist_ok=True)

# Create the main app without a prefix
app = FastAPI(title="Passport Photo Generator API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============= MODELS =============

class PassportPhotoMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    storage_mode: str  # "google_drive" or "local"
    drive_file_id: Optional[str] = None
    drive_file_url: Optional[str] = None
    local_file_path: Optional[str] = None
    user_email: Optional[str] = None
    name_on_photo: str
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    image_dimensions: str = "600x600"
    original_filename: str
    file_size_bytes: int
    processing_status: str = "success"

class ProcessResponse(BaseModel):
    success: bool
    mode: str
    drive_file_id: Optional[str] = None
    drive_file_url: Optional[str] = None
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    filename: str
    metadata_id: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str

# ============= HELPER FUNCTIONS =============

def sanitize_filename(name: str) -> str:
    """Sanitize name for use in filename"""
    # Remove special characters, keep only alphanumeric, spaces, hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_').lower()
    return sanitized

def detect_face_opencv(image_bytes: bytes) -> Optional[tuple]:
    """Detect face using OpenCV Haar Cascade"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            logger.warning("No face detected")
            return None
        
        # Get the largest face
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        logger.info(f"Face detected at ({x}, {y}) with size {w}x{h}")
        return (x, y, w, h, img.shape[1], img.shape[0])  # x, y, w, h, img_width, img_height
        
    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return None

def process_passport_photo(image_bytes: bytes, name: str, face_coords: Optional[tuple] = None) -> tuple[bytes, int]:
    """Process image to passport photo specifications"""
    try:
        # Open image with PIL
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        original_width, original_height = img.size
        logger.info(f"Original image size: {original_width}x{original_height}")
        
        # If no face coordinates provided, try to detect
        if face_coords is None:
            face_coords = detect_face_opencv(image_bytes)
        
        if face_coords:
            x, y, w, h, img_width, img_height = face_coords
            
            # Calculate crop box with proper headroom and padding
            # Face should occupy 70-80% of frame height
            target_face_height = 600 * 0.75  # 450px
            scale_factor = target_face_height / h
            
            # Add 30% headroom above face
            headroom = int(h * 0.3)
            # Add 15% padding on sides
            side_padding = int(w * 0.15)
            
            # Calculate crop dimensions (square)
            crop_size = int(max(w + 2 * side_padding, h + headroom + h * 0.2))
            
            # Center the crop around the face
            center_x = x + w // 2
            center_y = y + h // 2 - headroom // 2  # Shift up for headroom
            
            left = max(0, center_x - crop_size // 2)
            top = max(0, center_y - crop_size // 2)
            right = min(img_width, left + crop_size)
            bottom = min(img_height, top + crop_size)
            
            # Adjust if crop goes out of bounds
            if right - left < crop_size:
                if left == 0:
                    right = min(img_width, left + crop_size)
                else:
                    left = max(0, right - crop_size)
            
            if bottom - top < crop_size:
                if top == 0:
                    bottom = min(img_height, top + crop_size)
                else:
                    top = max(0, bottom - crop_size)
            
            # Crop the image
            img = img.crop((left, top, right, bottom))
            logger.info(f"Cropped to: {img.size}")
        else:
            # No face detected, use center crop as fallback
            logger.warning("No face detected, using center crop")
            min_dim = min(original_width, original_height)
            left = (original_width - min_dim) // 2
            top = (original_height - min_dim) // 2
            right = left + min_dim
            bottom = top + min_dim
            img = img.crop((left, top, right, bottom))
        
        # Resize to exactly 600x600px with high quality
        img = img.resize((600, 600), Image.Resampling.LANCZOS)
        logger.info(f"Resized to: {img.size}")
        
        # Add name overlay
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            except:
                font = ImageFont.load_default()
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position: bottom center, 40px from bottom
        text_x = (600 - text_width) // 2
        text_y = 600 - 40 - text_height
        
        # Draw semi-transparent black rectangle background
        padding = 10
        rect_coords = [
            text_x - padding,
            text_y - padding,
            text_x + text_width + padding,
            text_y + text_height + padding
        ]
        
        # Create a new image for the overlay with alpha
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(rect_coords, fill=(0, 0, 0, 180))
        
        # Composite the overlay
        img_rgba = img.convert('RGBA')
        img_rgba = Image.alpha_composite(img_rgba, overlay)
        img = img_rgba.convert('RGB')
        
        # Draw text on the final image
        draw = ImageDraw.Draw(img)
        draw.text((text_x, text_y), name, fill=(255, 255, 255), font=font)
        
        # Save to bytes with high quality
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95, dpi=(300, 300))
        output_bytes = output.getvalue()
        file_size = len(output_bytes)
        
        logger.info(f"Final image size: {file_size} bytes")
        return output_bytes, file_size
        
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

def upload_to_google_drive(image_bytes: bytes, filename: str) -> tuple[str, str]:
    """Upload file to Google Drive using service account"""
    try:
        if not GOOGLE_DRIVE_SERVICE:
            raise Exception("Google Drive service not initialized")
        
        # File metadata
        file_metadata = {
            'name': filename,
            'mimeType': 'image/jpeg'
        }
        
        # Add to specific folder if configured
        if GOOGLE_FOLDER_ID:
            file_metadata['parents'] = [GOOGLE_FOLDER_ID]
        
        # Create media upload
        media = MediaIoBaseUpload(
            io.BytesIO(image_bytes),
            mimetype='image/jpeg',
            resumable=True
        )
        
        # Upload file
        file = GOOGLE_DRIVE_SERVICE.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        web_view_link = file.get('webViewLink', f"https://drive.google.com/file/d/{file_id}/view")
        
        logger.info(f"File uploaded to Google Drive: {file_id}")
        return file_id, web_view_link
        
    except Exception as e:
        logger.error(f"Google Drive upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload to Google Drive: {str(e)}")

# ============= API ENDPOINTS =============

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB connection
        await db.command('ping')
        mongo_status = "connected"
    except Exception as e:
        logger.error(f"MongoDB health check failed: {str(e)}")
        mongo_status = "disconnected"
    
    return {
        "status": "healthy",
        "mongodb": mongo_status,
        "google_drive": "enabled (service account)" if GOOGLE_DRIVE_SERVICE else "disabled"
    }

@api_router.post("/process-passport")
async def process_passport(
    file: UploadFile = File(...),
    name: str = Form(...)
):
    """Process uploaded image and upload to Google Drive"""
    try:
        # Check if Google Drive is configured
        if not GOOGLE_DRIVE_SERVICE:
            raise HTTPException(
                status_code=500, 
                detail="Google Drive service not configured. Please contact administrator."
            )
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only JPG and PNG formats are supported.")
        
        # Validate name
        if not name or len(name) > 50:
            raise HTTPException(status_code=400, detail="Name is required and must be less than 50 characters.")
        
        # Validate name characters
        if not re.match(r"^[a-zA-Z0-9\s\-\']+$", name):
            raise HTTPException(status_code=400, detail="Name contains invalid characters.")
        
        # Read file
        image_bytes = await file.read()
        file_size = len(image_bytes)
        
        # Check file size (10MB limit)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
        
        logger.info(f"Processing image: {file.filename}, size: {file_size} bytes")
        
        # Detect face
        face_coords = detect_face_opencv(image_bytes)
        if not face_coords:
            raise HTTPException(
                status_code=400,
                detail="No face detected in the photo. Please upload a clear, frontal face photo."
            )
        
        # Process image
        processed_bytes, processed_size = process_passport_photo(image_bytes, name, face_coords)
        
        # Generate filename
        sanitized_name = sanitize_filename(name)
        timestamp = int(time.time())
        filename = f"passport_photo_{sanitized_name}_{timestamp}.jpg"
        
        # Upload to Google Drive
        try:
            drive_file_id, drive_file_url = upload_to_google_drive(processed_bytes, filename)
            logger.info(f"File uploaded to Google Drive: {drive_file_id}")
        except Exception as e:
            logger.error(f"Google Drive upload failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload to Google Drive: {str(e)}"
            )
        
        # Save metadata to MongoDB
        metadata = PassportPhotoMetadata(
            filename=filename,
            storage_mode="google_drive",
            drive_file_id=drive_file_id,
            drive_file_url=drive_file_url,
            local_file_path=None,
            user_email=None,
            name_on_photo=name,
            original_filename=file.filename or "unknown",
            file_size_bytes=processed_size
        )
        
        metadata_dict = metadata.model_dump()
        metadata_dict['upload_timestamp'] = metadata_dict['upload_timestamp'].isoformat()
        
        result = await db.passport_photos.insert_one(metadata_dict)
        metadata_id = str(result.inserted_id)
        
        logger.info(f"Metadata saved with ID: {metadata_id}")
        
        # Return success response
        return ProcessResponse(
            success=True,
            mode="google_drive",
            drive_file_id=drive_file_id,
            drive_file_url=drive_file_url,
            filename=filename,
            metadata_id=metadata_id,
            message="✓ Photo saved successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_passport: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@api_router.get("/photos")
async def get_photos(email: Optional[str] = None):
    """Get list of processed photos"""
    try:
        query = {}
        if email:
            query['user_email'] = email
        
        photos = await db.passport_photos.find(query, {"_id": 0}).sort("upload_timestamp", -1).to_list(100)
        
        # Convert ISO string timestamps back to datetime objects
        for photo in photos:
            if isinstance(photo['upload_timestamp'], str):
                photo['upload_timestamp'] = datetime.fromisoformat(photo['upload_timestamp'])
        
        return {"success": True, "photos": photos, "count": len(photos)}
    except Exception as e:
        logger.error(f"Error fetching photos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch photos")

# Custom endpoint to serve uploaded files with correct MIME type
@api_router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve uploaded passport photos"""
    try:
        file_path = UPLOADS_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return the file with correct content type
        return FileResponse(
            path=str(file_path),
            media_type="image/jpeg",
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        raise HTTPException(status_code=404, detail="File not found")

# Include the router in the main app
app.include_router(api_router)

# Mount uploads directory AFTER API routes to avoid conflicts
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB client closed")
