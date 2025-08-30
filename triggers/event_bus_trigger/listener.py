#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\triggers\event_bus_trigger\listener.py
# JUMLAH BARIS : 53
#######################################################################

from flowork_kernel.api_contract import BaseTriggerListener
class EventBusListener(BaseTriggerListener):
    """
    Listener that listens for specific events on the internal Flowork Event Bus.
    """
    def __init__(self, trigger_id: str, config: dict, services: dict, **kwargs):
        super().__init__(trigger_id, config, services, **kwargs)
        self.logger(f"EventBusListener instance created for rule_id: {self.rule_id}", "DEBUG")
        self.event_name_to_listen = self.config.get("event_name", "")
        self.event_bus = getattr(self, 'event_bus', None)
    def start(self):
        """
        Subscribes to the specified event on the Event Bus.
        """
        if not self.event_name_to_listen:
            self.logger(f"Event Bus Trigger '{self.rule_id}': Event name not configured. Trigger will not start.", "ERROR")
            return
        if not self.event_bus:
            self.logger(f"Event Bus Trigger '{self.rule_id}': Event Bus service is not available. Trigger failed.", "ERROR")
            return
        subscriber_id = f"trigger_listener_{self.rule_id}"
        self.event_bus.subscribe(self.event_name_to_listen, subscriber_id, self._handle_internal_event)
        self.is_running = True
        self.logger(f"Event Bus Trigger '{self.rule_id}': Started listening for event '{self.event_name_to_listen}'.", "INFO")
    def stop(self):
        """
        Unsubscribes from the Event Bus.
        (Conceptually, as EventBus currently lacks an unsubscribe method).
        """
        if self.is_running:
            self.is_running = False
            self.logger(f"Event Bus Trigger '{self.rule_id}': Subscription to event '{self.event_name_to_listen}' stopped (conceptually).", "INFO")
    def _handle_internal_event(self, event_data_from_bus: dict):
        """
        This method is automatically called by the EventBus when the event occurs.
        """
        if not self.is_running:
            return
        event_data_to_report = {
            "trigger_id": self.trigger_id,
            "rule_id": self.rule_id,
            "event_type": "event_bus_received",
            "source_event_name": self.event_name_to_listen,
            "source_event_data": event_data_from_bus
        }
        self._on_event(event_data_to_report)
