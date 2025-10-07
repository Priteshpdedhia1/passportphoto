#!/usr/bin/env python3
"""
Generate OAuth 2.0 refresh token for Google Drive access.
This allows the backend to upload files to YOUR personal Google Drive.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import os

# Scopes required for Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Your OAuth Client ID from Google Cloud Console
CLIENT_ID = "491928435319-kb0980vrquedndl8bviph3hc4i5sd1ot.apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-YOUR_CLIENT_SECRET"  # You need to get this from Google Cloud Console

def generate_token():
    """Generate OAuth token and save to file"""
    
    print("=" * 60)
    print("Google Drive OAuth Token Generator")
    print("=" * 60)
    print()
    print("This will open your browser and ask you to:")
    print("1. Sign in with YOUR Google account")
    print("2. Grant access to Google Drive")
    print("3. Generate a refresh token for the backend")
    print()
    
    # Create OAuth client config
    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    
    try:
        # Create the flow
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='http://localhost:8080/'
        )
        
        # Run the OAuth flow
        print("Opening browser for authentication...")
        print("If browser doesn't open, copy this URL:")
        print()
        
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='Authentication successful! You can close this window.'
        )
        
        # Save credentials
        creds_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        output_file = '/app/backend/oauth-credentials.json'
        with open(output_file, 'w') as f:
            json.dump(creds_data, f, indent=2)
        
        print()
        print("=" * 60)
        print("✓ SUCCESS!")
        print("=" * 60)
        print(f"Credentials saved to: {output_file}")
        print()
        print("Next steps:")
        print("1. Restart the backend: sudo supervisorctl restart backend")
        print("2. Try uploading a photo - it will now save to YOUR Google Drive!")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ ERROR")
        print("=" * 60)
        print(f"Failed to generate token: {str(e)}")
        print()
        print("Common issues:")
        print("- Make sure CLIENT_SECRET is set correctly")
        print("- Check that redirect URI http://localhost:8080/ is authorized")
        print("- Ensure you're using the correct Google Cloud project")
        print()

if __name__ == '__main__':
    generate_token()
