# 📡 Phase 2 Detailed Design: Alternative Data Fusion

## 1. The Core Challenge: Entity Resolution
The biggest bottleneck in Alternative Data is not scraping; it's **mapping**.
*   **Problem**: A Bill of Lading says "Hon Hai Precision Ind. Co Ltd".
*   **Requirement**: Map this to `AAPL` (Customer) or `2317.TW` (Supplier).

### 1.1 The `EntityResolver` Service (State-of-the-Art 2025)
**Approach**: Hybrid **Fuzzy Blocking + Vector Semantic Matching**.
*   **Fuzzy (RapidFuzz)**: Fast blocking to find candidate set (Top 50).
*   **Vector (All-MiniLM-L6-v2)**: Semantic re-ranking to handle "Apple" vs "Apple Corps" vs "AAPL".
*   **Graph (Neo4j)**: Traverse "Subsidiary Of" relationships.

**Database Schema: `entity_maps`**
```sql
CREATE TABLE entity_maps (
    raw_name TEXT NOT NULL,         -- "Hon Hai Precision", "Foxconn Technology Group"
    ticker TEXT NOT NULL,           -- "AAPL" (if mapping to customer ecosystem) or "HNHPF"
    entity_type VARCHAR(20),        -- "SUBSIDIARY", "SUPPLIER", "ALIAS"
    confidence_score FLOAT,         -- 0.95
    source VARCHAR(50)              -- "manual_override", "automatic_fuzzy"
);
```

**Workflow**:
1.  Scraper finds string "Space Exploration Technologies".
2.  `EntityResolver` checks DB.
3.  If exact match -> Return Ticker.
4.  If no match -> Run Fuzzy Search -> If score > 0.9 -> Auto-link.
5.  Else -> Flag for Human Review (or ignore).

---

## 2. Microservice: `gravitic-nebula` (Scraping Cluster)

### 2.1 Shipping Scraper (High Priority - Supply Chain)
**Objective**: "Nowcast" Revenue using Physical Goods movement.
**Data Sources (Tiered)**:
1.  **Bill of Lading (BoL)**: *ImportGenius/Panjiva* (Transaction level - High latency).
2.  **AIS Vessel Tracking**: *MarineTraffic/VesselFinder* (Real-time location).
    *   *Alpha Signal*: "Vessel 'Ever Given' carrying 2000 TEU for Target Corp is delayed at Suez."
3.  **Satellite/Geolocation**: *Orbital Insight* (Parking lot fill rates for Retail).

**Fusion Logic**:
*   Combine **AIS Arrival Time** + **BoL Manifest** = **Precise Revenue Recognition Date**.

### 2.2 Hiring Signal Tracker (Medium Priority - Strategy)
**Objective**: Differentiate maintenance hiring vs. expansion hiring.
**Target**: Company Careers Page (Greenhouse/Lever/Workday).
**Tools**: `Firecrawl` (ideal for turning weird DOMs into structured Data).

**Schema**:
```json
{
  "ticker": "NVDA",
  "role_title": "Senior Research Scientist - Generative AI",
  "department": "R&D",
  "location": "Santa Clara, CA",
  "posted_date": "2025-10-12"
}
```

**Processing Logic**:
1.  **Ingest**: Scrape all open roles weekly.
2.  **Classify**: Use **Gemini 2.0 Flash** to categorize roles: `[Engineering, Sales, G&A, Manufacturing]`.
3.  **Signal**: "Engineering roles up 15% QoQ" WHILE "Sales roles flat" = **New Product Phase**.

### 2.3 Digital Footprint (Medium Priority - Revenue Proxy)
**Objective**: Real-time revenue estimation for B2C.
**Target**: App Store Ranks (iOS/Android).

**Normalization**:
*   Raw Rank #14 -> Volatile.
*   **Smoothed Signal**: 7-day Moving Average of Rank.
*   *Alpha Signal*: Rank moved from #50 to #15 sustained for >14 days => **Viral Event**.

---

## 3. Signal Processing Pipeline (The "Quant" Layer)

Raw data is noise. We need **Alpha Signals**.

### 3.1 Advanced Statistical Engine
**Tools**: `Statsmodels` (Python) / `TimescaleDB` (Continuous Aggregates).

#### A. The Z-Score Engine (Anomaly Detection)
`Z_Score = (Current_Value - Mean_90_Day) / Std_Dev_90_Day`
*   **Trigger**: > 2.0 Sigma (Event).

#### B. Granger Causality Test (Predictive Power)
**Goal**: Prove that Signal X *actually predicts* Price Y.
*   Run `grangercausalitytests(stock_price, hiring_count, maxlag=4)`.
*   *Rule*: If p-value < 0.05, the signal is **Valid Alpha**. Discard otherwise.

#### C. Nowcasting Model (Revenue Prediction)
**Goal**: Estimate current quarter revenue *before* earnings.
*   **Model**: Kalman Filter or XGBoost Regressor.
*   **Inputs**: `[Daily_App_Downloads, Weekly_Job_Postings, Monthly_Import_TEUs]`.
*   **Output**: "Predicted Q3 Rev: $4.2B" (vs Consensus $4.0B).

### 3.2 Integration with `gravitic-celestial`
When `ExtractionEngine` generates a generic report, it queries the `Signals` DB:

1.  *Fetch Report*: NVDA Q3 Earnings.
2.  *Query Signals*: `SELECT * FROM signals WHERE ticker='NVDA' AND timestamp > (Now - 90 Days)`.
3.  *Inject Context*:
    *   "**Note**: Hiring data shows a +3 Sigma spike in R&D roles in Q2. Management commentary on 'New Products' is backed by hiring data."

---

## 4. Implementation Steps (No Code, Just Plan)

1.  **Repo Setup**: Initialize `gravitic-nebula` (Python/Typescript mix).
2.  **Database**: Spin up PostgreSQL with `pgvector` (for Entity Resolution) and `TimescaleDB` (for Time Series).
3.  **Base Scraper**: Build one generic `Crawlee` crawler for a simple test site.
4.  **Entity Resolver**: Build the "Fuzzy Matcher" module suitable for company names.
5.  **Signal API**: Build an internal API `GET /signals/{ticker}`.
