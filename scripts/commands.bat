@echo off
REM This script deploys the entire MySQL FastAPI stack with namespaced resources.

REM === Make script robust: Change to the script's own directory ===
cd /d "%~dp0"

REM --- Step 1: Verify Project Context ---
echo [INFO] Using current OpenShift project:
oc project -q
echo [INFO] If this is not the correct project, press Ctrl+C to abort.
timeout /t 5 >nul

REM --- Step 2: Deploy MySQL Database ---
echo [INFO] Deploying MySQL Database...
oc apply -f ..\infrastructure\k8s\01-mysql-secret.yaml
oc apply -f ..\infrastructure\k8s\02-mysql-pvc.yaml
oc apply -f ..\infrastructure\k8s\03-mysql-deployment.yaml
oc apply -f ..\infrastructure\k8s\04-mysql-service.yaml
echo [INFO] Waiting for MySQL to be ready...
oc wait --for=condition=ready pod -l app=mysql-db --timeout=300s
echo [SUCCESS] MySQL is ready.
echo.

REM --- Step 6: Deploy FastAPI Backend ---
echo [INFO] Deploying FastAPI Backend...
oc apply -f ..\infrastructure\k8s\05-fastapi-deployment.yaml
oc apply -f ..\infrastructure\k8s\06-fastapi-service.yaml
echo [INFO] Waiting for FastAPI to be ready...
oc wait --for=condition=ready pod -l app=mysql-api --timeout=300s
echo [SUCCESS] FastAPI Backend is ready.
echo.

REM --- Step 7: Initialize Data in MySQL ---
echo [INFO] Initializing data in MySQL...
FOR /F "tokens=*" %%g IN ('oc get pod -l app=mysql-db -o jsonpath="{.items[0].metadata.name}"') do (SET MYSQL_POD=%%g)
echo [INFO] Found MySQL pod: %MYSQL_POD%

echo [INFO] Copying SQL scripts to the pod...
oc cp .\create_data.sql %MYSQL_POD%:/tmp/create_data.sql
oc cp .\insert_data.sql %MYSQL_POD%:/tmp/insert_data.sql

echo [INFO] Executing SQL scripts inside the pod...
FOR /F "tokens=*" %%g IN ('oc get secret mysql-db-credentials -o jsonpath="{.data.MYSQL_ROOT_PASSWORD}" ^| base64 --decode') do (SET MYSQL_PASSWORD=%%g)

REM The logic here is to execute a command INSIDE the pod that reads the file already copied to /tmp
oc exec %MYSQL_POD% -- bash -c "mysql -u root -p'%MYSQL_PASSWORD%' mydatabase < /tmp/create_data.sql"
oc exec %MYSQL_POD% -- bash -c "mysql -u root -p'%MYSQL_PASSWORD%' mydatabase < /tmp/insert_data.sql"
echo [SUCCESS] Data initialized.
echo.

REM --- Step 8: Expose the Service with a Route ---
echo [INFO] Exposing the FastAPI service...
oc apply -f ..\infrastructure\k8s\07-fastapi-route.yaml
echo [SUCCESS] Route created.
echo.
echo [ACTION] Find your application URL by running:
echo oc get route mysql-api-route