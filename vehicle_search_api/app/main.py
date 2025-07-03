import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Security, Query
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


load_dotenv(dotenv_path="../.env") # Adjusted path to .env

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "require") # Default to require if not set
DB_SSL_CA = os.getenv("DB_SSL_CA")
DB_SSL_CERT = os.getenv("DB_SSL_CERT")
DB_SSL_KEY = os.getenv("DB_SSL_KEY")

if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError("Database credentials are not fully configured in environment variables.")

if not API_KEY:
    raise RuntimeError("API_KEY is not configured in environment variables.")

# Construct the database URL
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SSL arguments for SQLAlchemy
connect_args = {}
if DB_SSL_MODE and DB_SSL_MODE.lower() == "disabled":
    connect_args['ssl_disabled'] = True
else:  # Assumes SSL is required or preferred (e.g., "require")
    if DB_SSL_CA:
        connect_args['ssl_ca'] = DB_SSL_CA
    if DB_SSL_CERT:
        connect_args['ssl_cert'] = DB_SSL_CERT
    if DB_SSL_KEY:
        connect_args['ssl_key'] = DB_SSL_KEY
    # If DB_SSL_MODE is "require" and no specific CA/cert/key are provided,
    # mysql-connector-python attempts SSL by default.
    # An empty connect_args here is fine for that default behavior.

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
except Exception as e:
    # Log this error appropriately in a real application
    print(f"Error creating database engine: {e}")
    # Depending on policy, you might want to exit or let FastAPI start and fail on request
    # For now, we'll let it proceed, and requests will fail if the engine is None or invalid
    engine = None


app = FastAPI(title="Vehicle Search API", version="1.0.0")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )

class Vehicle(BaseModel):
    ficha_id: Optional[int] = None
    modelo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_transmision: Optional[str] = None
    matricula: Optional[str] = None
    vin: Optional[str] = None
    fecha_matriculacion: Optional[str] = None # Kept as string for flexibility
    kms: Optional[float] = None
    color: Optional[str] = None
    pvp_api: Optional[float] = None
    marca: Optional[str] = None
    # Add other fields from the schema as needed for the response

    class Config:
        from_attributes = True # For Pydantic v2 compatibility

class StockPayload(BaseModel):
    campos: List[str]
    datos: List[List[Any]]

@app.get("/cars/", response_model=List[Vehicle], dependencies=[Security(get_api_key)])
async def search_cars(
    make: Optional[str] = Query(None, alias="marca"),
    model: Optional[str] = Query(None, alias="modelo"),
    year: Optional[int] = Query(None, alias="year"), # Assuming year of fecha_matriculacion
    color: Optional[str] = Query(None, alias="color"),
    vin: Optional[str] = Query(None, alias="vin"),
    min_kms: Optional[float] = Query(None, alias="min_kms"),
    max_kms: Optional[float] = Query(None, alias="max_kms"),
    min_price: Optional[float] = Query(None, alias="min_price"),
    max_price: Optional[float] = Query(None, alias="max_price"),
    transmission: Optional[str] = Query(None, alias="tipo_transmision"),
    limit: int = Query(100, ge=1, le=1000) # Default limit for results, with validation
):
    if engine is None:
        raise HTTPException(status_code=503, detail="Database service is unavailable.")

    query_params = {}
    conditions = []

    base_query = """
    SELECT ficha_id, modelo, descripcion, tipo_transmision, matricula, vin, 
           DATE_FORMAT(fecha_matriculacion, '%Y-%m-%d') as fecha_matriculacion, 
           kms, color, pvp_api, marca,
           modelo_inv, marca_inv  -- Added _inv fields
    FROM vehicles_stock
    """

    if make:
        # Search for the make in 'marca' and 'marca_inv' fields
        conditions.append("(marca LIKE :make OR marca_inv LIKE :make)")
        query_params["make"] = f"%{make}%"
    if model:
        # Search for the model in 'modelo', 'descripcion', and 'modelo_inv' fields
        conditions.append("(modelo LIKE :model OR descripcion LIKE :model OR modelo_inv LIKE :model)")
        query_params["model"] = f"%{model}%"
    if year:
        conditions.append("YEAR(fecha_matriculacion) = :year")
        query_params["year"] = year
    if color:
        conditions.append("color LIKE :color")
        query_params["color"] = f"%{color}%"
    if vin:
        conditions.append("vin = :vin") # VIN should be an exact match
        query_params["vin"] = vin
    if min_kms is not None:
        conditions.append("kms >= :min_kms")
        query_params["min_kms"] = min_kms
    if max_kms is not None:
        conditions.append("kms <= :max_kms")
        query_params["max_kms"] = max_kms
    if min_price is not None:
        conditions.append("pvp_api >= :min_price")
        query_params["min_price"] = min_price
    if max_price is not None:
        conditions.append("pvp_api <= :max_price")
        query_params["max_price"] = max_price
    if transmission:
        conditions.append("tipo_transmision LIKE :transmission")
        query_params["transmission"] = f"%{transmission}%"

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " LIMIT :limit"
    query_params["limit"] = limit

    try:
        with engine.connect() as connection:
            result = connection.execute(text(base_query), query_params)
            cars_data = result.mappings().all() # Fetch all results as list of dict-like objects
            
            processed_cars_list = []
            for row_mapping in cars_data:
                row_dict = dict(row_mapping)
                
                # Fallback logic for modelo
                modelo_inv = row_dict.get("modelo_inv")
                if modelo_inv is not None and str(modelo_inv).strip() != "":
                    row_dict["modelo"] = modelo_inv

                # If 'modelo' is still null or empty, use 'descripcion' as a fallback.
                # Based on documentation/vehicle_stock_schema.md, the column is 'descripcion'.
                current_modelo = row_dict.get("modelo")
                if not current_modelo or not str(current_modelo).strip():
                    row_dict["modelo"] = row_dict.get("descripcion")

                # Fallback logic for marca
                marca_inv = row_dict.get("marca_inv")
                if marca_inv is not None and str(marca_inv).strip() != "":
                    row_dict["marca"] = marca_inv
                
                processed_cars_list.append(row_dict)
            
            return processed_cars_list
            
    except SQLAlchemyError as e:
        # Log the error e
        print(f"Database query error: {e}")
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    except Exception as e:
        # Log the error e
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/stock/", status_code=200, dependencies=[Security(get_api_key)])
async def update_stock(payload: StockPayload):
    if engine is None:
        raise HTTPException(status_code=503, detail="Database service is unavailable.")

    if not payload.datos:
        return {"message": "No data provided to update. Stock remains unchanged."}

    # Pre-process the 'campos' field if it's a list of tuples
    processed_campos = []
    if payload.campos and isinstance(payload.campos[0], (list, tuple)):
        processed_campos = [str(field[0]) for field in payload.campos]
    else:
        processed_campos = payload.campos

    # Convert list of lists to list of dictionaries
    try:
        list_of_dicts = [dict(zip(processed_campos, row)) for row in payload.datos]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing payload data: {e}")

    # Begin a transaction
    with engine.begin() as connection:
        try:
            # 1. Delete all existing data from the table
            connection.execute(text("DELETE FROM vehicles_stock"))

            # 2. Bulk insert the new data
            if list_of_dicts:
                # Get the table object from metadata (or define it)
                from sqlalchemy import Table, MetaData
                metadata = MetaData()
                vehicles_stock_table = Table('vehicles_stock', metadata, autoload_with=engine)
                
                connection.execute(vehicles_stock_table.insert(), list_of_dicts)

            return {"message": "Stock updated successfully", "records_added": len(list_of_dicts)}

        except SQLAlchemyError as e:
            # The 'with engine.begin()' context manager will automatically roll back the transaction on exception.
            print(f"Database transaction error: {e}")
            raise HTTPException(status_code=500, detail=f"Database transaction failed: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred during stock update: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during stock update: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to the Vehicle Search API. Access car data at /cars/ endpoint."}

# For local development, if you run this file directly:
# uvicorn vehicle_search_api.app.main:app --reload --port 8000 --host 0.0.0.0
# Ensure .env is in vehicle_search_api/
# To run from vehicle_search_api/app: uvicorn main:app --reload --port 8000 --host 0.0.0.0 --env-file ../.env
