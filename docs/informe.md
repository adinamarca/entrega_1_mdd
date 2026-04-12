# Entregable 1: DDD y Patrones de Diseno

**Asignatura:** Metodologia de Diseno de Software  
**Universidad de Valparaiso - Escuela de Ingenieria Informatica**  
**Fecha:** Abril 2026

---

## 1. Resumen Ejecutivo

El presente informe documenta el diseno y la implementacion de una propuesta de arquitectura de software para una empresa de logistica de ultima milla. Utilizando Domain-Driven Design (DDD) como enfoque principal, se modelo el dominio del negocio identificando 6 bounded contexts, se definio un lenguaje ubicuo consistente y se elaboro un context map que describe las relaciones entre los componentes del sistema. La implementacion de 4 casos de uso en Python demuestra la aplicacion coherente de 10 patrones de diseno (creacionales, estructurales y de comportamiento) y los 5 principios SOLID, garantizando un sistema desacoplado, extensible y alineado con el dominio del negocio.

---

## 2. Introduccion

Las empresas de logistica de ultima milla enfrentan desafios crecientes a medida que escalan sus operaciones. La integracion con multiples comercios, plataformas de e-commerce y canales propios genera una complejidad que, sin una arquitectura adecuada, deriva en sistemas fragiles, inconsistentes y dificiles de evolucionar.

El problema central no es tecnologico, sino conceptual: cuando distintas areas del negocio (ventas, operaciones, postventa, soporte) desarrollan sus sistemas de forma independiente, se generan representaciones contradictorias del mismo dominio. Un pedido puede estar "entregado" para operaciones pero "en reclamo" para soporte. Un repartidor puede figurar como disponible en un sistema y ocupado en otro.

Domain-Driven Design (DDD) aborda esta complejidad proponiendo que el software debe ser un reflejo fiel del dominio del negocio. A traves del lenguaje ubicuo, los bounded contexts y el context map, DDD permite separar responsabilidades sin perder coherencia global. Complementariamente, los patrones de diseno ofrecen soluciones probadas a problemas recurrentes de estructura y comportamiento, mientras que los principios SOLID garantizan que el codigo resultante sea mantenible, extensible y testeable.

Este trabajo aplica estos tres pilares (DDD, patrones de diseno y SOLID) al dominio de logistica de ultima milla, produciendo un modelo de dominio completo y una implementacion funcional de 4 casos de uso que evidencian la coherencia entre el diseno y el codigo.

---

## 3. Problema

Una empresa de logistica de ultima milla ha experimentado un crecimiento acelerado, integrandose con multiples comercios, plataformas de e-commerce y canales propios. Su operacion se sostiene sobre sistemas desarrollados independientemente por distintas areas, generando dificultades para coordinar el ciclo completo de un pedido. El negocio involucra areas de ventas, operaciones, postventa y soporte, cada una con responsabilidades claras pero con dinamicas propias. El comportamiento del sistema es altamente dinamico: un pedido puede cambiar de prioridad, reingresar al flujo, escalar a soporte o generar multiples eventos a lo largo de su ciclo de vida, y no siempre existe una unica representacion consistente de su estado.

---

## 4. Solucion

### 4.1 Diagrama de Dominio

El diagrama de dominio completo modela las 6 areas funcionales del sistema con sus entidades, value objects y relaciones. Se identifica a `Pedido` e `Incidencia` como Aggregate Roots principales.

![Diagrama de Dominio](diagramas/Diagrama%20de%20Dominio%20-%20Logistica%20Ultima%20Milla.png)

*Archivo fuente: `docs/diagramas/dominio.puml`*

### 4.2 Lenguaje Ubicuo

| Termino | Definicion |
|---|---|
| **Pedido** | Solicitud de entrega de un paquete desde un origen a un destino, creada desde un canal especifico. Es la entidad central del dominio. |
| **Canal** | Medio por el cual se origina un pedido: web, aplicacion movil, plataforma e-commerce o partner externo. |
| **Repartidor** | Persona encargada de ejecutar la entrega fisica del pedido. Tiene capacidad limitada y ubicacion rastreable. |
| **Despacho** | Proceso de asignar un pedido validado a un repartidor disponible, considerando estrategias de seleccion. |
| **Asignacion** | Vinculo formal entre un pedido y un repartidor para su entrega. Puede desactivarse en caso de reasignacion. |
| **Ruta** | Trayecto planificado que agrupa uno o mas pedidos para entrega secuencial por un repartidor. |
| **Incidencia** | Evento anomalo asociado a un pedido que requiere investigacion y resolucion formal. |
| **Intento de entrega** | Accion de intentar entregar un pedido que puede resultar exitosa o fallida. |
| **Reprogramacion** | Reagendamiento de un pedido tras un intento de entrega fallido. |
| **Ventana de tiempo** | Rango horario en el que se espera realizar la entrega (aplica a entregas programadas). |
| **Capacidad** | Cantidad maxima de pedidos que un repartidor puede transportar simultaneamente. |
| **Validacion** | Verificacion de que un pedido cumple con la informacion minima requerida para ser procesado. |
| **Tipo de entrega** | Clasificacion de la entrega: normal, express o programada. Cada tipo tiene reglas de validacion distintas. |
| **Tipo de carga** | Clasificacion del contenido: estandar, fragil o voluminoso. Afecta la asignacion de repartidor. |
| **Resolucion** | Resultado formal de la investigacion de una incidencia. Incluye descripcion, accion tomada e indicacion de reenvio. |

### 4.3 Bounded Contexts

Se identificaron 6 bounded contexts organizados en tres niveles de relevancia:

| Bounded Context | Subdominio | Tipo | Responsabilidad |
|---|---|---|---|
| **Pedidos** | Gestion Comercial | Core | Crear, validar y gestionar el ciclo de vida completo del pedido |
| **Repartidores** | Gestion de Flota | Core | Registrar repartidores, gestionar disponibilidad y capacidad |
| **Despacho** | Logistica | Core | Asignacion automatica/manual de pedidos a repartidores |
| **Rutas** | Logistica | Supporting | Definicion, ajuste dinamico y seguimiento de rutas |
| **Tracking** | Experiencia Cliente | Supporting | Visualizacion de estados, notificaciones, registro de eventos |
| **Incidencias** | Soporte | Generic | Reclamos, gestion de casos y resoluciones |

![Bounded Contexts](diagramas/Bounded%20Contexts.png)

*Archivo fuente: `docs/diagramas/bounded_contexts.puml`*

### 4.4 Context Map

El context map define las relaciones entre los bounded contexts:

![Context Map](diagramas/Context%20Map.png)

*Archivo fuente: `docs/diagramas/context_map.puml`*

### 4.5 Relaciones entre Contextos

| Relacion | Tipo | Descripcion |
|---|---|---|
| Pedidos -> Despacho | **Customer/Supplier** | Pedidos actua como proveedor de datos para que Despacho pueda realizar asignaciones. Despacho consume la informacion del pedido. |
| Repartidores -> Despacho | **Customer/Supplier** | Repartidores provee informacion de disponibilidad y capacidad al proceso de despacho. |
| Despacho -> Rutas | **Customer/Supplier** | Despacho alimenta las rutas con pedidos asignados para su planificacion. |
| Pedidos -> Tracking | **Conformist** | Tracking se adapta completamente al modelo de Pedidos para visualizar estados sin influir en el. |
| Pedidos -> Incidencias | **Customer/Supplier** | Incidencias referencia pedidos para asociar reclamos. Pedidos no conoce a Incidencias. |
| Tracking -> Notificaciones externas | **ACL** | Anti-Corruption Layer protege al dominio de los detalles de sistemas de notificacion externos. |
| Pedidos -> E-commerce/Partners | **ACL** | Adapter pattern traduce formatos de canales externos al modelo interno de pedidos. |

### 4.6 Patrones de Diseno

#### Patrones Creacionales

| Patron | Ubicacion en el problema | Justificacion |
|---|---|---|
| **Factory Method** | Creacion de pedidos desde distintos canales (Web, App, E-commerce, Partner) | Cada canal produce un pedido con datos y validaciones especificas. Agregar un nuevo canal requiere solo crear una nueva subclase de `PedidoFactory`, sin modificar el codigo existente. Aplica OCP. *Archivos: `src/pedidos/domain/factory.py`* |
| **Builder** | Construccion del objeto Pedido con multiples campos | El Pedido tiene campos obligatorios (origen, destino, tipo entrega, carga) y condicionales (ventana de tiempo solo para entregas programadas). Builder permite una construccion paso a paso, legible y controlada. *Archivo: `src/pedidos/domain/builder.py`* |
| **Singleton** | Pool de repartidores (`DriverPool`) | Se requiere un unico punto de acceso global para consultar la disponibilidad de la flota completa de repartidores. Multiples instancias generarian inconsistencias en la asignacion. *Archivo: `src/repartidores/domain/pool.py`* |

#### Patrones Estructurales

| Patron | Ubicacion en el problema | Justificacion |
|---|---|---|
| **Adapter** | Integracion de canales externos al formato interno de pedido | Los canales externos (e-commerce, partners) tienen interfaces distintas al modelo interno. El Adapter traduce estos formatos sin modificar el core del sistema. *Archivo: `src/despacho/application/adapter.py`* |
| **Facade** | Servicio de despacho (`DespachoService`) | El proceso de asignacion involucra multiples operaciones: buscar repartidor, validar capacidad, asignar pedido, crear asignacion, publicar evento. La Facade expone una interfaz simple (`asignar_pedido()`) que orquesta todo internamente. *Archivo: `src/despacho/application/despacho_service.py`* |
| **Decorator** | Validaciones apilables sobre pedidos | Se requieren distintas capas de validacion (base, express, programada, zona) que pueden combinarse sin modificar la clase base. Cada decorador agrega una verificacion especifica. *Archivo: `src/pedidos/domain/validador.py`* |

#### Patrones de Comportamiento

| Patron | Ubicacion en el problema | Justificacion |
|---|---|---|
| **State** | Ciclo de vida del Pedido (9 estados) y de la Incidencia (4 estados) | Las transiciones entre estados tienen reglas complejas y no lineales. State encapsula el comportamiento de cada estado y define las transiciones validas, evitando condicionales extensos. *Archivos: `src/pedidos/domain/estados.py`, `src/incidencias/domain/estados.py`* |
| **Strategy** | Algoritmos de asignacion de repartidores | Existen multiples criterios para seleccionar repartidor: proximidad, capacidad disponible, round-robin. Strategy permite intercambiar algoritmos en tiempo de ejecucion sin modificar el servicio de despacho. *Archivo: `src/despacho/domain/estrategias.py`* |
| **Observer** | Notificaciones ante cambios de estado del pedido | El EventBus desacopla la emision de eventos de dominio de los handlers que reaccionan a ellos (notificaciones, logging, etc.). *Archivo: `src/shared/domain_event.py`* |

### 4.7 Principios SOLID

| Principio | Donde se evidencia | Ejemplo concreto |
|---|---|---|
| **S - Single Responsibility** | Cada clase tiene una unica responsabilidad claramente definida | `Pedido` solo modela la entidad, `ValidadorPedido` solo valida, `PedidoRepository` solo persiste, `PedidoService` solo orquesta casos de uso. No hay clases "dios" que mezclen responsabilidades. |
| **O - Open/Closed** | Las clases estan abiertas para extension pero cerradas para modificacion | Factory Method: agregar `PartnerPedidoFactory` no requiere modificar fabricas existentes. Strategy: agregar `AsignacionPorZona` no modifica `DespachoService`. Decorator: agregar `ValidadorFragil` no modifica `ValidadorBase`. |
| **L - Liskov Substitution** | Las subclases pueden sustituir a sus clases base sin alterar el comportamiento | Todos los estados del pedido implementan `EstadoPedido` y son intercambiables. Todas las estrategias implementan `EstrategiaAsignacion` con el mismo contrato. Todas las fabricas implementan `PedidoFactory`. |
| **I - Interface Segregation** | Las interfaces son pequenas y especificas | `PedidoRepository` define solo los metodos de persistencia de pedidos. `RepartidorRepository` define los de repartidores. `ValidadorPedido` expone un solo metodo `validar()`. No hay interfaces monoliticas. |
| **D - Dependency Inversion** | Los modulos de alto nivel dependen de abstracciones | `PedidoService` recibe `PedidoRepository` (ABC abstracto), no `InMemoryPedidoRepository`. `DespachoService` recibe `EstrategiaAsignacion` (ABC), no una implementacion concreta. La inyeccion de dependencias se realiza en `main.py`. |

---

## 5. Conclusion

El desarrollo de este entregable permitio abordar un problema de complejidad real (logistica de ultima milla) aplicando de forma sistematica los principios de Domain-Driven Design, patrones de diseno y principios SOLID.

La separacion en 6 bounded contexts refleja fielmente las areas funcionales del negocio, cada una con su propio modelo de dominio y lenguaje. El context map explicita las dependencias entre contextos, evitando acoplamientos ocultos. La implementacion de los 4 casos de uso demuestra que el modelo no es solo teorico: las reglas de negocio (transiciones de estado, capacidad de repartidores, validaciones de pedidos, resoluciones obligatorias de incidencias) estan codificadas en el dominio y se ejecutan de forma consistente.

Los 10 patrones de diseno aplicados no fueron elegidos arbitrariamente, sino que responden a necesidades concretas del problema: State para los ciclos de vida no lineales, Factory Method para la diversidad de canales, Strategy para la flexibilidad en la asignacion, Decorator para la composicion de validaciones, y Facade para la simplificacion de procesos complejos.

La aplicacion de SOLID se evidencia en un codigo desacoplado donde cada clase tiene una unica razon de cambio, las extensiones no requieren modificaciones al codigo existente, y las dependencias apuntan siempre a abstracciones. Esto produce un sistema que puede evolucionar con el negocio sin introducir fragilidad.
