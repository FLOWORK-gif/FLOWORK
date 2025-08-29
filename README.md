<p align="center">
  <img src="https://raw.githubusercontent.com/flowork-dev/asset/refs/heads/main/banner.png" alt="Flowork Synapse Logo" width="150"/>
</p>

<h1 align="center">Flowork Synapse</h1>

<p align="center">
  <strong>Weaving Intelligence into Automation.</strong>
</p>

<p align="center">
  <b>An open-source, visual workflow orchestration platform to build complex automations with AI. No-code & Low-code friendly.</b>
</p>


<p align="center">
  <img src="https://img.shields.io/github/v/release/awenkolayaudico/flowork?style=for-the-badge" alt="Latest Release">
  <img src="https://img.shields.io/github/license/awenkolayaudico/flowork?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python Version 3.10+">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-orange?style=for-the-badge" alt="Platform">
</p>

---

<details>
  <summary><strong>📜 Table of Contents</strong> (Click to Expand)</summary>
  <ol>
    <li><a href="#-welcome-to-flowork">Welcome to Flowork!</a></li>
    <li><a href="#-apa-itu-flowork">What is Flowork?</a></li>
    <li><a href="#-tur-keliling-fitur-unggulan-flowork">Feature Showcase</a></li>
    <li><a href="#-philosophy--core-concepts">Philosophy & Core Concepts</a></li>
    <li><a href="#-installation--getting-started">Installation & Getting Started</a></li>
    <li><a href="#-quick-tutorial-hello-automation">Quick Tutorial</a></li>
    <li><a href="#-understanding-the-flowork-ecosystem">Understanding the Flowork Ecosystem</a></li>
    <li><a href="#-for-developers-contributing">For Developers (Contributing)</a></li>
    <li><a href="#-license">License</a></li>
    <li><a href="#-get-in-touch">Get in Touch</a></li>
  </ol>
</details>

---


### 👋 Welcome to Flowork!

Have you ever imagined building complex automations as easily as drawing a flowchart? Flowork is the answer to that imagination. It is a new generation **Visual Workflow Orchestration Platform** designed to transform the wildest ideas into elegant and efficient automations, directly from a digital canvas.

Forget messy scripts and endless lines of code. With Flowork, you are the architect. Design, connect, and run workflows that encompass *web scraping*, AI interactions, file management, scheduling, and even controlling other applications on your computer. Flowork is not just a tool; it's an ecosystem for limitless automation creativity.


### 🤔 What is Flowork?

Flowork is an *open-core* platform that enables anyone, from beginners to expert developers, to build powerful automations visually. In essence, you no longer "write" automation; you "design" it.

The platform is **portable and ready-to-use**, bundled with its own Python environment, so you don't have to worry about complex installations. Just download, extract, and run.

---
## 🚀 A Tour of Flowork's Key Features

Flowork is not just a tool, but a complete ecosystem for automation creativity. Let's explore some of the features that make it so powerful.

### 🎨 **Intuitive Visual Editor: Design, Don't Code**
Forget complex syntax. In Flowork, you build logic by dragging and connecting nodes on a digital canvas. Complex workflows become easy to understand, debug, and modify, even for non-programmers.

![GIF demonstrating the visual workflow editor in Flowork](https://raw.githubusercontent.com/flowork-dev/asset/7c538571c9e7ffd1a6239a07f09fc3981764497e/tutor1.gif)

---
### 🤖 **AI Architect: Turn Human Language into Workflows**
This is a game-changer. Simply write your objective in plain language (e.g., "Scrape the latest news from detik.com and save it to a text file"), and the **AI Architect** will automatically design and draw a ready-to-use workflow on the canvas for you.

![GIF of Flowork's AI Architect turning a text prompt into a visual workflow](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/AI%20ARCHITEC.gif)

---
### 🧠 **AI Trainer & Model Factory: Train Your Own AI**
Flowork empowers you to fine-tune local AI models.
1.  **AI Trainer:** Train a base AI model using your own data (e.g., customer service conversations) to make it an expert on a specific topic.
2.  **Model Factory:** After training, convert your model into the highly efficient GGUF format so it can run quickly right on your computer.

![GIF demonstrating the visual AI model training process in Flowork's AI Trainer](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/AI%20TRAINER.gif)

---
### AGENT **Agent Host: Delegate Missions to Autonomous AI Agents**
Our most advanced feature! Design an "Agent" by giving it:
* **A Brain:** An AI model (local/external) to think.
* **Tools:** Other modules (like Web Scraper, Email Sender) to act as its "hands".
* **A Mission:** A high-level objective.

The Agent will then autonomously plan and execute steps using its available tools to complete the mission.

![GIF showing a complex automation running with popups, demonstrating an AI Agent's capabilities](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/AUTOMATION.gif)

---
### ✨ **AI Image Generator (Stable Diffusion)**
Create stunning images directly from your workflow. Just provide a text prompt, and Flowork will use a locally-run AI model (like Stable Diffusion) to generate high-quality images.

![GIF of the AI Image Generator in Flowork creating an image from a text prompt](https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/IMAGE%20GENERATOR%20.gif)

---
### 🧩 **Nano-Modular Architecture & Module Factory**
* **Nano-Modular:** Some of Flowork's core services (like preset management) are built using visual workflows themselves. This means you can visually modify the application's core logic.
* **Module Factory:** Want to create a new module? Don't start from scratch. Visually design the properties UI and the `execute` logic, and Flowork will generate all the boilerplate code for you.

---
### ⏰ **Event-Driven Trigger System**
Run workflows automatically in response to various events:
* **Schedule (Cron):** "Run every morning at 9 AM."
* **File Changes:** "If a new file appears in the 'Downloads' folder..."
* **Application Processes:** "If `Photoshop.exe` is opened..."
* **Internal Events:** "If workflow A finishes, run workflow B."

---

### 🏛️ Philosophy & Core Concepts

Flowork is built on several powerful architectural principles:

1.  **Visual-First:** The belief that complex logic can be more easily understood and managed visually.
2.  **Total Modularity:** Every function is broken down into independent components (Modules, Plugins, Widgets) with clear "contracts," making the system highly stable and easy to extend.
3.  **Nano-Modular Core:** We take modularity to the extreme. Some of Flowork's core services (like preset management) are themselves visual workflows, which we call "Nano-Modules." This means the application's core logic can be modified visually.
4.  **AI as a First-Class Citizen:** AI is not an add-on; it's an integral part of the architecture. From intelligent routers to autonomous agents, Flowork is designed to be an AI orchestration platform.

### ⚙️ Installation & Getting Started

Getting started with Flowork is incredibly easy:

1.  Go to the **[Releases](https://github.com/FLOWORK-gif/FLOWORK/releases/tag/FLOWORK)** page.
2.  Download the `.EXE` file for your operating system (e.g., `Flowork.EXE`).
3.  Run `FLOWORK.exe` (or the appropriate launcher file). That's it!

The application will set up its own environment on the first run.

### 🎓 Quick Tutorial: "Hello, Automation!"

Let's create your first workflow in 60 seconds:
### 🗺️ Understanding the Flowork Ecosystem

Flowork consists of several types of extensible components:

| Component Type  | Description | Examples |
| :--- | :--- | :--- |
| **Module** | The primary building blocks for logic and actions within a workflow. | `If Condition`, `Web Scraper`, `Email Sender` |
| **Plugin** | Adds new functionality to the Flowork UI or backend. | `System Diagnostics`, `AI Brain Provider` |
| **Widget** | UI components that can be added to dashboards for interaction. | `Log Viewer`, `Prompt Sender`, `Toolbox` |
| **Trigger** | Listens for events and starts workflows automatically. | `Cron Trigger`, `File System Trigger` |
| **AI Provider**| "Drivers" that connect Flowork to various AI models. | `Google Gemini`, `Local GGUF Model` |

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
