# Deep Agency Web UI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Originated from Open Source, give back to Open Source.

This is the web UI for [`DeerFlow`](https://github.com/bytedance/deer-flow).

## Quick Start

### Prerequisites

- Node.js (v22.14.0+)
- pnpm (v10.6.2+) as package manager

### Configuration

Create a `.env` file in the project root and configure the following environment variables:


It's always a good idea to start with the given example file, and edit the `.env` file with your own values:

```bash
cp .env.example .env
```

## How to Install

Web UI uses `pnpm` as its package manager.
To install the dependencies, run:

```bash
cd web
pnpm install
```

## How to Run in Development Mode

> [!NOTE]
> Ensure the Python API service is running before starting the web UI.

Start the web UI development server:

```bash
cd web
pnpm dev
```

By default, the web UI will be available at `http://localhost:3000`.

You can set the `NEXT_PUBLIC_API_URL` environment variable if you're using a different host or location.

```ini
# .env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Docker

You can also run this project with Docker.

First, you need read the [configuration](#configuration) below. Make sure `.env` file is ready.

Second, to build a Docker image of your own web server:

```bash
docker build --build-arg NEXT_PUBLIC_API_URL=YOUR_DEER-FLOW_API -t deer-flow-web .
```

Final, start up a docker container running the web server:

```bash
# Replace deer-flow-web-app with your preferred container name
docker run -d -t -p 3000:3000 --env-file .env --name deer-flow-web-app deer-flow-web

# stop the server
docker stop deer-flow-web-app
```

### Docker Compose

You can also setup this project with the docker compose:

```bash
# building docker image
docker compose build

# start the server
docker compose up
```

## UI Architecture

### Design Inheritance

The DeerFlow Web UI builds upon design elements and architectural patterns from two major influences:

1. **DeerFlow Core Design Language**: 
   - Consistent visual styling from the DeerFlow ecosystem
   - Semantic color schemes and typography
   - Flow-based interaction patterns optimized for AI-assisted workflows

2. **CopilotKit Inspiration**:
   - Chat-based interaction model
   - Tool integration patterns for AI assistant capabilities
   - Streamlined command interfaces for tool discovery and execution

The combination of these influences creates a unified experience that balances power and simplicity. The UI embraces:

- **Contextual Actions**: Tools and capabilities appear when relevant to the current task
- **Progressive Disclosure**: Advanced features are accessible but don't overwhelm the initial experience
- **Consistent Feedback**: Clear visual indicators for async operations and AI processing

### Component Architecture

The UI is structured around reusable components that implement consistent patterns:

- **Dialog Components**: For configuration interfaces like the MCP server setup shown above
- **Stream Renderers**: For real-time rendering of AI-generated content
- **Tool Panels**: For displaying available tools and their status

This architecture makes it easier to maintain a consistent experience while enabling rapid iteration on new features.

## License

This project is open source and available under the [MIT License](../LICENSE).

## Acknowledgments

We extend our heartfelt gratitude to the open source community for their invaluable contributions.
DeerFlow is built upon the foundation of these outstanding projects:

In particular, we want to express our deep appreciation for:

- [Next.js](https://nextjs.org/) for their exceptional framework
- [Shadcn](https://ui.shadcn.com/) for their minimalistic components that powers our UI
- [Zustand](https://zustand.docs.pmnd.rs/) for their stunning state management
- [Framer Motion](https://www.framer.com/motion/) for their amazing animation library
- [React Markdown](https://www.npmjs.com/package/react-markdown) for their exceptional markdown rendering and customizability
- Last but not least, special thanks to [SToneX](https://github.com/stonexer) for his great contribution for [token-by-token visual effect](./src/core/rehype/rehype-split-words-into-spans.ts)

These outstanding projects form the backbone of DeerFlow and exemplify the transformative power of open source collaboration.
