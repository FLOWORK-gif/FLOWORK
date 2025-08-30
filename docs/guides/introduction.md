# Chapter 1: Introduction & API-First Philosophy

## 1.1. Welcome to the Flowork Engine
At its core, Flowork is a powerful workflow execution engine. The graphical user interface (UI) you see is just one of many ways to interact with this engine. This API opens a direct "door" to that engine, allowing you to automate it further, integrate it with other systems, or even build your own custom interfaces.

## 1.2. API-First Philosophy
The development of this API is grounded in an API-First philosophy. This means the core of Flowork is its backend, capable of running independently (headless), with all its functionality exposed through a stable and documented API. The existing graphical UI is treated as just another API client; it holds no special privileges or "backdoor" access. This approach ensures that Flowork can evolve into a true ecosystem, where a wide variety of applications and services can be built on top of it.

## 1.3. General Architecture
Communication with the Flowork API always follows this pattern:

1.  **Client**: This can be the Flowork UI itself, your Python script, Postman, or a `curl` command from the terminal.
2.  **Local API Server**: Requests from the Client are received by the `ApiServerService` running locally at `http://localhost:8989`.
3.  **Kernel & Services**: The API server then passes the command to the Kernel and the relevant services for execution.
4.  **Response (JSON)**: The result of the execution is returned to the Client in JSON format.