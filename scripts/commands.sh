#!/bin/bash
# This script is designed to be robust and run from any directory.

# === Make script robust: Change to the script's own directory ===
# This ensures that all relative paths (like ../infrastructure) work correctly.
cd "$(dirname "$0")"

# --- Step 1: Verify Project Context ---
echo "[INFO] Using current OpenShift project: $(oc project -q)"
echo "[INFO] If this is not the correct project, press Ctrl+C to abort."
sleep 5 # Give the user 5 seconds to read and abort if needed

# --- Step 2: Deploy MySQL Database ---
echo "[INFO] Deploying MySQL Database..."
oc apply -f ../infrastructure/k8s/01-mysql-secret.yaml
oc apply -f ../infrastructure/k8s/02-mysql-pvc.yaml
oc apply -f ../infrastructure/k8s/03-mysql-deployment.yaml
oc apply -f ../infrastructure/k8s/04-mysql-service.yaml
echo "[INFO] Waiting for MySQL to be ready..."
oc wait --for=condition=ready pod -l app=mysql --timeout=300s
echo "[SUCCESS] MySQL is ready."
echo ""

# --- Step 6: Deploy FastAPI Backend ---
echo "[INFO] Deploying FastAPI Backend..."
oc apply -f ../infrastructure/k8s/05-fastapi-deployment.yaml
oc apply -f ../infrastructure/k8s/06-fastapi-service.yaml
echo "[INFO] Waiting for FastAPI to be ready..."
oc wait --for=condition=ready pod -l app=fastapi --timeout=300s
echo "[SUCCESS] FastAPI Backend is ready."
echo ""

# --- Step 7: Initialize Data in MySQL ---
echo "[INFO] Initializing data in MySQL..."
MYSQL_POD=$(oc get pod -l app=mysql -o jsonpath='{.items[0].metadata.name}')
echo "[INFO] Found MySQL pod: $MYSQL_POD"

echo "[INFO] Copying SQL scripts to the pod..."
oc cp ./create_data.sql "$MYSQL_POD":/tmp/create_data.sql
oc cp ./insert_data.sql "$MYSQL_POD":/tmp/insert_data.sql

echo "[INFO] Executing SQL scripts inside the pod..."
MYSQL_PASSWORD=$(oc get secret mysql-credentials -o jsonpath='{.data.MYSQL_ROOT_PASSWORD}' | base64 --decode)
oc exec "$MYSQL_POD" -- bash -c "mysql -u root -p'$MYSQL_PASSWORD' mydatabase < /tmp/create_data.sql"
oc exec "$MYSQL_POD" -- bash -c "mysql -u root -p'$MYSQL_PASSWORD' mydatabase < /tmp/insert_data.sql"
echo "[SUCCESS] Data initialized."
echo ""

# --- Step 8: Expose the Service with a Route ---
echo "[INFO] Exposing the FastAPI service..."
oc apply -f ../infrastructure/k8s/07-fastapi-route.yaml
echo "[SUCCESS] Route created."
echo ""
echo "[ACTION] Find your application URL by running:"
echo "oc get route fastapi-route"