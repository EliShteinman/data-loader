# FastAPI MySQL Data Loader for OpenShift

## Overview

This project is a complete solution developed for an OpenShift exam. It consists of a FastAPI-based microservice designed to fetch all records from a single table named `data` in a MySQL database. The entire infrastructure, including the MySQL database and the FastAPI application, is deployed and managed on OpenShift using declarative YAML manifests and automated scripts.

The project adheres to principles of clean architecture by separating the Data Access Layer (DAL) from the API server, and follows security best practices by managing database credentials via OpenShift Secrets.

## Core Technologies

*   **Backend**: Python 3.11 with FastAPI
*   **Database**: MySQL 8.0
*   **Containerization**: Docker
*   **Orchestration**: OpenShift (Kubernetes)
*   **Database Driver**: `mysql-connector-python`

## Project Structure

The project follows a structured layout as required by the assignment:

```
data-loader/
├── infrastructure/
│   └── k8s/                   # All OpenShift/Kubernetes YAML manifests
│       ├── 01-mysql-secret.yaml
│       ├── 02-mysql-pvc.yaml
│       ├── 03-mysql-deployment.yaml
│       ├── 04-mysql-service.yaml
│       ├── 05-fastapi-deployment.yaml
│       ├── 06-fastapi-service.yaml
│       └── 07-fastapi-route.yaml
├── scripts/
│   ├── commands.sh            # Deployment script for macOS/Linux
│   ├── commands.bat           # Deployment script for Windows
│   ├── create_data.sql        # SQL script to create the 'data' table
│   └── insert_data.sql        # SQL script to insert sample data
├── services/
│   └── data_loader/
│       ├── data_loader.py     # The Data Access Layer (DAL) class
│       └── main.py            # The main FastAPI application
├── .gitignore
├── Dockerfile                 # Docker instructions for the FastAPI app
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation file
```

## Deployment to OpenShift (Primary Method)

This project is designed to be deployed end-to-end using the provided script.

### Prerequisites

1.  Access to an OpenShift cluster.
2.  The `oc` (OpenShift CLI) command-line tool installed and configured.
3.  A Docker Hub account.
4.  Docker Desktop (or Docker daemon) installed and running locally.

### Step-by-Step Instructions

1.  **Login to OpenShift CLI:**
    Open your terminal and log in to your OpenShift cluster.
    ```bash
    oc login --token=<your-token> --server=<your-server-url>
    ```

2.  **Select Your Project:**
    Choose the project (namespace) you want to deploy into. All resources will be created here.
    ```bash
    # Replace <your-project-name> with your actual project, e.g., a0533-dev
    oc project <your-project-name>
    ```

3.  **Login to Docker Hub:**
    Log in to your Docker Hub account to enable pushing the application image.
    ```bash
    docker login
    ```

4.  **Build and Push the Docker Image:**
    Navigate to the project's root directory (`data-loader`). Build the Docker image and push it to your Docker Hub repository.
    **Important:** Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username.
    ```bash
    # Build the image
    docker build -t YOUR_DOCKERHUB_USERNAME/data-loader-service:latest .

    # Push the image
    docker push YOUR_DOCKERHUB_USERNAME/data-loader-service:latest
    ```
    You also need to update the image path in `infrastructure/k8s/05-fastapi-deployment.yaml` to match the image you just pushed.

5.  **Run the Deployment Script:**
    The provided script automates the entire process of creating secrets, storage, deployments, services, and initializing the database.

    *   **On macOS or Linux:**
        ```bash
        # First, make the script executable (only needs to be done once)
        chmod +x scripts/commands.sh
        
        # Run the script from the project root directory
        ./scripts/commands.sh
        ```
    *   **On Windows:**
        ```bash
        # Run the script from the scripts directory
        cd scripts
        commands.bat
        ```

6.  **Verify the Deployment:**
    After the script finishes, it will instruct you to find your application's public URL.
    ```bash
    oc get route fastapi-route
    ```
    Copy the URL from the `HOST/PORT` column and paste it into your browser. To see the data, append `/data` to the URL.

    Example: `http://fastapi-route-my-project.example.com/data`

## Key Components Explained

#### `services/data_loader/`
*   **`data_loader.py`**: Contains the `DataLoader` class, which acts as the Data Access Layer (DAL). It is solely responsible for all database interactions: connecting, fetching data, and handling MySQL-specific errors.
*   **`main.py`**: The FastAPI application. It reads database credentials from environment variables (provided by OpenShift Secrets), initializes the `DataLoader`, and exposes a `/data` endpoint.

#### `infrastructure/k8s/`
This directory contains all the declarative manifests for OpenShift:
*   `01-mysql-secret.yaml`: Securely stores MySQL credentials.
*   `02-mysql-pvc.yaml`: Requests 1Gi of persistent storage for the database to ensure data survives pod restarts.
*   `03-mysql-deployment.yaml`: Defines how to run the MySQL container, connecting it to the secret and the persistent volume.
*   `04-mysql-service.yaml`: Creates a stable internal network endpoint (`mysql-service`) for the FastAPI app to connect to.
*   `05-fastapi-deployment.yaml`: Defines how to run the FastAPI application container, using the image from Docker Hub and injecting database credentials as environment variables.
*   `06-fastapi-service.yaml`: Creates a stable internal network endpoint for the FastAPI application.
*   `07-fastapi-route.yaml`: Exposes the FastAPI service to the public internet with a URL.

#### `scripts/`
*   **`commands.sh` / `commands.bat`**: Automation scripts that execute all necessary `oc` commands in the correct order to deploy the entire stack.
*   **`create_data.sql` & `insert_data.sql`**: SQL scripts used by the deployment script to initialize the database table and populate it with sample data.

---