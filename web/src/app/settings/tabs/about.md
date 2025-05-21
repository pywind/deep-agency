# 🦌 [About DeerFlow](https://github.com/bytedance/deer-flow)

> **From Open Source, Back to Open Source**

**DeerFlow** (**D**eep **E**xploration and **E**fficient **R**esearch **Flow**) is a community-driven AI automation framework inspired by the remarkable contributions of the open source community. Our mission is to seamlessly integrate language models with specialized tools for tasks such as web search, crawling, and Python code execution—all while giving back to the community that made this innovation possible.

---

### Core Frameworks
- **[LangChain](https://github.com/langchain-ai/langchain)**: A phenomenal framework that powers our LLM interactions and chains.
- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Enabling sophisticated multi-agent orchestration.
- **[Next.js](https://nextjs.org/)**: A cutting-edge framework for building web applications.

### UI Libraries
- **[Shadcn](https://ui.shadcn.com/)**: Minimalistic components that power our UI.
- **[Zustand](https://zustand.docs.pmnd.rs/)**: A stunning state management library.
- **[Framer Motion](https://www.framer.com/motion/)**: An amazing animation library.
- **[React Markdown](https://www.npmjs.com/package/react-markdown)**: Exceptional markdown rendering with customizability.
- **[SToneX](https://github.com/stonexer)**: For his invaluable contribution to token-by-token visual effects.

These outstanding projects form the backbone of DeerFlow and exemplify the transformative power of open source collaboration.

# 🔄 Agent Interoperability Protocols

> **Enabling Seamless Communication Between AI Agents**

## Model Context Protocol (MCP)

The **Model Context Protocol (MCP)** was developed by Anthropic to provide AI agents with helpful tools and context. It creates a standardized way for agents to access information and utilize tools, enhancing their capabilities while maintaining a consistent interaction framework.

---

## 🔄 Agent2Agent Protocol (A2A)

The **Agent2Agent (A2A) Protocol** is an open protocol launched by Google Cloud with support from over 50 technology partners. A2A enables AI agents to communicate with each other, securely exchange information, and coordinate actions across various enterprise platforms and applications.

### Key Design Principles

- **Embrace agentic capabilities**: Enables agents to collaborate in their natural, unstructured modalities
- **Build on existing standards**: Utilizes HTTP, SSE, JSON-RPC for easier integration with existing IT stacks
- **Secure by default**: Supports enterprise-grade authentication and authorization
- **Support for long-running tasks**: Flexible framework supporting quick tasks to deep research
- **Modality agnostic**: Supports various communication modalities including text, audio, and video streaming

### How A2A Works

A2A facilitates communication between a "client" agent and a "remote" agent through:

- **Capability discovery**: Agents advertise their capabilities through JSON "Agent Cards"
- **Task management**: Communication between agents is oriented toward task completion
- **Collaboration**: Agents can exchange messages to communicate context, replies, and artifacts
- **User experience negotiation**: Messages include content "parts" with specified formats

---

## 🌟 The Future of Agent Interoperability

Together, MCP and A2A protocols represent a significant advancement in AI agent interoperability, fostering innovation and creating more powerful and versatile agentic systems. These protocols are designed to unlock the full potential of collaborative AI agents by enabling them to work across diverse platforms and cloud environments.

For more information, visit [Google's A2A Protocol Announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/).
