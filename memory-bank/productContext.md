# Product Context: Database Synchronization Utility

## 1. Problem Statement

The user needs to perform frequent local queries on data that resides in an external database. Directly querying the external database multiple times a day for various local analyses can be inefficient, slow, or may put an unnecessary load on the source system. Furthermore, the user might not always have a stable or fast connection to the external database when they need to perform these local analyses.

## 2. Solution Overview

A Python utility will be developed to periodically extract data from a specific view in the external database and load it into a local SQLite database. This local database will serve as a readily accessible, fast-performing cache for the user's analytical queries.

## 3. How It Should Work

1.  **Configuration:** The user will configure the utility with connection details for the external database (e.g., type, host, port, username, password, database name) and the name of the specific view to be synchronized. The local SQLite database file path will also be configurable.
2.  **Execution:** The user will run the Python script.
3.  **Connection:** The script will connect to the external database.
4.  **Data Extraction:** It will query the specified view to fetch all relevant data.
5.  **Local Database Update:**
    *   If the local SQLite database or the target table doesn't exist, it will be created based on the schema of the fetched data.
    *   The script will then populate/update the local table with the data from the view. A common approach is to replace all existing data in the local table with the fresh data from the view (truncate-and-load), ensuring the local copy is a current snapshot. Other strategies (e.g., upsert) can be considered if partial updates are more appropriate and identifiable.
6.  **Completion:** The script will indicate successful completion or report any errors encountered.
7.  **Local Querying:** After synchronization, the user can connect to the local SQLite database using any SQLite-compatible tool to perform their queries quickly and efficiently.

## 4. User Experience Goals

-   **Simplicity:** The utility should be easy to configure and run.
-   **Reliability:** The synchronization process should be robust and handle common database connection or query issues gracefully.
-   **Speed (Local Queries):** The primary benefit is fast local querying once the data is synchronized. The synchronization process itself should be reasonably efficient.
-   **Transparency:** Clear feedback on the synchronization status (success, failure, number of records processed if feasible).
