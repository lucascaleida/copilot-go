# Schema for `vehicles_stock` table

This document outlines the schema for the `vehicles_stock` table, typically found in the local SQLite database (`mysql_to_sqlite_sync/data/local_vehicles_stock.db`) and synchronized from an external source.

## Columns

| Column Name                 | Data Type | Description (Inferred/Known)                                  |
|-----------------------------|-----------|---------------------------------------------------------------|
| `ficha_id`                  | BIGINT    | Vehicle record identifier.                                    |
| `workflow_nombre`           | TEXT      | Name of the workflow.                                         |
| `workflow_id`               | BIGINT    | Identifier for the workflow.                                  |
| `workflow_estado`           | TEXT      | Current state of the vehicle in the workflow.                 |
| `workflow_estado_id`        | BIGINT    | Identifier for the workflow state.                            |
| `workflow_subestado`        | TEXT      | Current sub-state of the vehicle in the workflow.             |
| `workflow_subestado_id`     | BIGINT    | Identifier for the workflow sub-state.                        |
| `modelo`                    | TEXT      | Vehicle model. (Key field for API query)                      |
| `origen_custom`             | TEXT      | Custom origin information.                                    |
| `descripcion`               | TEXT      | Description of the vehicle.                                   |
| `tipo_transmision`          | TEXT      | Transmission type (e.g., Automatic, Manual). (Key field for API query) |
| `matricula`                 | TEXT      | License plate number.                                         |
| `vin`                       | TEXT      | Vehicle Identification Number. (Key field for API query)      |
| `fecha_matriculacion`       | DATETIME  | Vehicle registration date. Used to derive 'Year'. (Key field for API query) |
| `fecha_matriculacion_JAWA`  | DATETIME  | Specific registration date for JAWA system (quoted name).     |
| `kms_vehiculo`              | FLOAT     | Kilometers of the vehicle (potentially a duplicate or raw value). |
| `kms`                       | FLOAT     | Kilometers of the vehicle. (Key field for API query)          |
| `kms_manual`                | TEXT      | Manually entered kilometers (e.g., if different from `kms`).  |
| `color`                     | TEXT      | Vehicle color. (Key field for API query)                      |
| `interior`                  | TEXT      | Interior description or color.                                |
| `color_interior`            | TEXT      | Specific interior color.                                      |
| `equipamiento`              | TEXT      | Equipment or features of the vehicle.                         |
| `fiscalidad`                | FLOAT     | Tax-related value.                                            |
| `pvp`                       | TEXT      | Retail price (PVP - Precio Venta Público), as text.           |
| `garantia`                  | TEXT      | Warranty information.                                         |
| `comercial`                 | TEXT      | Salesperson or commercial contact.                            |
| `fecha_reserva`             | TEXT      | Reservation date.                                             |
| `observaciones`             | TEXT      | General observations or notes.                                |
| `color_registro`            | TEXT      | Registered color of the vehicle.                              |
| `fiscalidad_GO`             | TEXT      | Tax-related value for GO system (quoted name).                |
| `marca`                     | TEXT      | Vehicle make/brand. (Key field for API query)                 |
| `color_api`                 | TEXT      | Alternative color field, possibly for API use.                |
| `interior_api`              | TEXT      | Alternative interior field, possibly for API use.             |
| `fiscalidad_api`            | FLOAT     | Tax-related value, possibly for API use.                      |
| `pvp_api`                   | FLOAT     | Retail price (PVP), as a numeric value for API. (Key field for API query) |
| `precio_base_api`           | FLOAT     | Base price, possibly for API use.                             |
| `origen`                    | TEXT      | Origin of the vehicle or data.                                |
| `marca_inv`                 | TEXT      | Make/brand from inventory system.                             |
| `modelo_inv`                | TEXT      | Model from inventory system.                                  |
| `version_inv`               | TEXT      | Version from inventory system.                                |
| `codigo_jato_inv`           | TEXT      | JATO code from inventory system.                              |
| `publicar_inv`              | TEXT      | Publication status in inventory system.                       |
| `fecha_publicado_inv`       | TEXT      | Publication date in inventory system.                         |
| `codigo_progresion`         | TEXT      | Progression code.                                             |
| `tipo_venta`                | TEXT      | Type of sale (e.g., New, Used).                               |
| `clase_vehiculo`            | TEXT      | Vehicle class (e.g., Car, Van).                               |
| `grossvalue`                | FLOAT     | Gross value of the vehicle.                                   |
| `ubicacion`                 | TEXT      | Location of the vehicle.                                      |
| `fecha_factura_compra`      | TEXT      | Purchase invoice date.                                        |
| `vehicle_stock_id`          | TEXT      | Unique identifier for the vehicle stock entry.                |
