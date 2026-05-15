# Entregable 2 — Servicio Web de Logistica Ultima Milla

Iteracion del Entregable 1 expuesto como **servicio web HTTP** con FastAPI bajo arquitectura **Cliente-Servidor + Layered + Serverless complementario**.

## Requisitos

- Python 3.10+
- `pip install -r requirements.txt`

## Ejecucion

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Una vez levantado:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health: <http://localhost:8000/health>

## Tests

```bash
pytest -v
```

22 tests cubren autenticacion/autorizacion, los 4 casos de uso y las reglas de negocio.

## Usuarios demo (definidos en `src/infrastructure/auth/roles.py`)

| Usuario | Password | Rol |
|---|---|---|
| operador1 | op123 | operador |
| repartidor1 | rep123 | repartidor |
| admin1 | admin123 | admin |
| integracion1 | int123 | integracion |

## Flujo de prueba completo

```bash
# 1. Obtener token (operador)
TOKEN=$(curl -sS -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"operador1","password":"op123"}' | jq -r .access_token)

# 2. Registrar un repartidor (con token de admin)
ADMIN=$(curl -sS -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"admin123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/repartidores \
  -H "Authorization: Bearer $ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Carlos","max_pedidos":3,"max_peso_kg":50,"latitud":-33.45,"longitud":-70.65}'

# 3. Crear un pedido
PID=$(curl -sS -X POST http://localhost:8000/pedidos \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "canal":"web",
    "origen":{"calle":"Av P","numero":"100","ciudad":"Santiago","comuna":"Providencia"},
    "punto_origen_id":"BOD-001",
    "destino":{"calle":"Calle D","numero":"456","ciudad":"Santiago","comuna":"Las Condes"},
    "destinatario":{"nombre":"Juan","telefono":"+56912345678"},
    "tipo_entrega":"express","tipo_carga":"estandar","peso_kg":5
  }' | jq -r .pedido_id)

# 4. Validar y poner pendiente
curl -X POST http://localhost:8000/pedidos/$PID/validar -H "Authorization: Bearer $TOKEN"

curl -X PUT http://localhost:8000/pedidos/$PID/estado \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"accion":"poner_pendiente"}'

# 5. Asignar (eligiendo estrategia)
curl -X POST http://localhost:8000/pedidos/$PID/asignar \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"estrategia":"proximidad"}'

# 6. Registrar incidencia
curl -X POST http://localhost:8000/incidencias \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"pedido_id\":\"$PID\",\"tipo\":\"retraso\",\"descripcion\":\"Demora reportada\"}"
```

## Arquitectura

```
src/
├── api/                          # Capa de Presentacion (Cliente-Servidor)
│   ├── app.py                    # Factory FastAPI, wire de handlers serverless
│   ├── dependencies.py           # DI container
│   ├── controllers/              # Endpoints HTTP (MVC: Controllers)
│   ├── middleware/               # auth + error_handler
│   └── schemas/                  # DTOs Pydantic (request/response)
│
├── application/                  # Capa Service Layer (orquesta casos de uso)
│   └── *_service.py              # Reutilizados del Entregable 1
│
├── domain/                       # Capa de Dominio (entidades, reglas, patrones GoF)
│   ├── shared/                   # Value objects compartidos
│   ├── pedidos/                  # Aggregate + State + Factory + Builder + Decorator
│   ├── repartidores/             # Entity + Singleton (DriverPool)
│   ├── despacho/                 # Asignacion + Strategy
│   └── incidencias/              # Aggregate + State
│
├── infrastructure/               # Capa de Infraestructura (implementaciones concretas)
│   ├── repositories/             # InMemory repos (Repository pattern)
│   ├── auth/                     # JWT + RBAC
│   └── events/                   # (reservado para event bus externo)
│
└── serverless/                   # Componentes event-driven (FaaS simulados)
    ├── notificaciones_handler.py # Reacciona a PedidoCambioEstado
    ├── webhook_handler.py        # Reacciona a PedidoCreado
    └── reportes_handler.py       # Job batch
```

## Endpoints expuestos

| Metodo | Ruta | Caso de uso | Roles permitidos |
|---|---|---|---|
| POST | `/auth/login` | Login (obtiene JWT) | publico |
| POST | `/pedidos` | Crear pedido | operador, integracion |
| GET | `/pedidos/{id}` | Consultar pedido | todos |
| POST | `/pedidos/{id}/validar` | Validar (Decorator chain) | operador |
| PUT | `/pedidos/{id}/estado` | Cambiar estado (State pattern) | operador, repartidor |
| POST | `/repartidores` | Registrar repartidor | admin |
| GET | `/repartidores/disponibles` | Listar disponibles | operador, admin |
| PUT | `/repartidores/{id}/disponibilidad` | Cambiar disponibilidad | repartidor, admin |
| POST | `/pedidos/{id}/asignar` | Asignar (Facade + Strategy) | operador |
| POST | `/pedidos/{id}/reasignar` | Reasignar | operador |
| POST | `/incidencias` | Registrar incidencia | operador, repartidor |
| POST | `/incidencias/{id}/analizar` | Iniciar analisis | operador, admin |
| POST | `/incidencias/{id}/resolver-iniciar` | Iniciar resolucion | operador, admin |
| PUT | `/incidencias/{id}/resolver` | Cerrar con resolucion | operador, admin |
| GET | `/health` | Healthcheck | publico |

## Decisiones arquitectonicas

Documentadas en el informe (pendiente):

- **Estilo:** Cliente-Servidor + Layered + Serverless complementario
- **Atributos de calidad priorizados:** Disponibilidad, Rendimiento, Escalabilidad, Seguridad, Modificabilidad
- **Patrones arquitectonicos:** Service Layer, Repository, MVC (adaptado a REST)
- **Patrones GoF (del Entregable 1, intactos):** Factory Method, Builder, Singleton, State, Strategy, Adapter, Facade, Decorator, Observer
