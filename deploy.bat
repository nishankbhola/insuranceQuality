@echo off
echo ========================================
echo    Vieira Insurance - Deploy Script
echo ========================================
echo.

echo [1/6] Building frontend...
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

echo [2/6] Fixing static file paths for VPS...
cd frontend\build
powershell -Command "(Get-Content index.html) -replace 'src=\"/static/', 'src=\"/quality/static/' | Set-Content index.html"
powershell -Command "(Get-Content index.html) -replace 'href=\"/static/', 'href=\"/quality/static/' | Set-Content index.html"
cd ..\..
echo ✓ Static file paths fixed
echo.

echo [3/6] Creating build directory on VPS...
ssh root@31.97.113.225 "mkdir -p /root/quality-app/frontend/build"
echo ✓ Build directory created
echo.

echo [4/6] Uploading frontend to VPS...
scp -r frontend\build\* root@31.97.113.225:/root/quality-app/frontend/build/
if %errorlevel% neq 0 (
    echo ERROR: Frontend upload failed!
    pause
    exit /b 1
)
echo ✓ Frontend uploaded successfully
echo.

echo [5/6] Uploading backend changes...
scp backend\app.py root@31.97.113.225:/root/quality-app/backend/
scp backend\quote_comparison_service.py root@31.97.113.225:/root/quality-app/backend/
scp backend\requirements.txt root@31.97.113.225:/root/quality-app/backend/
scp -r backend\extractors root@31.97.113.225:/root/quality-app/backend/
scp -r backend\validator root@31.97.113.225:/root/quality-app/backend/
if %errorlevel% neq 0 (
    echo ERROR: Backend upload failed!
    pause
    exit /b 1
)
echo ✓ Backend uploaded successfully
echo.

echo [6/6] Setting permissions and restarting services on VPS...
ssh root@31.97.113.225 "chmod -R 755 /root/quality-app/frontend/build/ && systemctl restart quality-app && systemctl reload nginx"
if %errorlevel% neq 0 (
    echo ERROR: Service restart failed!
    pause
    exit /b 1
)
echo ✓ Services restarted successfully
echo.

echo [7/7] Deployment complete!
echo.
echo ========================================
echo    Deployment Summary
echo ========================================
echo ✓ Frontend built and uploaded
echo ✓ Static file paths fixed for VPS
echo ✓ Backend updated
echo ✓ Services restarted
echo ✓ Nginx reloaded
echo.
echo Your app is now live at:
echo https://www.brokergpt.ca/quality
echo.
echo ========================================
pause 