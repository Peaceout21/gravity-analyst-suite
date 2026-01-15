# 🌌 Gravitic Nebula

**The "Alpha" Layer for the Gravitic Financial Platform.**

`gravitic-nebula` is a specialized microservice designed to ingest, normalize, and signal-process **Alternative Data** for financial analysis. It acts as the "Eyes" of the platform, feeding high-quality signals to the "Brain" (`gravitic-celestial`).

## 🏗️ Architecture
See [DESIGN.md](./DESIGN.md) for the detailed SOTA 2025 architecture.

### Key Modules
*   **`scrapers/`**: High-volume data ingestion using **Crawlee** and **Firecrawl**.
    *   `shipping/`: Bill of Lading & AIS Vessel Tracking.
    *   `hiring/`: Career page monitoring.
    *   `digital/`: App Store & Web Traffic analytics.
*   **`transformers/`**:
    *   **Entity Resolution**: Hybrid Fuzzy+Vector matching to map raw names to Tickers.
    *   **Signal Processing**: Z-Score anomalies, Granger Causality tests, and Nowcasting models.
*   **`db/`**: PostgreSQL + TimescaleDB schema definitions.

## 🚀 Getting Started
(Coming Soon - Phase 2 Implementation)
