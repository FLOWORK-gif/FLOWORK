```markdown
# Chapter 5: Practical Scenarios & Examples

This chapter demonstrates how to combine API calls to achieve larger goals.

## 5.1. Create & Run a Preset from Scratch via API

This is a common workflow: defining a workflow, saving it, and then running it, all without touching the UI.

#### Step 1: Prepare Workflow Data in JSON Format

Create a file on your computer, for example, `new_workflow.json`, with the following content. This defines a simple `START -> Debug Popup` workflow.
```json
{
    "name": "My Cool API Preset",
    "workflow_data": {
        "nodes": [
            {
                "id": "a1b2c3d4-e5f6-4a3b-8c7d-1e2f3a4b5c6d",
                "name": "START",
                "module_id": "set_variable_module",
                "config_values": {
                    "note_variable": "This workflow was created and run entirely via API!"
                }
            },
            {
                "id": "f6e5d4c3-b2a1-4c3d-8e7f-6a5b4c3d2e1f",
                "name": "Show Output (Popup)",
                "module_id": "debug_popup_module"
            }
        ],
        "connections": [
            {
                "id": "c1d2e3f4-a5b6-4a3b-8c7d-9f8e7d6c5b4a",
                "from": "a1b2c3d4-e5f6-4a3b-8c7d-1e2f3a4b5c6d",
                "to": "f6e5d4c3-b2a1-4c3d-8e7f-6a5b4c3d2e1f"
            }
        ]
    }
}