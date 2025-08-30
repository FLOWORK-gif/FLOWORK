# Time Trigger (Cron)

> Automatically executes a workflow based on a very specific and recurring time schedule. This is the backbone for all scheduled tasks, from daily reports to weekly maintenance.

## Metadata

| Attribute | Value |
| --- | --- |
| ID | `cron_trigger` |
| Tier | Free |
| Version | 1.0 |
| Author | Awenk Audico |

## How to Use
**Concept:**
Cron is an industry-standard task scheduler. You define the execution time using a pattern (e.g., 'every day at 5 PM', 'every Monday').

**How to Use:**
1. Drag & drop this trigger to the right panel to create a new Rule.
2. In the editor window, use the interactive UI to set your schedule. Choose between 'Every X Minutes', 'Hourly', 'Daily', or 'Weekly'.
3. Select the 'Preset to Run' from the dropdown list.
4. Ensure 'Enable This Rule' is checked, then Save.

**Optimization Examples:**
- **Daily Reports:** Set to run 'Daily' at '09:00' to send a sales report email.
- **Data Sync:** Schedule to run 'Every 30 Minutes' to fetch the latest data from an API.

