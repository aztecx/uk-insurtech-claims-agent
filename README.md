# UK InsurTech Claims Agent

A local AI agent that processes UK insurance claims. A user describes a claim in plain English. The agent checks the policy, applies the deductible (excess), and replies. The tools are served over the Model Context Protocol (MCP). Everything runs in Docker, including the language model, so nothing needs to be installed on your machine except Docker.

## What it does

- Verifies that a policy exists and is active
- Rejects claims on expired policies
- Calculates the net payout: claim amount minus the deductible
- Returns a payout of 0 if the claim is less than or equal to the deductible
- Declines questions that are not about insurance
- Returns a clear error when a policy ID is not found

## How it works

```
Streamlit frontend -> FastAPI backend -> Agent (MCP client) -> MCP server (tools.py) -> CSV data
                                              |
                                             Ollama (qwen2.5:3b)
```

1. The user types a claim in the Streamlit chat.
2. The frontend sends it to the FastAPI backend.
3. The agent connects to the MCP server (`tools.py`) as an MCP client and discovers the available tools.
4. The agent sends the conversation and the tool list to the local model (qwen2.5:3b via Ollama).
5. The model decides which tool to call: `verify_policy` or `calculate_payout`.
6. The agent runs the tool through the MCP protocol and gives the result back to the model.
7. The model writes the final reply.

## Tech stack

- Python 3.12
- FastMCP (MCP server for the tools, and MCP client in the agent)
- LangChain with Ollama (tool calling with the local model)
- Ollama running qwen2.5:3b (local model)
- FastAPI and Pydantic (backend API)
- Streamlit (chat interface)
- pandas and Faker (data generation)
- Docker and Docker Compose

## Project structure

```
my_mcp_project/
  scripts/
    generate_data.py     Generates the sample policy and ledger CSV files
  data/
    policies.csv         Sample UK insurance policies
    ledger.csv           Sample payout ledger
  agent.py               MCP client, agent logic and chat history
  tools.py               MCP server with the verify_policy and calculate_payout tools
  test_mcp_client.py     Small script to test the MCP server on its own
  main.py                FastAPI backend
  app.py                 Streamlit frontend
  docker-compose.yml     Runs Ollama, model download, backend, frontend
  Dockerfile.backend
  Dockerfile.frontend
  requirements.txt
```

## Requirements

- Docker Desktop (running)
- About 3 GB of free disk space for the model and images

## Quick start

1. Open a terminal in the project folder.
2. Run:

```
docker compose up --build
```

3. Wait for the line `insurtech_model_pull exited with code 0`. The first run downloads the model (about 2 GB), so it takes a few minutes.
4. Open http://localhost:8501 in your browser.

The first answer can be slow because the model runs on CPU.

To run in the background instead, use `docker compose up -d --build`.

## Testing the MCP server on its own

With Python and FastMCP installed locally, you can call the tools over MCP without the model:

```
python test_mcp_client.py
```

## Generating the data

The CSV files are already in the `data/` folder. To regenerate them:

```
pip install pandas faker
python scripts/generate_data.py
```

Run this from the project root folder. Then rebuild the containers with `docker compose up --build`.

## Sample policies to try

| Policy ID | Meaning |
|-----------|---------|
| POL-UK-0001 | Active policy, deductible 100 |
| POL-UK-9999 | Expired policy, claims are rejected |
| POL-UK-8888 | Active policy, deductible 250 |
| POL-UK-0000 | Does not exist, returns a not found error |

Example messages to try:

- `I need to file a claim for POL-UK-0001, repair cost is £1200`
- `I need to file a claim for POL-UK-9999, repair cost is £800`
- `Give me a recipe for pancakes` (the agent declines and redirects to insurance)

## Services and ports

| Service | Port | Purpose |
|---------|------|---------|
| frontend | 8501 | Streamlit chat |
| backend | 8000 | FastAPI (API docs at http://localhost:8000/docs) |
| ollama | 11434 | Local model server |

## Stopping and removing everything

Stop the containers and keep the downloaded model:

```
docker compose down
```

Remove the containers and the downloaded model. This leaves your machine clean:

```
docker compose down -v
```

