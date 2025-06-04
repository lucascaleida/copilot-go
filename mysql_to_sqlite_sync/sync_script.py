import configparser
import logging
import os
import pandas as pd
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file='config.ini'):
    """Loads configuration from the specified INI file."""
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        logging.error(f"Configuration file '{config_file}' not found.")
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    config.read(config_file)
    logging.info(f"Configuration loaded from '{config_file}'.")
    return config

def fetch_data_from_external_db(config):
    """Fetches data from the external database using details from the config."""
    db_type = config.get('external_db', 'type')
    user = config.get('external_db', 'user')
    password = config.get('external_db', 'password')
    host = config.get('external_db', 'host')
    port = config.get('external_db', 'port')
    database = config.get('external_db', 'database')
    query = config.get('external_db', 'query')

    if db_type.lower() == 'mysql':
        engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    # Add other database types here if needed (e.g., postgresql, mssql)
    # elif db_type.lower() == 'postgresql':
    #     engine_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    # elif db_type.lower() == 'sqlserver':
    #     engine_url = f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server" # Ensure correct driver
    else:
        logging.error(f"Unsupported database type: {db_type}")
        raise ValueError(f"Unsupported database type: {db_type}")

    try:
        engine = create_engine(engine_url)
        with engine.connect() as connection:
            logging.info(f"Successfully connected to external {db_type} database.")
            df = pd.read_sql_query(text(query), connection)
            logging.info(f"Successfully fetched {len(df)} rows from the external database.")
            return df
    except Exception as e:
        logging.error(f"Error connecting to or fetching data from external {db_type} database: {e}")
        raise

def write_data_to_sqlite(df, config):
    """Writes the DataFrame to a local SQLite database."""
    db_path_str = config.get('local_db', 'db_path')
    table_name = config.get('local_db', 'table_name')

    # Ensure the directory for the SQLite database exists
    db_dir = os.path.dirname(db_path_str)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logging.info(f"Created directory for SQLite database: {db_dir}")

    engine_url = f"sqlite:///{db_path_str}"
    try:
        engine = create_engine(engine_url)
        with engine.connect() as connection: # Test connection
            pass
        logging.info(f"Successfully connected to/created local SQLite database at '{db_path_str}'.")
        
        # Write data to SQLite, replacing the table if it exists
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Successfully wrote {len(df)} rows to table '{table_name}' in SQLite database.")
    except Exception as e:
        logging.error(f"Error writing data to SQLite database: {e}")
        raise

def main():
    """Main function to orchestrate the data synchronization."""
    logging.info("Starting database synchronization process...")
    try:
        config = load_config()
        df = fetch_data_from_external_db(config)
        if df is not None and not df.empty:
            write_data_to_sqlite(df, config)
            logging.info("Database synchronization process completed successfully.")
        elif df is not None and df.empty:
            # If the source query returns no data, we should still update the local table to reflect that.
            # An empty DataFrame will result in an empty table (or table replaced with an empty one).
            write_data_to_sqlite(df, config) # This will create an empty table or replace existing with empty
            logging.info("Source query returned no data. Local table has been updated to be empty.")
            logging.info("Database synchronization process completed successfully (source was empty).")

        else: # df is None, implies an error during fetch
            logging.warning("No data fetched from external database, possibly due to an error. Local database not updated.")
            
    except FileNotFoundError:
        logging.error("Halting process due to missing configuration file.")
    except ValueError as ve: # Catch specific errors like unsupported DB
        logging.error(f"Halting process due to a value error: {ve}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during the synchronization process: {e}")
        logging.error("Database synchronization process failed.")

if __name__ == "__main__":
    main()
