# FastAPI MySQL Data Loader for OpenShift

## Overview

This project provides a robust, production-ready template for deploying a Python FastAPI application with a MySQL backend on OpenShift. The entire infrastructure is defined using declarative Kubernetes manifests and can be deployed automatically with a single script.

The architecture emphasizes best practices, including:
- **Separation of Concerns:** A dedicated Data Access Layer (DAL) in Python.
- **Configuration Management:** Clear separation between configuration (`ConfigMap`) and secrets (`Secret`).
- **Reliability:** Health and readiness probes for service monitoring.
- **Performance:** Use of a database connection pool.
- **Automation:** Cross-platform deployment scripts for both Linux/macOS and Windows.

---

## Core Technologies

*   **Backend**: Python 3.11 with FastAPI
*   **Database**: MySQL 8.0
*   **Containerization**: Docker
*   **Orchestration**: OpenShift / Kubernetes
*   **Database Driver**: `mysql-connector-python`

---

## Project Structure

```
.
├── infrastructure/
│   └── k8s/                # All Kubernetes/OpenShift YAML manifests
├── scripts/
│   ├── commands.sh         # Automated deployment script for Linux/macOS
│   ├── commands.bat        # Automated deployment script for Windows
│   └── ...                 # SQL initialization scripts
├── services/
│   └── data_loader/
│       ├── data_loader.py  # Data Access Layer (DAL) with Connection Pooling
│       └── main.py         # Main FastAPI application
├── Dockerfile              # Production-ready Dockerfile for the FastAPI app
├── demo_guide.md           # Step-by-step manual deployment guide (Hebrew)
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

---

## Automated Deployment

The project can be deployed end-to-end using the provided automation scripts.

### Prerequisites

1.  Access to an OpenShift cluster.
2.  The `oc` (OpenShift CLI) command-line tool installed and authenticated.
3.  A Docker Hub account and `docker login` executed.
4.  Docker Desktop (or Docker daemon) installed and running.

### Instructions

1.  **Clone the repository** and navigate to the project root.
2.  **Choose your script** (`scripts/commands.sh` for Linux/macOS, `scripts/commands.bat` for Windows).
3.  **Run the script**, providing your Docker Hub username as the first argument.

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

The script will build and push the Docker image, apply all Kubernetes manifests, initialize the database, and print the final application URL.

---

## Manual Deployment Guide

For a detailed, step-by-step guide with explanations for each command (ideal for presentations or learning), please refer to the manual deployment guide.

**➡️ [Click here to view the Manual Deployment Guide (demo_guide.md)](./demo_guide.md)**

This guide provides separate commands for Linux/macOS and Windows where applicable.