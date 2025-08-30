# Chapter 2: Getting Started

Let's make your first API call in minutes.

## 2.1. Prerequisites
Before you begin, ensure you have:
- A running Flowork project on your machine.
- All Python dependencies installed (especially `requests`).
- A tool for making HTTP calls (e.g., `curl`, Postman, Insomnia).

## 2.2. Enabling the API Server
The API server is part of the Flowork application itself. To run it:

1.  **Ensure Correct Configuration**: Open your `data/settings.json` file and make sure `"webhook_enabled"` is set to `true`.
2.  **Run Flowork**: Execute `python main.py` in your terminal.
3.  **Verify the Log**: You should see a success message that the API server is running on port 8989.

## 2.3. Your First API Call
Open a **second terminal** (leave the first one running Flowork) and execute the following `curl` command to get a list of all existing presets:
```bash
curl -X GET http://localhost:8989/api/v1/presets