@echo off
setlocal

REM סקריפט זה מבצע פריסה מלאה של תשתית MySQL ואפליקציית FastAPI ל-OpenShift.

REM === שלב טכני: וידוא שהסקריפט רץ מהתיקייה הנכונה ===
cd /d "%~dp0"

REM --- NEW: Configuration ---
IF "%~1"=="" (
    echo [ERROR] Docker Hub username must be provided as the first argument.
    echo [USAGE] commands.bat ^<your-dockerhub-username^>
    exit /b 1
)
SET "DOCKERHUB_USERNAME=%~1"
SET "IMAGE_NAME=data-loader-service"

REM --- FIXED: יצירת תג ייחודי מ-hash של git או חותמת זמן (בדומה לסקריפט ה-bash) ---
FOR /F "tokens=*" %%g IN ('git rev-parse --short HEAD 2^>nul') DO SET "IMAGE_TAG=%%g"
IF NOT DEFINED IMAGE_TAG (
    FOR /F "tokens=*" %%g IN ('powershell -Command "Get-Date -UFormat +%%s"') DO SET "IMAGE_TAG=%%g"
)
SET "FULL_IMAGE_NAME=docker.io/%DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%"

REM --- NEW: Step 1.5: Build and Push Docker Image ---
echo [INFO] Building and pushing image: %FULL_IMAGE_NAME%
REM FIXED: הוספת linux/arm64 כדי להתאים לסקריפט המקורי וליצור תמונה מרובת-ארכיטקטורות
docker buildx build --no-cache --platform linux/amd64,linux/arm64 -t "%FULL_IMAGE_NAME%" --push ..
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build and push failed.
    exit /b 1
)
echo [SUCCESS] Image pushed successfully to Docker Hub.
echo.

REM --- שלב 1 לשעבר: אימות סביבת העבודה (משימה 1) ---
echo [INFO] Using current OpenShift project:
oc project -q
echo [INFO] If this is not the correct project, press Ctrl+C to abort.
timeout /t 5 >nul

REM --- שלב 2: פריסת מסד הנתונים MySQL (משימה 2) ---
echo [INFO] Deploying MySQL Database...
oc apply -f ..\infrastructure\k8s\01-mysql-secret.yaml
oc apply -f ..\infrastructure\k8s\02-mysql-pvc.yaml
oc apply -f ..\infrastructure\k8s\03-mysql-deployment.yaml
oc apply -f ..\infrastructure\k8s\04-mysql-service.yaml
echo [INFO] Waiting for MySQL to be ready...
oc wait --for=condition=ready pod -l app=mysql-db --timeout=300s
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] MySQL pod did not become ready in time.
    exit /b 1
)
echo [SUCCESS] MySQL is ready.
echo.

REM --- שלב 3: פריסת אפליקציית FastAPI (משימה 6) ---
echo [INFO] Deploying FastAPI Backend...
REM UPDATED: שימוש ב-PowerShell להחלפה דינמית של שם המשתמש והתג
powershell -Command "(Get-Content -Raw ..\infrastructure\k8s\05-fastapi-deployment.yaml).Replace('YOUR_DOCKERHUB_USERNAME', '%DOCKERHUB_USERNAME%').Replace(':latest', ':%IMAGE_TAG%') | oc apply -f -"
oc apply -f ..\infrastructure\k8s\06-fastapi-service.yaml
echo [INFO] Waiting for FastAPI to be ready...
oc wait --for=condition=ready pod -l app=mysql-api --timeout=300s
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] FastAPI pod did not become ready in time.
    exit /b 1
)
echo [SUCCESS] FastAPI Backend is ready.
echo.

REM --- שלב 4: אתחול הנתונים במסד הנתונים (משימה 7) ---
echo [INFO] Initializing data in MySQL...
FOR /F "tokens=*" %%g IN ('oc get pod -l app=mysql-db -o jsonpath="{.items[0].metadata.name}"') DO SET "MYSQL_POD=%%g"
echo [INFO] Found MySQL pod: %MYSQL_POD%

REM --- FIXED: פיענוח סיסמת Base64 באמצעות PowerShell (אין פקודת base64 מובנית ב-Windows) ---
echo [INFO] Fetching and decoding MySQL password...
FOR /F "tokens=*" %%g IN ('oc get secret mysql-db-credentials -o jsonpath="{.data.MYSQL_ROOT_PASSWORD}"') DO SET "B64_PASSWORD=%%g"
FOR /F "usebackq tokens=*" %%h IN (`powershell -NoProfile -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%B64_PASSWORD%'))"`) DO SET "MYSQL_PASSWORD=%%h"

REM --- IMPROVED: הזנת סקריפטי ה-SQL ישירות לתוך ה-Pod במקום להעתיק אותם תחילה ---
echo [INFO] Executing SQL scripts inside the pod...
oc exec -i "%MYSQL_POD%" -- mysql -u root -p"%MYSQL_PASSWORD%" mydatabase < ".\create_data.sql"
oc exec -i "%MYSQL_POD%" -- mysql -u root -p"%MYSQL_PASSWORD%" mydatabase < ".\insert_data.sql"
echo [SUCCESS] Data initialized.
echo.

REM --- שלב 5: חשיפת השירות לעולם החיצון (משימה 8) ---
echo [INFO] Exposing the FastAPI service...
oc apply -f ..\infrastructure\k8s\07-fastapi-route.yaml
echo [SUCCESS] Route created.
echo.

REM --- שלב סופי: הצגת כתובת ה-URL של האפליקציה ---
echo =================================================================
echo             DEPLOYMENT COMPLETE
echo =================================================================
FOR /F "tokens=*" %%g IN ('oc get route mysql-api-route -o jsonpath="{.spec.host}"') DO SET "ROUTE_URL=%%g"
echo Your application is available at the following URL:
echo http://%ROUTE_URL%
echo.
echo To fetch data, navigate to:
echo http://%ROUTE_URL%/data
echo.
echo To view the interactive API documentation (Swagger UI), navigate to:
echo http://%ROUTE_URL%/docs
echo =================================================================

endlocal