# Active Context: Vehicle Search API

## 1. Current Work Focus (as of 2025-07-03)

-   **Phase:** Feature Development - Vehicle Search API.
-   **Activity:** Creating a new endpoint to handle full updates of the vehicle stock.
-   **Objective:** Implement a secure `POST /stock/` endpoint that uses a "truncate-and-load" strategy to refresh the `vehicles_stock` table in the database.

## 2. Recent Changes & Decisions

-   **New Endpoint:** Added a `POST /stock/` endpoint to `vehicle_search_api/app/main.py`.
-   **Request Model:** Created a `StockPayload` Pydantic model to validate the incoming JSON data, which consists of `campos` (fields) and `datos` (rows).
-   **Transaction Management:** The entire database operation (DELETE followed by bulk INSERT) is wrapped in a transaction (`with engine.begin() as connection...`) to ensure atomicity. If any part fails, the transaction is automatically rolled back.
-   **Data Handling:** The incoming list of lists is converted into a list of dictionaries, which is then used for a bulk insert operation with SQLAlchemy Core for efficiency.
-   **Security:** The new endpoint is protected by the same `X-API-Key` header authentication as the existing `/cars/` search endpoint.

## 3. Next Steps (Immediate)

1.  **Update Memory Bank:**
    -   Update `activeContext.md` (this file) - **Completed**.
    -   Update `progress.md` to reflect the new endpoint implementation.
2.  **Deployment:** The changes will need to be committed and pushed to trigger the GitHub Actions workflow, which will deploy the updated application to Azure.
3.  **Testing:** After deployment, the new `/stock/` endpoint will require testing to ensure it functions correctly.

## 4. Active Considerations & Questions

-   **Schema Consistency:** The success of the endpoint relies on the `campos` in the payload matching the column names in the `vehicles_stock` table. The current implementation uses `autoload_with=engine` to reflect the table schema, which is robust.
-   **Performance:** For very large datasets, the "truncate-and-load" operation might take some time. The current bulk insert is efficient, but this is a point to monitor if the stock size grows significantly.

## 5. Important Patterns & Preferences (Reinforced)

-   **Transactional Integrity:** All database write operations should be atomic. The use of `engine.begin()` is the correct pattern.
-   **Secure by Default:** All new endpoints must be protected by the established API key mechanism.
-   **Efficient Data Operations:** Use bulk operations (like SQLAlchemy's bulk insert) instead of row-by-row operations for performance.
-   **Clear Documentation (Memory Bank):** Continue detailed updates for all new features.
