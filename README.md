# Passport Photo Generator

A production-ready full-stack web application that automatically generates passport photos with face detection, proper cropping, and name overlay. Features optional Google Drive integration for cloud storage.

## ✨ Features

- **Automatic Face Detection**: Uses face-api.js for client-side face detection
- **Smart Cropping**: Crops images to passport specifications (600x600px, 2x2 inches, 300 DPI)
- **Name Overlay**: Adds name text with semi-transparent background
- **Dual Storage Mode**: 
  - Google Drive (with OAuth) for cloud storage
  - Local download (no authentication required)
- **Real-time Preview**: See face detection results instantly
- **Modern UI**: Responsive, accessible design with Tailwind CSS
- **MongoDB Storage**: Metadata tracking for all processed photos

## 🏗️ Tech Stack

### Frontend
- React 19
- Tailwind CSS
- face-api.js (face detection)
- Google Identity Services (OAuth)
- Axios
- Lucide React (icons)
- Sonner (toast notifications)

### Backend
- FastAPI (Python)
- MongoDB (via Motor)
- Pillow (image processing)
- OpenCV (face detection)
- Google Drive API

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and Yarn
- Python 3.8+
- MongoDB (local or Atlas)

### Option 1: Local Mode (No Google Drive)

**No configuration needed! Just run:**

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend (in another terminal)
cd frontend
yarn install
yarn start
```

Visit `http://localhost:3000` - photos will be downloaded to your device.

### Option 2: With Google Drive Integration

#### Step 1: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Passport Photo Generator"
3. Enable the **Google Drive API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Drive API" and enable it

4. Configure OAuth Consent Screen:
   - Go to "APIs & Services" → "OAuth consent screen"
   - Select "External" (unless you have Google Workspace)
   - Fill in:
     - **App name**: Passport Photo Generator
     - **User support email**: your@email.com
     - **Developer contact**: your@email.com
   - Add scope: `https://www.googleapis.com/auth/drive.file`
   - Add test users: your@email.com

5. Create OAuth 2.0 Client ID:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: **Web application**
   - Name: "Passport Photo Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:3000`
   - Authorized redirect URIs:
     - `http://localhost:3000`
   - Click "Create" and copy the **Client ID**

#### Step 2: Configure Environment

Create `/app/frontend/.env`:
```env
REACT_APP_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
REACT_APP_BACKEND_URL=http://localhost:8001
```

Create `/app/backend/.env`:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=passport_photos_db
GOOGLE_FOLDER_ID=  # Optional: specific Drive folder
CORS_ORIGINS=*
BACKEND_URL=http://localhost:8001
```

#### Step 3: Run the Application

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend
cd frontend
yarn install
yarn start
```

Visit `http://localhost:3000` and sign in with Google!

### How to Use:

#### Option 1: Download Mode (Default - No Configuration)
Works immediately without any setup:
```bash
# Just start the app and use it!
# Upload photo → Enter name → Generate → Download
```
- ✅ No sign-in required
- ✅ Photos downloaded directly to device
- ✅ Complete privacy - nothing stored in cloud
- ✅ Perfect for testing and quick use

#### Option 2: Google Drive Mode (Optional)
Requires Google OAuth setup (see GOOGLE_DRIVE_SETUP.md):
```bash
# 1. Configure Google Client ID
# 2. Users sign in with Google
# 3. Photos save automatically to their Google Drive
```
- ✅ Cloud storage in user's Google Drive
- ✅ Access from any device
- ✅ Automatic backup
- ✅ Shareable links

#### Dual Mode Support
The app intelligently supports BOTH modes:
- **With placeholder Client ID**: Shows Google sign-in button, but users can still use without signing in (download mode)
- **With valid Client ID**: Users can choose to sign in (Drive) or continue without sign-in (download)
- **Without Client ID**: Pure download mode only

### Current Configuration:
- ✅ **Download Mode**: Fully functional - photos can be downloaded
- ✅ **Google Drive Option**: Visible but requires real OAuth credentials to use
- 📝 To enable Google Drive: Follow setup instructions in GOOGLE_DRIVE_SETUP.md

## 📖 How It Works

### User Flow

1. **Upload Photo**: Drag-and-drop or browse for a JPG/PNG image (max 10MB)
2. **Face Detection**: Automatic face detection with confidence percentage
3. **Enter Name**: Input your name (max 50 characters, letters/spaces/hyphens only)
4. **Generate**: 
   - *Google Drive mode*: Sign in, then click "Generate Passport Photo"
   - *Local mode*: Click "Generate Passport Photo" (no sign-in)
5. **Download/Save**: Photo saved to Drive or downloaded locally

### Processing Pipeline

#### Frontend
1. Load face-api.js models from CDN
2. Detect face on uploaded image (client-side preview)
3. Show bounding box and confidence score
4. Send image + name to backend API

#### Backend
1. Validate file (type, size, name)
2. Detect face using OpenCV Haar Cascade
3. Calculate crop dimensions:
   - Face occupies 70-80% of frame height
   - 30% headroom above face
   - 15% padding on sides
   - Maintain 1:1 aspect ratio
4. Crop and resize to 600x600px (LANCZOS resampling)
5. Add name overlay:
   - Font: DejaVu Sans Bold, 24px
   - Semi-transparent black background (180 alpha)
   - Position: Bottom center, 40px from bottom
6. Save to Google Drive OR local uploads folder
7. Store metadata in MongoDB

## 🗄️ MongoDB Schema

```javascript
{
  _id: ObjectId,
  filename: "passport_photo_john_doe_1234567890.jpg",
  storage_mode: "google_drive" | "local",
  drive_file_id: "abc123...",  // if Google Drive
  drive_file_url: "https://drive.google.com/file/d/...",
  local_file_path: "/uploads/passport_photo_...",  // if local
  user_email: "user@example.com",  // if Google Drive
  name_on_photo: "John Doe",
  upload_timestamp: ISODate("2025-01-15T10:30:00Z"),
  image_dimensions: "600x600",
  original_filename: "IMG_1234.jpg",
  file_size_bytes: 245678,
  processing_status: "success"
}
```

## 🔌 API Endpoints

### `POST /api/process-passport`

**Request**:
- `file`: Image file (multipart/form-data)
- `name`: String (form field)
- `Authorization`: Bearer token (header, optional)

**Response (Google Drive)**:
```json
{
  "success": true,
  "mode": "google_drive",
  "drive_file_id": "abc123",
  "drive_file_url": "https://drive.google.com/file/d/abc123/view",
  "filename": "passport_photo_john_doe_1234567890.jpg",
  "metadata_id": "507f1f77bcf86cd799439011",
  "message": "Photo saved to Google Drive successfully!"
}
```

**Response (Local)**:
```json
{
  "success": true,
  "mode": "local",
  "file_path": "/uploads/passport_photo_john_doe_1234567890.jpg",
  "download_url": "http://localhost:8001/uploads/passport_photo_john_doe_1234567890.jpg",
  "filename": "passport_photo_john_doe_1234567890.jpg",
  "metadata_id": "507f1f77bcf86cd799439011",
  "message": "Photo processed successfully!"
}
```

### `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "google_drive": "optional (configured via user OAuth)"
}
```

### `GET /api/photos?email=user@example.com`

**Response**:
```json
{
  "success": true,
  "photos": [...],
  "count": 5
}
```

## 🎨 Design Specifications

### Output Image
- **Size**: 600x600 pixels
- **Physical size**: 2x2 inches
- **Resolution**: 300 DPI
- **Format**: JPEG (quality 95%)
- **Aspect ratio**: 1:1 (square)

### Face Positioning
- Face height: 70-80% of frame height
- Headroom: 30% above face
- Side padding: 15% on each side

### Name Overlay
- **Font**: DejaVu Sans Bold, 24px
- **Color**: White (255, 255, 255)
- **Background**: Black with 180 alpha (semi-transparent)
- **Position**: Bottom center, 40px from bottom edge
- **Padding**: 10px around text

## 🔒 Security

- **User OAuth**: Google Drive access uses user's own OAuth token (user consent)
- **No service accounts**: No backend credentials exposed
- **File validation**: Type, size, and content validation
- **Name sanitization**: Prevent directory traversal and injection
- **CORS**: Configured for specific origins
- **Rate limiting**: Recommended for production (10 req/min per user)

## 🧪 Testing

### Manual Test Cases

1. **Happy Path**:
   - Upload clear portrait photo
   - Verify face detection success
   - Enter name "John Doe"
   - Generate photo
   - Verify download/Drive link works

2. **No Face**:
   - Upload landscape photo
   - Verify error: "No face detected"
   - Verify submit button disabled

3. **Multiple Faces**:
   - Upload group photo
   - Verify warning: "Multiple faces detected"
   - Verify largest face used

4. **Large File**:
   - Upload 15MB image
   - Verify error: "File exceeds 10MB"

5. **Invalid Format**:
   - Upload .gif or .bmp file
   - Verify error: "Only JPG and PNG supported"

6. **Authentication** (Google Drive mode):
   - Try generating without sign-in
   - Verify sign-in prompt
   - Sign in and verify features enabled

## 🐛 Troubleshooting

### Frontend Issues

**"redirect_uri_mismatch" error**:
- Add `http://localhost:3000` to authorized JavaScript origins in Google Cloud Console

**"Access blocked: This app's request is invalid"**:
- Add your email to test users in OAuth consent screen
- Verify OAuth consent screen is properly configured

**Face detection not working**:
- Check browser console for model loading errors
- Ensure CDN is accessible: https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/

### Backend Issues

**"No face detected" for clear photos**:
- OpenCV Haar Cascade may need tuning
- Try adjusting `scaleFactor` and `minNeighbors` in `detect_face_opencv()`

**MongoDB connection failed**:
- Verify MongoDB is running: `sudo service mongodb status`
- Check connection string in `.env`

**Google Drive upload failed**:
- Verify user granted Drive access during OAuth
- Check access token validity
- Ensure Drive API is enabled in Google Cloud Console

## 📦 Deployment

### Frontend (Vercel/Netlify)

1. Build command: `yarn build`
2. Output directory: `build`
3. Environment variables:
   - `REACT_APP_GOOGLE_CLIENT_ID`: Your Google Client ID
   - `REACT_APP_BACKEND_URL`: Your backend URL
4. Update authorized origins in Google Cloud Console with your domain

### Backend (Railway/Render/AWS)

1. Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
2. Environment variables:
   - `MONGO_URL`: MongoDB Atlas connection string
   - `DB_NAME`: passport_photos_db
   - `GOOGLE_FOLDER_ID`: (optional)
   - `CORS_ORIGINS`: Your frontend domain
   - `BACKEND_URL`: Your backend URL
3. Ensure `/uploads` directory is writable (or use cloud storage)

### MongoDB (Atlas)

1. Create cluster at https://www.mongodb.com/cloud/atlas
2. Whitelist application server IP (or 0.0.0.0/0 for development)
3. Create database user with read/write permissions
4. Copy connection string to backend `.env`

## 📝 License

MIT License - feel free to use for personal or commercial projects!

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 🙏 Acknowledgments

- [face-api.js](https://github.com/vladmandic/face-api) by Vladimir Mandic
- [FastAPI](https://fastapi.tiangolo.com/) by Sebastián Ramírez
- [OpenCV](https://opencv.org/) for computer vision
- [Google Drive API](https://developers.google.com/drive)

---

**Made with ❤️ for automatic passport photo generation**
