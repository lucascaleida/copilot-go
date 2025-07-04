import os
import json
import requests
from dotenv import load_dotenv
import pytest

# Load environment variables from the .env file located in the same directory
# This makes the test self-contained within the vehicle_search_api directory
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    # Fallback for running from the root directory
    load_dotenv()


# --- API Configuration ---
# The test will target the deployed Azure service
API_URL = "https://concesur-vehicle-api.azurewebsites.net"
API_KEY = os.getenv("API_KEY")

# Check if the API key is available
if not API_KEY:
    pytest.fail("API_KEY not found in environment variables. Please check your .env file.")

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# --- Test Data ---
# This is the exact payload provided, with Python objects serialized into
# JSON-compatible formats (e.g., datetime to string, Decimal to string).
TEST_PAYLOAD = {
    'campos': [
        ('ficha_id', 'bigint', 'NO', '', '0', ''),
        ('workflow_nombre', 'longtext', 'YES', '', None, ''),
        ('workflow_id', 'bigint', 'NO', '', '0', ''),
        ('workflow_estado', 'longtext', 'YES', '', None, ''),
        ('workflow_estado_id', 'bigint', 'NO', '', '0', ''),
        ('workflow_subestado', 'longtext', 'YES', '', None, ''),
        ('workflow_subestado_id', 'bigint', 'NO', '', '0', ''),
        ('modelo', 'varchar(255)', 'YES', '', None, ''),
        ('origen_custom', 'text', 'YES', '', None, ''),
        ('descripcion', 'varchar(255)', 'YES', '', None, ''),
        ('tipo_transmision', "enum('AUTOMATIC','MANUAL','OTHER')", 'YES', '', None, ''),
        ('matricula', 'varchar(20)', 'YES', '', None, ''),
        ('vin', 'varchar(50)', 'YES', '', None, ''),
        ('fecha_matriculacion', 'datetime', 'YES', '', None, ''),
        ('fecha_matriculacion_JAWA', 'datetime', 'YES', '', None, ''),
        ('kms_vehiculo', 'bigint', 'YES', '', None, ''),
        ('kms', 'bigint', 'YES', '', None, ''),
        ('kms_manual', 'text', 'YES', '', None, ''),
        ('color', 'varchar(100)', 'YES', '', None, ''),
        ('interior', 'varchar(100)', 'YES', '', None, ''),
        ('color_interior', 'text', 'YES', '', None, ''),
        ('equipamiento', 'text', 'YES', '', None, ''),
        ('fiscalidad', 'bit(1)', 'YES', '', None, ''),
        ('pvp', 'text', 'YES', '', None, ''),
        ('garantia', 'longtext', 'YES', '', None, ''),
        ('comercial', 'text', 'YES', '', None, ''),
        ('fecha_reserva', 'text', 'YES', '', None, ''),
        ('observaciones', 'text', 'YES', '', None, ''),
        ('color_registro', 'text', 'YES', '', None, ''),
        ('fiscalidad_GO', 'text', 'YES', '', None, ''),
        ('marca', 'varchar(100)', 'YES', '', None, ''),
        ('color_api', 'varchar(100)', 'YES', '', None, ''),
        ('interior_api', 'varchar(100)', 'YES', '', None, ''),
        ('fiscalidad_api', 'decimal(10,2)', 'YES', '', None, ''),
        ('pvp_api', 'decimal(10,2)', 'YES', '', None, ''),
        ('precio_base_api', 'decimal(10,2)', 'YES', '', None, ''),
        ('origen', 'varchar(200)', 'YES', '', None, ''),
        ('marca_inv', 'text', 'YES', '', None, ''),
        ('modelo_inv', 'text', 'YES', '', None, ''),
        ('version_inv', 'text', 'YES', '', None, ''),
        ('codigo_jato_inv', 'text', 'YES', '', None, ''),
        ('publicar_inv', 'longtext', 'YES', '', None, ''),
        ('fecha_publicado_inv', 'text', 'YES', '', None, ''),
        ('codigo_progresion', 'text', 'YES', '', None, ''),
        ('tipo_venta', 'text', 'YES', '', None, ''),
        ('clase_vehiculo', "enum('UNKNOWN','CAR','VAN','MOTORCYCLE','TRUCK','OTHER','NOTAPPLICABLE','BUS','LIGHTTRUCK')", 'YES', '', None, ''),
        ('grossvalue', 'decimal(10,2)', 'YES', '', None, ''),
        ('ubicacion', 'text', 'YES', '', None, ''),
        ('fecha_factura_compra', 'text', 'YES', '', None, ''),
        ('vehicle_stock_id', 'varchar(100)', 'YES', '', None, '')
    ],
    'datos': [
        (590105, 'Grupo Concesur Comercial', 6, 'Stock A1 NEW', 1347, 'Stock A1 NEW', 3128, 'Clase C', None, 'C 200 d Berlina', 'AUTOMATIC', '9666MXB', 'W1KAF0DB3RR231262', '2024-12-16T00:00:00', None, 0, 0, '1.000', 'Plata Mojave metalizado', 'Símil de cuero ARTICO negro', None, None, 1, '46500.00', None, None, None, None, None, None, 'MERCEDES-BENZ', '2859', '4111', '21.00', '40413.22', '0.00', '', None, None, None, None, None, None, None, None, 'CAR', '48900.00', 'ALCALA CAMPA', None, 'A1-N20568'),
        (590463, 'Grupo Concesur Comercial', 6, 'Stock A1 NEW', 1347, 'Stock A1 NEW', 3128, 'FORTWO COUPE', None, 'FORTWO COUPE MICRO', 'MANUAL', '3999HXB', 'WME4513801K783948', '2014-05-05T00:00:00', '0001-01-01T00:00:00', 8839, None, None, '', '', None, None, None, '999999.99', None, None, None, None, None, None, 'Smart', None, None, None, None, None, None, 'SMART', 'FORTWO', 'BERLINA', 'yMjAxMDE3ODE3ODQzMjA', 'Si', None, None, None, 'CAR', None, None, None, None),
        (591059, 'Grupo Concesur Comercial', 6, 'Stock A1 NEW', 1347, 'Stock A1 NEW', 3128, 'FORTWO COUPE', None, 'FORTWO COUPE MICRO', 'MANUAL', '3999HXB', 'WME4513801K783948', '2014-05-05T00:00:00', '0001-01-01T00:00:00', 8839, None, None, '', '', None, None, None, None, None, None, None, None, None, None, 'Smart', None, None, None, None, None, None, 'SMART', 'FORTWO', 'BERLINA', None, 'No', '05/05/2025', None, None, 'CAR', None, None, None, None),
        (591948, 'Grupo Concesur Comercial', 6, 'STOCK M1 NEW', 1351, 'STOCK M1 NEW', 3134, 'Range Rover Evoque', None, 'RR EVOQUE 1.5 PHEV AWD 5P. SWB R-DYNAMIC S 300CV AUTO', 'OTHER', '9809MNC', 'SALZA2BT5PH219113', '2024-02-02T00:00:00', None, 0, 0, None, 'Pintura sólida', '', None, None, 1, None, None, None, None, None, None, None, 'LAND ROVER', '', '', '21.00', '49325.03', '0.00', '', 'Land-Rover', 'Range Rover Evoque', 'P300e PHEV S 4WD Auto 227 kW (309 CV)', '.', 'Si', '13/06/2025', None, None, 'CAR', '59683.29', '...', None, 'M1-N247'),
        (591949, 'Grupo Concesur Comercial', 6, 'STOCK M1 NEW', 1351, 'STOCK M1 NEW', 3134, 'Range Rover Evoque', None, 'RR Evoque 1.5 PHEV S 300 Cv Auto', 'OTHER', '3562MSS', 'SALZA2BTXRH251252', '2024-07-01T00:00:00', None, 0, 0, None, 'Seoul Pearl Silver', 'Piel', None, None, 1, None, None, None, None, None, None, None, 'LAND ROVER', '1CS', '', '21.00', '50729.99', '0.00', '', 'Land-Rover', 'Range Rover Evoque', 'P300e PHEV S 4WD Auto 227 kW (309 CV)', None, 'Si', '13/06/2025', None, None, 'CAR', '61383.29', None, None, 'M1-N367'),
        (591950, 'Grupo Concesur Comercial', 6, 'STOCK M1 NEW', 1351, 'STOCK M1 NEW', 3134, 'F-Pace', None, 'F-PACE 2.0DAWD 5P SWB SE 204CV AUTO', 'OTHER', '3706MTW', 'SADCA2BN3RA730012', '2024-09-02T00:00:00', None, 0, 0, None, 'Santorini Black', 'Piel', None, None, 1, None, None, None, None, None, None, None, 'Jaguar', '1AG', '', '21.00', '0.00', '0.00', '', 'Jaguar', 'F-Pace', '2.0D I4 MHEV R-Dynamic S AWD Auto 150 kW (204 CV)', None, None, None, None, None, 'CAR', '0.00', None, None, 'M1-N370'),
        (591951, 'Grupo Concesur Comercial', 6, 'STOCK M1 NEW', 1351, 'STOCK M1 NEW', 3134, 'F-Pace', None, 'JAGUA F-PACE', 'MANUAL', '7227MVG', 'SADCA2BN0RA741579', '2024-09-25T00:00:00', None, 0, 0, None, 'Eiger Grey', 'Piel', None, None, 1, None, None, None, None, None, None, None, 'Jaguar', '1DF', '', '21.00', '57248.75', '0.00', '', 'JAGUAR', 'F-PACE', 'TODOTERRENO', None, None, None, None, None, 'CAR', '69270.99', None, None, 'M1-N371'),
        (591952, 'Grupo Concesur Comercial', 6, 'STOCK M1 NEW', 1351, 'STOCK M1 NEW', 3134, 'Range Rover', None, 'RANGE ROVER 3.0 AWD 5P. SWB AUTOBIOGRAPHY 350CV AUTO', 'OTHER', '4574MZV', 'SALKABB99RA232173', '2025-04-04T00:00:00', None, 0, 0, None, 'Santorini Black', 'Piel', None, None, 1, None, None, None, None, None, None, None, 'LAND ROVER', '1AG', '', '21.00', '157414.71', '0.00', '', 'LAND ROVER', 'RANGE ROVER', 'TODOTERRENO', None, None, None, None, None, 'CAR', '190471.80', None, None, 'M1-N384'),
        (591954, 'Grupo Concesur Comercial', 6, 'STOCK M1 NEW', 1351, 'STOCK M1 NEW', 3134, 'Range Rover', None, 'RR Range Rover 4.4D SDV8 SWB Vogue', 'OTHER', 'M1/N000430', 'SALKABB9XSA256455', None, None, 0, 0, None, 'Fuji White', 'Piel', None, None, 1, None, None, None, None, None, None, None, 'LAND ROVER', 'FW', '', '21.00', '162681.75', '0.00', '', 'LAND ROVER', '', '2025', None, None, None, None, None, 'CAR', '196844.92', None, None, 'M1-N430'),
        (591955, 'Grupo Concesur Comercial', 6, 'STOCK M1 NEW', 1351, 'STOCK M1 NEW', 3134, 'Range Rover Evoque', None, 'RR Evoque 1.5 PHEV S 300 Cv Auto', 'OTHER', '0027MXV', 'SALZA2BT1RH251446', '2025-01-15T00:00:00', None, 0, 0, None, 'Santorini Black', 'Piel', None, None, 1, None, None, None, None, None, None, None, 'LAND ROVER', '1AG', '', '21.00', '50729.99', '0.00', '', 'Land-Rover', 'Range Rover Evoque', 'P300e PHEV S 4WD Auto 227 kW (309 CV)', None, None, None, None, None, 'CAR', '61383.29', None, None, 'M1-N431')
    ]
}

@pytest.mark.skipif(not API_KEY, reason="API_KEY is not configured")
def test_update_stock_azure():
    """
    Tests the POST /stock/ endpoint on the deployed Azure service to ensure
    it can successfully receive, process, and store a full stock update.
    """
    endpoint_url = f"{API_URL}/stock/"
    
    try:
        response = requests.post(
            endpoint_url,
            headers=HEADERS,
            data=json.dumps(TEST_PAYLOAD, default=str) # Use default=str for safety
        )
        
        # 1. Check for a successful HTTP status code
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response: {response.text}"
        
        # 2. Parse the JSON response
        response_data = response.json()
        
        # 3. Check for the success message and correct number of records
        assert response_data.get("message") == "Stock updated successfully"
        assert response_data.get("records_added") == len(TEST_PAYLOAD['datos'])
        
        print(f"\nSUCCESS: POST /stock/ endpoint test against Azure passed.")
        print(f"Response: {response_data}")

    except requests.exceptions.ConnectionError as e:
        pytest.fail(
            f"Connection to the Azure API failed at {API_URL}. "
            f"Please ensure the service is running and accessible. Error: {e}"
        )
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during the test: {e}")

# To run this test:
# 1. Ensure you have an internet connection and the Azure service is deployed.
# 2. Make sure the .env file with the correct API_KEY is in the `vehicle_search_api` directory.
# 3. Install dependencies:
#    pip install -r vehicle_search_api/requirements.txt
# 4. Run pytest from the project root directory:
#    pytest vehicle_search_api/tests/test_api.py
