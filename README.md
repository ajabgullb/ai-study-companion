# AI Study Companion

A multi-agent system that helps you study any topic end-to-end: finding relevant resources, generating structured study content from them, and critiquing that content to flag gaps and suggest improvements — looping until the output is solid.

## How It Works

The system is built around three cooperating agents:

- **Resource Agent** — given a topic, searches for and surfaces relevant resources (articles, papers, docs, tutorials) to ground the content that follows.
- **Generation Agent** — synthesizes the gathered resources into structured study material: explanations, summaries, notes, or practice questions.
- **Critic Agent** — reviews the generated content for accuracy, completeness, and clarity, then either approves it or sends it back to the Generation Agent with specific feedback for revision.

```
Topic ──▶ Resource Agent ──▶ Generation Agent ──▶ Critic Agent
                                     ▲                  │
                                     └──── revise ───────┘
                                              │
                                          approved
                                              │
                                              ▼
                                      Final Content
```

## Tech Stack

**Backend:** FastAPI, Python 3.11+, Supabase (Auth + Postgres)
**Frontend:** React, TypeScript, Vite
**Agents:** LLM-driven (OpenAI API or compatible), with a custom orchestrator coordinating agent hand-offs

## Project Structure

```
ai-study-companion/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── resource_agent.py
│   │   │   ├── generation_agent.py
│   │   │   ├── critic_agent.py
│   │   │   └── orchestrator.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── services/
│   │   │   └── supabase_client.py
│   │   ├── schemas/
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── .env.example
├── docs/
├── .github/workflows/
└── README.md
```

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (manages Python versions and dependencies — no separate Python install needed)
- Node.js 18+
- A Supabase project (for auth and database)
- An LLM API key (e.g. OpenAI)

### Backend Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency and environment management — no manual virtualenv activation needed.

```bash
cd backend
uv sync                    # creates .venv and installs locked dependencies
cp .env.example .env       # then fill in your keys
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env       # then fill in your keys
npm run dev
```

The app will be available at `http://localhost:5173`.

### Environment Variables

**backend/.env**
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_llm_api_key
```

**frontend/.env**
```
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_BASE_URL=http://localhost:8000
```

## Roadmap

- [ ] Resource Agent — topic-based resource retrieval
- [ ] Generation Agent — structured content synthesis
- [ ] Critic Agent — review and revision feedback loop
- [ ] Orchestrator — agent coordination and state management
- [ ] Supabase auth integration (sign up, login, sessions)
- [ ] Frontend study interface
- [ ] Deployment (backend + frontend)

## License

MIT