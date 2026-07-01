ai-study-companion/
│
├── .github/
│   └── workflows/          # CI/CD pipelines (GitHub Actions)
│
├── frontend/               # React + TypeScript (Vite)
│   ├── src/
│   │   ├── app/            # App entry, providers, router
│   │   ├── assets/         # Static files (images, fonts)
│   │   ├── components/     # Shared, reusable UI components only
│   │   ├── features/       # Feature-sliced modules (the heart of the app)
│   │   │   ├── auth/
│   │   │   │   ├── api/        # API calls for this feature
│   │   │   │   ├── components/ # Feature-specific components
│   │   │   │   ├── hooks/
│   │   │   │   ├── stores/     # Zustand/Context state for this feature
│   │   │   │   └── types/
│   │   │   ├── chat/
│   │   │   ├── quiz/
│   │   │   ├── notes/
│   │   │   └── dashboard/
│   │   ├── hooks/          # Global shared hooks
│   │   ├── lib/            # Utilities, API client (axios/ky instance)
│   │   ├── stores/         # Global state (if any)
│   │   └── types/          # Global TypeScript types + generated API types
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
│
├── backend/                # FastAPI + LangGraph
│   ├── app/
│   │   ├── api/            # Route layer only — thin, no logic here
│   │   │   ├── v1/
│   │   │   │   ├── routers/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── chat.py
│   │   │   │   │   ├── quiz.py
│   │   │   │   │   └── notes.py
│   │   │   │   └── deps.py     # Shared FastAPI dependencies (get_db, get_current_user)
│   │   │   └── __init__.py
│   │   ├── agents/         # LangGraph agent definitions
│   │   │   ├── study_agent/
│   │   │   │   ├── graph.py    # LangGraph StateGraph definition
│   │   │   │   ├── nodes.py    # Individual node functions
│   │   │   │   ├── state.py    # TypedDict state schema
│   │   │   │   └── tools.py    # Tools the agent can call
│   │   │   ├── quiz_agent/
│   │   │   └── supervisor.py   # Multi-agent supervisor/orchestrator
│   │   ├── core/           # App-wide infrastructure
│   │   │   ├── config.py       # Settings via pydantic-settings
│   │   │   ├── security.py     # JWT, password hashing
│   │   │   ├── logging.py      # Structured logging setup
│   │   │   └── exceptions.py   # Custom exception handlers
│   │   ├── db/             # Database layer
│   │   │   ├── base.py         # SQLAlchemy declarative base
│   │   │   ├── session.py      # Async engine + session factory
│   │   │   └── migrations/     # Alembic migration files
│   │   ├── models/         # SQLAlchemy ORM models (pure DB schema)
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   └── note.py
│   │   ├── schemas/        # Pydantic schemas (request/response validation)
│   │   │   ├── user.py
│   │   │   ├── chat.py
│   │   │   └── note.py
│   │   ├── services/       # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── chat_service.py     # Calls into agents/
│   │   │   └── note_service.py
│   │   ├── repositories/   # DB access layer (queries live here)
│   │   │   ├── user_repo.py
│   │   │   └── note_repo.py
│   │   └── main.py         # FastAPI app factory
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── alembic.ini
│   ├── pyproject.toml      # Dependencies via uv/poetry
│   └── Dockerfile
│
├── docker/                 # Supporting Docker configs
│   ├── nginx/
│   │   └── nginx.conf      # Reverse proxy config
│   └── postgres/
│       └── init.sql        # DB init scripts if needed
│
├── scripts/                # Bash utility scripts
│   ├── start.sh
│   ├── migrate.sh
│   └── seed.sh
│
├── .env.example            # Template — commit this, NOT .env
├── .env                    # Actual secrets — add to .gitignore
├── docker-compose.yml      # Local dev orchestration
├── docker-compose.prod.yml # Production overrides
├── Makefile                # Human-friendly command aliases
└── README.md

