# Active Context: Vehicle Search API

## 1. Current Work Focus (as of 2025-07-04)

-   **Phase:** Feature Enhancement - Vehicle Search API.
-   **Activity:** Enhancing the `GET /cars/` endpoint with new search capabilities and improving logging.
-   **Objective:** Allow users to filter vehicles by store (`tienda`) and condition (`vo_vn`), and to provide this information in the response. Also, to limit verbose logging.

## 2. Recent Changes & Decisions

-   **New Search Filters:** Added `tienda` and `vo_vn` as optional query parameters to the `GET /cars/` endpoint.
-   **Response Enhancement:** The API response for a vehicle search now includes `tienda` and `vo_vn` fields.
-   **Data Parsing:** Implemented logic to parse the `workflow_estado` field from the database to extract the store and vehicle condition.
-   **Logging Improvement:** The raw payload logging for the `POST /stock/` endpoint is now limited to the first 10 records to avoid overly verbose logs.
-   **Documentation:** Updated the `vehicle_search_api_integration.md` guide to reflect the new search parameters and response fields.

## 3. Next Steps (Immediate)

1.  **Update Memory Bank:**
    -   Update `activeContext.md` (this file) - **Completed**.
    -   Update `progress.md` to reflect the new search features.
2.  **Deployment:** The changes will need to be committed and pushed to trigger the GitHub Actions workflow for deployment.
3.  **Testing:** After deployment, the new search filters (`tienda`, `vo_vn`) need to be thoroughly tested.

## 4. Active Considerations & Questions

-   **`workflow_estado` Parsing:** The logic to extract `tienda` and `vo_vn` assumes a specific space-delimited format (`Stock <TIENDA> <VO_VN>`). This is a potential point of failure if the source data format changes. This dependency should be noted.
-   **Schema Consistency:** The success of the stock update endpoint still relies on the `campos` in the payload matching the column names in the `vehicles_stock` table.

## 5. Important Patterns & Preferences (Reinforced)

-   **Extend, Don't Break:** New features were added to the existing search endpoint without altering its core functionality for existing integrations.
-   **Clear Documentation:** All API changes are immediately reflected in the user-facing integration guide.
-   **Maintainable Logging:** Logs should be useful for debugging without being excessively large.
