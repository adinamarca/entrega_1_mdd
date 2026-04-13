"""
Entregable 1: DDD y Patrones de Diseno
=======================================
Demostracion de los 4 casos de uso implementados:
  1. Gestion de Pedidos
  2. Gestion de Repartidores
  3. Asignacion y Despacho
  4. Gestion de Incidencias

Patrones de diseno utilizados:
  - Creacionales: Factory Method, Builder, Singleton, Abstract Factory
  - Estructurales: Adapter, Facade, Decorator
  - Comportamiento: State, Strategy, Observer
"""

from src.despacho.application.despacho_service import DespachoService
from src.despacho.domain.estrategias import (
    AsignacionPorCapacidad,
    AsignacionPorProximidad,
    AsignacionRoundRobin,
)
from src.incidencias.application.incidencia_service import IncidenciaService
from src.incidencias.domain.value_objects import TipoIncidencia
from src.incidencias.infrastructure.in_memory_repo import InMemoryIncidenciaRepository
from src.pedidos.application.pedido_service import PedidoService
from src.pedidos.domain.estados import TransicionInvalidaError
from src.pedidos.infrastructure.in_memory_repo import InMemoryPedidoRepository
from src.repartidores.application.repartidor_service import RepartidorService
from src.repartidores.domain.pool import DriverPool
from src.repartidores.infrastructure.in_memory_repo import InMemoryRepartidorRepository
from src.shared.domain_event import EventBus


SEPARADOR = "=" * 70
SUBSEPARADOR = "-" * 50


def crear_datos_pedido(
    canal: str = "web",
    tipo_entrega: str = "normal",
    tipo_carga: str = "estandar",
    peso: float = 5.0,
    ciudad_destino: str = "Santiago",
    ventana: str | None = None,
) -> dict:
    """Helper para crear datos de pedido de prueba."""
    datos = {
        "origen_calle": "Av. Principal",
        "origen_numero": "100",
        "origen_ciudad": "Santiago",
        "origen_comuna": "Providencia",
        "punto_origen_id": "BOD-001",
        "destino_calle": "Calle Destino",
        "destino_numero": "456",
        "destino_ciudad": ciudad_destino,
        "destino_comuna": "Las Condes",
        "destinatario_nombre": "Juan Perez",
        "destinatario_telefono": "+56912345678",
        "destinatario_email": "juan@email.com",
        "tipo_entrega": tipo_entrega,
        "tipo_carga": tipo_carga,
        "peso_kg": peso,
    }
    if ventana:
        datos["ventana_tiempo"] = ventana
    return datos


def demo_caso_uso_1(pedido_service: PedidoService, event_bus: EventBus) -> list[str]:
    """Caso de uso 1: Gestion de Pedidos.

    Demuestra: Factory Method (canales), Builder (construccion),
    Decorator (validaciones), State (transiciones).
    """
    print(f"\n{SEPARADOR}")
    print("CASO DE USO 1: GESTION DE PEDIDOS")
    print(SEPARADOR)

    pedido_ids = []

    # --- Factory Method: crear pedidos desde distintos canales ---
    print(f"\n{SUBSEPARADOR}")
    print("[Factory Method] Creando pedidos desde distintos canales...")
    print(SUBSEPARADOR)

    canales = ["web", "app_movil", "ecommerce", "partner"]
    for canal in canales:
        pedido = pedido_service.crear_pedido(canal, crear_datos_pedido(canal=canal))
        pedido_ids.append(pedido.pedido_id)
        print(f"  Creado desde canal '{canal}': {pedido}")

    # --- Decorator: validacion con decoradores apilados ---
    print(f"\n{SUBSEPARADOR}")
    print("[Decorator] Validando pedidos con validadores apilados...")
    print(SUBSEPARADOR)

    # Pedido valido
    errores = pedido_service.validar_pedido(pedido_ids[0])
    print(f"  Pedido web - Errores: {errores if errores else 'Ninguno (valido)'}")

    # Pedido express con peso excesivo (debe fallar validacion)
    pedido_express = pedido_service.crear_pedido(
        "web", crear_datos_pedido(tipo_entrega="express", peso=25.0)
    )
    errores = pedido_service.validar_pedido(pedido_express.pedido_id)
    print(f"  Pedido express 25kg - Errores: {errores}")

    # Pedido a zona no atendida
    pedido_zona = pedido_service.crear_pedido(
        "web", crear_datos_pedido(ciudad_destino="Temuco")
    )
    errores = pedido_service.validar_pedido(pedido_zona.pedido_id)
    print(f"  Pedido a Temuco - Errores: {errores}")

    # --- State: transiciones de estado ---
    print(f"\n{SUBSEPARADOR}")
    print("[State] Transiciones de estado del pedido...")
    print(SUBSEPARADOR)

    pid = pedido_ids[0]
    pedido = pedido_service.obtener_pedido(pid)
    print(f"  Estado actual: {pedido.estado_nombre}")

    pedido_service.poner_pendiente(pid)
    print(f"  -> Pendiente de asignacion: {pedido.estado_nombre}")

    # --- State: validacion de transiciones invalidas ---
    print(f"\n{SUBSEPARADOR}")
    print("[State] Transiciones invalidas (errores controlados)...")
    print(SUBSEPARADOR)

    # Intentar poner en ruta un pedido pendiente (no asignado)
    try:
        pedido_service.iniciar_ruta(pid)
    except TransicionInvalidaError as e:
        print(f"  ERROR esperado: {e}")

    # Crear pedido, entregarlo y luego intentar retroceder
    pedido_entrega = pedido_service.crear_pedido("web", crear_datos_pedido())
    pid_e = pedido_entrega.pedido_id
    pedido_service.validar_pedido(pid_e)
    pedido_service.poner_pendiente(pid_e)
    # Simulamos asignacion manual para demostrar state
    pedido_entrega = pedido_service.obtener_pedido(pid_e)
    pedido_entrega.asignar("repartidor-temp")
    pedido_service.iniciar_ruta(pid_e)
    pedido_service.entregar(pid_e)
    print(f"  Pedido entregado: {pedido_entrega.estado_nombre}")

    try:
        pedido_service.iniciar_ruta(pid_e)
    except TransicionInvalidaError as e:
        print(f"  ERROR esperado (retroceder desde entregado): {e}")

    # Cancelar pedido e intentar continuar
    pedido_cancel = pedido_service.crear_pedido("web", crear_datos_pedido())
    pedido_service.cancelar(pedido_cancel.pedido_id)
    print(f"  Pedido cancelado: {pedido_cancel.estado_nombre}")

    try:
        pedido_service.validar_pedido(pedido_cancel.pedido_id)
    except TransicionInvalidaError as e:
        print(f"  ERROR esperado (continuar desde cancelado): {e}")

    # Flujo no lineal: En ruta -> Intento fallido -> Reprogramado -> Asignado
    print(f"\n{SUBSEPARADOR}")
    print("[State] Flujo no lineal: intento fallido y reprogramacion...")
    print(SUBSEPARADOR)
    pedido_nl = pedido_service.crear_pedido("app_movil", crear_datos_pedido(canal="app_movil"))
    pid_nl = pedido_nl.pedido_id
    pedido_service.validar_pedido(pid_nl)
    pedido_service.poner_pendiente(pid_nl)
    pedido_nl = pedido_service.obtener_pedido(pid_nl)
    pedido_nl.asignar("repartidor-temp")
    print(f"  {pedido_nl.estado_nombre}")
    pedido_service.iniciar_ruta(pid_nl)
    print(f"  -> {pedido_nl.estado_nombre}")
    pedido_service.registrar_intento_fallido(pid_nl)
    print(f"  -> {pedido_nl.estado_nombre}")
    pedido_service.reprogramar(pid_nl)
    print(f"  -> {pedido_nl.estado_nombre}")

    return pedido_ids


def demo_caso_uso_2(repartidor_service: RepartidorService) -> list[str]:
    """Caso de uso 2: Gestion de Repartidores.

    Demuestra: Singleton (DriverPool), Repository pattern.
    """
    print(f"\n{SEPARADOR}")
    print("CASO DE USO 2: GESTION DE REPARTIDORES")
    print(SEPARADOR)

    repartidor_ids = []

    # --- Registrar repartidores ---
    print(f"\n{SUBSEPARADOR}")
    print("[Singleton/Repository] Registrando repartidores...")
    print(SUBSEPARADOR)

    repartidores_data = [
        ("Carlos Gomez", 3, 50.0, -33.45, -70.65),
        ("Maria Lopez", 2, 30.0, -33.42, -70.60),
        ("Pedro Diaz", 4, 80.0, -33.40, -70.62),
    ]

    for nombre, max_ped, max_peso, lat, lon in repartidores_data:
        r = repartidor_service.registrar_repartidor(nombre, max_ped, max_peso, lat, lon)
        repartidor_ids.append(r.repartidor_id)
        print(f"  Registrado: {r}")

    # --- Singleton: verificar misma instancia ---
    print(f"\n{SUBSEPARADOR}")
    print("[Singleton] Verificando pool unico...")
    print(SUBSEPARADOR)

    pool1 = DriverPool()
    pool2 = DriverPool()
    print(f"  pool1 is pool2: {pool1 is pool2} (Singleton confirmado)")
    print(f"  Repartidores en pool: {len(pool1.listar_todos())}")

    # --- Consultar disponibilidad ---
    print(f"\n{SUBSEPARADOR}")
    print("[Repository] Consultando disponibilidad...")
    print(SUBSEPARADOR)

    disponibles = repartidor_service.consultar_disponibles()
    print(f"  Disponibles: {len(disponibles)}")
    for r in disponibles:
        print(f"    - {r}")

    # Cambiar disponibilidad
    repartidor_service.cambiar_disponibilidad(repartidor_ids[1], False)
    print(f"\n  Maria Lopez marcada como NO disponible")
    disponibles = repartidor_service.consultar_disponibles()
    print(f"  Disponibles ahora: {len(disponibles)}")

    # Restaurar disponibilidad
    repartidor_service.cambiar_disponibilidad(repartidor_ids[1], True)

    # --- Verificar capacidad ---
    print(f"\n{SUBSEPARADOR}")
    print("[Domain] Verificando regla de capacidad...")
    print(SUBSEPARADOR)

    r = repartidor_service.obtener_repartidor(repartidor_ids[1])
    print(f"  {r.nombre}: capacidad {r.capacidad.max_pedidos} pedidos")
    r.asignar_pedido("pedido-1")
    r.asignar_pedido("pedido-2")
    print(f"  Asignados 2 pedidos. Tiene capacidad: {r.tiene_capacidad}")

    try:
        r.asignar_pedido("pedido-3")
    except ValueError as e:
        print(f"  ERROR esperado (capacidad excedida): {e}")

    # Limpiar para demo posterior
    r.liberar_pedido("pedido-1")
    r.liberar_pedido("pedido-2")

    return repartidor_ids


def demo_caso_uso_3(
    pedido_service: PedidoService,
    despacho_service: DespachoService,
    pedido_ids: list[str],
) -> None:
    """Caso de uso 3: Asignacion y Despacho.

    Demuestra: Strategy (algoritmos), Facade (orquestacion), Adapter (traduccion).
    """
    print(f"\n{SEPARADOR}")
    print("CASO DE USO 3: ASIGNACION Y DESPACHO")
    print(SEPARADOR)

    # Preparar pedido para asignacion
    pid = pedido_ids[0]
    # Ya esta validado y pendiente del caso de uso 1

    # --- Strategy: asignacion por proximidad ---
    print(f"\n{SUBSEPARADOR}")
    print("[Strategy + Facade] Asignacion por proximidad...")
    print(SUBSEPARADOR)

    despacho_service.cambiar_estrategia(AsignacionPorProximidad())
    asignacion = despacho_service.asignar_pedido(pid)
    pedido = pedido_service.obtener_pedido(pid)
    print(f"  Pedido asignado: {pedido}")
    print(f"  Asignacion: {asignacion}")

    # --- Strategy: cambio de estrategia y nuevo pedido ---
    print(f"\n{SUBSEPARADOR}")
    print("[Strategy] Cambiando a estrategia por capacidad...")
    print(SUBSEPARADOR)

    despacho_service.cambiar_estrategia(AsignacionPorCapacidad())

    # Crear y preparar otro pedido
    pedido2 = pedido_service.crear_pedido("ecommerce", crear_datos_pedido(canal="ecommerce"))
    pedido_service.validar_pedido(pedido2.pedido_id)
    pedido_service.poner_pendiente(pedido2.pedido_id)

    asignacion2 = despacho_service.asignar_pedido(pedido2.pedido_id)
    pedido2 = pedido_service.obtener_pedido(pedido2.pedido_id)
    print(f"  Pedido asignado: {pedido2}")
    print(f"  Asignacion: {asignacion2}")

    # --- Reasignacion ---
    print(f"\n{SUBSEPARADOR}")
    print("[Facade] Reasignacion de pedido...")
    print(SUBSEPARADOR)

    despacho_service.cambiar_estrategia(AsignacionRoundRobin())
    nueva_asignacion = despacho_service.reasignar_pedido(pedido2.pedido_id)
    pedido2 = pedido_service.obtener_pedido(pedido2.pedido_id)
    print(f"  Pedido reasignado: {pedido2}")
    print(f"  Nueva asignacion: {nueva_asignacion}")

    # --- Error: intentar asignar pedido no pendiente ---
    print(f"\n{SUBSEPARADOR}")
    print("[Validacion] Intentar asignar pedido no pendiente...")
    print(SUBSEPARADOR)

    pedido_no_listo = pedido_service.crear_pedido("web", crear_datos_pedido())
    try:
        despacho_service.asignar_pedido(pedido_no_listo.pedido_id)
    except ValueError as e:
        print(f"  ERROR esperado: {e}")


def demo_caso_uso_4(
    incidencia_service: IncidenciaService,
    pedido_service: PedidoService,
) -> None:
    """Caso de uso 4: Gestion de Incidencias.

    Demuestra: State (ciclo de incidencia), reglas de negocio (resolucion obligatoria).
    """
    print(f"\n{SEPARADOR}")
    print("CASO DE USO 4: GESTION DE INCIDENCIAS")
    print(SEPARADOR)

    # Crear un pedido entregado para asociar incidencia
    pedido = pedido_service.crear_pedido("web", crear_datos_pedido())
    pid = pedido.pedido_id
    pedido_service.validar_pedido(pid)
    pedido_service.poner_pendiente(pid)
    pedido = pedido_service.obtener_pedido(pid)
    pedido.asignar("repartidor-temp")
    pedido_service.iniciar_ruta(pid)
    pedido_service.entregar(pid)
    print(f"\n  Pedido entregado para demo: {pedido}")

    # --- Registrar incidencia ---
    print(f"\n{SUBSEPARADOR}")
    print("[State] Registrando incidencia sobre pedido entregado...")
    print(SUBSEPARADOR)

    incidencia = incidencia_service.registrar_incidencia(
        pedido_id=pid,
        tipo=TipoIncidencia.PRODUCTO_NO_RECIBIDO,
        descripcion="Cliente indica que no recibio el paquete",
    )
    print(f"  Incidencia creada: {incidencia}")

    # --- Avanzar estados ---
    print(f"\n{SUBSEPARADOR}")
    print("[State] Avanzando ciclo de vida de la incidencia...")
    print(SUBSEPARADOR)

    incidencia_service.iniciar_analisis(incidencia.incidencia_id)
    print(f"  -> {incidencia.estado_nombre}")

    incidencia_service.iniciar_resolucion(incidencia.incidencia_id)
    print(f"  -> {incidencia.estado_nombre}")

    # --- Error: cerrar sin resolucion ---
    print(f"\n{SUBSEPARADOR}")
    print("[Regla de negocio] Intentar cerrar sin resolucion...")
    print(SUBSEPARADOR)

    try:
        incidencia_service.intentar_resolver_sin_resolucion(incidencia.incidencia_id)
    except ValueError as e:
        print(f"  ERROR esperado: {e}")

    # --- Resolver correctamente ---
    print(f"\n{SUBSEPARADOR}")
    print("[State] Resolviendo incidencia con resolucion...")
    print(SUBSEPARADOR)

    incidencia_service.resolver(
        incidencia_id=incidencia.incidencia_id,
        descripcion_resolucion="Se verifico con el repartidor y se confirma entrega fallida",
        accion_tomada="Reenvio programado para manana",
        requiere_reenvio=True,
    )
    print(f"  -> {incidencia.estado_nombre}")
    print(f"  Resolucion: {incidencia.resolucion}")

    # --- Segunda incidencia: producto danado ---
    print(f"\n{SUBSEPARADOR}")
    print("[Domain] Segunda incidencia: producto danado...")
    print(SUBSEPARADOR)

    incidencia2 = incidencia_service.registrar_incidencia(
        pedido_id=pid,
        tipo=TipoIncidencia.PRODUCTO_DANADO,
        descripcion="Paquete llego con dano visible",
    )
    print(f"  Incidencia creada: {incidencia2}")

    incidencias_pedido = incidencia_service.listar_por_pedido(pid)
    print(f"  Total incidencias para este pedido: {len(incidencias_pedido)}")


def main() -> None:
    print("\n" + "=" * 70)
    print("  ENTREGABLE 1: DDD Y PATRONES DE DISENO")
    print("  Logistica de Ultima Milla")
    print("=" * 70)

    # --- Inicializacion (DIP: inyeccion de dependencias) ---
    DriverPool.reset()
    event_bus = EventBus()

    # Observer: suscribir handlers a eventos
    event_bus.subscribe(
        type(None).__mro__[0],  # placeholder
        lambda e: None,
    )

    pedido_repo = InMemoryPedidoRepository()
    repartidor_repo = InMemoryRepartidorRepository()
    incidencia_repo = InMemoryIncidenciaRepository()

    pedido_service = PedidoService(pedido_repo, event_bus)
    repartidor_service = RepartidorService(repartidor_repo)
    despacho_service = DespachoService(
        pedido_repo, AsignacionPorProximidad(), event_bus
    )
    incidencia_service = IncidenciaService(incidencia_repo, pedido_repo, event_bus)

    # Observer: registrar handler para cambios de estado
    from src.pedidos.domain.eventos import PedidoCambioEstado

    event_bus.subscribe(
        PedidoCambioEstado,
        lambda e: print(f"    [Observer] Evento: {e.estado_anterior} -> {e.estado_nuevo}"),
    )

    # --- Ejecutar los 4 casos de uso ---
    pedido_ids = demo_caso_uso_1(pedido_service, event_bus)
    repartidor_ids = demo_caso_uso_2(repartidor_service)
    demo_caso_uso_3(pedido_service, despacho_service, pedido_ids)
    demo_caso_uso_4(incidencia_service, pedido_service)

    # --- Resumen ---
    print(f"\n{SEPARADOR}")
    print("RESUMEN")
    print(SEPARADOR)
    print(f"  Pedidos creados: {len(pedido_service.listar_pedidos())}")
    print(f"  Repartidores registrados: {len(repartidor_service.listar_todos())}")
    print(f"  Repartidores disponibles: {len(repartidor_service.consultar_disponibles())}")
    print()
    print("  Patrones demostrados:")
    print("    Creacionales: Factory Method, Builder, Singleton")
    print("    Estructurales: Adapter, Facade, Decorator")
    print("    Comportamiento: State, Strategy, Observer")
    print()
    print("  Principios SOLID aplicados: SRP, OCP, LSP, ISP, DIP")
    print(f"\n{SEPARADOR}\n")


if __name__ == "__main__":
    main()
