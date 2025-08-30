# Application Process Trigger

> A unique trigger that monitors other applications running on your computer. You can create automations that react to when a program, game, or other service is opened or closed.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `process_trigger` |
| Tier | Free |
| Version | 1.0 |
| Author | Awenk Audico |

## How to Use
**Concept:**
This trigger periodically checks the list of running processes on your operating system. If the process name you specify appears (starts) or disappears (stops), it will trigger a preset.

**How to Use:**
1. Create a new Rule.
2. Enter the process name of the application, including its extension (e.g., `notepad.exe`, `chrome.exe`, `Spotify.exe`). You can see process names in the Task Manager (Windows) or Activity Monitor (Mac).
3. Choose whether to trigger when the process 'Starts' or 'Stops'.
4. Select the Preset to run.

**Optimization Examples:**
- **Gaming Mode:** When `valorant.exe` starts, trigger a workflow to mute notifications, open Discord, and dim your room lights.
- **Productivity Mode:** When `Photoshop.exe` starts, run a preset that opens your last project folder and plays a focus playlist on Spotify.

## API Reference

::: triggers.process_trigger.listener
