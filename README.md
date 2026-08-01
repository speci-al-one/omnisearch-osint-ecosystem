# OmniSearch Integrated OSINT Ecosystem v1.0

A unified cyber reconnaissance and open-source intelligence (OSINT) pipeline built in Python. This framework demonstrates the **Relational Rooting Technique** by dynamically linking target artifacts across multiple structural modules using a central SQLite data ledger.

## ⚡ Integrated Core Modules (5-in-1 Suite)
1. **Core Ledger (Project 1):** FastPeopleSearch, IPLocation, and Whoxy data-broker tracking layer.
2. **SocialHunter (Project 2):** High-speed multi-platform social media username checker with optimized query parameters.
3. **ImageTracker (Project 3):** EXIF digital image forensic and metadata extraction engine.
4. **GeoIntel Map (Project 4):** Automated geospatial visualization leveraging interactive Leaflet/Folium map rendering.
5. **CyberTrace Hub (Project 5):** Corporate data breach and public credential exposure audit subsystem.

## 🚀 Getting Started

### Prerequisites
Install the required system dependency packages via pip:
```bash
pip install rich requests pillow folium
```

### Running the Orchestrator
Execute the core automation script from your terminal:
```bash
python complete_osint.py
```

## 🛠️ System Architecture (Data Flow Matrix)
- **Central Storage:** Local relational `osint_root.db` utilizing UUID schema keys.
- **Threading Model:** Lightweight defensive request parameters with micro-timeout configurations.

