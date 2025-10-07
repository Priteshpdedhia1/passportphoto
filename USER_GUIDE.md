# Passport Photo Generator - User Guide

Welcome to the Passport Photo Generator! This application automatically creates passport-sized photos (600x600px, 2x2 inches) with face detection, smart cropping, and name overlay.

## 🎯 Quick Start

The app works in **two modes**:

### Mode 1: Download Mode (No Sign-In Required)
✅ **Use immediately** - no configuration needed  
✅ Upload photo → Enter name → Generate → Download  
✅ Complete privacy - nothing uploaded to cloud  
✅ Photos saved directly to your device  

### Mode 2: Google Drive Mode (Optional)
✅ Sign in with Google account  
✅ Photos automatically saved to your Google Drive  
✅ Access from any device  
✅ Automatic cloud backup  

## 📋 How to Use

### Step 1: Upload Your Photo

1. **Drag and drop** your photo onto the upload zone, or **click to browse**
2. **Supported formats**: JPG, PNG
3. **File size limit**: Maximum 10MB
4. **Photo requirements**:
   - Clear, frontal face photo
   - Good lighting
   - Face clearly visible
   - No sunglasses or hats covering face

### Step 2: Face Detection

- The app will **automatically detect** your face
- You'll see a **confidence percentage** (higher is better)
- **Green status** = face detected successfully
- **Red status** = no face detected, try another photo

**Tips for better detection**:
- Use a well-lit photo
- Face should be centered
- Look directly at camera
- Remove obstructions (sunglasses, hands, etc.)

### Step 3: Enter Your Name

- Type your full name in the input field
- **Character limit**: 50 characters
- **Allowed characters**: Letters, spaces, hyphens, apostrophes
- Your name will appear at the bottom of the passport photo

### Step 4: Generate & Save

**Without Google Sign-In (Download Mode)**:
1. Click "**Generate Passport Photo**"
2. Wait for processing (usually 2-5 seconds)
3. Click "**Download Photo**" button
4. Photo will be saved to your device's Downloads folder

**With Google Sign-In (Drive Mode)**:
1. Click "**Sign in with Google**" in the header
2. Authorize Drive access
3. Click "**Generate Passport Photo**"
4. Photo automatically saved to your Google Drive
5. Click "**View in Google Drive**" to open

## ✨ Features

### Automatic Processing
- **Face Detection**: AI-powered face detection
- **Smart Cropping**: Face positioned with proper headroom (70-80% of frame)
- **Precise Sizing**: Exactly 600x600px at 300 DPI (2x2 inches)
- **Name Overlay**: Professional text with semi-transparent background
- **High Quality**: JPEG format at 95% quality

### Validation & Safety
- ✅ File type validation (JPG/PNG only)
- ✅ File size check (max 10MB)
- ✅ Name format validation
- ✅ Face detection verification
- ✅ Clear error messages

### Metadata Tracking
All processed photos are logged in the database with:
- Filename and timestamp
- Original filename
- User email (if signed in)
- Storage location (Drive or local)
- Processing status

## 🔒 Privacy & Security

### Download Mode (Without Sign-In)
- ✅ **Complete privacy** - no account required
- ✅ **No data collection** - nothing stored on server
- ✅ **Local processing** - photo processed and returned
- ✅ **Immediate deletion** - server copy deleted after download

### Google Drive Mode (With Sign-In)
- ✅ **Your OAuth token** - uses your Google account
- ✅ **Your Drive** - photos saved to YOUR Google Drive
- ✅ **Limited scope** - only access files the app creates
- ✅ **Private files** - only you can access them
- ✅ **No backend storage** - photos go directly to your Drive

## 📊 Output Specifications

Your processed passport photo will have:

| Specification | Value |
|--------------|--------|
| **Dimensions** | 600 x 600 pixels |
| **Physical Size** | 2 x 2 inches |
| **Resolution** | 300 DPI |
| **Format** | JPEG |
| **Aspect Ratio** | 1:1 (square) |
| **Quality** | 95% (high quality) |
| **Face Height** | 70-80% of frame |
| **Headroom** | 30% above face |
| **Side Padding** | 15% on each side |

## ❓ Common Issues & Solutions

### "No face detected"
**Problem**: The app can't find a face in your photo  
**Solutions**:
- ✅ Use a clearer photo with better lighting
- ✅ Make sure face is centered and not tilted
- ✅ Remove sunglasses, hats, or obstructions
- ✅ Try a different photo with frontal face view

### "Multiple faces detected"
**Problem**: More than one face in the photo  
**Solution**: 
- ⚠️ The app will use the largest/most prominent face
- ✅ For best results, upload a photo with only your face

### "File too large"
**Problem**: Image exceeds 10MB limit  
**Solutions**:
- ✅ Compress the image using online tools
- ✅ Reduce resolution before uploading
- ✅ Convert to JPG (usually smaller than PNG)

### "Invalid file type"
**Problem**: File format not supported  
**Solutions**:
- ✅ Convert to JPG or PNG
- ✅ Only JPG and PNG are supported
- ❌ GIF, BMP, TIFF not supported

### Google sign-in not working
**Problem**: Can't sign in with Google  
**Solutions**:
- ✅ Check if cookies are enabled
- ✅ Disable ad blockers temporarily
- ✅ Try incognito/private browsing mode
- ✅ Contact administrator to configure OAuth (see GOOGLE_DRIVE_SETUP.md)

### Download not starting
**Problem**: Download button doesn't work  
**Solutions**:
- ✅ Check if browser allows downloads
- ✅ Disable popup blockers
- ✅ Try right-click → "Save link as"
- ✅ Copy download URL and paste in new tab

## 🎨 UI Guide

### Header
- **Left**: App logo and title
- **Right**: "Sign in with Google" button (or user profile if signed in)

### Main Area
- **Left Column**: Upload and input section
  - Upload zone
  - Face detection status
  - Name input field
  - Generate button

- **Right Column**: Instructions and results
  - How it works guide
  - Specifications
  - Success message with download/Drive link

### Footer
- App description
- Mode information
- Made with Emergent badge

## 💡 Tips for Best Results

1. **Photo Quality**: Use high-resolution photos (at least 800x800px)
2. **Lighting**: Natural daylight or well-lit indoor lighting
3. **Background**: Plain, uncluttered background works best
4. **Expression**: Neutral expression, eyes open
5. **Distance**: Face should fill frame but not be too close
6. **Angle**: Look straight at camera, no tilt

## 🚀 Advanced Usage

### For Developers
- See **README.md** for technical documentation
- See **GOOGLE_DRIVE_SETUP.md** for OAuth configuration
- API endpoint: `POST /api/process-passport`
- MongoDB metadata collection: `passport_photos`

### Batch Processing
- Upload one photo at a time
- Click "Upload Another Photo" after each generation
- All photos saved to same Drive folder (if signed in)

### Custom Folder (Google Drive)
- Administrator can configure specific Drive folder
- Set `GOOGLE_FOLDER_ID` in backend `.env`
- All users' photos saved to that folder

## 📞 Support

### Issues & Bugs
- Check this user guide first
- Review **README.md** for technical details
- Check browser console for errors (F12)

### Feature Requests
- Open an issue on the project repository
- Contact the development team

### Google Drive Setup
- See **GOOGLE_DRIVE_SETUP.md** for detailed OAuth setup
- Administrator access to Google Cloud Console required

## 🔄 Updates

### Current Version: 1.0.0

**Features**:
- ✅ Face detection with face-api.js
- ✅ Server-side face validation with OpenCV
- ✅ Smart cropping and resizing
- ✅ Name overlay with custom styling
- ✅ Google Drive integration (optional)
- ✅ Local download mode
- ✅ MongoDB metadata storage
- ✅ Comprehensive validation
- ✅ Mobile-responsive design

---

**Made with ❤️ for automatic passport photo generation**  
**Powered by Emergent**
