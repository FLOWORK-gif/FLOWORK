# Internal Event Bus Trigger

> Creates reactive workflows. This trigger listens for 'signals' or 'events' published by other modules, allowing you to build interconnected and intelligent systems.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `event_bus_trigger` |
| Tier | Free |
| Version | 1.0.0 |
| Author | Flowork Core |

## How to Use
**Concept:**
The Event Bus is a central message board. One module (the 'Publisher') can shout a message (an event), and this trigger (the 'Subscriber') will hear it if it's interested in the message topic.

**How to Use:**
1. In one workflow, use the 'Publish Event' module to send a signal when an important task is complete. Give the event a clear name, e.g., `PROCESS_A_COMPLETE`.
2. In the Trigger Manager page, create a new Rule using this trigger.
3. In its properties, enter the exact same event name (`PROCESS_A_COMPLETE`).
4. Select another workflow that you want to run in response.

**Optimization Examples:**
- **Chained Workflows:** Automatically run the 'Process B' workflow ONLY IF the 'Process A' workflow has completed successfully and published an event.
- **Centralized Notifications:** Several different workflows can publish a `SEND_CRITICAL_NOTIFICATION` event, and a single workflow triggered by this event is responsible for sending it to Telegram.

## API Reference

::: triggers.event_bus_trigger.listener
