# Runbook

> Local commands, environment variables, and port configurations for testing, building, and running the `lemonade-store` suite.

## Local Commands

Convenience targets are managed via the project `Makefile`. Python 3.11+ is required.

### Setup & Installation
```bash
# Install the package in editable mode with development and documentation extras
make install
```

### Formatting & Linting
```bash
# Run Ruff lint checks on source and test directories
make lint

# Run Mypy static type verification
make type

# Format the codebase with Ruff
make fmt
```

### Running Tests
```bash
# Run the pytest suite
make test

# Run tests with terminal coverage reporting
make test-cov
```

### Build & Clean
```bash
# Run all verification steps (combines lint, type, and test targets)
make all

# Build mkdocs documentation strictly
make docs

# Remove python caches, build files, and egg-info directories
make clean
```

> [!NOTE]
> Running `make all` runs `lint type test` sequentially and is the required pre-commit and pre-PR verification command.

---

## Environment Variables

The suite expects the following environment variables to be set depending on the task:

| Variable Name | Purpose | Description |
|---|---|---|
| `GH_TOKEN` / `GITHUB_TOKEN` | VCS Credentials | Used by agents and scripts for authenticating requests to GitHub APIs, checking issues/PRs, and updating specifications. |
| `OPENAI_API_KEY` | LLM API Access | Key for OpenAI models, used by agent workflows (e.g. Aider, SWE-agent, Swarm scripts). |
| `GEMINI_API_KEY` | LLM API Access | Key for Google Gemini models, used by local coding agents. |
| `DEEPSEEK_API_KEY` | LLM API Access | Key for DeepSeek models. |
| `OPENHANDS_API_KEY` | LLM API Access | Key for OpenHands platform integration. |
| `QODO_API_KEY` | LLM API Access | Key for Qodo (CodiumAI) code quality tools. |

---

## Port Assignments

The offline-first architecture assigns dedicated, static ports to avoid port collision on a single local workstation:

| Port | Service / Application | Description |
|---|---|---|
| **`13305`** | `lemond` (Lemonade Server) | The core Lemonade App runtime API. Department Podman plugins register with and route events through this endpoint. |
| **`5000`** | Department API (Local) | Reserved for department-specific plugin backend API containers. |
| **`8000`** | Department API (Local) | Reserved for department-specific plugin backend API containers. |
| **`3000`** | Web UI / Frontend | Local port for department web frontends or the Cloudflare pages local dev server. |

---

## Related

- [[README]] — project wiki entry point
- [[conventions]] — coding style, linting, and package structure guidelines
- [[departments]] — department contracts and repository registry
