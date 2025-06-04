import configparser
import logging
import os
import pandas as pd
from sqlalchemy import create_engine, text
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom exception for source data fetching issues
class SourceConnectionError(Exception):
    pass

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
    """Fetches data from the primary external database using details from the config."""
    try:
        db_type = config.get('external_db', 'type')
        user = config.get('external_db', 'user')
        password = config.get('external_db', 'password')
        host = config.get('external_db', 'host')
        port = config.get('external_db', 'port')
        database = config.get('external_db', 'database')
        query = config.get('external_db', 'query')
    except configparser.NoSectionError:
        logging.error("Missing 'external_db' section in config.")
        raise SourceConnectionError("Missing 'external_db' section in config.")
    except configparser.NoOptionError as e:
        logging.error(f"Missing option in 'external_db' section: {e}")
        raise SourceConnectionError(f"Missing option in 'external_db' section: {e}")


    if db_type.lower() == 'mysql':
        engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    else:
        logging.error(f"Unsupported database type in 'external_db': {db_type}")
        raise SourceConnectionError(f"Unsupported database type in 'external_db': {db_type}")

    try:
        engine = create_engine(engine_url)
        with engine.connect() as connection:
            logging.info(f"Successfully connected to primary external {db_type} database at {host}.")
            df = pd.read_sql_query(text(query), connection)
            logging.info(f"Successfully fetched {len(df)} rows from the primary external database.")
            return df
    except Exception as e:
        logging.error(f"Error connecting to or fetching data from primary external {db_type} database: {e}")
        # Raise a custom exception to be caught by main for fallback logic
        raise SourceConnectionError(f"Failed to fetch from primary external_db: {e}")

def fetch_data_from_sqlite(config):
    """Fetches data from the local SQLite database to be used as a fallback source."""
    try:
        db_path_str = config.get('local_db', 'db_path')
        table_name = config.get('local_db', 'table_name')
    except configparser.NoSectionError:
        logging.error("Missing 'local_db' section in config for fallback.")
        return None
    except configparser.NoOptionError as e:
        logging.error(f"Missing option in 'local_db' section for fallback: {e}")
        return None

    if not os.path.exists(db_path_str):
        logging.warning(f"Local SQLite DB for fallback not found at: {db_path_str}")
        return None

    engine_url = f"sqlite:///{db_path_str}"
    try:
        engine = create_engine(engine_url)
        with engine.connect() as connection:
            logging.info(f"Attempting to use local SQLite DB '{db_path_str}' (table: {table_name}) as fallback data source.")
            # Check if table exists
            query_check_table = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
            result = pd.read_sql_query(text(query_check_table), connection)
            if result.empty:
                logging.warning(f"Table '{table_name}' not found in local SQLite DB '{db_path_str}'. Cannot use as fallback.")
                return None
            
            df = pd.read_sql_query(text(f"SELECT * FROM {table_name}"), connection)
            logging.info(f"Successfully fetched {len(df)} rows from local SQLite DB (fallback source).")
            return df
    except Exception as e:
        logging.error(f"Error reading data from local SQLite DB (fallback source): {e}")
        return None

def write_data_to_sqlite(df, config):
    """Writes the DataFrame to a local SQLite database."""
    try:
        db_path_str = config.get('local_db', 'db_path')
        table_name = config.get('local_db', 'table_name')
    except configparser.NoSectionError:
        logging.error("Missing 'local_db' section in config for target.")
        raise
    except configparser.NoOptionError as e:
        logging.error(f"Missing option in 'local_db' section for target: {e}")
        raise

    db_dir = os.path.dirname(db_path_str)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logging.info(f"Created directory for SQLite database: {db_dir}")

    engine_url = f"sqlite:///{db_path_str}"
    try:
        engine = create_engine(engine_url)
        # Test connection implicitly via to_sql
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Successfully wrote {len(df)} rows to table '{table_name}' in SQLite database '{db_path_str}'.")
    except Exception as e:
        logging.error(f"Error writing data to SQLite database '{db_path_str}': {e}")
        raise

def write_data_to_azure_mysql(df, config):
    """Writes the DataFrame to the Azure MySQL database."""
    try:
        db_type = config.get('azure_mysql_db', 'type')
        user = config.get('azure_mysql_db', 'user')
        password = config.get('azure_mysql_db', 'password')
        host = config.get('azure_mysql_db', 'host')
        port = config.get('azure_mysql_db', 'port')
        database = config.get('azure_mysql_db', 'database')
        table_name = config.get('azure_mysql_db', 'table_name')
        ssl_mode = config.get('azure_mysql_db', 'ssl_mode', fallback='require') # Default to require for Azure
        # ssl_ca = config.get('azure_mysql_db', 'ssl_ca', fallback=None)
        # ssl_cert = config.get('azure_mysql_db', 'ssl_cert', fallback=None)
        # ssl_key = config.get('azure_mysql_db', 'ssl_key', fallback=None)

    except configparser.NoSectionError:
        logging.error("Missing 'azure_mysql_db' section in config.")
        raise
    except configparser.NoOptionError as e:
        logging.error(f"Missing option in 'azure_mysql_db' section: {e}")
        raise

    if db_type.lower() != 'mysql':
        logging.error(f"Unsupported database type in 'azure_mysql_db': {db_type}")
        raise ValueError(f"Unsupported database type for Azure target: {db_type}")

    connect_args = {}
    # Translate ssl_mode from config to mysql-connector-python specific arguments
    if ssl_mode and ssl_mode.lower() != 'disabled' and ssl_mode.lower() != 'prefer': # prefer is complex, treat as disabled for now if not explicitly handled
        connect_args['ssl_disabled'] = False # Enable SSL
        
        # For verify-ca or verify-full, a CA certificate is typically required.
        # mysql-connector-python defaults ssl_verify_cert to False if ssl_ca is not set,
        # and to True if ssl_ca is set.
        ssl_ca_path = config.get('azure_mysql_db', 'ssl_ca', fallback=None)
        if ssl_ca_path:
            connect_args['ssl_ca'] = ssl_ca_path
            # connect_args['ssl_verify_cert'] = True # Usually default if ssl_ca is provided

        # Add client cert and key if provided
        ssl_cert_path = config.get('azure_mysql_db', 'ssl_cert', fallback=None)
        ssl_key_path = config.get('azure_mysql_db', 'ssl_key', fallback=None)
        if ssl_cert_path:
            connect_args['ssl_cert'] = ssl_cert_path
        if ssl_key_path:
            connect_args['ssl_key'] = ssl_key_path
            
    elif ssl_mode and ssl_mode.lower() == 'disabled':
        connect_args['ssl_disabled'] = True

    engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    
    try:
        logging.info(f"Attempting to connect to Azure MySQL with connect_args: {connect_args}")
        engine = create_engine(engine_url, connect_args=connect_args)
        # Test connection by trying to create the table (or replace it)
        # Pandas to_sql will create the database if it doesn't exist, if the user has perms.
        # However, it's better if the database 'vehicles_db' already exists.
        # The table will be replaced.
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Successfully wrote {len(df)} rows to table '{table_name}' in Azure MySQL database '{database}' at {host}.")
    except Exception as e:
        logging.error(f"Error writing data to Azure MySQL database '{database}' at {host}: {e}")
        raise

def main():
    """Main function to orchestrate the data synchronization."""
    logging.info("Starting database synchronization process...")
    
    parser = argparse.ArgumentParser(description="Synchronize data from a source to a target database.")
    parser.add_argument('--target', type=str, choices=['azure', 'local_sqlite'], 
                        help="Specify the target database (azure or local_sqlite). Overrides config default.")
    args = parser.parse_args()

    try:
        config = load_config()

        # Determine target
        cli_target = args.target
        config_default_target = config.get('general', 'default_target', fallback='azure').lower()
        target_argument_enabled = config.getboolean('general', 'target_argument_enabled', fallback=True)

        chosen_target = config_default_target
        if cli_target and target_argument_enabled:
            chosen_target = cli_target.lower()
            logging.info(f"Using command-line specified target: {chosen_target}")
        else:
            logging.info(f"Using default target from config: {chosen_target}")

        # Fetch data (with fallback)
        data_df = None
        try:
            logging.info("Attempting to fetch data from primary external database...")
            data_df = fetch_data_from_external_db(config)
        except SourceConnectionError as e:
            logging.warning(f"Failed to fetch from primary external database: {e}")
            fallback_enabled = config.getboolean('general', 'fallback_to_local_source_on_failure', fallback=False)
            if fallback_enabled:
                logging.info("Attempting to use local SQLite database as fallback source...")
                data_df = fetch_data_from_sqlite(config)
                if data_df is None:
                    logging.error("Fallback from local SQLite also failed or provided no data.")
                elif data_df.empty:
                    logging.info("Fallback from local SQLite succeeded but returned no data.")
                else:
                    logging.info("Successfully used local SQLite as fallback data source.")
            else:
                logging.warning("Fallback to local source is disabled in config.")
        
        if data_df is None:
            logging.error("Failed to fetch data from any source. Halting process.")
            return
        
        # Write data to chosen target
        if data_df is not None: # This check includes empty DataFrame
            if chosen_target == 'azure':
                write_data_to_azure_mysql(data_df, config)
            elif chosen_target == 'local_sqlite':
                write_data_to_sqlite(data_df, config)
            else:
                logging.error(f"Invalid target specified or determined: {chosen_target}")
                return # Exit if target is not recognized

            if data_df.empty:
                logging.info("Source data was empty. Target table has been updated/created as empty.")
            
            logging.info("Database synchronization process completed successfully.")

    except FileNotFoundError:
        logging.error("Halting process due to missing configuration file.")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.error(f"Configuration error: {e}. Halting process.")
    except ValueError as ve:
        logging.error(f"Halting process due to a value error: {ve}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during the synchronization process: {e}", exc_info=True)
        logging.error("Database synchronization process failed.")

if __name__ == "__main__":
    main()
