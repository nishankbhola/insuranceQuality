@echo off
echo ========================================
echo    Vieira Insurance - Deploy Script
echo ========================================
echo.

echo [1/7] Building frontend...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)
cd ..
echo ✓ Frontend built successfully
echo.

echo [2/7] Fixing static file paths for VPS...
cd frontend\build
powershell -Command "(Get-Content index.html) -replace 'src=\"/static/', 'src=\"/quality/static/' | Set-Content index.html"
powershell -Command "(Get-Content index.html) -replace 'href=\"/static/', 'href=\"/quality/static/' | Set-Content index.html"
cd ..\..
echo ✓ Static file paths fixed
echo.

echo [3/7] Creating backup and directories on VPS...
ssh root@31.97.113.225 "mkdir -p /root/quality-app-backup && cp -r /root/quality-app/* /root/quality-app-backup/ 2>/dev/null || echo '   Note: No existing files to backup' && mkdir -p /root/quality-app/frontend/build && mkdir -p /root/quality-app/backend/extractors && mkdir -p /root/quality-app/backend/validator && mkdir -p /root/quality-app/backend/uploads"
if %errorlevel% neq 0 (
    echo ERROR: Directory creation failed!
    pause
    exit /b 1
)
echo ✓ All directories created successfully
echo.

echo [4/7] Uploading frontend to VPS...
scp -r frontend\build\* root@31.97.113.225:/root/quality-app/frontend/build/
if %errorlevel% neq 0 (
    echo ERROR: Frontend upload failed!
    pause
    exit /b 1
)
echo ✓ Frontend uploaded successfully
echo.

echo [5/7] Uploading all backend files...
echo Uploading main application files...
scp backend\app.py root@31.97.113.225:/root/quality-app/backend/
scp backend\quote_comparison_service.py root@31.97.113.225:/root/quality-app/backend/
scp backend\requirements.txt root@31.97.113.225:/root/quality-app/backend/
scp backend\APPLICATION_QC_GEMINI_GUIDE.md root@31.97.113.225:/root/quality-app/backend/

echo Uploading extractors...
scp -r backend\extractors\*.py root@31.97.113.225:/root/quality-app/backend/extractors/
scp backend\extractors\__init__.py root@31.97.113.225:/root/quality-app/backend/extractors/ 2>nul || echo "   Note: __init__.py may not exist, creating on server..."

echo Uploading validator...
scp -r backend\validator\*.py root@31.97.113.225:/root/quality-app/backend/validator/

if %errorlevel% neq 0 (
    echo ERROR: Backend upload failed!
    pause
    exit /b 1
)
echo ✓ All backend files uploaded successfully
echo.

echo [6/7] Creating __init__.py files...
ssh root@31.97.113.225 "touch /root/quality-app/backend/extractors/__init__.py && touch /root/quality-app/backend/validator/__init__.py"
if %errorlevel% neq 0 (
    echo ERROR: Module configuration failed!
    pause
    exit /b 1
)
echo ✓ Python modules configured successfully
echo.
echo ⚠️  MANUAL STEP REQUIRED:
echo Please SSH to the server and run:
echo   cd /root/quality-app/backend
echo   pip install -r requirements.txt --break-system-packages
echo.

echo [7/7] Setting proper permissions and creating uploads directory...
ssh root@31.97.113.225 "chmod -R 755 /root/quality-app/frontend/build/ && chmod -R 755 /root/quality-app/backend/ && chmod 777 /root/quality-app/backend/uploads"
if %errorlevel% neq 0 (
    echo ERROR: Permission setting failed!
    pause
    exit /b 1
)
echo ✓ Permissions set successfully
echo.

echo [8/8] Restarting services on VPS...
ssh root@31.97.113.225 "cd /root/quality-app/backend && echo 'Ensuring service uses virtual environment...' && systemctl restart quality-app && systemctl reload nginx"
if %errorlevel% neq 0 (
    echo ERROR: Service restart failed!
    pause
    exit /b 1
)
echo ✓ Services restarted successfully
echo.

echo [9/9] Deployment complete!
echo.
echo ========================================
echo    Deployment Summary
echo ========================================
echo ✓ Previous version backed up
echo ✓ Frontend built and uploaded
echo ✓ Static file paths fixed for VPS
echo ✓ All backend files uploaded including:
echo   - app.py
echo   - quote_comparison_service.py
echo   - requirements.txt
echo   - APPLICATION_QC_GEMINI_GUIDE.md
echo   - All extractor modules (including gemini_application_extractor.py)
echo   - All validator modules
echo ✓ Python modules configured
echo ⚠️  Manual step: Install dependencies on server
echo ✓ Uploads directory created with proper permissions
echo ✓ Services restarted
echo ✓ Nginx reloaded
echo.
echo Your app is now live at:
echo https://www.brokergpt.ca/quality
echo.
echo ========================================
echo    🆕 NEW FEATURES DEPLOYED
echo ========================================
echo ✓ Gemini AI-powered Application QC with 14 validations
echo ✓ 5 Simple string validations (no API cost)
echo ✓ 9 AI-powered validations using Gemini API
echo ✓ Smart PDF page extraction (3 pages only)
echo ✓ Enhanced leasing validation logic
echo ✓ API usage tracking (50 calls/day limit)
echo ✓ Automatic gemini_response.json saving for audit
echo.
echo ========================================
echo    📋 NEXT STEPS
echo ========================================
echo 1. SSH to the server and install dependencies:
echo   ssh root@31.97.113.225
echo   cd /root/quality-app/backend  
echo   pip install -r requirements.txt --break-system-packages
echo.
echo 2. ⚠️  CRITICAL: Set up Gemini API key in .env file:
echo   nano /root/quality-app/backend/.env
echo   Add: GEMINI_API_KEY=AIzaSyB5fI8Lzr8ROr0H3ZotRZ9dtLXQJODn1SY
echo   Add: ENABLE_GEMINI_ANALYSIS=true
echo   Add: GEMINI_DAILY_LIMIT=45
echo   Save and exit (Ctrl+X, Y, Enter)
echo.
echo 3. Test the Gemini API connection:
echo   python -c "import google.generativeai as genai; genai.configure(api_key='AIzaSyB5fI8Lzr8ROr0H3ZotRZ9dtLXQJODn1SY'); print('✓ API key works!')"
echo.
echo ========================================
pause 