# Vehicle Search API Integration Guide

This document provides the necessary information to integrate with the Vehicle Search API, allowing external systems to query and manage vehicle stock data.

## 1. API Endpoints

The API provides two main endpoints: one for searching vehicles and one for updating the entire vehicle stock.

### 1.1. Vehicle Search

-   **Method:** `GET`
-   **Production URL:** `https://concesur-vehicle-api.azurewebsites.net/cars/`
-   **Description:** Allows for flexible filtering of the vehicle stock based on various attributes.

### 1.2. Stock Update

-   **Method:** `POST`
-   **Production URL:** `https://concesur-vehicle-api.azurewebsites.net/stock/`
-   **Description:** Replaces the entire vehicle stock with the data provided in the request payload. This is a "truncate-and-load" operation, ensuring the database is an exact snapshot of the provided data.

## 2. Authentication

The API is secured using an API key. This key must be included in the header of all requests to both endpoints.

-   **Authentication Method:** API Key
-   **Header Name:** `X-API-Key`
-   **API Key Value:** The API key is configured in the API's environment. The client system will need to be provided with this key.

**Example Header:**
`X-API-Key: YOUR_PROVIDED_API_KEY`

If the API key is missing or invalid, the API will respond with an HTTP `403 Forbidden` error.

## 3. Search Endpoint (`GET /cars/`)

### 3.1. Request Query Parameters

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
| `tienda`           | `tienda`         | string    | Filter by store code (e.g., A1, M1). Case-insensitive, partial match (LIKE). | `A1`             |
| `vo_vn`            | `vo_vn`          | string    | Filter by vehicle condition ('NEW' for new, 'VO' for used). Case-insensitive, partial match (LIKE). | `NEW`            |
| `limit`            | `limit`          | integer   | Maximum number of results to return. Default: 100. Min: 1, Max: 1000.       | `50`             |

### 3.2. Response Structure (`GET /cars/`)

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
| `tienda`              | string        | The store code, parsed from `workflow_estado`.                                |
| `vo_vn`               | string        | The vehicle condition ('NEW' or 'VO'), parsed from `workflow_estado`.         |

## 4. Stock Update Endpoint (`POST /stock/`)

### 4.1. Request Body Structure

The `/stock/` endpoint expects a JSON object in the request body with the following structure:

```json
{
  "campos": ["field1", "field2", "field3", ...],
  "datos": [
    ["value1_row1", "value2_row1", "value3_row1", ...],
    ["value1_row2", "value2_row2", "value3_row2", ...],
    ...
  ]
}
```

-   `campos` (list of strings or list of lists/tuples): The names of the database columns. The order of names must correspond to the order of values in each sub-array of `datos`. The API is flexible and can accept a simple list of strings (e.g., `["vin", "marca"]`) or a more complex list of tuples/lists from a database schema description (e.g., `[["vin", "varchar"], ["marca", "varchar"]]`). The API will automatically extract the column name.
-   `datos` (list of lists): Each inner list represents a single vehicle record, with values in the same order as the `campos` list.

### 4.2. Response Structure (`POST /stock/`)

-   **On Success (HTTP `200 OK`):**
    ```json
    {
      "message": "Stock updated successfully",
      "records_added": 550
    }
    ```
-   **If `datos` is empty (HTTP `200 OK`):**
    ```json
    {
      "message": "No data provided to update. Stock remains unchanged."
    }
    ```
-   **On Failure (e.g., HTTP `500 Internal Server Error`):**
    ```json
    {
      "detail": "Database transaction failed: [specific error message]"
    }
    ```

## 5. Example Usage

### Example Search Request (`curl`)

```bash
curl -X 'GET' \
  'https://concesur-vehicle-api.azurewebsites.net/cars/?marca=mercedes&tienda=A1&vo_vn=NEW&limit=100' \
  -H 'accept: application/json' \
  -H 'X-API-Key: YOUR_PROVIDED_API_KEY'
```

### Example Stock Update Request (`curl`)

```bash
curl -X 'POST' \
  'https://concesur-vehicle-api.azurewebsites.net/stock/' \
  -H 'accept: application/json' \
  -H 'X-API-Key: YOUR_PROVIDED_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "campos": ["vin", "marca", "modelo", "color", "kms", "pvp_api"],
    "datos": [
      ["VIN001", "Toyota", "Corolla", "Blue", 25000, 21000.00],
      ["VIN002", "Honda", "Civic", "Red", 30000, 22000.00]
    ]
  }'
```

## 6. Error Handling

The API uses standard HTTP status codes to indicate success or failure:

-   **`200 OK`**: The request was successful.
-   **`400 Bad Request`**: The request body for the stock update is malformed.
-   **`403 Forbidden`**: Authentication failed (e.g., missing or invalid API key).
-   **`422 Unprocessable Entity`**: The request was well-formed, but contained invalid data for one or more parameters (e.g., `limit` outside allowed range).
-   **`500 Internal Server Error`**: An unexpected error occurred on the server (e.g., database query or transaction error).
-   **`503 Service Unavailable`**: The database service is not available.
