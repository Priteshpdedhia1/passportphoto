# Google Drive Integration Setup Guide

This guide will help you configure Google Drive integration for the Passport Photo Generator. **Note: This is completely optional** - the app works perfectly in local mode without Google Drive!

## Quick Start (No Google Drive)

The app works immediately without any configuration:
- Photos are downloaded to your device
- No sign-in required
- All features work except cloud storage

## Enable Google Drive (Optional)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "**Select a project**" → "**New Project**"
3. Enter project name: "**Passport Photo Generator**"
4. Click "**Create**"

### Step 2: Enable Google Drive API

1. In the left sidebar, navigate to "**APIs & Services**" → "**Library**"
2. Search for "**Google Drive API**"
3. Click on it and press "**Enable**"

### Step 3: Configure OAuth Consent Screen

1. Go to "**APIs & Services**" → "**OAuth consent screen**"
2. Select "**External**" (unless you have Google Workspace)
3. Click "**Create**"

4. Fill in required fields:
   - **App name**: Passport Photo Generator
   - **User support email**: your@email.com
   - **Developer contact email**: your@email.com
   
5. Click "**Save and Continue**"

6. On **Scopes** page:
   - Click "**Add or Remove Scopes**"
   - Search and select: `https://www.googleapis.com/auth/drive.file`
   - This scope allows the app to create and access only files it creates
   - Click "**Update**" and "**Save and Continue**"

7. On **Test users** page:
   - Click "**Add Users**"
   - Add your email address for testing
   - Click "**Save and Continue**"

8. Review and click "**Back to Dashboard**"

### Step 4: Create OAuth 2.0 Client ID

1. Go to "**APIs & Services**" → "**Credentials**"
2. Click "**Create Credentials**" → "**OAuth 2.0 Client ID**"

3. Configure:
   - **Application type**: Web application
   - **Name**: Passport Photo Web Client
   
4. Add **Authorized JavaScript origins**:
   ```
   http://localhost:3000
   http://localhost:5173
   ```
   (Add your production domain when deploying)

5. Add **Authorized redirect URIs**:
   ```
   http://localhost:3000
   ```
   (Add your production domain when deploying)

6. Click "**Create**"

7. **Copy the Client ID** - you'll need this!

### Step 5: Configure the Application

#### Frontend Configuration

Edit `/app/frontend/.env`:

```env
REACT_APP_GOOGLE_CLIENT_ID=1234567890-abc123def456.apps.googleusercontent.com
REACT_APP_BACKEND_URL=http://localhost:8001
```

Replace the placeholder with your actual Client ID from Step 4.

#### Backend Configuration (Optional)

Edit `/app/backend/.env`:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=passport_photos_db
GOOGLE_FOLDER_ID=  # Optional: see below
CORS_ORIGINS=*
BACKEND_URL=http://localhost:8001
```

**Optional: Use a Specific Drive Folder**

1. Go to [Google Drive](https://drive.google.com/)
2. Create a new folder called "Passport Photos"
3. Open the folder
4. Copy the folder ID from the URL:
   - URL format: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - Example: `https://drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
   - Folder ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
5. Add to backend `.env`: `GOOGLE_FOLDER_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

If left empty, photos will be saved to the root of the user's Drive.

### Step 6: Restart Services

```bash
# Restart backend
sudo supervisorctl restart backend

# Restart frontend
sudo supervisorctl restart frontend
```

### Step 7: Test the Integration

1. Open the app in your browser
2. You should now see a "**Sign in with Google**" button in the header
3. Click it and sign in with the email you added as a test user
4. Upload a photo, enter a name, and generate
5. Photo will be saved to your Google Drive!
6. Check Drive to verify the file was created

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Solution**: 
- Go to Google Cloud Console → Credentials
- Edit your OAuth 2.0 Client ID
- Add the exact URL you're using to "Authorized JavaScript origins"
- Example: If you're on `http://localhost:3000`, add that exact URL

### Error: "Access blocked: This app's request is invalid"

**Solution**:
- Go to OAuth consent screen
- Click "**Add Users**" under Test users
- Add your email address
- Save and try again

### Error: "idpiframe_initialization_failed"

**Solution**:
- Check if cookies are enabled in your browser
- Disable any browser extensions that block third-party cookies
- Try in an incognito/private window

### Sign-in button doesn't appear

**Solution**:
- Check if `REACT_APP_GOOGLE_CLIENT_ID` is set in frontend `.env`
- Verify the client ID doesn't have extra spaces or quotes
- Restart the frontend service
- Check browser console for errors

### Photos not saving to Drive

**Solution**:
- Check browser console for errors
- Verify you granted Drive access during OAuth
- Ensure Google Drive API is enabled in Cloud Console
- Try signing out and signing in again

### "Invalid token" error

**Solution**:
- The OAuth token may have expired
- Click the sign-out button and sign in again
- Tokens are valid for 1 hour by default

## Production Deployment

When deploying to production:

1. **Update OAuth origins**:
   - Add your production domain to authorized JavaScript origins
   - Example: `https://yourdomain.com`

2. **Update environment variables**:
   - Set production URLs in `.env` files
   - Use HTTPS for all production URLs

3. **Publish OAuth App**:
   - Go to OAuth consent screen
   - Click "**Publish App**"
   - This removes the "testing" limitation

4. **Consider verification**:
   - For public apps with many users, consider Google verification
   - This removes the "unverified app" warning

## Security Notes

- **User OAuth**: The app uses the user's own OAuth token (not a service account)
- **User consent**: Users explicitly grant permission to access their Drive
- **Limited scope**: Only `drive.file` scope - app can only access files it creates
- **No backend secrets**: Client ID is public, no secrets exposed in frontend
- **Private files**: All created files are private to the user by default

## Features with Google Drive

- ✅ Photos saved to your Google Drive
- ✅ Access from any device
- ✅ Automatic backup
- ✅ Shareable links
- ✅ Integration with Google ecosystem
- ✅ User profile displayed in header
- ✅ One-click access to Drive after upload

## Local Mode (No Google Drive)

- ✅ Works immediately, no setup
- ✅ Photos downloaded to device
- ✅ No sign-in required
- ✅ Complete privacy (nothing uploaded)
- ✅ Faster processing (no network calls)

## Need Help?

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Drive API Reference](https://developers.google.com/drive/api/v3/reference)
- Check the main [README.md](README.md) for general app documentation
