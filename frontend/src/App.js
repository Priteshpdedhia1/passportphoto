import { useState, useEffect } from 'react';
import '@/App.css';
import * as faceapi from 'face-api.js';
import axios from 'axios';
import { Upload, Loader2, CheckCircle2, AlertCircle, User, Camera, Download, LogOut } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

// Check if Google Drive mode is enabled
const GOOGLE_DRIVE_ENABLED = GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== '';

function App() {
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [faceDetected, setFaceDetected] = useState(null);
  const [faceConfidence, setFaceConfidence] = useState(0);
  const [detecting, setDetecting] = useState(false);
  const [name, setName] = useState('');
  const [processing, setProcessing] = useState(false);
  const [processedImage, setProcessedImage] = useState(null);
  const [driveLink, setDriveLink] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [googleUser, setGoogleUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);

  // Google OAuth initialization
  useEffect(() => {
    if (!GOOGLE_DRIVE_ENABLED) return;

    const initializeGoogleAuth = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleCallback
        });
        
        window.google.accounts.id.renderButton(
          document.getElementById('googleSignInButton'),
          { 
            theme: 'outline', 
            size: 'large',
            text: 'signin_with',
            shape: 'pill'
          }
        );
      }
    };

    // Load Google Identity Services
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = initializeGoogleAuth;
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  const handleGoogleCallback = (response) => {
    // Decode JWT to get user info
    const payload = JSON.parse(atob(response.credential.split('.')[1]));
    setGoogleUser({
      name: payload.name,
      email: payload.email,
      picture: payload.picture
    });

    // Get access token using Google Identity Services
    const client = window.google.accounts.oauth2.initTokenClient({
      client_id: GOOGLE_CLIENT_ID,
      scope: 'https://www.googleapis.com/auth/drive.file',
      callback: (tokenResponse) => {
        setAccessToken(tokenResponse.access_token);
        toast.success('Signed in successfully!');
      },
    });
    client.requestAccessToken();
  };

  const handleLogout = () => {
    setGoogleUser(null);
    setAccessToken(null);
    toast.success('Signed out successfully');
  };

  // Load face-api models
  useEffect(() => {
    const loadModels = async () => {
      try {
        const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';
        await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
        await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
        setModelsLoaded(true);
      } catch (err) {
        console.error('Error loading face-api models:', err);
        toast.error('Failed to load face detection models');
      }
    };
    loadModels();
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    // Reset states
    setError('');
    setSuccess(false);
    setProcessedImage(null);
    setDriveLink(null);
    setDownloadUrl(null);
    setFaceDetected(null);

    // Validate file type
    if (!file.type.match('image/(jpeg|jpg|png)')) {
      setError('Only JPG and PNG formats are supported.');
      toast.error('Invalid file format');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit.');
      toast.error('File too large');
      return;
    }

    setImageFile(file);

    // Load image for preview
    const reader = new FileReader();
    reader.onload = async (e) => {
      setUploadedImage(e.target.result);
      
      // Detect face
      if (modelsLoaded) {
        await detectFace(e.target.result);
      }
    };
    reader.readAsDataURL(file);
  };

  const detectFace = async (imageSrc) => {
    setDetecting(true);
    try {
      const img = await faceapi.fetchImage(imageSrc);
      const detections = await faceapi.detectAllFaces(img).withFaceLandmarks();

      if (detections.length === 0) {
        setFaceDetected(false);
        toast.error('No face detected. Please upload a clear, frontal face photo.');
      } else {
        const largestFace = detections.reduce((prev, current) => 
          (prev.detection.score > current.detection.score) ? prev : current
        );
        
        setFaceDetected(true);
        setFaceConfidence(Math.round(largestFace.detection.score * 100));
        
        if (detections.length > 1) {
          toast.warning('Multiple faces detected. Using the most prominent one.');
        } else if (largestFace.detection.score < 0.7) {
          toast.warning('Face detection uncertain. Photo may not process well.');
        } else {
          toast.success(`Face detected with ${Math.round(largestFace.detection.score * 100)}% confidence`);
        }
      }
    } catch (err) {
      console.error('Face detection error:', err);
      setFaceDetected(false);
      toast.error('Face detection failed');
    } finally {
      setDetecting(false);
    }
  };

  const handleNameChange = (e) => {
    const value = e.target.value;
    // Allow only letters, spaces, hyphens, apostrophes
    if (/^[a-zA-Z0-9\s\-']*$/.test(value) && value.length <= 50) {
      setName(value);
    }
  };

  const handleSubmit = async () => {
    if (!imageFile || !name || faceDetected === false) return;

    // Allow processing without sign-in (will download instead of saving to Drive)
    setProcessing(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      formData.append('name', name);

      const headers = {};
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
      }

      const response = await axios.post(`${API}/process-passport`, formData, {
        headers: headers,
        responseType: 'json'
      });

      if (response.data.success) {
        setSuccess(true);
        
        if (response.data.mode === 'google_drive') {
          setDriveLink(response.data.drive_file_url);
          toast.success('Photo saved to Google Drive successfully!');
        } else {
          setDownloadUrl(response.data.download_url);
          toast.success('Photo processed successfully! Click download below.');
        }
      }
    } catch (err) {
      console.error('Processing error:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to process photo. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  const handleReset = () => {
    setUploadedImage(null);
    setImageFile(null);
    setFaceDetected(null);
    setFaceConfidence(0);
    setName('');
    setProcessedImage(null);
    setDriveLink(null);
    setDownloadUrl(null);
    setSuccess(false);
    setError('');
  };

  const canSubmit = uploadedImage && name && faceDetected === true;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <Camera className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Passport Photo Generator</h1>
            </div>
            
            {GOOGLE_DRIVE_ENABLED && (
              <div>
                {googleUser ? (
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <img src={googleUser.picture} alt="Profile" className="w-8 h-8 rounded-full" />
                      <span className="text-sm text-gray-700">{googleUser.name}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
                      data-testid="logout-button"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                ) : (
                  <div id="googleSignInButton" data-testid="google-signin-button"></div>
                )}
              </div>
            )}

            {!GOOGLE_DRIVE_ENABLED && (
              <div className="text-sm text-gray-600 bg-yellow-50 px-4 py-2 rounded-lg border border-yellow-200">
                <span className="font-semibold">Local Mode:</span> Photos will be downloaded
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload & Input */}
          <div className="space-y-6">
            {/* Upload Zone */}
            <div className="bg-white rounded-xl shadow-lg p-8" data-testid="upload-section">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">1. Upload Photo</h2>
              
              {!uploadedImage ? (
                <div
                  className={`border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer
                    ${dragActive 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                    }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById('fileInput').click()}
                  data-testid="upload-dropzone"
                >
                  <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-lg font-medium text-gray-700 mb-2">Drop your photo here</p>
                  <p className="text-sm text-gray-500 mb-4">or click to browse</p>
                  <p className="text-xs text-gray-400">JPG or PNG • Max 10MB</p>
                  <input
                    id="fileInput"
                    type="file"
                    accept=".jpg,.jpeg,.png"
                    onChange={handleFileInput}
                    className="hidden"
                    data-testid="file-input"
                  />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="relative rounded-lg overflow-hidden">
                    <img src={uploadedImage} alt="Uploaded" className="w-full h-auto" data-testid="uploaded-image-preview" />
                    {detecting && (
                      <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                        <div className="text-white text-center">
                          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-2" />
                          <p>Detecting face...</p>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Face Detection Status */}
                  {faceDetected !== null && (
                    <div className={`flex items-center space-x-2 p-3 rounded-lg ${
                      faceDetected 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-red-50 border border-red-200'
                    }`} data-testid="face-detection-status">
                      {faceDetected ? (
                        <>
                          <CheckCircle2 className="w-5 h-5 text-green-600" />
                          <span className="text-sm font-medium text-green-800">
                            Face detected ({faceConfidence}% confidence)
                          </span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-5 h-5 text-red-600" />
                          <span className="text-sm font-medium text-red-800">
                            No face detected
                          </span>
                        </>
                      )}
                    </div>
                  )}
                  
                  <button
                    onClick={handleReset}
                    className="w-full px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                    data-testid="clear-button"
                  >
                    Upload Different Photo
                  </button>
                </div>
              )}
            </div>

            {/* Name Input */}
            {uploadedImage && (
              <div className="bg-white rounded-xl shadow-lg p-8" data-testid="name-input-section">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">2. Enter Your Name</h2>
                <div className="space-y-2">
                  <label htmlFor="nameInput" className="block text-sm font-medium text-gray-700">
                    Full Name
                  </label>
                  <input
                    id="nameInput"
                    type="text"
                    value={name}
                    onChange={handleNameChange}
                    placeholder="Enter name for passport photo"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                    maxLength={50}
                    data-testid="name-input"
                  />
                  <p className="text-xs text-gray-500">{name.length}/50 characters</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            {uploadedImage && (
              <div className="bg-white rounded-xl shadow-lg p-8" data-testid="submit-section">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">3. Generate Photo</h2>
                
                {/* Mode info */}
                {GOOGLE_DRIVE_ENABLED && !accessToken && (
                  <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">
                      <strong>Download Mode:</strong> Sign in with Google to save directly to your Drive, or continue without sign-in to download the photo.
                    </p>
                  </div>
                )}
                
                {GOOGLE_DRIVE_ENABLED && accessToken && (
                  <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-800">
                      <strong>Google Drive Mode:</strong> Your photo will be saved to Google Drive.
                    </p>
                  </div>
                )}

                <button
                  onClick={handleSubmit}
                  disabled={!canSubmit || processing}
                  className={`w-full px-6 py-4 rounded-lg font-semibold text-white text-lg transition-all transform
                    ${canSubmit && !processing
                      ? 'bg-blue-600 hover:bg-blue-700 hover:scale-105 shadow-lg hover:shadow-xl'
                      : 'bg-gray-300 cursor-not-allowed'
                    }`}
                  data-testid="generate-button"
                >
                  {processing ? (
                    <span className="flex items-center justify-center space-x-2">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Processing your photo...</span>
                    </span>
                  ) : (
                    'Generate Passport Photo'
                  )}
                </button>

                {error && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg" data-testid="error-message">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column - Preview & Result */}
          <div className="space-y-6">
            {/* Instructions */}
            {!uploadedImage && (
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">How it works</h2>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
                      1
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Upload a clear photo</h3>
                      <p className="text-sm text-gray-600">Make sure your face is clearly visible and well-lit</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
                      2
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Enter your name</h3>
                      <p className="text-sm text-gray-600">Your name will be added at the bottom of the photo</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
                      3
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Generate & Save</h3>
                      <p className="text-sm text-gray-600">
                        {GOOGLE_DRIVE_ENABLED 
                          ? 'Save to Google Drive (with sign-in) or download (without sign-in)'
                          : 'Download your passport photo to your device'
                        }
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h3 className="font-semibold text-blue-900 mb-2">Specifications</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Size: 600x600 pixels (2x2 inches)</li>
                    <li>• Resolution: 300 DPI</li>
                    <li>• Format: JPEG</li>
                    <li>• Background: Automatic cropping</li>
                  </ul>
                </div>
              </div>
            )}

            {/* Success Result */}
            {success && (
              <div className="bg-white rounded-xl shadow-lg p-8" data-testid="success-section">
                <div className="text-center mb-6">
                  <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Success!</h2>
                  <p className="text-gray-600">
                    {driveLink 
                      ? 'Your passport photo has been saved to Google Drive'
                      : 'Your passport photo is ready to download'
                    }
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-700 mb-1">Specifications</p>
                    <p className="text-xs text-gray-600">600x600px | 2x2 inches | 300 DPI | JPEG</p>
                  </div>

                  {driveLink && (
                    <a
                      href={driveLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-center transition-colors"
                      data-testid="view-in-drive-button"
                    >
                      View in Google Drive
                    </a>
                  )}

                  {downloadUrl && (
                    <a
                      href={downloadUrl}
                      download
                      className="flex items-center justify-center space-x-2 w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
                      data-testid="download-button"
                    >
                      <Download className="w-5 h-5" />
                      <span>Download Photo</span>
                    </a>
                  )}

                  <button
                    onClick={handleReset}
                    className="w-full px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-lg transition-colors"
                    data-testid="upload-another-button"
                  >
                    Upload Another Photo
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-600">
          <p>Passport Photo Generator • Automatic face detection and cropping</p>
          <p className="mt-2 text-xs text-gray-500">
            {GOOGLE_DRIVE_ENABLED 
              ? 'Sign in with Google to save to Drive, or use without sign-in to download photos'
              : 'Photos are downloaded directly to your device'
            }
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
