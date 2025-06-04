# Tech Context: Database Synchronization Utility

## 1. Core Technologies

-   **Programming Language:** Python (version 3.7+ recommended for broader library support and f-strings, etc.).
-   **Local Database:** SQLite3.
-   **External Database Interface:**
    -   Standard Python DB API 2.0 compliant libraries.
    -   `pandas` for reading from SQL and writing to SQL (uses SQLAlchemy or specific connectors under the hood).
    -   `SQLAlchemy Core` (optional, for more generic SQL dialect handling if needed, or if pandas is used).
    -   Specific database connectors as required by the source database (e.g., `psycopg2-binary`, `mysql-connector-python`, `pyodbc`). The exact connector will depend on the user's external database.

## 2. Development Setup

-   A Python environment (e.g., venv, conda).
-   Installation of necessary Python packages via `pip`. A `requirements.txt` file will be maintained.
    -   Initially: `pandas` (which pulls in `numpy` and often `sqlalchemy`).
    -   The specific database connector for the external DB.
-   An IDE or text editor (e.g., VS Code, PyCharm).
-   Access to a sample or test version of the external database view, if possible, for development and testing.
-   A SQLite client (e.g., DB Browser for SQLite, `sqlite3` CLI) for inspecting the local database.

## 3. Technical Constraints & Considerations

-   **Database Credentials:** Secure handling of external database credentials is paramount. Options:
    -   Environment variables (recommended for production-like setups).
    -   Configuration file (e.g., `config.ini`, `config.json`) with appropriate file permissions and .gitignore entry.
    -   User input at runtime (less suitable for automation).
    *For initial development, a configuration file might be the most straightforward, with clear instructions on securing it.*
-   **Data Volume:** The performance of "truncate-and-load" might degrade with extremely large datasets. If the view contains millions of rows, alternative strategies or optimizations (chunking data, direct database-to-database tools if available) might be needed in the future. For now, pandas' `to_sql` with `if_exists='replace'` is a good starting point.
-   **Schema Changes:** The current plan assumes the schema of the source view is relatively stable. If the view's schema changes frequently, the script might break or require manual updates to the local table structure. Pandas `to_sql` can often handle creating the table based on the DataFrame's dtypes, which helps with initial setup.
-   **Network Reliability:** The script needs a stable network connection to the external database during the synchronization process.
-   **Python Version:** Ensure compatibility with the Python version available in the user's environment.

## 4. Key Dependencies (Initial List for `requirements.txt`)

```
# Core data handling
pandas

# For SQLite (often built-in with Python, but pandas might use SQLAlchemy for it)
sqlalchemy # SQLAlchemy is used by pandas.to_sql for many database types

# Placeholder for the external database connector - TO BE DETERMINED
# Example: psycopg2-binary (for PostgreSQL)
# Example: mysql-connector-python (for MySQL)
# Example: pyodbc (for SQL Server, Oracle, etc.)
```
The specific external database connector will be added once the user specifies the database type.

## 5. Tool Usage Patterns

-   **Configuration File:** A `config.ini` file will be used to store database connection strings, view names, and local SQLite file paths. The `configparser` module in Python will be used to read this file.
-   **Logging:** Python's built-in `logging` module configured to output to both console and a file (e.g., `sync.log`).
