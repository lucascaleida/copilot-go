# MySQL to SQLite Synchronization Utility

This Python script synchronizes data from a specified view in a MySQL database to a local SQLite database. It reads connection details and the query from `config.ini`.

## Prerequisites

-   Python 3.7+
-   `pip` (Python package installer)
-   Access to the external MySQL database.

## Setup Instructions

1.  **Clone/Download the Project:**
    Ensure all project files (`sync_script.py`, `config.ini`, `requirements.txt`, `.gitignore`, `README.md`) are in a directory, for example, named `mysql_to_sqlite_sync/`.

2.  **Navigate to the Project Directory:**
    Open your terminal or command prompt and change to the project directory:
    ```bash
    cd path/to/mysql_to_sqlite_sync
    ```

3.  **Create and Activate a Python Virtual Environment (Recommended):**
    This isolates the project's dependencies.
    ```bash
    python3 -m venv venv  # Or 'python -m venv venv' if 'python3' is not found
    ```
    Activate the virtual environment:
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    Your terminal prompt should change to indicate you are in the virtual environment (e.g., `(venv) ...$`).

4.  **Install Required Python Packages:**
    With the virtual environment activated, install the dependencies listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Verify Configuration (`config.ini`):**
    Open the `config.ini` file and ensure all details are correct, especially:
    -   `[external_db]` section: `host`, `port`, `database`, `user`, `password`, and `query`.
    -   `[local_db]` section: `db_path` (default is `data/local_vehicles_stock.db`) and `table_name` (default is `vehicles_stock`).
    **Important Security Note:** The `config.ini` file contains the database password. Ensure this file is kept secure and is not committed to version control if you are using Git (the provided `.gitignore` file should prevent this).

## How to Run the Script

1.  **Ensure Virtual Environment is Active:**
    If you've closed your terminal since setting up, navigate back to the project directory and reactivate the virtual environment (see Step 3 in Setup).

2.  **Execute the Script:**
    Run the `sync_script.py` from within the project directory:
    ```bash
    python sync_script.py
    ```

## Expected Output

-   **Console Logs:** The script will print log messages to the console, indicating:
    -   Configuration loading.
    -   Connection attempts to the MySQL database.
    -   Number of rows fetched from MySQL.
    -   Connection/creation of the local SQLite database.
    -   Number of rows written to the SQLite table.
    -   Success or error messages.
-   **SQLite Database File:**
    -   A directory named `data/` will be created within your project folder (if it doesn't already exist).
    -   Inside `data/`, a SQLite database file (e.g., `local_vehicles_stock.db`, as per `config.ini`) will be created or updated.
    -   This database will contain a table (e.g., `vehicles_stock`) with the synchronized data.

## Troubleshooting

-   **`ModuleNotFoundError`:** Ensure your virtual environment is active and you have run `pip install -r requirements.txt`.
-   **Connection Errors to MySQL:**
    -   Verify network connectivity to the MySQL server (`143.42.30.41` on port `3306`).
    -   Check that the credentials (`user`, `password`) and database details (`host`, `port`, `database`) in `config.ini` are correct.
    -   Ensure the MySQL user `consultas_concesur` has the necessary permissions to connect from your IP address and execute the specified query on `v_stock`.
-   **`FileNotFoundError` for `config.ini`:** Make sure you are running the script from the root of the `mysql_to_sqlite_sync` directory where `config.ini` is located.
-   **SQLite Errors:** Check file system permissions if the script cannot create the `data/` directory or the `.db` file.

## To Deactivate the Virtual Environment (When Done)

Simply type:
```bash
deactivate
