#!/bin/bash
# This script performs a full deployment of the MySQL and FastAPI infrastructure to OpenShift.

# === Technical Step: Ensure the script runs from its own directory ===
cd "$(dirname "$0")"

# --- Configuration ---
if [ -z "$1" ]; then
    echo "[ERROR] Docker Hub username must be provided as the first argument."
    echo "[USAGE] ./commands.sh <your-dockerhub-username>"
    exit 1
fi
DOCKERHUB_USERNAME="$1"
IMAGE_NAME="data-loader-service"
# Create a unique tag from git hash or a timestamp
IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || date +%s)
FULL_IMAGE_NAME="docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
set -e # Exit immediately if a command exits with a non-zero status.

# --- Step 1: Build and Push Docker Image ---
echo "[INFO] Building and pushing image: ${FULL_IMAGE_NAME}"
# Run the build from the project root directory (..), where the Dockerfile is located
(cd .. && docker buildx build --no-cache --platform linux/amd64,linux/arm64 -t "${FULL_IMAGE_NAME}" --push .)
echo "[SUCCESS] Image pushed successfully to Docker Hub."
echo ""

# --- Step 1.5: Verify Workspace ---
echo "[INFO] Using current OpenShift project: $(oc project -q)"
echo "[INFO] If this is not the correct project, press Ctrl+C to abort."
sleep 5

# --- Step 2: Deploy MySQL Database ---
echo "[INFO] Deploying MySQL Database..."
oc apply -f ../infrastructure/k8s/00-mysql-configmap.yaml
oc apply -f ../infrastructure/k8s/01-mysql-secret.yaml
oc apply -f ../infrastructure/k8s/02-mysql-pvc.yaml
oc apply -f ../infrastructure/k8s/03-mysql-deployment.yaml
oc apply -f ../infrastructure/k8s/04-mysql-service.yaml
echo "[INFO] Waiting for MySQL pod to become ready..."
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=mysql-db --timeout=300s
echo "[SUCCESS] MySQL pod is ready."

# --- Wait for MySQL internal initialization ---
echo "[INFO] Allowing time for MySQL internal initialization..."
sleep 15
echo "[SUCCESS] MySQL is fully initialized."
echo ""

# --- Step 3: Deploy FastAPI Backend ---
echo "[INFO] Deploying FastAPI Backend..."
# Use sed to dynamically replace the username and tag in the deployment YAML
sed -e "s|YOUR_DOCKERHUB_USERNAME|${DOCKERHUB_USERNAME}|g" \
    -e "s|:latest|:${IMAGE_TAG}|g" \
    "../infrastructure/k8s/05-fastapi-deployment.yaml" | oc apply -f -
oc apply -f ../infrastructure/k8s/06-fastapi-service.yaml
echo "[INFO] Waiting for FastAPI pod to be ready..."
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=mysql-api --timeout=300s
echo "[SUCCESS] FastAPI Backend is ready."
echo ""

# --- Step 4: Initialize Data in Database ---
echo "[INFO] Initializing data in MySQL..."
MYSQL_POD=$(oc get pod -l app.kubernetes.io/instance=mysql-db -o jsonpath='{.items[0].metadata.name}')
echo "[INFO] Found MySQL pod: $MYSQL_POD"

echo "[INFO] Fetching MySQL root password..."
MYSQL_PASSWORD=$(oc get secret mysql-db-credentials -o jsonpath='{.data.MYSQL_ROOT_PASSWORD}' | base64 --decode)

echo "[INFO] Executing SQL scripts via streaming..."
oc exec -i "$MYSQL_POD" -- mysql -u root -p"$MYSQL_PASSWORD" mydatabase < ./create_data.sql
oc exec -i "$MYSQL_POD" -- mysql -u root -p"$MYSQL_PASSWORD" mydatabase < ./insert_data.sql
echo "[SUCCESS] Data initialized."
echo ""

# --- Step 5: Expose the Service ---
echo "[INFO] Exposing the FastAPI service..."
oc apply -f ../infrastructure/k8s/07-fastapi-route.yaml
echo "[SUCCESS] Route created."
echo ""

# --- Final Step: Display Application URL ---
echo "================================================================="
echo "            DEPLOYMENT COMPLETE"
echo "================================================================="
ROUTE_URL=$(oc get route mysql-api-route -o jsonpath='{.spec.host}')
echo "Your application is available at the following URL:"
echo "https://${ROUTE_URL}"
echo ""
echo "To fetch data, navigate to:"
echo "https://${ROUTE_URL}/data"
echo ""
echo "To view the interactive API documentation (Swagger UI), navigate to:"
echo "https://${ROUTE_URL}/docs"
echo "================================================================="