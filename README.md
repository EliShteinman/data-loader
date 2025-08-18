# FastAPI MySQL Data Loader for OpenShift

## Overview

This project provides a robust, production-ready template for deploying a Python FastAPI application with a MySQL backend on OpenShift. Originating as an exam assignment to fetch data via a `GET` request, this project has been significantly expanded to showcase a complete, best-practice architecture for building and deploying cloud-native microservices.

The entire infrastructure is defined using declarative Kubernetes manifests and can be deployed automatically with a single script for both Linux/macOS and Windows.

### Features & Best Practices Implemented

-   **Full CRUD API:** The API was extended from a single `GET` endpoint to full Create, Read, Update, and Delete functionality.
-   **Modular API Architecture:** Uses FastAPI's `APIRouter` to keep API logic clean, organized, and scalable.
-   **High-Performance DAL:** Implements a MySQL **Connection Pool** in the Data Access Layer (DAL) to handle concurrent requests efficiently.
-   **Declarative Infrastructure (IaC):** All OpenShift/Kubernetes resources are defined in standardized YAML manifests.
-   **Advanced Configuration Management:** Clear separation between non-sensitive configuration (`ConfigMap`) and secrets (`Secret`).
-   **Reliability & Health Monitoring:** Includes **liveness and readiness probes** for both the API and the database to ensure service stability and automated recovery.
-   **Resource Management:** Defines CPU and memory `requests` and `limits` to guarantee performance and prevent resource starvation in a shared environment.
-   **Full Automation:** Provides cross-platform deployment scripts (`.sh` and `.bat`) for a complete, one-command setup.

---

## Core Technologies

*   **Backend**: Python 3.11 with FastAPI & Pydantic
*   **Database**: MySQL 8.0
*   **Containerization**: Docker
*   **Orchestration**: OpenShift / Kubernetes
*   **Database Driver**: `mysql-connector-python`

---

## Project Structure & Documentation

The project is organized into distinct directories, each with its own detailed documentation.

```
.
├── infrastructure/
│   └── k8s/
│       ├── README.md       # (Hebrew) In-depth explanation of all YAML manifests
│       └── ...             # All Kubernetes/OpenShift YAML manifests
├── scripts/
│   ├── commands.sh         # Automated deployment script for Linux/macOS
│   └── commands.bat        # Automated deployment script for Windows
├── services/
│   └── data_loader/
│       ├── routers/        # FastAPI APIRouter for CRUD operations
│       ├── README.md       # (Hebrew) In-depth explanation of the Python code architecture
│       ├── data_loader.py  # Data Access Layer (DAL) with Connection Pooling
│       ├── main.py         # Main FastAPI application entrypoint
│       └── models.py       # Pydantic data models
├── Dockerfile              # Dockerfile for the FastAPI app
├── demo_guide.md           # Step-by-step manual deployment guide (Hebrew)
└── README.md               # This file
```

### In-Depth Documentation

*   **[Python Code Architecture](./services/data_loader/README.md):** A detailed, educational walkthrough of the Python application's structure, from a basic implementation to the final production-ready design. (Hebrew)
*   **[Kubernetes Manifests Explained](./infrastructure/k8s/README.md):** A breakdown of each YAML file, explaining its role in the overall infrastructure. (Hebrew)

---

## Automated Deployment

For a quick setup, use the provided automation scripts.

### Prerequisites

1.  Access to an OpenShift cluster and the `oc` CLI.
2.  A Docker Hub account (`docker login` executed).
3.  Docker Desktop (or Docker daemon) running.

### Instructions

Run the appropriate script from the `scripts/` directory, providing your Docker Hub username as the first argument.

#### For Linux / macOS
```bash
# Make the script executable
chmod +x scripts/commands.sh

# Run the deployment
./scripts/commands.sh your-dockerhub-username
```

#### For Windows
```batch
.\scripts\commands.bat your-dockerhub-username
```
The script will build the image, deploy all resources, initialize the database, and print the final application URL.

---

## Manual & Educational Deployment Guide

For a detailed, step-by-step guide with explanations for each command, ideal for presentations or learning, please refer to the manual deployment guide.

**➡️ [Click here to view the Manual Deployment Guide (demo_guide.md)](./demo_guide.md)**

This guide is in Hebrew and provides separate commands for different operating systems.

---