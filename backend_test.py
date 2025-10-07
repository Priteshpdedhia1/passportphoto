#!/usr/bin/env python3
"""
Backend API Testing for Passport Photo Generator
Tests all backend endpoints and functionality
"""

import requests
import sys
import os
import json
from datetime import datetime
from pathlib import Path
import time

# Get backend URL from frontend env
BACKEND_URL = "https://snapid-generator-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class PassportPhotoAPITester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED - {message}")
        else:
            print(f"❌ {test_name}: FAILED - {message}")
            
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        })
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                mongodb_status = data.get('mongodb', 'unknown')
                
                if mongodb_status == 'connected':
                    self.log_result(
                        "Health Check", 
                        True, 
                        f"Backend healthy, MongoDB connected",
                        {"status_code": response.status_code, "data": data}
                    )
                else:
                    self.log_result(
                        "Health Check", 
                        False, 
                        f"Backend healthy but MongoDB not connected: {mongodb_status}",
                        {"status_code": response.status_code, "data": data}
                    )
            else:
                self.log_result(
                    "Health Check", 
                    False, 
                    f"Health endpoint returned {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Health Check", 
                False, 
                f"Failed to connect to backend: {str(e)}",
                {"error": str(e)}
            )
    
    def test_process_passport_no_file(self):
        """Test /api/process-passport without file (should fail)"""
        try:
            response = requests.post(f"{API_BASE}/process-passport", timeout=10)
            
            if response.status_code == 422:  # FastAPI validation error
                self.log_result(
                    "Process Passport - No File", 
                    True, 
                    "Correctly rejected request without file",
                    {"status_code": response.status_code}
                )
            else:
                self.log_result(
                    "Process Passport - No File", 
                    False, 
                    f"Expected 422, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Process Passport - No File", 
                False, 
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_process_passport_invalid_file(self):
        """Test /api/process-passport with invalid file type"""
        try:
            # Create a fake text file
            files = {'file': ('test.txt', 'This is not an image', 'text/plain')}
            data = {'name': 'Test User'}
            
            response = requests.post(f"{API_BASE}/process-passport", files=files, data=data, timeout=10)
            
            if response.status_code == 400:
                self.log_result(
                    "Process Passport - Invalid File", 
                    True, 
                    "Correctly rejected non-image file",
                    {"status_code": response.status_code}
                )
            else:
                self.log_result(
                    "Process Passport - Invalid File", 
                    False, 
                    f"Expected 400, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Process Passport - Invalid File", 
                False, 
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_process_passport_no_name(self):
        """Test /api/process-passport without name (should fail)"""
        try:
            # Create a minimal valid image (1x1 pixel PNG)
            import io
            from PIL import Image
            
            img = Image.new('RGB', (1, 1), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            files = {'file': ('test.png', img_bytes.getvalue(), 'image/png')}
            # No name provided
            
            response = requests.post(f"{API_BASE}/process-passport", files=files, timeout=10)
            
            if response.status_code == 422:  # FastAPI validation error
                self.log_result(
                    "Process Passport - No Name", 
                    True, 
                    "Correctly rejected request without name",
                    {"status_code": response.status_code}
                )
            else:
                self.log_result(
                    "Process Passport - No Name", 
                    False, 
                    f"Expected 422, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Process Passport - No Name", 
                False, 
                f"Test failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_process_passport_invalid_name(self):
        """Test /api/process-passport with invalid name characters"""
        try:
            # Create a minimal valid image
            import io
            from PIL import Image
            
            img = Image.new('RGB', (100, 100), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            files = {'file': ('test.png', img_bytes.getvalue(), 'image/png')}
            data = {'name': 'Test@User#123!'}  # Invalid characters
            
            response = requests.post(f"{API_BASE}/process-passport", files=files, data=data, timeout=10)
            
            if response.status_code == 400:
                self.log_result(
                    "Process Passport - Invalid Name", 
                    True, 
                    "Correctly rejected name with invalid characters",
                    {"status_code": response.status_code}
                )
            else:
                self.log_result(
                    "Process Passport - Invalid Name", 
                    False, 
                    f"Expected 400, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Process Passport - Invalid Name", 
                False, 
                f"Test failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_process_passport_no_face(self):
        """Test /api/process-passport with image containing no face"""
        try:
            # Create a simple geometric image with no face
            import io
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (300, 300), color='blue')
            draw = ImageDraw.Draw(img)
            draw.rectangle([50, 50, 250, 250], fill='red')
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            files = {'file': ('no_face.jpg', img_bytes.getvalue(), 'image/jpeg')}
            data = {'name': 'Test User'}
            
            response = requests.post(f"{API_BASE}/process-passport", files=files, data=data, timeout=15)
            
            if response.status_code == 400:
                response_data = response.json()
                if "No face detected" in response_data.get('detail', ''):
                    self.log_result(
                        "Process Passport - No Face", 
                        True, 
                        "Correctly detected no face in image",
                        {"status_code": response.status_code, "detail": response_data.get('detail')}
                    )
                else:
                    self.log_result(
                        "Process Passport - No Face", 
                        False, 
                        f"Got 400 but wrong error message: {response_data.get('detail')}",
                        {"status_code": response.status_code, "response": response_data}
                    )
            else:
                self.log_result(
                    "Process Passport - No Face", 
                    False, 
                    f"Expected 400, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Process Passport - No Face", 
                False, 
                f"Test failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_get_photos_endpoint(self):
        """Test /api/photos endpoint"""
        try:
            response = requests.get(f"{API_BASE}/photos", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'success' in data and 'photos' in data and 'count' in data:
                    self.log_result(
                        "Get Photos", 
                        True, 
                        f"Successfully retrieved photos list (count: {data['count']})",
                        {"status_code": response.status_code, "count": data['count']}
                    )
                else:
                    self.log_result(
                        "Get Photos", 
                        False, 
                        "Response missing required fields",
                        {"status_code": response.status_code, "data": data}
                    )
            else:
                self.log_result(
                    "Get Photos", 
                    False, 
                    f"Expected 200, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Get Photos", 
                False, 
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests for Passport Photo Generator")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Run tests in order
        self.test_health_endpoint()
        self.test_process_passport_no_file()
        self.test_process_passport_invalid_file()
        self.test_process_passport_no_name()
        self.test_process_passport_invalid_name()
        self.test_process_passport_no_face()
        self.test_get_photos_endpoint()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test runner"""
    tester = PassportPhotoAPITester()
    success = tester.run_all_tests()
    
    # Save results to file
    results_file = "/app/test_reports/backend_test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "backend_url": BACKEND_URL,
            "total_tests": tester.tests_run,
            "passed_tests": tester.tests_passed,
            "success_rate": f"{(tester.tests_passed/tester.tests_run)*100:.1f}%",
            "results": tester.results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())