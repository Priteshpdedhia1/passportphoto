#!/usr/bin/env python3
"""
Web-based OAuth setup for Google Drive
"""
import json
from urllib.parse import urlencode

CLIENT_ID = "491928435319-kb0980vrquedndl8bviph3hc4i5sd1ot.apps.googleusercontent.com"
CLIENT_SECRET = "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"

# Step 1: Generate authorization URL
print()
print("=" * 80)
print("GOOGLE DRIVE OAUTH SETUP")
print("=" * 80)
print()
print("STEP 1: Click this URL and authorize with YOUR Google account:")
print()

params = {
    'client_id': CLIENT_ID,
    'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
    'response_type': 'code',
    'scope': 'https://www.googleapis.com/auth/drive.file',
    'access_type': 'offline',
    'prompt': 'consent'
}

auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
print(auth_url)
print()
print("-" * 80)
print("STEP 2: After authorization, you'll see an authorization code.")
print("Copy that code and paste it below:")
print("-" * 80)
print()

try:
    auth_code = input("Enter authorization code: ").strip()
    
    if not auth_code:
        print("Error: No code entered")
        exit(1)
    
    # Exchange code for tokens
    import requests
    
    print()
    print("Exchanging code for tokens...")
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        tokens = response.json()
        
        # Save credentials
        creds_data = {
            'token': tokens.get('access_token'),
            'refresh_token': tokens.get('refresh_token'),
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scopes': ['https://www.googleapis.com/auth/drive.file']
        }
        
        output_file = '/app/backend/oauth-credentials.json'
        with open(output_file, 'w') as f:
            json.dump(creds_data, f, indent=2)
        
        print()
        print("=" * 80)
        print("✓ SUCCESS!")
        print("=" * 80)
        print(f"OAuth credentials saved to: {output_file}")
        print()
        print("Next steps:")
        print("1. Run: sudo supervisorctl restart backend")
        print("2. Try uploading a photo - it will now save to YOUR Google Drive!")
        print()
        
    else:
        print()
        print("✗ Error exchanging code:")
        print(response.text)
        
except KeyboardInterrupt:
    print("\n\nCancelled by user")
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
