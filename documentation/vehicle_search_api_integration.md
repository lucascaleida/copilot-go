# Vehicle Search API Integration Guide for LLM Tools

This document provides the necessary information to integrate with the Vehicle Search API, allowing LLM tools to query vehicle stock data.

## 1. API Endpoint

The primary endpoint for searching vehicles is:

-   **Method:** `GET`
-   **URL:** `/cars/`

The base URL of the API will depend on its deployment environment (e.g., `http://localhost:8000` if running locally via Docker, or a specific production URL).

## 2. Authentication

The API is secured using an API key.

-   **Authentication Method:** API Key
-   **Header Name:** `X-API-Key`
-   **API Key Value:** The API key is configured in the API's environment. The LLM tool or its administrator will need to be provided with this key.

**Example Header:**
`X-API-Key: YOUR_PROVIDED_API_KEY`

If the API key is missing or invalid, the API will respond with an HTTP `403 Forbidden` error.

## 3. Request Query Parameters

The `/cars/` endpoint accepts the following optional query parameters to filter the vehicle search:

| Parameter          | Alias In Code    | Data Type | Description                                                                 | Example Value    |
|--------------------|------------------|-----------|-----------------------------------------------------------------------------|------------------|
| `marca`            | `make`           | string    | Filter by vehicle make (brand). Case-insensitive, partial match (LIKE).     | `Toyota`         |
| `modelo`           | `model`          | string    | Filter by vehicle model. Case-insensitive, partial match (LIKE).            | `Corolla`        |
| `year`             | `year`           | integer   | Filter by the year of registration (`fecha_matriculacion`).                 | `2023`           |
| `color`            | `color`          | string    | Filter by vehicle color. Case-insensitive, partial match (LIKE).            | `Blue`           |
| `vin`              | `vin`            | string    | Filter by Vehicle Identification Number. Exact match.                       | `123ABCDEF456GHI`|
| `min_kms`          | `min_kms`        | float     | Minimum kilometers.                                                         | `10000`          |
| `max_kms`          | `max_kms`        | float     | Maximum kilometers.                                                         | `50000`          |
| `min_price`        | `min_price`      | float     | Minimum price (based on `pvp_api`).                                         | `15000`          |
| `max_price`        | `max_price`      | float     | Maximum price (based on `pvp_api`).                                         | `25000`          |
| `tipo_transmision` | `transmission`   | string    | Filter by transmission type. Case-insensitive, partial match (LIKE).        | `Automatic`      |
| `limit`            | `limit`          | integer   | Maximum number of results to return. Default: 100. Min: 1, Max: 1000.       | `50`             |

**Note on `marca` and `modelo`:** The API internally prioritizes `marca_inv` and `modelo_inv` fields from the database if they are available, falling back to the standard `marca` and `modelo` fields. The query parameters `marca` and `modelo` will search against the standard fields.

## 4. Response Structure

The API returns a JSON array of vehicle objects. Each object in the array represents a vehicle and contains the following fields:

| Field                 | Data Type     | Description                                                                   |
|-----------------------|---------------|-------------------------------------------------------------------------------|
| `ficha_id`            | integer       | Unique identifier for the vehicle record.                                     |
| `modelo`              | string        | Vehicle model. (Value might come from `modelo_inv` if available).             |
| `descripcion`         | string        | Description of the vehicle.                                                   |
| `tipo_transmision`    | string        | Transmission type (e.g., "Automatic", "Manual").                              |
| `matricula`           | string        | License plate number.                                                         |
| `vin`                 | string        | Vehicle Identification Number.                                                |
| `fecha_matriculacion` | string        | Vehicle registration date, formatted as "YYYY-MM-DD".                         |
| `kms`                 | float         | Kilometers of the vehicle.                                                    |
| `color`               | string        | Vehicle color.                                                                |
| `pvp_api`             | float         | Retail price (Precio Venta Público) from the API-specific field.              |
| `marca`               | string        | Vehicle make/brand. (Value might come from `marca_inv` if available).         |

All fields are optional and will be `null` if not available for a specific vehicle.

## 5. Example Usage

### Example Request (using `curl`)

Assuming the API is running at `http://localhost:8000` and your API key is `YOUR_SECRET_API_KEY`:

```bash
curl -X GET "http://localhost:8000/cars/?marca=Toyota&color=Red&limit=2" \
     -H "X-API-Key: YOUR_SECRET_API_KEY"
```

### Example Response

```json
[
  {
    "ficha_id": 101,
    "modelo": "Camry",
    "descripcion": "Reliable family sedan",
    "tipo_transmision": "Automatic",
    "matricula": "1234ABC",
    "vin": "VIN12345TOYOTACAMRY",
    "fecha_matriculacion": "2022-05-15",
    "kms": 25000.0,
    "color": "Red",
    "pvp_api": 28000.0,
    "marca": "Toyota"
  },
  {
    "ficha_id": 105,
    "modelo": "RAV4",
    "descripcion": "Compact SUV, red",
    "tipo_transmision": "Automatic",
    "matricula": "5678DEF",
    "vin": "VIN67890TOYOTARAV4",
    "fecha_matriculacion": "2023-01-20",
    "kms": 15000.0,
    "color": "Red",
    "pvp_api": 32000.0,
    "marca": "Toyota"
  }
]
```

## 6. Error Handling

The API uses standard HTTP status codes to indicate success or failure:

-   **`200 OK`**: The request was successful, and the response body contains the vehicle data (which might be an empty list if no vehicles match the criteria).
-   **`403 Forbidden`**: Authentication failed (e.g., missing or invalid API key).
    ```json
    {
      "detail": "Could not validate credentials"
    }
    ```
-   **`422 Unprocessable Entity`**: The request was well-formed, but contained invalid data for one or more parameters (e.g., `limit` outside allowed range). FastAPI provides detailed error messages.
-   **`500 Internal Server Error`**: An unexpected error occurred on the server (e.g., database query error).
    ```json
    {
      "detail": "Database query error: [specific error message]"
    }
    ```
    or
    ```json
    {
      "detail": "An unexpected error occurred: [specific error message]"
    }
    ```
-   **`503 Service Unavailable`**: The database service is not available (e.g., connection issue at API startup).
    ```json
    {
      "detail": "Database service is unavailable."
    }
    ```

LLM tools should be prepared to handle these responses appropriately.
