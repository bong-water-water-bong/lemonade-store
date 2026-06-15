# Runbook

> Local commands, environment variables, and port configurations for testing, building, and running the `lemonade-store` suite.

## Local Commands

Convenience targets are managed via the project `Makefile`. Python 3.11+ is required.

### Setup & Installation
```bash
# Install the package in editable mode with development and documentation extras
make install

# Optional: install local Lemonade SDK / GAIA agent bridge packages
make install-agents
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

`make install` must stay lightweight and must not install model runtime
packages. Use `make install-agents` only on workstations that need to run
the local `lemonade-agents` bridge against Lemonade SDK / GAIA.

---

## Environment Variables

### Global Environment Variables

The suite expects the following environment variables to be set depending on the task:

| Variable Name | Purpose | Description |
|---|---|---|
| `GH_TOKEN` / `GITHUB_TOKEN` | VCS Credentials | Used by agents and scripts for authenticating requests to GitHub APIs, checking issues/PRs, and updating specifications. |
| `OPENAI_API_KEY` | LLM API Access | Key for OpenAI models, used by agent workflows (e.g. Aider, SWE-agent, Swarm scripts). |
| `GEMINI_API_KEY` | LLM API Access | Key for Google Gemini models, used by local coding agents. |
| `DEEPSEEK_API_KEY` | LLM API Access | Key for DeepSeek models. |
| `OPENHANDS_API_KEY` | LLM API Access | Key for OpenHands platform integration. |
| `QODO_API_KEY` | LLM API Access | Key for Qodo (CodiumAI) code quality tools. |

### Cashier Service Environment Variables

All cashier services are configured via environment variables prefixed with `LC_`. Ensure the following are set in the runtime environment:

- `LC_LEMOND_PORT`: The port on which the embedded subprocess manager runs (defaults to `13400`).
- `LC_API_PORT`: The port for the REST API (defaults to `8000`).
- `LC_OLLAMA_BASE_URL`: URL to access Ollama (defaults to `http://localhost:11434`).
- `LC_DEBUG`: Set to `true` or `1` for verbose logging.

---

## Port Assignments

The offline-first architecture assigns dedicated, static ports to avoid port collision on a single local workstation:

| Port | Service / Application | Description |
|---|---|---|
| **`13305`** | `lemond` (Lemonade Server) | The core Lemonade App runtime API. Department Podman plugins register with and route events through this endpoint. |
| **`13400`** | `lemond_process` | Subprocess manager for local LLM-assisted parsing in the cashier department. |
| **`11434`** | Ollama | Local LLM inference server. |
| **`8000`** | Department API / API Server | Reserved for department-specific plugin backend API containers or cashier API service. |
| **`5000`** | Department API (Local) | Reserved for department-specific plugin backend API containers. |
| **`3000`** | Web UI / Frontend | Local port for department web frontends or the Cloudflare pages local dev server. |

---

## Cashier Setup & Lifecycle Commands

The `lemonade-cashier` repository contains helper scripts to bootstrap and control the `lemond_process` subprocess manager and fetch embeddable assets.

### Setup (Fetching Resources)

To bootstrap the local lemond subprocess manager environment, run:

```bash
./setup_lemond.sh
```

This script:
1. Downloads embeddable models and resource artifacts.
2. Prepares local database directories and virtual environments.
3. Sets up standard system layouts.

### Start & Stop Service Control

Use the cashier command line tools to manage the backend lifecycle:

- **Start**: `lemond-start` launches the embedded subprocess manager and binds it to port `13400`.
- **Stop**: `lemond-stop` gracefully terminates all active cashier subprocesses.
- **Setup**: `lemond-setup` performs a sanity check on the installation environment.

---

## Related

- [[README]] — project wiki entry point
- [[conventions]] — coding style, linting, and package structure guidelines
- [[departments]] — department contracts and repository registry
