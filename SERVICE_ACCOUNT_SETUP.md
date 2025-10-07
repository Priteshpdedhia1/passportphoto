# Google Service Account Setup Guide

## Complete Step-by-Step Instructions

### Step 1: Go to Google Cloud Console

1. Open: https://console.cloud.google.com/
2. Make sure you're in the **Passport Photo Generator** project (top left)

### Step 2: Create Service Account

1. In the left sidebar, click on **"IAM & Admin"**
2. Click **"Service Accounts"**
3. Click **"+ CREATE SERVICE ACCOUNT"** (blue button at top)

### Step 3: Configure Service Account Details

**Page 1 - Service account details:**
- **Service account name**: `passport-photo-uploader`
- **Service account ID**: (auto-generated, like `passport-photo-uploader@...`)
- **Service account description**: `Service account for uploading passport photos to Google Drive`
- Click **"CREATE AND CONTINUE"**

**Page 2 - Grant access (Optional):**
- Skip this page - just click **"CONTINUE"**

**Page 3 - Grant users access (Optional):**
- Skip this page - just click **"DONE"**

### Step 4: Create and Download JSON Key

1. You'll see your new service account in the list
2. Click on the **service account email** (something like `passport-photo-uploader@passport-photo-generator-xxxxx.iam.gserviceaccount.com`)
3. Go to the **"KEYS"** tab at the top
4. Click **"ADD KEY"** → **"Create new key"**
5. Select **"JSON"** as the key type
6. Click **"CREATE"**
7. A JSON file will automatically download to your computer
   - Filename will be like: `passport-photo-generator-xxxxx-xxxxxxxxxx.json`

### Step 5: Copy the Service Account Email

From the JSON file you just downloaded, find and copy the **"client_email"** value.

It will look like:
```
passport-photo-uploader@passport-photo-generator-xxxxx.iam.gserviceaccount.com
```

### Step 6: Share Your Drive Folder with Service Account

1. Open your Google Drive folder:
   https://drive.google.com/drive/folders/1RvRRAMG1mXtsn-7wO4cRgzAF3sKqf5YW

2. Click the **"Share"** button (top right)

3. In the "Add people and groups" field, paste the service account email:
   ```
   passport-photo-uploader@passport-photo-generator-xxxxx.iam.gserviceaccount.com
   ```

4. Set permission to **"Editor"** (so it can create files)

5. **IMPORTANT**: Uncheck "Notify people" (service accounts don't receive emails)

6. Click **"Share"**

### Step 7: Share the JSON Key File with Me

**Option A: Copy-Paste (Recommended)**

1. Open the downloaded JSON file in a text editor (Notepad, TextEdit, etc.)
2. Copy the ENTIRE content (should start with `{` and end with `}`)
3. Paste it in your next message to me

Example format (your actual file will have real values):
```json
{
  "type": "service_account",
  "project_id": "passport-photo-generator-xxxxx",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "passport-photo-uploader@...",
  "client_id": "123456789",
  ...
}
```

**Option B: If Copy-Paste Doesn't Work**

Create a paste on pastebin.com (private) and share the link.

## What I'll Do Next

Once you share the JSON key:

1. I'll securely store it in `/app/backend/service-account-key.json`
2. Update the backend code to use service account authentication
3. Remove all Google OAuth sign-in UI
4. Remove download buttons
5. Configure auto-upload to your specific Drive folder
6. Test the complete flow

## Security Notes

✅ **Service account keys are sensitive** - treat them like passwords
✅ The key will be stored securely in your backend environment
✅ Only the backend will have access to it
✅ Users won't see or interact with it
✅ The key only has access to Google Drive (not your entire Google account)
✅ You can revoke the key anytime from Google Cloud Console

## After Setup

Users will experience:
1. Upload photo
2. Enter name
3. Click "Generate"
4. See "Success! Photo saved" message
5. No download option
6. All files automatically saved to your Drive folder

## Troubleshooting

### Can't find IAM & Admin
- Look in the hamburger menu (☰) on the left
- Or search for "Service Accounts" in the search bar at top

### Don't see "+ CREATE SERVICE ACCOUNT" button
- Make sure you're the project owner
- Check if you're in the right project (top left dropdown)

### Service account email not working in Drive sharing
- Make sure you copied the entire email
- Make sure you selected "Editor" permission
- Make sure you unchecked "Notify people"

### JSON file has very long private_key
- That's normal! Private keys are long
- Make sure to copy the entire file including the newlines (\n)

## Ready?

Once you have:
1. ✅ Created the service account
2. ✅ Downloaded the JSON key file
3. ✅ Shared your Drive folder with the service account email

**Send me the JSON key content**, and I'll configure everything!
