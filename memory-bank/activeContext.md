# Active Context: Database Synchronization Utility

## 1. Current Work Focus (as of 2025-06-18 12:20)

-   **Phase:** Deployment - Vehicle Search API.
-   **Activity:** Troubleshooting and updating GitHub Actions workflow for CI/CD.
-   **Issue:** Workflow failed at ACR Login step due to missing `username` for `azure/docker-login@v1`.
-   **Fix:** Updated `.github/workflows/deploy-to-azure.yml` to use `fromJson(secrets.AZURE_CREDENTIALS).clientId` and `fromJson(secrets.AZURE_CREDENTIALS).clientSecret` for ACR login username and password.
-   **Azure Resources Created (Unchanged):**
    -   Resource Group: `concesur-rg`
    -   ACR: `concesurvehicleapicr`
    -   App Service Plan: `concesurvehicleapiplan`
    -   App Service: `concesur-vehicle-api`
    -   Service Principal: `GitHubActionsVehicleAPI`.
-   **GitHub Configuration (Unchanged):**
    -   Secrets configured.
    -   Workflow file `.github/workflows/deploy-to-azure.yml` updated.
-   **Objective:** User to commit and push updated workflow file. Monitor and verify deployment.

## 2. Recent Changes & Decisions

-   **New Project Initiated:** Vehicle Search API.
-   **Technology Stack for API:** FastAPI, Docker, Python, SQLAlchemy, Uvicorn.
-   **Authentication Method:** API Key (`X-API-Key` header).
-   **Configuration Management for API:** `.env` file for API key and database credentials (passed as environment variables to Docker).
-   **Database Schema Source:** Leveraged existing local SQLite DB to infer schema for `vehicles_stock` on Azure.
-   **Implemented `_inv` Field Fallback (2025-06-18):** Modified `vehicle_search_api/app/main.py` to use `marca_inv` and `modelo_inv` as primary sources, falling back to `marca` and `modelo` if the `_inv` versions are empty or null.

## 3. Next Steps (Immediate)

1.  **Update Memory Bank:**
    -   Update `activeContext.md` (this file) - Completed.
    -   Update `progress.md` to reflect the workflow update - In progress.
2.  **User Action: Commit and Push Updated Workflow:**
    -   User to commit changes to `.github/workflows/deploy-to-azure.yml` and push to `main`.
3.  **Monitor GitHub Action:**
    -   Observe the workflow run in the GitHub "Actions" tab.
    -   Troubleshoot any issues that arise during the build or deployment steps.
4.  **Verify Deployment:**
    -   Once the workflow succeeds, test the API at `https://concesur-vehicle-api.azurewebsites.net`.
    -   Check `/docs` for interactive API documentation.
    -   Perform test queries using the API key.
5.  **Finalize Documentation:**
    -   Update `progress.md` upon successful deployment and verification.

## 4. Active Considerations & Questions

-   **GitHub Actions Workflow:**
    -   Monitor the first run for any potential issues, especially with ACR authentication or Docker build context.
    -   Ensure the `Configure App Service Application Settings` step correctly applies all environment variables.
-   **Deployed Application:**
    -   Verify the API is responsive and connects to the database successfully.
    -   Check API key authentication.

## 5. Important Patterns & Preferences (for new API)

-   **Secure by Default:** API key authentication is a primary requirement.
-   **Environment-Driven Configuration:** Align with Docker best practices.
-   **Simplicity in Endpoint Design:** Focus on common, straightforward query parameters.
-   **Leverage Existing Infrastructure:** Use the already populated Azure MySQL database.
-   **Clear Documentation (Memory Bank):** Continue detailed updates.
