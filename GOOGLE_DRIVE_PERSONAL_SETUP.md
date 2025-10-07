# Google Drive Setup for Personal Accounts

## The Problem

Service accounts cannot upload to personal Google Drive folders. They only work with:
- Google Workspace Shared Drives (requires paid Workspace subscription)
- Domain-wide delegation (Workspace only)

## Solution: Use Your Personal OAuth Token

Instead of a service account, we'll use YOUR Google account credentials to upload files. Users won't need to sign in - the backend will use your stored credentials.

## Step-by-Step Setup

### Step 1: Generate OAuth Token (One-Time)

I'll create a script that helps you generate a refresh token.

Run this command in the Emergent terminal:

```bash
python3 /app/backend/generate_oauth_token.py
```

This will:
1. Open a URL in your browser
2. Ask you to sign in with YOUR Google account
3. Generate a refresh token
4. Save it to `/app/backend/oauth-credentials.json`

### Step 2: Update Backend Configuration

The backend will automatically use the refresh token to upload files to your Drive folder.

### Step 3: Test

Upload a photo through the app - it will be saved to your Drive folder using your credentials.

## How It Works

1. **User uploads photo** → Frontend sends to backend
2. **Backend processes** → Face detection, cropping, name overlay
3. **Backend uploads** → Uses YOUR OAuth token to upload to YOUR Drive folder
4. **User sees success** → Simple "Photo saved!" message

## Security

- ✅ Your OAuth token is stored securely on the backend only
- ✅ Users never see or access your credentials
- ✅ Token has limited scope (only Google Drive access)
- ✅ You can revoke access anytime from Google Account settings

## Benefits

- ✅ Works with personal Google accounts
- ✅ No monthly Workspace fees
- ✅ Users don't need Google accounts
- ✅ All files go to YOUR Drive folder
- ✅ You control everything

## Alternative: Local Storage + Manual Sync

If you prefer not to use your personal OAuth:

1. Backend saves files to `/app/backend/uploads/`
2. You manually upload to Drive when needed
3. Or use a sync script (rclone, etc.)

---

**Ready to proceed with OAuth setup? Let me know and I'll create the token generation script for you.**
