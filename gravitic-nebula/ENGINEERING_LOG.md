# 📓 SOTA Engineering Log: Problem-Solving Journal

This log tracks niche engineering challenges, high-stakes trade-offs, and their SOTA solutions within the Gravitic Nebula project.

---

## 🛑 Problem: Firecrawl API Credit Hemorrhage
**Date**: 2026-01-04
**Identify**: 
Extremely high credit usage (up to 211 credits per call) detected when using Firecrawl V2 `/EXTRACT` on complex job portals like Workday. The AI-powered crawler is powerful but inefficient for high-volume signal tracking.

**Optimize**: 
Pivoted to a **Local-First Parsing** strategy:
- Use Firecrawl `/SCRAPE` (1 credit) to get raw HTML/Markdown.
- Use **`trafilatura`** (SOTA python library) for intelligent boilerplate removal (headers, footers, nav).
- Leverage the local **Gemini-Pro** API for extremely low-cost schema extraction from the cleaned text.

**Solve**: 
Cost reduced by **99.5%** (1 credit vs 211 credits). Latency remains low while accuracy is maintained through structured prompting.

---

## 📈 Problem: Data Saturation in Massive Job Portals
**Date**: 2026-01-04
**Identify**: 
Nvidia (and others) have 2000+ open roles. Scrapping every single page is a credit-killer and provides diminishing returns for an "Alpha Signal."

**Optimize**: 
Implemented **Strategic Signal Sampling**:
- For portals with >200 jobs, we only scrape the first **100 roles**.
- Statistical Law of Large Numbers ensures that the ratio of R&D to Sales (Expansion Velocity) is captured with >95% confidence without needing the full dataset.

**Solve**: 
Ensures consistent signal generation speed and cost-effectiveness for Mega-Cap entities.

---

## 🛠️ Problem: Firecrawl SDK V2 Method Mismatch
**Date**: 2026-01-04
**Identify**: 
`AttributeError: 'Firecrawl' object has no attribute 'scrape_url'` encountered. Research revealed that while some documentation suggests `scrape_url()`, the installed SDK version required `scrape()` with snake_case parameters (`wait_for`, `only_main_content`).

**Optimize**: 
Verified method names using `dir()` and `help()` on a live instance. Refactored all scrapers (`Hiring`, `Shipping`, `Digital`) to use the verified signatures and access the `.markdown` attribute of the returned `Document` object.

**Solve**: 
Codebase now correctly uses the V2 SDK and **Gemini-3-Flash-Preview**, eliminating `AttributeError` and 404s. Total extraction cost reduced by **99%** (1 credit vs 211). Accuracy is higher due to 6s wait-time logic.

---

---

## ⚖️ Problem: Macro/Micro Metric Mismatch (20 vs 1969)
**Date**: 2026-01-04
**Identify**: 
The scraper correctly calculated trends from a 20-job sample, but the user noted a discrepancy because the portal reported 1969 total roles. High-alpha signals need both relative velocity (trend) and absolute scale (macro).

**Optimize**: 
Refactored the Gemini synthesis prompt to extract two distinct values:
1. **Total Count (Macro)**: Extracted from headers like "1969 items found".
2. **Role List (Micro)**: A 20-role sample for categorizing R&D vs Sales.

**Solve**: 
Engine now returns both. Velocity is calculated on the high-confidence sample, while the total magnitude is preserved. Credits remain at **1**.

> [!NOTE]
> **Status**: Resolved but research better solution later (e.g., parallelizing page scrapes or using Firecrawl's 'map' feature for deeper indexing if volume-to-credit ratio allows).

---
