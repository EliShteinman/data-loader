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

## Deployment to OpenShift (Automated)

This project is designed to be deployed end-to-end with a single script.

### Prerequisites

1.  Access to an OpenShift cluster.
2.  The `oc` (OpenShift CLI) command-line tool installed and authenticated.
3.  A Docker Hub account.
4.  Docker Desktop (or Docker daemon) installed, running, and authenticated (`docker login`).

### Deployment Steps

1.  **Select Your OpenShift Project:**
    Ensure you are in the correct OpenShift project where you want to deploy the resources.
    ```bash
    # Replace <your-project-name> with your actual project
    oc project <your-project-name>
    ```

2.  **Run the Deployment Script:**
    The script automates everything: building and pushing the image, creating secrets, storage, deployments, services, and initializing the database.

    *   **On macOS or Linux:**
        Navigate to the project's root directory.
        ```bash
        # First, make the script executable
        chmod +x scripts/commands.sh
        
        # Run the script, providing your Docker Hub username as an argument
        ./scripts/commands.sh your-dockerhub-username
        ```
    *   **On Windows:**
        Navigate to the project's root directory.
        ```batch
        REM Run the script, providing your Docker Hub username as an argument
        .\scripts\commands.bat your-dockerhub-username
        ```

3.  **Access the Application:**
    The script will print the final application URL upon completion. To see the data, append `/data` to the URL, or `/docs` for the interactive API documentation.
    
    Example: `http://mysql-api-route-my-project.example.com/data`

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