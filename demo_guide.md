# מדריך פריסה חיה: אפליקציית FastAPI ו-MySQL ל-OpenShift

מדריך זה מציג פריסה מלאה של אפליקציה ותשתית ל-OpenShift, שלב אחר שלב.
הוא מדגים שתי שיטות עיקריות:
1.  **דקלרטיבית (עם קבצי YAML):** השיטה המומלצת לפרודקשן (Infrastructure as Code).
2.  **אימפרטיבית (עם פקודות CLI ישירות):** לשימוש מהיר ולפיתוח.

---

## שלב 0: הכנות

ודא שהכלים הבאים מותקנים ומוכנים לשימוש:
*   `oc` (OpenShift CLI)
*   `docker`
*   `git`

#### 1. התחברות ל-OpenShift
```bash
# (בצע לפני ההדגמה)
oc login --token=<your-token> --server=<your-server-url>
```

#### 2. יצירת פרויקט חדש
```bash
oc new-project my-live-demo
```

#### 3. התחברות ל-Docker Hub
```bash
# (בצע לפני ההדגמה)
docker login
```

#### 4. הגדרת משתנים
**!!! חשוב:** בצע שלב זה בטרמינל שבו תריץ את שאר הפקודות.

<details>
<summary>💻 <strong>עבור Linux / macOS</strong></summary>

```bash
# !!! החלף את 'your-dockerhub-username' בשם המשתמש שלך ב-Docker Hub !!!
export DOCKERHUB_USERNAME='your-dockerhub-username'
```

</details>

<details>
<summary>🪟 <strong>עבור Windows (CMD)</strong></summary>

```batch
@REM !!! החלף את 'your-dockerhub-username' בשם המשתמש שלך ב-Docker Hub !!!
set "DOCKERHUB_USERNAME=your-dockerhub-username"
```
</details>

---

## שלב 1: בניית והעלאת Docker Image

ניצור תג ייחודי ונבנה את האימג' של האפליקציה. לאחר מכן, נעלה אותו ל-Docker Hub.

<details>
<summary>💻 <strong>עבור Linux / macOS</strong></summary>

```bash
# יצירת תג ייחודי להדגמה
export IMAGE_TAG=manual-demo-$(date +%s)

# בנייה והעלאה
echo "Building and pushing image: ${DOCKERHUB_USERNAME}/data-loader-service:${IMAGE_TAG}"
docker buildx build --platform linux/amd64,linux/arm64 --no-cache -t ${DOCKERHUB_USERNAME}/data-loader-service:${IMAGE_TAG} --push ..
```

</details>

<details>
<summary>🪟 <strong>עבור Windows (CMD)</strong></summary>

```batch
@REM יצירת תג ייחודי להדגמה
FOR /F "tokens=*" %%g IN ('powershell -Command "Get-Date -UFormat +%%s"') DO SET "IMAGE_TAG=manual-demo-%%g"

@REM בנייה והעלאה
echo "Building and pushing image: %DOCKERHUB_USERNAME%/data-loader-service:%IMAGE_TAG%"
docker buildx build --platform linux/amd64,linux/arm64 --no-cache -t "%DOCKERHUB_USERNAME%/data-loader-service:%IMAGE_TAG%" --push ..
```
</details>

---

## שיטה א': הדרך המומלצת (דקלרטיבית עם YAML)

שיטה זו משתמשת בקבצי תצורה (מניפסטים) כדי להגדיר את המצב הרצוי של המערכת.

### שלב 2: יצירת תצורה, סודות ואחסון

כפרקטיקה מומלצת, אנו מפרידים בין תצורה כללית (ב-`ConfigMap`) לבין מידע רגיש (ב-`Secret`). בנוסף, אנו מבקשים נפח אחסון קבוע (PVC) עבור מסד הנתונים.

```bash
oc apply -f infrastructure/k8s/00-mysql-configmap.yaml
oc apply -f infrastructure/k8s/01-mysql-secret.yaml
oc apply -f infrastructure/k8s/02-mysql-pvc.yaml
echo "--- ConfigMap, Secret and PVC created."
oc get configmap,secret,pvc
```

### שלב 3: פריסת MySQL

נפרוס את מסד הנתונים באמצעות `Deployment` ו-`Service`.

```bash
oc apply -f infrastructure/k8s/03-mysql-deployment.yaml
oc apply -f infrastructure/k8s/04-mysql-service.yaml
echo "--- Waiting for MySQL pod to become ready..."
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=mysql-db --timeout=300s
echo "--- MySQL pod is ready. Allowing time for internal database initialization..."
sleep 15 # ב-Windows, השתמש ב-timeout /t 15 >nul
echo "--- MySQL is fully initialized!"
```

### שלב 4: פריסת FastAPI

נפרוס את שירות ה-API. הפקודה הבאה משתמשת בכלי מתאים למערכת ההפעלה כדי להחליף את שם המשתמש והתג ב-YAML באופן דינמי.

<details>
<summary>💻 <strong>עבור Linux / macOS (עם sed)</strong></summary>

```bash
sed -e "s|YOUR_DOCKERHUB_USERNAME|${DOCKERHUB_USERNAME}|g" \
    -e "s|:latest|:${IMAGE_TAG}|g" \
    "infrastructure/k8s/05-fastapi-deployment.yaml" | oc apply -f -
```

</details>

<details>
<summary>🪟 <strong>עבור Windows (עם PowerShell)</strong></summary>

```batch
powershell -Command "(Get-Content -Raw infrastructure\k8s\05-fastapi-deployment.yaml).Replace('YOUR_DOCKERHUB_USERNAME', '%DOCKERHUB_USERNAME%').Replace(':latest', ':%IMAGE_TAG%') | oc apply -f -"
```
</details>

```bash
# המשך פריסת ה-API
oc apply -f infrastructure/k8s/06-fastapi-service.yaml
echo "--- Waiting for FastAPI to be ready..."
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=mysql-api --timeout=300s
echo "--- FastAPI is ready!"
```

### שלב 5: חשיפת האפליקציה (Route)

```bash
oc apply -f infrastructure/k8s/07-fastapi-route.yaml
echo "--- Route created."
```

---

## המשך התהליך (זהה לשתי השיטות)

### שלב 6: אתחול הנתונים ב-DB

#### א. מציאת ה-Pod והסיסמה

<details>
<summary>💻 <strong>עבור Linux / macOS</strong></summary>

```bash
MYSQL_POD=$(oc get pod -l app.kubernetes.io/instance=mysql-db -o jsonpath='{.items[0].metadata.name}')
MYSQL_PASSWORD=$(oc get secret mysql-db-credentials -o jsonpath='{.data.MYSQL_ROOT_PASSWORD}' | base64 --decode)
echo "Found MySQL Pod: $MYSQL_POD"
```

</details>

<details>
<summary>🪟 <strong>עבור Windows (CMD)</strong></summary>

```batch
FOR /F "tokens=*" %%g IN ('oc get pod -l app.kubernetes.io/instance=mysql-db -o jsonpath="{.items[0].metadata.name}"') DO SET "MYSQL_POD=%%g"
FOR /F "tokens=*" %%g IN ('oc get secret mysql-db-credentials -o jsonpath="{.data.MYSQL_ROOT_PASSWORD}"') DO SET "B64_PASSWORD=%%g"
FOR /F "usebackq tokens=*" %%h IN (`powershell -NoProfile -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%B64_PASSWORD%'))"`) DO SET "MYSQL_PASSWORD=%%h"
echo Found MySQL Pod: %MYSQL_POD%
```
</details>

#### ב. אתחול הנתונים (שיטה א': הזרמה ישירה)

<details>
<summary>💻 <strong>עבור Linux / macOS</strong></summary>

```bash
echo "Running initialization using Method A (Streaming)..."
oc exec -i "$MYSQL_POD" -- mysql -u root -p"$MYSQL_PASSWORD" mydatabase < scripts/create_data.sql
oc exec -i "$MYSQL_POD" -- mysql -u root -p"$MYSQL_PASSWORD" mydatabase < scripts/insert_data.sql
echo "Database initialized successfully using Method A!"
```
</details>

<details>
<summary>🪟 <strong>עבור Windows (CMD)</strong></summary>

```batch
echo Running initialization using Method A (Streaming)...
oc exec -i "%MYSQL_POD%" -- mysql -u root -p"%MYSQL_PASSWORD%" mydatabase < scripts\create_data.sql
oc exec -i "%MYSQL_POD%" -- mysql -u root -p"%MYSQL_PASSWORD%" mydatabase < scripts\insert_data.sql
echo Database initialized successfully using Method A!
```
</details>

---

### שלב 7: מציאת הכתובת ובדיקה

<details>
<summary>💻 <strong>עבור Linux / macOS</strong></summary>

```bash
ROUTE_URL=$(oc get route mysql-api-route -o jsonpath='{.spec.host}')
echo "======================================================"
echo "Application URL: https://${ROUTE_URL}"
echo "Data Endpoint:   https://${ROUTE_URL}/data"
echo "API Docs:        https://${ROUTE_URL}/docs"
echo "======================================================"
```
</details>

<details>
<summary>🪟 <strong>עבור Windows (CMD)</strong></summary>

```batch
FOR /F "tokens=*" %%g IN ('oc get route mysql-api-route -o jsonpath="{.spec.host}"') DO SET "ROUTE_URL=%%g"
echo ======================================================
echo Application URL: https://%ROUTE_URL%
echo Data Endpoint:   https://%ROUTE_URL%/data
echo API Docs:        https://%ROUTE_URL%/docs
echo ======================================================
```
</details>

---

## שלב 8: ניקוי הסביבה

### אפשרות א': מחיקה סלקטיבית באמצעות תוויות (מומלץ)
מכיוון שסימנו את כל הרכיבים שלנו עם התווית `app.kubernetes.io/part-of=data-loader-app`, אנו יכולים למחוק אותם באופן ממוקד.

```bash
# פקודה זו מוחקת את כל הרכיבים העיקריים (Deployments, Services, Routes, וכו')
oc delete all --selector=app.kubernetes.io/part-of=data-loader-app

# פקודה זו מוחקת את שאר הרכיבים שהפקודה 'all' לא תופסת
oc delete pvc,secret,configmap --selector=app.kubernetes.io/part-of=data-loader-app
```

### אפשרות ב': מחיקת הפרויקט כולו
**אזהרה:** פעולה זו תמחק את כל מה שנמצא בפרויקט `my-live-demo`.

```bash
oc delete project my-live-demo
```