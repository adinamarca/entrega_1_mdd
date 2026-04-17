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

## Justificación de Patrones y Principios SOLID

Para abordar la complejidad de la logística de última milla, se aplicaron los siguientes patrones y principios, optimizando la mantenibilidad y modularidad:

- **Patrones Creacionales**
- Factory Method: Permite crear distintos tipos de pedidos según canal y tipo, encapsulando la lógica de instanciación.
- Builder: Facilita la construcción de pedidos con diferentes combinaciones de datos requeridos/progresivos.
- Singleton: Garantiza un único EventBus centralizado para eventos de dominio, evitando inconsistencias.

- **Patrones Estructurales**

- Adapter: Unifica la entrada de pedidos provenientes de múltiples fuentes al modelo interno.
- Facade: Simplifica la interface de asignación/despacho, ocultando su complejidad.
- Decorator: Añade dinámicamente características a los pedidos, como requisitos especiales, sin modificar la clase base.

- **Patrones de Comportamiento**

- State: Gestiona el ciclo de vida dinámico de los pedidos y sus transiciones de estado válidas.
- Strategy: Permite intercambiar algoritmos de asignación según condiciones operativas.
- Observer: Implementado vía EventBus para notificar y coordinar reacciones entre contextos desacoplados.

- **Principios SOLID**

- SRP: Cada clase asume una única responsabilidad (ej. Pedido, PedidoRepository).
- OCP: Nuevas estrategias y funcionalidades pueden agregarse sin modificar el código existente.
- LSP: Las subclases de estados mantienen la integridad de las transiciones de Pedido.
- ISP: Interfaces específicas y separadas para cada tipo de repositorio (lectura/escritura).
- DIP: Los servicios dependen de abstracciones, facilitando simulación y pruebas.

## Regenerar Diagramas

```bash
cd docs/diagramas
plantuml -tpng *.puml
```
