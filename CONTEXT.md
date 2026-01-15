# Project Context and Session Notes

## What This Project Is

Gravity Analyst Suite is an MVP product offering that combines three data intelligence layers into a unified financial analysis platform:

1. **gravitic-macro**: Polymarket prediction market scraper and indexer
2. **gravitic-celestial**: Streamlit dashboard UI that fuses all data sources
3. **gravitic-nebula**: Alternative data signals (hiring, shipping, digital, social)

## Architecture Decision

We chose **git submodules** over copying code because:
- The three component repos (macro, celestial, nebula) already exist independently on GitHub
- Submodules prevent code duplication
- Each component can be developed and versioned separately
- Master repo acts as an orchestration layer with documentation and setup scripts

## Repository Structure

```
github.com/Peaceout21/gravity-analyst-suite (master repo)
  |-- gravitic-macro/     (submodule -> github.com/Peaceout21/gravitic-macro)
  |-- gravitic-celestial/ (submodule -> github.com/Peaceout21/gravitic-celestial)
  |-- gravitic-nebula/    (submodule -> github.com/Peaceout21/gravitic-nebula)
  |-- README.md           (full setup guide)
  |-- QUICK_START.md      (cheat sheet)
  |-- STRUCTURE.md        (directory overview)
  |-- setup.sh            (creates venvs, installs deps)
  |-- update.sh           (pulls latest from all submodules)
  |-- .gitignore          (protects .env, venvs, .db files)
```

## Key Files Protected by .gitignore

- `.env` files (API keys for Gemini, Firecrawl)
- `*-venv/` directories (Python virtual environments)
- `*.db` files (local SQLite databases like market_index.db, nebula_signals.db)
- IDE and OS files

## How to Clone and Run

```bash
git clone --recurse-submodules https://github.com/Peaceout21/gravity-analyst-suite.git
cd gravity-analyst-suite
./setup.sh
```

## How to Sync When Component Repos Update

```bash
./update.sh
# Then optionally commit the updated submodule references:
git add . && git commit -m "Update submodules" && git push
```

## Data Flow

1. gravitic-macro scrapes Polymarket -> stores in market_index.db
2. gravitic-nebula fetches alt data -> stores in nebula_signals.db
3. gravitic-celestial reads both DBs and displays fused view in Streamlit

## API Keys Required

- GEMINI_API_KEY: For AI-powered report analysis in celestial
- FIRECRAWL_API_KEY: For web scraping in nebula

These go in `.env` files in gravitic-celestial and gravitic-nebula directories.

## What Was Accomplished This Session

1. Cloned all three repos into ~/Documents/gravity-analyst-suite
2. Created master documentation (README, QUICK_START, STRUCTURE)
3. Created setup.sh for automated environment setup
4. Initially copied code directly (wrong approach)
5. Refactored to use git submodules (correct approach)
6. Created update.sh for easy submodule syncing
7. Pushed master repo to github.com/Peaceout21/gravity-analyst-suite

## Next Steps for Future Sessions

- Add API keys to .env files
- Run setup.sh to create virtual environments
- Test the full workflow: macro ingestion -> nebula sync -> celestial dashboard
- Consider adding CI/CD or automated testing
- Document any issues encountered during actual use
