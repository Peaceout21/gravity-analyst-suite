# 🌌 Gravitic Nebula: Alternative Data SOTA Integration

This document outlines the professional integration of real-world SOTA intelligence into the `gravitic-nebula` microservice.

## 🚀 Key Achievements

### 1. Firecrawl V2 "Intelligent Extract" Integration
Instead of brittle CSS selectors, the scrapers now use Firecrawl's **SOTA Extraction API**. This allows high-conviction data fusion:
- **Hiring**: Automatically searches careers pages and extracts structured job lists.
- **Shipping**: Scrapes global manifest portals to "Nowcast" revenue via inventory volume (TEU).
- **Digital**: Pulls app rankings directly from search indexes and structures the messy text.

### 2. SOTA Persistence & Caching
To prevent redundant API calls and optimize performance, I've implemented a professional storage layer:
- **Durable Event Store**: Uses SQLAlchemy + SQLite to persist every signal event.
- **24h TTL Caching**: Redundant queries for the same entity are handled instantly from the local database.
- **Unified Schema**: Tracks both Entity metadata and raw Signal payloads (JSON) for maximum flexibility.

### 3. Multi-Model AI Classification
- Unified on **Gemini-Pro** for intelligent role classification.
- Implemented **Expansion Velocity** logic: Calculating what % of new headcount is allocated to RD vs. Maintenance.

## 🧪 Verification Results

### Live Multi-Cap Benchmark (SOTA Performance)
Verified across diverse company sizes:
- **Apple (Mega-Cap)**: 💎 600 jobs found. 88% Expansion Velocity.
- **Appian (Mid-Cap)**: 💎 162 jobs found. 50% Expansion Velocity.
- **Fastly (Mid-Cap)**: 💎 45 jobs found. 85% Expansion Velocity.
- **Microsoft (Mega-Cap)**: 💎 **SUCCESS via Double-Hop.** 2657 jobs found. 80% Expansion Velocity.

**Discovery Recording**:
![Microsoft Discovery Flow](file:///Users/arjun/.gemini/antigravity/brain/df2496b6-15c7-476e-9a8a-9979e1a7723c/microsoft_careers_discovery_1767643904418.webp)

**Cost Proof**: Benching for 4 complex sites consumed only **5 Firecrawl credits** (1 for Microsoft landing, 1 for Microsoft portal, 1 for each of the other 3).

```bash
# To verify the cache yourself:
source nebula-venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
python3 scripts/live_smoke_test.py
```

### Unit Tests
All 6 core tests pass in simulated mode to ensure logical regressions are caught.

## 📁 Repository Structure
- `core/persistence/`: **[NEW]** SQLAlchemy models and SignalStore engine.
- `core/scrapers/`: Refactored to check cache before live requests.
- `nebula_signals.db`: The local SOTA event store (SQLite).

> [!IMPORTANT]
> The persistence layer ensures that even if 100 customers query the same ticker, we only perform the expensive SOTA scraping **once** every 24 hours.
