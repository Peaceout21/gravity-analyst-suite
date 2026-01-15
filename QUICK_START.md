# ⚡ Quick Start Cheat Sheet

## One-Time Setup

```bash
cd ~/Documents/gravity-analyst-suite
chmod +x setup.sh
./setup.sh
```

## Daily Workflow

### Terminal 1: Macro Data (Run every 2-3 days)
```bash
cd ~/Documents/gravity-analyst-suite/gravitic-macro
source macro-venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
python3 scripts/test_ingestion.py
```

### Terminal 2: Nebula Data (Run daily)
```bash
cd ~/Documents/gravity-analyst-suite/gravitic-nebula
source nebula-venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
python3 scripts/run_alpha_sync.py TSLA,NVDA,AAPL
# Add your watchlist tickers ↑
```

### Terminal 3: Dashboard (Keep running)
```bash
cd ~/Documents/gravity-analyst-suite/gravitic-celestial
source celestial-venv/bin/activate
export PYTHONPATH=$PYTHONPATH:../gravitic-macro
streamlit run ui/app.py
```

## API Keys Needed

Create `.env` files in each repo:

**gravitic-celestial/.env**
```
GEMINI_API_KEY=your_key_here
FIRECRAWL_API_KEY=your_key_here
```

**gravitic-nebula/.env**
```
GEMINI_API_KEY=your_key_here
FIRECRAWL_API_KEY=your_key_here
```

## Dashboard Tabs

- **Tab 2**: 📄 Analyze Reports (Paste earnings text)
- **Tab 6**: 🪐 Nebula Alpha (Alternative signals)
- **Tab 7**: 📡 Macro Radar (Prediction markets)

## Troubleshooting

**Import Error?**
```bash
export PYTHONPATH=$PYTHONPATH:../gravitic-macro
```

**No Data?**
- Run Macro ingestion first
- Run Nebula sync for your tickers
- Check `.env` files have API keys

**Dashboard Won't Start?**
```bash
pip install streamlit
```

## File Locations

- Macro Index: `gravitic-macro/market_index.db`
- Nebula Signals: `gravitic-nebula/nebula_signals.db`
- Dashboard: `http://localhost:8501`

---

**See [README.md](./README.md) for full documentation**
