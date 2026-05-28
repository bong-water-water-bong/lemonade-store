# Runbook

This runbook documents ports, environment variables, and start/setup commands for the `lemonade-cashier` system and its subprocesses/integrations.

## Network Port Allocation

The following local ports are assigned to key services in the Lemonade Store microservices architecture. No other service should bind to these ports:

| Port | Service | Description |
|---|---|---|
| **13400** | `lemond_process` | Subprocess manager for local LLM-assisted parsing |
| **8000** | API Server | REST API service |
| **11434** | Ollama | Local LLM inference server |
| **13305** | `lemond` | Lemonade App runtime |

## Environment Variables

All cashier services are configured via environment variables prefixed with `LC_`. Ensure the following are set in the runtime environment:

- `LC_LEMOND_PORT`: The port on which the embedded subprocess manager runs (defaults to `13400`).
- `LC_API_PORT`: The port for the REST API (defaults to `8000`).
- `LC_OLLAMA_BASE_URL`: URL to access Ollama (defaults to `http://localhost:11434`).
- `LC_DEBUG`: Set to `true` or `1` for verbose logging.

## Setup & Lifecycle Commands

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
