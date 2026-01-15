# Gravitic Macro Radar 🔮📉

A modular macro-intelligence package for the Gravity platform. It tracks real-time probabilities from prediction markets (Polymarket) to provide a "Market-Implied Truth" layer for financial analysis.

## Features
- **Polymarket Scraper**: Fetches live macro and ticker-linked event data via Gamma API.
- **Discovery Engine**: Maps stock tickers (e.g., NVDA) to relevant prediction themes (AI, Chips, Semiconductors).
- **LLM Filter**: Uses Gemini 2.0 Flash to filter out "noise" (pop culture, sports) and keep high-alpha signals.
- **TimeSeries Persistence**: Stores probability snapshots in a local SQLite database with sector and ticker metadata.

## Structure
- `core/scrapers/`: Scrapers and discovery logic.
- `core/persistence/`: Time-series database management.
- `scripts/`: Diagnostic and verification tools.

## Setup
1. Create a virtual environment:
   ```bash
   python3 -m venv macro-venv
   source macro-venv/bin/activate
   pip install -r pyproject.toml
   ```
2. Configure `.env` with your `GOOGLE_API_KEY`.
3. Run the discovery test:
   ```bash
   python3 scripts/test_discovery.py
   ```

## Development Status
Current exploration: **Phase 20 - Polymarket Macro Radar**.
*Note: Polymarket API search/filter parameters currently exhibit inconsistent behavior for specific ticker keywords.*
