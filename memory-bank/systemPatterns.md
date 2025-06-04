# System Patterns: Database Synchronization Utility

## 1. System Architecture Overview

The system is a Python script performing an Extract, Load (EL) process. It supports multiple sources (primary external, fallback local) and multiple targets (local SQLite, Azure MySQL), configurable via a file and command-line arguments.

```mermaid
graph LR
    subgraph Sources
        A[Primary External DB View (MySQL)]
        C[Local SQLite DB (as Fallback Source)]
    end

    subgraph Targets
        E[Local SQLite DB (as Target)]
        F[Azure MySQL DB (as Target)]
    end

    B(Python Script);
    D[User];
    G[config.ini];
    H[CLI Arguments --target];

    D -- Runs --> B;
    H -- Influences --> B;
    G -- Configures --> B;

    A -- Read via Python DB Connector --> B;
    B -- Optionally Reads if A fails --> C;
    
    B -- Write via SQLite3/MySQL Connector --> E;
    B -- Write via MySQL Connector (SSL) --> F;

    D -- Queries --> E;
    D -- Queries --> F;
```

## 2. Key Technical Decisions

-   **Language:** Python 3.x.
-   **Data Sources:**
    -   Primary: External MySQL database (configurable).
    -   Fallback: Local SQLite database (configurable, used if primary source fails).
-   **Data Targets:**
    -   Local SQLite database.
    -   Azure MySQL database (configurable, includes SSL connection).
-   **Default Target:** Azure MySQL, configurable in `config.ini`.
-   **Target Selection:** Can be overridden via command-line argument (`--target`).
-   **External Database Connectivity:** `SQLAlchemy` and `mysql-connector-python` for MySQL connections. `sqlite3` (via SQLAlchemy/Pandas) for SQLite.
-   **Configuration Management:** `config.ini` file for all connection parameters, source query, target details, SSL settings, and operational flags (e.g., fallback enabling, default target).
-   **Data Handling:** Pandas DataFrames for internal data manipulation.
-   **SSL for Azure:** `ssl_mode` (e.g., 'require') configured for Azure MySQL connections.

## 3. Design Patterns

-   **Configuration-Driven:** Script behavior heavily driven by `config.ini`.
-   **Command-Line Overrides:** Specific configurations (like target DB) can be overridden at runtime.
-   **Modular Design:**
    -   Separate functions for:
        -   Configuration loading.
        -   Fetching from primary external DB.
        -   Fetching from fallback SQLite DB.
        -   Writing to local SQLite DB.
        -   Writing to Azure MySQL DB.
    -   Main orchestrator function manages the workflow, including source selection, fallback, and target dispatch.
-   **Error Handling:**
    -   Try-except blocks for database operations, file I/O.
    -   Custom `SourceConnectionError` to manage fallback logic.
    -   Comprehensive logging via Python's `logging` module.
-   **Fallback Mechanism:** If the primary data source is unavailable, the script can use a local SQLite database as an alternative source.
-   **Idempotency:** The "truncate-and-load" strategy for writing to targets ensures idempotency.

## 4. Data Synchronization Strategy

-   **Primary Strategy: Truncate-and-Load:**
    -   Applies to both local SQLite and Azure MySQL targets.
    -   Ensures the target table is an exact replica of the (chosen) source data at the time of sync.
    -   **Process:**
        1.  Fetch all data from the determined source (primary or fallback).
        2.  If the target table exists, it's effectively replaced with new data (Pandas `to_sql` with `if_exists='replace'` handles dropping/recreating or deleting rows and inserting).
        3.  Insert all fetched data into the target table.
-   **Alternative (Future Consideration): Upsert (Update or Insert):**
    -   Remains a future consideration if performance with truncate-and-load becomes an issue for very large datasets with minimal changes.

## 5. Logging and Feedback

-   Use Python's `logging` module.
-   Log key steps: script start/end, configuration loading, connection attempts (source/target), data fetching (source, number of rows), data loading (target, number of rows), fallback activation, errors encountered.
-   Provide clear messages to the console.
