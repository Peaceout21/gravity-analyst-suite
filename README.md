# 🌌 Gravity Analyst Suite - Master Setup Guide

**Your Complete MVP Product Offering: Fused Intelligence Platform**

This suite combines prediction market intelligence, alternative data signals, and AI-powered analysis into a unified dashboard for competitive advantage in financial analysis.

---

## 📦 What's Inside

The Gravity Analyst Suite consists of three integrated repositories:

### 1. [gravitic-macro](./gravitic-macro/) - Polymarket Truth Layer
**Purpose**: Prediction market data and intelligence
**What it does**:
- Scrapes and indexes Polymarket prediction markets
- Provides local search capabilities (because Polymarket API is unreliable)
- Hydrates markets with live odds data
- Core truth engine for macro sentiment

**Key Features**:
- Local market index database
- Deep search functionality
- Live odds hydration
- Ticker-to-market mapping

### 2. [gravitic-celestial](./gravitic-celestial/) - Master Dashboard UI
**Purpose**: The main interface and fusion layer
**What it does**:
- Unified Streamlit dashboard
- Integrates Macro + Nebula data streams
- AI-powered report analysis (Gemini 2.0)
- Multi-tab interface for different analysis modes

**Key Features**:
- 📡 Macro Radar: Search prediction markets by ticker
- 🪐 Nebula Alpha: View alternative data signals
- 📄 Report Analyzer: Extract KPIs from earnings reports
- 🔮 Automated signal fusion

### 3. [gravitic-nebula](./gravitic-nebula/) - Alternative Alpha Signals
**Purpose**: Web3 and alternative data collection
**What it does**:
- Tracks hiring signals (company growth indicators)
- Monitors shipping/logistics data
- Aggregates digital footprint metrics
- Social sentiment analysis

**Key Features**:
- Multi-source data aggregation
- Persistent signal database
- Ticker-based sync system
- Real-time alternative data

---

## 🚀 Quick Start (The "Live" Workflow)

### Prerequisites
- Python 3.8+
- Git
- API Keys (Gemini, Firecrawl)

### Step 0: Initial Setup

```bash
# Navigate to the suite directory
cd ~/Documents/gravity-analyst-suite

# Create virtual environments for each repo
cd gravitic-macro && python3 -m venv macro-venv && cd ..
cd gravitic-celestial && python3 -m venv celestial-venv && cd ..
cd gravitic-nebula && python3 -m venv nebula-venv && cd ..
```

### Step 1: Initialize Macro Index (Polymarket Data)

Run this **once every few days** to keep market data fresh:

```bash
cd ~/Documents/gravity-analyst-suite/gravitic-macro
source macro-venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# Install dependencies (first time only)
pip install -r requirements.txt

# Populate local market index
python3 scripts/test_ingestion.py
```

**What this does**: Creates `market_index.db` with searchable Polymarket data.

### Step 2: Fetch Alternative Data (Nebula Signals)

Run this **daily or before analysis** to refresh signals:

```bash
cd ~/Documents/gravity-analyst-suite/gravitic-nebula
source nebula-venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# Install dependencies (first time only)
pip install -r requirements.txt

# Fetch signals for your target tickers (adjust as needed)
python3 scripts/run_alpha_sync.py TSLA,NVDA,AAPL
```

**What this does**: Updates `nebula_signals.db` with latest hiring, shipping, digital, and social signals.

### Step 3: Launch Master Dashboard (Celestial)

This is your main interface:

```bash
cd ~/Documents/gravity-analyst-suite/gravitic-celestial
source celestial-venv/bin/activate

# CRITICAL: Add macro to Python path for live search
export PYTHONPATH=$PYTHONPATH:../gravitic-macro

# Install dependencies (first time only)
pip install -r requirements.txt

# Launch dashboard
streamlit run ui/app.py
```

**Access**: Dashboard opens automatically at `http://localhost:8501`

---

## 🎯 Dashboard Features Guide

### 📡 Tab 7: Macro Radar (Prediction Markets)

**Action**:
1. Enter a ticker (e.g., `NVDA`)
2. Click "Scan Prediction Markets"

**How it works**:
- Uses gravitic-macro's deep search in local index
- Hydrates results with live Polymarket odds
- Shows market sentiment and probabilities

**Requirement**: `gravitic-macro` must be in `PYTHONPATH`

### 🪐 Tab 6: Nebula Alpha (Alternative Data)

**Action**: View signals dashboard

**How it works**:
- Reads from `gravitic-nebula/nebula_signals.db`
- Displays hiring, shipping, digital, social metrics
- Time-series visualization

**Requirement**: Data must be synced via Nebula scripts first

### 📄 Tab 2: Analyze New Report (AI-Powered KPI Extraction)

**Action**:
1. Paste earnings press release or report
2. Click "Analyze"

**How it works**:
- Gemini 2.0 extracts key metrics (revenue, guidance, sentiment)
- Automatically pulls related Nebula + Macro signals
- Provides fused intelligence view

**Requirement**: `GEMINI_API_KEY` in `.env`

---

## 🔑 API Keys Setup

Each repository needs its own `.env` file:

### gravitic-macro/.env
```env
# Add any Polymarket API keys if needed
```

### gravitic-celestial/.env
```env
GEMINI_API_KEY=your_gemini_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### gravitic-nebula/.env
```env
GEMINI_API_KEY=your_gemini_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

**Get your keys**:
- Gemini: https://ai.google.dev/
- Firecrawl: https://firecrawl.dev/

---

## 🛠️ Pro Tips

### Terminal Management
Keep **3 terminal tabs** open for easy workflow:
- Tab 1: `gravitic-macro` (for index updates)
- Tab 2: `gravitic-nebula` (for signal syncs)
- Tab 3: `gravitic-celestial` (for dashboard)

### Data Refresh Schedule
- **Macro Index**: Every 2-3 days (markets don't change that fast)
- **Nebula Signals**: Daily or before key analysis sessions
- **Live Dashboard**: Keep running during analysis

### Troubleshooting

**"ImportError: No module named macro_core"**
```bash
# Make sure you're exporting PYTHONPATH when running Celestial
export PYTHONPATH=$PYTHONPATH:../gravitic-macro
```

**"No data available in Nebula Alpha"**
```bash
# Run the sync script for your tickers first
cd gravitic-nebula
source nebula-venv/bin/activate
python3 scripts/run_alpha_sync.py YOUR_TICKER
```

**Dashboard won't load**
```bash
# Check if Streamlit is installed
pip install streamlit
# Check if you're in the right directory
cd gravitic-celestial
```

---

## 📊 Typical Analysis Workflow

1. **Morning Data Prep** (10 minutes)
   - Sync Nebula signals for watchlist tickers
   - Check if Macro index needs refresh

2. **Dashboard Session** (Active Analysis)
   - Launch Celestial dashboard
   - Use Macro Radar for prediction market sentiment
   - Check Nebula Alpha for alternative signals
   - Paste earnings reports for AI analysis

3. **Ongoing Monitoring**
   - Keep dashboard running
   - Refresh data as needed
   - Export insights for reports

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│   gravitic-celestial (Master Dashboard) │
│   ├─ Streamlit UI                       │
│   ├─ Gemini AI Integration              │
│   └─ Data Fusion Layer                  │
└────────────┬────────────────────────────┘
             │
       ┌─────┴─────┐
       │           │
┌──────▼─────┐ ┌──▼──────────────┐
│ gravitic-  │ │ gravitic-nebula │
│   macro    │ │                 │
│ ┌────────┐ │ │ ┌─────────────┐│
│ │Market  │ │ │ │Hiring Data  ││
│ │Index DB│ │ │ │Shipping Data││
│ └────────┘ │ │ │Digital Data ││
│            │ │ │Social Data  ││
│ Polymarket │ │ └─────────────┘│
│ Search     │ │ Signal DB      │
└────────────┘ └────────────────┘
```

---

## 📚 Additional Resources

- Each repository has its own detailed README:
  - [gravitic-macro/README.md](./gravitic-macro/README.md)
  - [gravitic-celestial/README.md](./gravitic-celestial/README.md)
  - [gravitic-nebula/README.md](./gravitic-nebula/README.md)

---

## 🎓 Learning Path

1. **Week 1**: Setup and familiarization
   - Install all dependencies
   - Run through Quick Start workflow
   - Explore each dashboard tab

2. **Week 2**: Data collection
   - Build your watchlist of tickers
   - Set up daily Nebula sync routine
   - Understand Macro market types

3. **Week 3**: Analysis patterns
   - Combine Macro + Nebula signals
   - Test AI report analysis
   - Develop your workflow

4. **Week 4**: Production use
   - Automate data refresh (cron jobs)
   - Create analysis templates
   - Build reporting cadence

---

## 🚨 Important Notes

- **API Costs**: Monitor your Gemini API usage (AI analysis can add up)
- **Data Privacy**: All data is stored locally in SQLite databases
- **Rate Limits**: Be mindful of Polymarket scraping frequency
- **Updates**: Pull latest changes regularly from each repo

---

## 🤝 Support

For issues with individual components, check the respective repository README files.

---

**Built with**: Python, Streamlit, Gemini AI, SQLite, Beautiful Soup, Firecrawl

**License**: Check individual repository licenses

**Version**: MVP 1.0

---

*Last Updated: January 2026*
