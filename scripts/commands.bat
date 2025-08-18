@echo off
setlocal

REM This script performs a full deployment of the MySQL and FastAPI infrastructure to OpenShift.

REM === Technical Step: Ensure the script runs from its own directory ===
cd /d "%~dp0"

REM --- Configuration ---
IF "%~1"=="" (
    echo [ERROR] Docker Hub username must be provided as the first argument.
    echo [USAGE] commands.bat ^<your-dockerhub-username^>
    exit /b 1
)
SET "DOCKERHUB_USERNAME=%~1"
SET "IMAGE_NAME=data-loader-service"

REM --- Create a unique tag from git hash or a timestamp ---
FOR /F "tokens=*" %%g IN ('git rev-parse --short HEAD 2^>nul') DO SET "IMAGE_TAG=%%g"
IF NOT DEFINED IMAGE_TAG (
    FOR /F "tokens=*" %%g IN ('powershell -Command "Get-Date -UFormat +%%s"') DO SET "IMAGE_TAG=%%g"
)
SET "FULL_IMAGE_NAME=docker.io/%DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%"

REM --- Step 1: Build and Push Docker Image ---
echo [INFO] Building and pushing image: %FULL_IMAGE_NAME%
docker buildx build --no-cache --platform linux/amd64,linux/arm64 -t "%FULL_IMAGE_NAME%" --push ..
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build and push failed.
    exit /b 1
)
echo [SUCCESS] Image pushed successfully to Docker Hub.
echo.

REM --- Step 1.5: Verify Workspace ---
echo [INFO] Using current OpenShift project:
oc project -q
echo [INFO] If this is not the correct project, press Ctrl+C to abort.
timeout /t 5 >nul

REM --- Step 2: Deploy MySQL Database ---
echo [INFO] Deploying MySQL Database...
REM UPDATED: Added the new ConfigMap
oc apply -f ..\infrastructure\k8s\00-mysql-configmap.yaml
oc apply -f ..\infrastructure\k8s\01-mysql-secret.yaml
oc apply -f ..\infrastructure\k8s\02-mysql-pvc.yaml
oc apply -f ..\infrastructure\k8s\03-mysql-deployment.yaml
oc apply -f ..\infrastructure\k8s\04-mysql-service.yaml
echo [INFO] Waiting for MySQL pod to become ready...
REM UPDATED: Using the new standard label to find the pod
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=mysql-db --timeout=300s
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] MySQL pod did not become ready in time.
    exit /b 1
)
echo [SUCCESS] MySQL pod is ready.

REM --- ADDED: Wait for MySQL internal initialization ---
echo [INFO] Allowing time for MySQL internal initialization...
timeout /t 15 >nul
echo [SUCCESS] MySQL is fully initialized.
echo.

REM --- Step 3: Deploy FastAPI Backend ---
echo [INFO] Deploying FastAPI Backend...
REM Use PowerShell to dynamically replace the username and tag in the deployment YAML
powershell -Command "(Get-Content -Raw ..\infrastructure\k8s\05-fastapi-deployment.yaml).Replace('YOUR_DOCKERHUB_USERNAME', '%DOCKERHUB_USERNAME%').Replace(':latest', ':%IMAGE_TAG%') | oc apply -f -"
oc apply -f ..\infrastructure\k8s\06-fastapi-service.yaml
echo [INFO] Waiting for FastAPI pod to be ready...
REM UPDATED: Using the new standard label to find the pod
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=mysql-api --timeout=300s
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] FastAPI pod did not become ready in time.
    exit /b 1
)
echo [SUCCESS] FastAPI Backend is ready.
echo.

REM --- Step 4: Initialize Data in Database ---
echo [INFO] Initializing data in MySQL...
REM UPDATED: Using the new standard label to find the pod
FOR /F "tokens=*" %%g IN ('oc get pod -l app.kubernetes.io/instance=mysql-db -o jsonpath="{.items[0].metadata.name}"') DO SET "MYSQL_POD=%%g"
echo [INFO] Found MySQL pod: %MYSQL_POD%

REM --- Decode Base64 password using PowerShell ---
echo [INFO] Fetching and decoding MySQL password...
FOR /F "tokens=*" %%g IN ('oc get secret mysql-db-credentials -o jsonpath="{.data.MYSQL_ROOT_PASSWORD}"') DO SET "B64_PASSWORD=%%g"
FOR /F "usebackq tokens=*" %%h IN (`powershell -NoProfile -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%B64_PASSWORD%'))"`) DO SET "MYSQL_PASSWORD=%%h"

REM --- Stream SQL scripts directly into the pod ---
echo [INFO] Executing SQL scripts via streaming...
oc exec -i "%MYSQL_POD%" -- mysql -u root -p"%MYSQL_PASSWORD%" mydatabase < ".\create_data.sql"
oc exec -i "%MYSQL_POD%" -- mysql -u root -p"%MYSQL_PASSWORD%" mydatabase < ".\insert_data.sql"
echo [SUCCESS] Data initialized.
echo.

REM --- Step 5: Expose the Service ---
echo [INFO] Exposing the FastAPI service...
oc apply -f ..\infrastructure\k8s\07-fastapi-route.yaml
echo [SUCCESS] Route created.
echo.

REM --- Final Step: Display Application URL ---
echo =================================================================
echo             DEPLOYMENT COMPLETE
echo =================================================================
FOR /F "tokens=*" %%g IN ('oc get route mysql-api-route -o jsonpath="{.spec.host}"') DO SET "ROUTE_URL=%%g"
echo Your application is available at the following URL:
REM UPDATED: Displaying the URL with https, as it should be
echo https://%ROUTE_URL%
echo.
echo To fetch data, navigate to:
echo https://%ROUTE_URL%/data
echo.
echo To view the interactive API documentation (Swagger UI), navigate to:
echo https://%ROUTE_URL%/docs
echo =================================================================

endlocal