#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\event_bus_service\event_bus_service.py
# JUMLAH BARIS : 49
#######################################################################

import json
import threading
from typing import Dict, Any, Callable
from ..base_service import BaseService
class EventBusService(BaseService):
    """
    Service that provides a centralized message bus for different parts of the application
    to communicate without being directly coupled.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self._subscribers: Dict[str, Dict[str, Callable]] = {}
        self.kernel.write_to_log("Service 'EventBus' initialized.", "DEBUG")
    def publish(self, event_name: str, event_data: Dict[str, Any], publisher_id: str = "SYSTEM"):
        """
        Publishes an event to all registered subscribers.
        Args:
            event_name (str): The name of the event to publish.
            event_data (Dict[str, Any]): The data payload to send with the event.
            publisher_id (str): The ID of the module or service publishing the event.
        """
        self.kernel.write_to_log(f"EVENT PUBLISHED: Name='{event_name}', Publisher='{publisher_id}'", "INFO")
        self.kernel.write_to_log(f"EVENT DATA: {json.dumps(event_data, indent=2)}", "DETAIL")
        if event_name in self._subscribers:
            for subscriber_id, callback in list(self._subscribers[event_name].items()):
                self.kernel.write_to_log(f"EventBus: Notifying subscriber '{subscriber_id}' for event '{event_name}'...", "DEBUG")
                try:
                    threading.Thread(target=callback, args=(event_data,)).start()
                except Exception as e:
                    self.kernel.write_to_log(f"Error executing subscriber '{subscriber_id}' for event '{event_name}': {e}", "ERROR")
    def subscribe(self, event_name: str, subscriber_id: str, callback: Callable):
        """
        Subscribes a component to a specific event.
        Args:
            event_name (str): The name of the event to subscribe to.
            subscriber_id (str): A unique ID for the subscriber to prevent duplicates.
            callback (Callable): The function to call when the event is published.
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = {}
        self._subscribers[event_name][subscriber_id] = callback
        self.kernel.write_to_log(f"SUBSCRIBE: Component '{subscriber_id}' successfully subscribed to event '{event_name}'.", "INFO")
