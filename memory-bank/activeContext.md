# Active Context: Vehicle Search API

## 1. Current Work Focus (as of 2025-07-10)

-   **Phase:** Feature Enhancement - Excel Inventory Upload.
-   **Activity:** Added new endpoints for uploading Excel inventory data to server memory.
-   **Objective:** Allow users to upload Excel files containing vehicle inventory stock data that will be stored in server memory (not in database) for future search operations.

## 2. Recent Changes & Decisions

-   **New Excel Upload Endpoints:** Added two new endpoints for inventory management:
    -   `POST /inventory/upload/` - Uploads Excel files with vehicle inventory data to server memory
    -   `GET /inventory/info/` - Returns information about currently loaded inventory data
-   **Excel Processing:** Implemented pandas-based Excel file processing with support for .xlsx and .xls formats
-   **Memory Storage:** Added global variables `inventory_data` and `inventory_upload_time` to store inventory data in server memory
-   **Dependencies:** Added `pandas` and `openpyxl` to requirements.txt for Excel processing
-   **Enhanced Logging:** Excel upload endpoint logs first 3 records for debugging and provides detailed statistics
-   **Previous Search Filters:** Added `tienda` and `vo_vn` as optional query parameters to the `GET /cars/` endpoint
-   **Response Enhancement:** The API response for a vehicle search includes `tienda` and `vo_vn` fields
-   **Data Parsing:** Implemented logic to parse the `workflow_estado` field from the database to extract store and vehicle condition

## 3. Next Steps (Immediate)

1.  **Future Search Endpoints:** User mentioned they will request specific endpoints to search vehicles from the memory-stored inventory data
2.  **Deployment:** The changes will need to be committed and pushed to trigger the GitHub Actions workflow for deployment
3.  **Testing:** After deployment, test the new Excel upload endpoints:
    -   `POST /inventory/upload/` with sample Excel file
    -   `GET /inventory/info/` to verify data loading

## 4. Active Considerations & Questions

-   **Memory vs Database:** The new inventory data is stored in server memory (not database) as requested. This data will be lost on server restart.
-   **Excel Schema Flexibility:** The upload endpoint accepts any Excel format but expects the headers provided by the user (Adid, Marca, Modelo, etc.)
-   **Future Search Implementation:** Will need to implement search endpoints that query the in-memory DataFrame instead of the database
-   **`workflow_estado` Parsing:** The logic to extract `tienda` and `vo_vn` assumes a specific space-delimited format (`Stock <TIENDA> <VO_VN>`)
-   **Schema Consistency:** The success of the stock update endpoint still relies on the `campos` in the payload matching the column names in the `vehicles_stock` table

## 5. Important Patterns & Preferences (Reinforced)

-   **Extend, Don't Break:** New features were added to the existing search endpoint without altering its core functionality for existing integrations.
-   **Clear Documentation:** All API changes are immediately reflected in the user-facing integration guide.
-   **Maintainable Logging:** Logs should be useful for debugging without being excessively large.
