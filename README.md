# Entregable 1: DDD y Patrones de Diseno

Logistica de Ultima Milla - Metodologia de Diseno de Software, Universidad de Valparaiso.

## Requisitos

- Python 3.10+
- PlantUML (opcional, para regenerar diagramas)

## Ejecucion

Desde la raiz del proyecto `entregable_1/`:

```bash
python3 -m src.main
```

Esto ejecuta los 4 casos de uso implementados:

1. **Gestion de Pedidos** - Creacion multicanal, validacion, transiciones de estado
2. **Gestion de Repartidores** - Registro, disponibilidad, capacidad
3. **Asignacion y Despacho** - Asignacion automatica, reasignacion, cambio de estrategia
4. **Gestion de Incidencias** - Registro, ciclo de vida, resolucion

## Estructura del Proyecto

```
entregable_1/
├── src/
│   ├── shared/              # Shared Kernel (Value Objects, EventBus)
│   ├── pedidos/             # BC: Gestion de Pedidos
│   ├── repartidores/        # BC: Gestion de Repartidores
│   ├── despacho/            # BC: Asignacion y Despacho
│   ├── incidencias/         # BC: Gestion de Incidencias
│   └── main.py              # Demo de los 4 casos de uso
├── docs/
│   ├── informe.md           # Informe completo
│   └── diagramas/           # Diagramas PlantUML + PNG generados
└── README.md
```

## Patrones de Diseno

- **Creacionales:** Factory Method, Builder, Singleton
- **Estructurales:** Adapter, Facade, Decorator
- **Comportamiento:** State, Strategy, Observer

## Regenerar Diagramas

```bash
cd docs/diagramas
plantuml -tpng *.puml
```
