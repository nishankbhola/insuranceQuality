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

echo [3/7] Creating all necessary directories on VPS...
ssh root@31.97.113.225 "mkdir -p /root/quality-app/frontend/build && mkdir -p /root/quality-app/backend/extractors && mkdir -p /root/quality-app/backend/validator && mkdir -p /root/quality-app/backend/uploads"
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
scp backend\qc_checklist.py root@31.97.113.225:/root/quality-app/backend/
scp backend\requirements.txt root@31.97.113.225:/root/quality-app/backend/

echo Uploading extractors...
scp -r backend\extractors\*.py root@31.97.113.225:/root/quality-app/backend/extractors/

echo Uploading validator...
scp -r backend\validator\*.py root@31.97.113.225:/root/quality-app/backend/validator/

if %errorlevel% neq 0 (
    echo ERROR: Backend upload failed!
    pause
    exit /b 1
)
echo ✓ All backend files uploaded successfully
echo.

echo [6/7] Setting proper permissions and creating uploads directory...
ssh root@31.97.113.225 "chmod -R 755 /root/quality-app/frontend/build/ && chmod -R 755 /root/quality-app/backend/ && chmod 777 /root/quality-app/backend/uploads"
if %errorlevel% neq 0 (
    echo ERROR: Permission setting failed!
    pause
    exit /b 1
)
echo ✓ Permissions set successfully
echo.

echo [7/7] Restarting services on VPS...
ssh root@31.97.113.225 "systemctl restart quality-app && systemctl reload nginx"
if %errorlevel% neq 0 (
    echo ERROR: Service restart failed!
    pause
    exit /b 1
)
echo ✓ Services restarted successfully
echo.

echo [8/8] Deployment complete!
echo.
echo ========================================
echo    Deployment Summary
echo ========================================
echo ✓ Frontend built and uploaded
echo ✓ Static file paths fixed for VPS
echo ✓ All backend files uploaded including:
echo   - app.py
echo   - quote_comparison_service.py
echo   - qc_checklist.py
echo   - requirements.txt
echo   - All extractor modules
echo   - All validator modules
echo ✓ Uploads directory created with proper permissions
echo ✓ Services restarted
echo ✓ Nginx reloaded
echo.
echo Your app is now live at:
echo https://www.brokergpt.ca/quality
echo.
echo ========================================
pause 