# File System Trigger

> Monitors a folder and automatically reacts to file activity. This trigger is your system's eyes and ears within the file explorer, ready to act on new files, changes, or deletions.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `file_system_trigger` |
| Tier | Free |
| Version | 1.0 |
| Author | Awenk Audico |

## How to Use
**Concept:**
This trigger uses a 'watchdog' to monitor a directory. When a specified activity occurs (e.g., a new file appears), it will immediately trigger a preset.

**How to Use:**
1. Drag & drop this trigger to the right.
2. Click 'Browse...' to select the folder you want to watch.
3. Check the relevant event types: 'On Created', 'On Modified', or 'On Deleted'. You can select more than one.
4. Specify the Preset to be executed.

**Optimization Examples:**
- **Automated ETL:** Monitor an 'uploads' folder. Every time a new CSV file arrives, automatically run a workflow to read, process, and insert its data into a database.
- **Image Conversion:** Watch a 'raw_images' folder. For every new .PNG file, trigger a workflow to convert it to .JPG and move it to another folder.

## API Reference

::: triggers.file_system_trigger.listener
