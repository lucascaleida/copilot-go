# Project Brief: Database Synchronization Utility

## 1. Core Requirements

The primary goal of this project is to develop a Python utility that synchronizes data from a specific view in an external database to a local SQLite database. This utility will be executed multiple times daily to ensure the local database remains up-to-date.

## 2. Key Objectives

- **Data Extraction:** Implement functionality to connect to an external database and read data from a specified view.
- **Local Storage:** Create and manage a local SQLite database to store the extracted data.
- **Data Synchronization:** Develop a process to update the local SQLite database with the latest data from the external database view. This includes handling new, updated, and potentially deleted records (strategy to be defined).
- **Automation/Execution:** The script should be designed for frequent, potentially automated, execution.
- **Language:** Python will be the primary programming language.

## 3. Scope

- **In Scope:**
    - Python script for data extraction and loading.
    - SQLite database creation and schema management (based on the source view).
    - Configuration for connecting to the external database (credentials, connection strings, view name).
    - Basic error handling and logging.
- **Out of Scope (initially, unless specified later):**
    - A sophisticated GUI for the utility.
    - Complex data transformation beyond what's necessary for storage.
    - Real-time synchronization (the current requirement is for periodic batch updates).
    - Scheduling mechanism for the script (the user will run it manually or set up their own scheduler).

## 4. Success Criteria

- The utility successfully connects to the source database and reads the specified view.
- The utility creates/updates the local SQLite database with the data from the view.
- The synchronization process is repeatable and reliable.
- The local SQLite database accurately reflects the data from the source view after synchronization.

## 5. Additional Project: Vehicle Search API (New as of 2025-06-04)

### 5.1. Core Requirement

Develop a FastAPI application, containerized with Docker, to expose an API endpoint for searching vehicle data stored in the Azure MySQL database (`vehicles_db`, `vehicles_stock` table). This API will be secured with an API key.

### 5.2. Key Objectives

-   **API Endpoint:** Create an endpoint (e.g., `/cars/`) that allows querying vehicles based on common criteria like make, model, color, year, etc.
-   **Database Connectivity:** Connect to the Azure MySQL database to fetch data.
-   **API Key Authentication:** Secure the endpoint using a provided API key.
-   **Dockerization:** Package the FastAPI application into a Docker container for deployment.
-   **Technology:** Use FastAPI, Python, Docker.
-   **Data Source:** The `vehicles_stock` table in the `vehicles_db` Azure MySQL database.

### 5.3. Scope

-   **In Scope:**
    -   FastAPI application development.
    -   Dockerfile creation.
    -   API endpoint for searching vehicles with basic parameters.
    -   API key authentication mechanism.
    -   Connection to Azure MySQL.
    -   `.env` file for API key and potentially database credentials.
-   **Out of Scope (initially):**
    -   Complex search functionalities beyond typical parameters.
    -   User interface for the API.
    -   Deployment orchestration beyond Docker.

### 5.4. Success Criteria

-   The FastAPI application runs successfully in a Docker container.
-   The `/cars/` endpoint is accessible and returns vehicle data based on query parameters.
-   The endpoint is protected by the specified API key.
-   The API correctly queries the Azure MySQL database.
