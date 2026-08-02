# OmniSearch Integrated OSINT Ecosystem

A unified cyber-reconnaissance and OSINT pipeline that links all discovered
artifacts about a target to a single root identifier (UUID) using one central
SQLite ledger — the **Relational Rooting Technique**.

## Modules

| # | Module | Purpose |
|---|--------|---------|
| 1 | `omnisearch.py` | Core ledger: FastPeopleSearch / Whoxy / IPLocation (demo) |
| 2 | `socialhunter.py` | Cross-platform username availability checker |
| 3 | `imagetracker.py` | EXIF + GPS metadata extraction from images |
| 4 | `geointel.py` | Interactive Folium map of collected coordinates |
| 5 | `cybertrace.py` | Data-breach audit (simulated, optional HIBP API) |

> **Note:** FastPeopleSearch, Whoxy and the breach audit run in clearly
> labelled **demo mode** — paid APIs are replaced with sample records so the
> full pipeline is runnable offline. The IP geolocation module uses the free
> `ip-api.com` endpoint and performs real lookups.

## Architecture

target query ──► orchestrator.py ──► target_id (UUID)
                        │
        ┌───────────────┼───────────────────┐
        │               │                   │
  socialhunter    imagetracker        cybertrace
        │               │                   │
        └───────────────┼───────────────────┘
                        ▼
                 osint_root.db (SQLite)
                        │
                        ▼
                 geointel.py ──► interactive map (HTML)

## Installation

```bash
pip install -r requirements.txt
