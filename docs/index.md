<p align="center">
  <img src="https://raw.githubusercontent.com/flowork-dev/asset/refs/heads/main/banner.png" alt="Flowork Logo" width="150"/>
</p>

<h1 align="center">Flowork Synapse</h1>

<p align="center">
  <strong>Weaving Intelligence into Automation.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/awenkolayaudico/flowork?style=for-the-badge" alt="Release">
  <img src="https://img.shields.io/github/license/awenkolayaudico/flowork?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-orange?style=for-the-badge" alt="Platform">
</p>

---

### 👋 Welcome to Flowork!

![Flowork Demo](https://raw.githubusercontent.com/flowork-dev/asset/7c538571c9e7ffd1a6239a07f09fc3981764497e/tutor1.gif)

Have you ever imagined building complex automations as easily as drawing a flowchart? Flowork is the answer to that imagination. It is a new generation **Visual Workflow Orchestration Platform** designed to transform the wildest ideas into elegant and efficient automations, directly from a digital canvas.

Forget messy scripts and endless lines of code. With Flowork, you are the architect. Design, connect, and run workflows that encompass *web scraping*, AI interactions, file management, scheduling, and even controlling other applications on your computer. Flowork is not just a tool; it's an ecosystem for limitless automation creativity.


### 🤔 What is Flowork?

![Flowork Demo](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/AI%20TRAINER.gif)

(AI TRAINER)

Flowork is an *open-core* platform that enables anyone, from beginners to expert developers, to build powerful automations visually. In essence, you no longer "write" automation; you "design" it.

The platform is **portable and ready-to-use**, bundled with its own Python environment, so you don't have to worry about complex installations. Just download, extract, and run.

### 🚀 Key Features

Flowork comes with a suite of advanced features ready to go:

* **🎨 Intuitive Visual Editor:** Easily design workflows using a drag-and-drop interface. Connect nodes to create complex logic without a single line of code.
* **🧩 Nano-Modular Architecture:** A revolutionary concept where even some of Flowork's core services are built using visual workflows. This provides an unprecedented level of customization.
* **⏰ Trigger-Based Automation:** Automatically run workflows in response to various events:
    * **Time & Schedule (Cron):** "Run every morning at 9 AM."
    * **File Changes:** "If a new file appears in the 'Downloads' folder..."
    * **Application Processes:** "If Photoshop.exe is opened..."
    * **Internal Events:** "If workflow A finishes, run workflow B."
* **🤖 Artificial Intelligence (AI) Hub:** Flowork is designed with AI as a first-class citizen.
    * Connect to external AI providers like **Google Gemini**.
    * Run **local AI models (GGUF & Hugging Face)** for maximum privacy and speed, including for *image generation* (Stable Diffusion) and *text generation*.

![Flowork Demo](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/AUTOMATION.gif)

* **🧠 Autonomous AI Agents:** Our most advanced feature! Use the **Agent Host** to delegate high-level objectives to an AI. Give it a "brain" (AI model), "tools" (other modules), and a "mission," then let the agent autonomously figure out how to complete it.
* **🌍 Extensible Ecosystem:** With a clear "API Contract" system, anyone can create and share:
    * **Modules:** New logic/action blocks.
    * **Plugins:** Add core functionality to the UI or backend.
    * **Widgets:** UI components for custom dashboards.
    * **Triggers:** New ways to start workflows.
* **🔒 Code Compilation & Security:** Protect your intellectual property with the integrated **Nuitka Compiler**, which transforms Python scripts into secure, compiled files.
* **📦 Portable & Ready-to-Go:** No Python installation required. Download the ZIP, extract, and run `Flowork.exe` directly.

### 🏛️ Philosophy & Core Concepts

Flowork is built on several powerful architectural principles:

1.  **Visual-First:** The belief that complex logic can be more easily understood and managed visually.
2.  **Total Modularity:** Every function is broken down into independent components (Modules, Plugins, Widgets) with clear "contracts," making the system highly stable and easy to extend.
3.  **Nano-Modular Core:** We take modularity to the extreme. Some of Flowork's core services (like preset management) are themselves visual workflows, which we call "Nano-Modules." This means the application's core logic can be modified visually.
4.  **AI as a First-Class Citizen:** AI is not an add-on; it's an integral part of the architecture. From intelligent routers to autonomous agents, Flowork is designed to be an AI orchestration platform.

![Flowork Demo](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/AI%20ARCHITEC.gif)

### ⚙️ Installation & Getting Started

Getting started with Flowork is incredibly easy:

1.  Go to the **[Releases](https://github.com/FLOWORK-gif/FLOWORK)** page.
2.  Download the `.EXE` file for your operating system (e.g., `Flowork.EXE`).
3.  Run `FLOWORK.exe` (or the appropriate launcher file). That's it!

The application will set up its own environment on the first run.

### 🎓 Quick Tutorial: "Hello, Automation!"

Let's create your first workflow in 60 seconds:


### ✨ AI IMAGE GENERATOR

![Flowork Demo](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/IMAGE%20GENERATOR%20.gif)

### 🗺️ Understanding the Flowork Ecosystem

Flowork consists of several types of extensible components:

| Component Type | Description                                                               | Examples                                    |
| :------------- | :------------------------------------------------------------------------ | :------------------------------------------ |
| **Module** | The primary building blocks for logic and actions within a workflow.      | `If Condition`, `Web Scraper`, `Email Sender` |
| **Plugin** | Adds new functionality to the Flowork UI or backend.                      | `System Diagnostics`, `AI Brain Provider`   |
| **Widget** | UI components that can be added to dashboards for interaction.            | `Log Viewer`, `Prompt Sender`, `Toolbox`      |
| **Trigger** | Listens for events and starts workflows automatically.                    | `Cron Trigger`, `File System Trigger`       |
| **AI Provider**| "Drivers" that connect Flowork to various AI models.                      | `Google Gemini`, `Local GGUF Model`         |

### 💻 For Developers (Contributing)

We welcome contributions! The best way to start is by creating your own module.

* **Module Factory (Generator):** The easiest way! Open the "Developer" -> "Open Module Factory" tab inside Flowork. You can visually design the property UI and the `execute` logic, and Flowork will generate all the boilerplate code for you!
* **Documentation:** We are in the process of building comprehensive documentation. In the meantime, please explore the code of existing modules in the `modules/` folder to understand the structure.
* **Contribution Flow:**
    1.  Fork this repository.
    2.  Create a new branch (`git checkout -b feature/awesome-new-feature`).
    3.  Make your changes.
    4.  Commit your changes (`git commit -m 'Add some awesome feature'`).
    5.  Push to your branch (`git push origin feature/awesome-new-feature`).
    6.  Open a Pull Request.

### 📜 License

This project is licensed under the [MIT](https://raw.githubusercontent.com/flowork-dev/asset/refs/heads/main/LICENSE.md) License - see the `LICENSE.md` file for details.

### 💬 Get in Touch

* **Awenk Audico** (Lead Developer) - [sahidinaola@gmail.com](mailto:sahidinaola@gmail.com)
* **Project Website:** [www.teetah.art](https://www.teetah.art)

Made with ❤️ and thousands of lines of code in Indonesia.