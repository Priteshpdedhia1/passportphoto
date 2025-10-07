#!/usr/bin/env python3
"""
Simple OAuth setup for Google Drive - generates authorization URL
"""

CLIENT_ID = "491928435319-kb0980vrquedndl8bviph3hc4i5sd1ot.apps.googleusercontent.com"
REDIRECT_URI = "https://snapid-generator-1.preview.emergentagent.com/oauth/callback"
SCOPES = "https://www.googleapis.com/auth/drive.file"

print("=" * 70)
print("Google Drive OAuth Setup - Manual Method")
print("=" * 70)
print()
print("STEP 1: Authorize Access")
print("-" * 70)
print()
print("Click this URL to authorize (sign in with YOUR Google account):")
print()

auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri={REDIRECT_URI}&"
    f"response_type=code&"
    f"scope={SCOPES}&"
    f"access_type=offline&"
    f"prompt=consent"
)

print(auth_url)
print()
print("-" * 70)
print("STEP 2: After Authorization")
print("-" * 70)
print()
print("After you authorize, you'll be redirected to a URL like:")
print(f"{REDIRECT_URI}?code=AUTHORIZATION_CODE")
print()
print("Copy the ENTIRE URL and send it to me.")
print()
print("=" * 70)
