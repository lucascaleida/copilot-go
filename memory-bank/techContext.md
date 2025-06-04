# Tech Context: Database Synchronization Utility

## 1. Core Technologies

-   **Programming Language:** Python (version 3.7+ recommended).
-   **Command-Line Interface:** `argparse` module (Python standard library) for handling runtime arguments (e.g., target selection).
-   **Data Sources:**
    -   Primary: MySQL (external, self-hosted or cloud).
    -   Fallback: SQLite3 (local file-based).
-   **Data Targets:**
    -   SQLite3 (local file-based).
    -   Azure MySQL (cloud-hosted MySQL, requires SSL).
-   **Database Interaction:**
    -   `pandas` for reading from SQL and writing to SQL.
    -   `SQLAlchemy` as an abstraction layer used by pandas and for engine creation.
    -   `mysql-connector-python` as the specific connector for all MySQL communications (source and Azure target).

## 2. Development Setup

-   Python environment (e.g., venv, conda).
-   Installation of Python packages via `pip` from `requirements.txt`.
-   IDE or text editor.
-   Access to the primary external MySQL database and the target Azure MySQL database for testing.
-   SQLite client for inspecting the local database.

## 3. Technical Constraints & Considerations

-   **Database Credentials:** Secure handling remains crucial. `config.ini` stores them; consider environment variables for production.
-   **Azure MySQL Connectivity:**
    -   Requires SSL. `ssl_mode` is configured in `config.ini` (e.g., 'require').
    -   If Azure's default CA is not sufficient or if client certificates are used, `ssl_ca`, `ssl_cert`, `ssl_key` might be needed in `config.ini`.
    -   The database specified in `[azure_mysql_db]` (e.g., `vehicles_db`) must exist, or the user must have permissions to create it. The script handles table creation/replacement.
-   **Network Reliability:**
    -   The script now has a fallback mechanism: if the primary external MySQL source is unreachable, it can use the local SQLite DB as a source.
    -   Stable connection to the chosen *target* (SQLite or Azure MySQL) is still required during the write phase.
-   **Data Volume:** "Truncate-and-load" performance considerations remain for very large datasets.
-   **Schema Changes:** The script assumes the source schema (from primary external DB or fallback SQLite) is consistent for the target table.
-   **Python Version:** Compatibility with Python 3.7+ is targeted.

## 4. Key Dependencies (`requirements.txt`)

```
# Core data handling
pandas

# SQLAlchemy is used by pandas.to_sql for many database types and for engine creation
sqlalchemy

# MySQL connector for both primary source and Azure MySQL target
mysql-connector-python
```
(`argparse` is part of the Python standard library and does not need to be listed in `requirements.txt`.)

## 5. Tool Usage Patterns

-   **Configuration File (`config.ini`):**
    -   Centralized storage for all database connection strings (primary source, local SQLite, Azure MySQL).
    -   Stores source query, table names, SSL parameters for Azure.
    -   Contains general operational settings: `default_target`, `target_argument_enabled`, `fallback_to_local_source_on_failure`.
    -   Read using Python's `configparser` module.
-   **Command-Line Arguments:**
    -   `argparse` module used to process arguments like `--target` to override the default target database.
-   **Logging:** Python's built-in `logging` module configured for detailed operational feedback to console (and potentially a file, though not explicitly configured in script yet).
-   **Custom Exceptions:** `SourceConnectionError` used to manage control flow for source fallback.
