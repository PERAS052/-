---
name: aggregator-store
description: "Use when working on the aggregator-store project. Focus on backend FastAPI, SQLAlchemy models, auth, marketplaces, and frontend React/Vite integration."
author: GitHub Copilot
---
This custom agent is for the `aggregator-store` workspace.

Use this agent instead of the default when the task involves:
- backend Python API routes, database models, migrations, and auth flows
- frontend React + Vite pages, components, state management, and API integration
- Docker / Compose / nginx configuration for local development and deployment
- cross-cutting full-stack bug fixes, feature development, or code review in this repo

Preferred tools:
- `read_file`, `list_dir`, `file_search`, `grep_search` for understanding code and project structure
- `create_file`, `replace_string_in_file`, `multi_replace_string_in_file` for edits
- `run_in_terminal` only when needed for installs, builds, or tests

Avoid:
- making large changes outside `backend/`, `frontend/`, `nginx/`, or `docker-compose.yml`
- using external network or out-of-repo resources unless explicitly requested
