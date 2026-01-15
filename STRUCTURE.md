# 📁 Gravity Analyst Suite - Directory Structure

```
~/Documents/gravity-analyst-suite/
│
├── README.md                    # Master setup guide (YOU ARE HERE)
├── QUICK_START.md              # Cheat sheet for daily use
├── STRUCTURE.md                # This file
├── setup.sh                    # Automated setup script
│
├── gravitic-macro/             # Polymarket Truth Layer
│   ├── README.md               # Macro-specific documentation
│   ├── macro-venv/             # Virtual environment (created by setup)
│   ├── macro_core/             # Core prediction market logic
│   ├── scripts/                
│   │   └── test_ingestion.py  # Run this to build market index
│   ├── market_index.db         # Local Polymarket database (created after ingestion)
│   └── pyproject.toml
│
├── gravitic-celestial/         # Master Dashboard UI
│   ├── README.md               # Celestial-specific documentation
│   ├── ARCHITECTURE.md         # System architecture details
│   ├── DEPLOY.md               # Deployment guide
│   ├── celestial-venv/         # Virtual environment (created by setup)
│   ├── core/                   # Business logic
│   ├── ui/
│   │   └── app.py              # Main Streamlit dashboard (RUN THIS)
│   ├── scripts/
│   ├── docker/
│   ├── .env                    # API keys (YOU CREATE THIS)
│   └── pyproject.toml
│
└── gravitic-nebula/            # Alternative Alpha Signals
    ├── README.md               # Nebula-specific documentation
    ├── DESIGN.md               # Design decisions
    ├── WALKTHROUGH.md          # Feature walkthrough
    ├── ENGINEERING_LOG.md      # Development notes
    ├── nebula-venv/            # Virtual environment (created by setup)
    ├── core/                   # Data collection logic
    ├── scripts/
    │   └── run_alpha_sync.py   # Run this to fetch signals
    ├── tests/
    ├── nebula_signals.db       # Alternative data database (created after sync)
    ├── .env                    # API keys (YOU CREATE THIS)
    └── pyproject.toml
```

## Key Files to Interact With

### Setup Phase
1. `setup.sh` - Run once to create all virtual environments

### Daily Operations
2. `gravitic-macro/scripts/test_ingestion.py` - Refresh market data
3. `gravitic-nebula/scripts/run_alpha_sync.py` - Fetch alternative signals
4. `gravitic-celestial/ui/app.py` - Launch dashboard

### Configuration
5. `gravitic-celestial/.env` - API keys for dashboard
6. `gravitic-nebula/.env` - API keys for data fetching

### Databases (Auto-created)
7. `gravitic-macro/market_index.db` - Polymarket cache
8. `gravitic-nebula/nebula_signals.db` - Alternative data storage

## Documentation Hierarchy

```
README.md (Master)
    │
    ├─ QUICK_START.md (Cheat Sheet)
    ├─ STRUCTURE.md (This File)
    │
    ├─ gravitic-macro/README.md (Macro Details)
    │
    ├─ gravitic-celestial/README.md (Dashboard Details)
    │   ├─ ARCHITECTURE.md
    │   └─ DEPLOY.md
    │
    └─ gravitic-nebula/README.md (Nebula Details)
        ├─ DESIGN.md
        ├─ WALKTHROUGH.md
        └─ ENGINEERING_LOG.md
```

## Data Flow

```
1. Polymarket (Web) → test_ingestion.py → market_index.db
2. Alt Data Sources → run_alpha_sync.py → nebula_signals.db  
3. Both DBs → app.py (Dashboard) → Browser (You!)
```

## Virtual Environments

Each repo has its own isolated Python environment:

- `macro-venv/` - For macro data collection
- `celestial-venv/` - For dashboard runtime
- `nebula-venv/` - For alternative data fetching

Always activate the correct venv before running scripts!
