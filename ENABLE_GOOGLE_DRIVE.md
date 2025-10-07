# Enable Google Drive Integration

## What You Need
- A Google Cloud Project with OAuth 2.0 Client ID
- 10 minutes to complete setup

## Quick Command to Enable

Once you have your Google Client ID, run this command in the Emergent terminal:

```bash
# Replace YOUR_CLIENT_ID with your actual Client ID from Google Cloud Console
echo 'REACT_APP_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com' >> /app/frontend/.env

# Restart the frontend to apply changes
sudo supervisorctl restart frontend
```

## Step-by-Step Setup

### 1. Get Your Google Client ID (First Time Only)

If you haven't created a Google Cloud Project yet:

1. **Create Project**: https://console.cloud.google.com/
   - Click "New Project"
   - Name: "Passport Photo Generator"
   - Click "Create"

2. **Enable Drive API**:
   - Go to "APIs & Services" → "Library"
   - Search "Google Drive API"
   - Click "Enable"

3. **Configure OAuth**:
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External"
   - Fill in app name and your email
   - Add scope: `https://www.googleapis.com/auth/drive.file`
   - Add your email as test user

4. **Create Client ID**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Type: "Web application"
   - Authorized JavaScript origins:
     ```
     https://snapid-generator-1.preview.emergentagent.com
     ```
   - Authorized redirect URIs:
     ```
     https://snapid-generator-1.preview.emergentagent.com
     ```
   - Click "Create"
   - **Copy the Client ID**

### 2. Add Client ID to Your App

**Option A: Using Terminal (Recommended)**

```bash
# In Emergent terminal, run:
echo 'REACT_APP_GOOGLE_CLIENT_ID=1234567890-abc123def.apps.googleusercontent.com' >> /app/frontend/.env

# Replace with your actual Client ID from step 1
```

**Option B: Edit File Directly**

1. Open `/app/frontend/.env`
2. Add this line at the end:
   ```
   REACT_APP_GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com
   ```
3. Save the file

### 3. Restart Frontend

```bash
sudo supervisorctl restart frontend
```

Wait 5-10 seconds for the app to restart.

### 4. Test It!

1. Open your app: https://snapid-generator-1.preview.emergentagent.com/
2. You should now see **"Sign in with Google"** button in the header
3. Click it to sign in
4. Upload a photo, enter name, and generate
5. Photo will be saved to your Google Drive!

## Verification

After enabling, you should see:

✅ "Sign in with Google" button in header  
✅ No "Local Mode" message (or it changes to "Google Drive available")  
✅ After signing in: User profile picture and name appear  
✅ After generating: "View in Google Drive" button  

## Troubleshooting

### "Sign in with Google" button doesn't appear

**Solution**:
```bash
# Check if Client ID is set
cat /app/frontend/.env | grep GOOGLE_CLIENT_ID

# If not showing, add it:
echo 'REACT_APP_GOOGLE_CLIENT_ID=YOUR_ID.apps.googleusercontent.com' >> /app/frontend/.env

# Restart
sudo supervisorctl restart frontend
```

### "redirect_uri_mismatch" error

**Solution**:
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth 2.0 Client
3. Make sure **Authorized JavaScript origins** includes:
   ```
   https://snapid-generator-1.preview.emergentagent.com
   ```
4. Make sure **Authorized redirect URIs** includes:
   ```
   https://snapid-generator-1.preview.emergentagent.com
   ```

### "Access blocked: This app's request is invalid"

**Solution**:
1. Go to Google Cloud Console → OAuth consent screen
2. Scroll to "Test users"
3. Click "Add Users"
4. Add your email address
5. Click "Save"

### Sign-in works but photos don't save to Drive

**Solution**:
- Check if you granted Drive access during sign-in
- Make sure Google Drive API is enabled in Cloud Console
- Try signing out and signing in again

## Optional: Use Specific Drive Folder

To save all photos to a specific folder:

1. Create a folder in Google Drive
2. Open the folder and copy its ID from URL:
   ```
   https://drive.google.com/drive/folders/1ABC123XYZ
                                          ^^^^^^^^^ This is the folder ID
   ```
3. Add to `/app/backend/.env`:
   ```bash
   echo 'GOOGLE_FOLDER_ID=1ABC123XYZ' >> /app/backend/.env
   sudo supervisorctl restart backend
   ```

## Switching Between Modes

### Use Local Download Mode (Current):
```bash
# Remove the Google Client ID line from /app/frontend/.env
sed -i '/REACT_APP_GOOGLE_CLIENT_ID/d' /app/frontend/.env
sudo supervisorctl restart frontend
```

### Use Google Drive Mode:
```bash
# Add the Client ID
echo 'REACT_APP_GOOGLE_CLIENT_ID=YOUR_ID.apps.googleusercontent.com' >> /app/frontend/.env
sudo supervisorctl restart frontend
```

### Use Both Modes (Dual Mode):
- Keep the Client ID configured
- Users can choose: sign in for Drive OR continue without sign-in for download
- This is the most flexible option

## Complete Documentation

For more details, see:
- `/app/GOOGLE_DRIVE_SETUP.md` - Detailed setup guide
- `/app/README.md` - Technical documentation
- `/app/USER_GUIDE.md` - User instructions

## Quick Reference

**Files to Edit**:
- Frontend config: `/app/frontend/.env`
- Backend config: `/app/backend/.env` (optional, for folder)

**Commands**:
```bash
# Add Google Client ID
echo 'REACT_APP_GOOGLE_CLIENT_ID=YOUR_ID' >> /app/frontend/.env

# Restart services
sudo supervisorctl restart frontend
sudo supervisorctl restart backend  # Only if you changed backend .env

# Check if it's running
curl -s https://snapid-generator-1.preview.emergentagent.com/ | grep -o "Sign in with Google"
```

## Need Help?

- Check `/app/GOOGLE_DRIVE_SETUP.md` for detailed troubleshooting
- Verify your Client ID at: https://console.cloud.google.com/apis/credentials
- Make sure authorized URIs match your exact domain
