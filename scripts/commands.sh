#!/bin/bash
# סקריפט זה מבצע פריסה מלאה של תשתית MySQL ואפליקציית FastAPI ל-OpenShift.

# === שלב טכני: וידוא שהסקריפט רץ מהתיקייה הנכונה ===
cd "$(dirname "$0")"

# --- NEW: Configuration ---
if [ -z "$1" ]; then
    echo "[ERROR] Docker Hub username must be provided as the first argument."
    echo "[USAGE] ./commands.sh <your-dockerhub-username>"
    exit 1
fi
DOCKERHUB_USERNAME="$1"
IMAGE_NAME="data-loader-service"
# יצירת תג ייחודי מ-hash של git או חותמת זמן
IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || date +%s)
FULL_IMAGE_NAME="docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
set -e # עצירה אוטומטית במקרה של שגיאה

# --- NEW: Step 1.5: Build and Push Docker Image ---
echo "[INFO] Building and pushing image: ${FULL_IMAGE_NAME}"
# הרצת הבנייה מתיקיית השורש של הפרויקט (..), שם נמצא ה-Dockerfile
(cd .. && docker buildx build --no-cache --platform linux/amd64,linux/arm64 -t "${FULL_IMAGE_NAME}" --push .)
echo "[SUCCESS] Image pushed successfully to Docker Hub."
echo ""

# --- שלב 1 לשעבר: אימות סביבת העבודה (משימה 1) ---
echo "[INFO] Using current OpenShift project: $(oc project -q)"
echo "[INFO] If this is not the correct project, press Ctrl+C to abort."
sleep 5 # השהייה של 5 שניות כדי לאפשר למשתמש לקרוא ולעצור במידת הצורך.

# --- שלב 2: פריסת מסד הנתונים MySQL (משימה 2) ---
echo "[INFO] Deploying MySQL Database..."
oc apply -f ../infrastructure/k8s/01-mysql-secret.yaml
oc apply -f ../infrastructure/k8s/02-mysql-pvc.yaml
oc apply -f ../infrastructure/k8s/03-mysql-deployment.yaml
oc apply -f ../infrastructure/k8s/04-mysql-service.yaml
echo "[INFO] Waiting for MySQL to be ready..."
oc wait --for=condition=ready pod -l app=mysql-db --timeout=300s
echo "[SUCCESS] MySQL is ready."
echo ""

# --- שלב 3: פריסת אפליקציית FastAPI (משימה 6) ---
echo "[INFO] Deploying FastAPI Backend..."
# UPDATED: שימוש ב-sed להחלפה דינמית של שם המשתמש והתג
sed -e "s|YOUR_DOCKERHUB_USERNAME|${DOCKERHUB_USERNAME}|g" \
    -e "s|:latest|:${IMAGE_TAG}|g" \
    "../infrastructure/k8s/05-fastapi-deployment.yaml" | oc apply -f -
oc apply -f ../infrastructure/k8s/06-fastapi-service.yaml
echo "[INFO] Waiting for FastAPI to be ready..."
oc wait --for=condition=ready pod -l app=mysql-api --timeout=300s
echo "[SUCCESS] FastAPI Backend is ready."
echo ""

# --- שלב 4: אתחול הנתונים במסד הנתונים (משימה 7) ---
echo "[INFO] Initializing data in MySQL..."
MYSQL_POD=$(oc get pod -l app=mysql-db -o jsonpath='{.items[0].metadata.name}')
echo "[INFO] Found MySQL pod: $MYSQL_POD"
echo "[INFO] Copying SQL scripts to the pod..."
oc cp ./create_data.sql "$MYSQL_POD":/tmp/create_data.sql
oc cp ./insert_data.sql "$MYSQL_POD":/tmp/insert_data.sql
echo "[INFO] Executing SQL scripts inside the pod..."
MYSQL_PASSWORD=$(oc get secret mysql-db-credentials -o jsonpath='{.data.MYSQL_ROOT_PASSWORD}' | base64 --decode)
oc exec "$MYSQL_POD" -- bash -c "mysql -u root -p'$MYSQL_PASSWORD' mydatabase < /tmp/create_data.sql"
oc exec "$MYSQL_POD" -- bash -c "mysql -u root -p'$MYSQL_PASSWORD' mydatabase < /tmp/insert_data.sql"
echo "[SUCCESS] Data initialized."
echo ""

# --- שלב 5: חשיפת השירות לעולם החיצון (משימה 8) ---
echo "[INFO] Exposing the FastAPI service..."
oc apply -f ../infrastructure/k8s/07-fastapi-route.yaml
echo "[SUCCESS] Route created."
echo ""

# --- שלב סופי: הצגת כתובת ה-URL של האפליקציה ---
echo "================================================================="
echo "            DEPLOYMENT COMPLETE"
echo "================================================================="
ROUTE_URL=$(oc get route mysql-api-route -o jsonpath='{.spec.host}')
echo "Your application is available at the following URL:"
echo "http://${ROUTE_URL}"
echo ""
echo "To fetch data, navigate to:"
echo "http://${ROUTE_URL}/data"
echo ""
echo "To view the interactive API documentation (Swagger UI), navigate to:"
echo "http://${ROUTE_URL}/docs"
echo "================================================================="