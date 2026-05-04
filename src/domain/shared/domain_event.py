from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Clase base para todos los eventos de dominio."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


class EventBus:
    """Observer pattern: bus de eventos para desacoplar emisores de suscriptores."""

    def __init__(self) -> None:
        self._subscribers: dict[type, list] = {}

    def subscribe(self, event_type: type, handler: callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._subscribers.get(type(event), []):
            handler(event)
