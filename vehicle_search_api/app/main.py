import os
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Security, Query, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy import create_engine, text, Column, BigInteger, String, Float, DateTime
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from datetime import datetime


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

@app.middleware("http")
async def log_request_body(request: Request, call_next):
    if request.url.path == "/stock/" and request.method == "POST":
        # Read the body, which consumes the stream
        body = await request.body()
        # Log the raw body for debugging, limited to 10 records
        print("--- RAW STOCK PAYLOAD RECEIVED TO DEBUG (first 10 records) ---")
        try:
            data = json.loads(body.decode())
            if 'datos' in data and isinstance(data['datos'], list):
                data['datos'] = data['datos'][:10]
            print(json.dumps(data, indent=2)) # Pretty print
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If decoding or parsing fails, print the raw body
            print(body.decode(errors='ignore'))
        print("----------------------------------")

        # The stream has been consumed, so we need to pass the body back
        # to the actual endpoint by recreating the receive channel.
        async def receive():
            return {"type": "http.request", "body": body}
        
        # Create a new request object with the recreated receive channel
        request = Request(request.scope, receive)

    response = await call_next(request)
    return response

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
    tienda: Optional[str] = None
    vo_vn: Optional[str] = None
    # Add other fields from the schema as needed for the response

    class Config:
        from_attributes = True # For Pydantic v2 compatibility

class StockPayload(BaseModel):
    campos: List[Any]  # Allow list of anything to handle complex input
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
    tienda: Optional[str] = Query(None),
    vo_vn: Optional[str] = Query(None, description="Filter for new ('NEW') or used ('VO') vehicles"),
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
           modelo_inv, marca_inv, workflow_estado
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

    if tienda:
        conditions.append("workflow_estado LIKE :tienda")
        query_params["tienda"] = f"%{tienda}%"
    if vo_vn:
        conditions.append("workflow_estado LIKE :vo_vn")
        query_params["vo_vn"] = f"%{vo_vn}%"

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
                
                # Parse tienda and vo_vn from workflow_estado
                workflow_estado = row_dict.get("workflow_estado")
                if workflow_estado and isinstance(workflow_estado, str):
                    parts = workflow_estado.split()
                    # Expected format: "Stock <TIENDA> <VO_VN>"
                    if len(parts) >= 3:
                        row_dict["tienda"] = parts[1]
                        row_dict["vo_vn"] = parts[2]
                    elif len(parts) == 2:
                        if parts[1].upper() in ['NEW', 'VO']:
                            row_dict["vo_vn"] = parts[1]
                        else:
                            row_dict["tienda"] = parts[1]
                
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

# Schema definition for type conversion
VEHICLE_STOCK_SCHEMA = {
    'ficha_id': BigInteger, 'workflow_nombre': String, 'workflow_id': BigInteger,
    'workflow_estado': String, 'workflow_estado_id': BigInteger, 'workflow_subestado': String,
    'workflow_subestado_id': BigInteger, 'modelo': String, 'origen_custom': String,
    'descripcion': String, 'tipo_transmision': String, 'matricula': String, 'vin': String,
    'fecha_matriculacion': DateTime, 'fecha_matriculacion_JAWA': DateTime,
    'kms_vehiculo': Float, 'kms': Float, 'kms_manual': String, 'color': String,
    'interior': String, 'color_interior': String, 'equipamiento': String,
    'fiscalidad': Float, 'pvp': String, 'garantia': String, 'comercial': String,
    'fecha_reserva': String, 'observaciones': String, 'color_registro': String,
    'fiscalidad_GO': String, 'marca': String, 'color_api': String, 'interior_api': String,
    'fiscalidad_api': Float, 'pvp_api': Float, 'precio_base_api': Float, 'origen': String,
    'marca_inv': String, 'modelo_inv': String, 'version_inv': String,
    'codigo_jato_inv': String, 'publicar_inv': String, 'fecha_publicado_inv': String,
    'codigo_progresion': String, 'tipo_venta': String, 'clase_vehiculo': String,
    'grossvalue': Float, 'ubicacion': String, 'fecha_factura_compra': String,
    'vehicle_stock_id': String
}

def convert_value(value, target_type):
    """Converts a string value to a specified SQLAlchemy type, handling errors."""
    if value is None or value == '':
        return None

    try:
        if target_type == BigInteger:
            return int(float(str(value).replace(',', '.')))
        elif target_type == Float:
            return float(str(value).replace(',', '.'))
        elif target_type == DateTime:
            # Try to parse different date formats
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(str(value), fmt)
                except ValueError:
                    continue
            # If all formats fail, return None
            return None
        return str(value)
    except (ValueError, TypeError):
        return None

@app.post("/stock/", status_code=200, dependencies=[Security(get_api_key)])
async def update_stock(payload: StockPayload):
    if engine is None:
        raise HTTPException(status_code=503, detail="Database service is unavailable.")

    if not payload.datos:
        return {"message": "No data provided to update. Stock remains unchanged."}

    processed_campos = [str(c) for c in payload.campos]
    
    list_of_dicts = []
    for row in payload.datos:
        record = {}
        for i, field in enumerate(processed_campos):
            if field in VEHICLE_STOCK_SCHEMA:
                target_type = VEHICLE_STOCK_SCHEMA[field]
                raw_value = row[i] if i < len(row) else None
                record[field] = convert_value(raw_value, target_type)
        list_of_dicts.append(record)

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
