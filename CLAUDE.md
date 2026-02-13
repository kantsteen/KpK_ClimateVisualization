# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Climate data visualization prototype for "Kloden på Kanten" (Climate on the Edge). Vue 3 frontend with interactive Mapbox choropleth maps and D3.js charts, backed by a FastAPI Python API serving CO2 emissions and temperature anomaly data.

## Development Commands

All frontend commands run from `frontend/`:

```bash
# Frontend
cd frontend
npm run dev        # Vite dev server at http://localhost:5173
npm run build      # Production build → frontend/dist/
npm run lint       # ESLint with auto-fix and cache
npm run format     # Prettier formatting for src/

# Backend (from project root, with .venv activated)
.venv\Scripts\activate                          # Windows
uvicorn backend.app:app --reload --port 8000    # API at http://localhost:8000
```

Both servers must run simultaneously — the frontend fetches from the backend at localhost:8000.

## Architecture

**Frontend** (`frontend/`) — Vue 3 SPA using Composition API (`<script setup>`) exclusively.
- `App.vue` — Root component: Mapbox GL map (top 65vh) with CO2 choropleth + control panel (metric toggle, year slider 1950-2024), and a chart area (bottom 35vh) with a 2-column grid.
- `TemperatureTimeline.vue` — D3.js animated line chart of NASA temperature anomalies with auto-play animation, tooltip, and responsive viewBox scaling.
- Map uses Mapbox **feature state** (not layer repaint) for efficient color updates keyed by ISO 3166-1 alpha-3 country codes.
- Mapbox token loaded via `import.meta.env.VITE_MAPBOX_TOKEN` from `frontend/.env`.
- Path alias: `@/` maps to `./src/`.

**Backend** (`backend/`) — FastAPI with CORS allowing `http://localhost:5173`.
- `app.py` — Two endpoints:
  - `GET /api/co2/all` — CO2 emissions by country and year (1950-2024, filtered by ISO code and co2_per_capita ≤ 100)
  - `GET /api/temperature` — NASA GISTEMP annual temperature anomalies (J-D column)
- `data/` — CSV data files: `owid-co2-data.csv` (OWID), `NASA_GISTEMP.csv` (NASA GISTEMP baseline 1951-1980)

**Utility scripts** (project root) — Python scripts for sea-level-rise analysis:
- `explore_geotiff.py` — Analyzes elevation height distribution from GeoTIFF raster data
- `generate_flood_geojson.py` — Converts elevation raster to flood zone GeoJSON polygons (EPSG:25832 → EPSG:4326)

## Code Style

- **Prettier**: no semicolons, single quotes, 100 char print width
- **ESLint**: flat config (v9+), Vue essential rules, Prettier integration
- **Vue**: Composition API with `<script setup>` only — no Options API
- D3 and Mapbox use direct DOM manipulation within Vue lifecycle hooks (`onMounted`/`onUnmounted`)

## Data Flow

Frontend `ref()` state → fetch from backend on mount → Mapbox feature state updates on year/metric change. D3 chart fetches temperature data independently and manages its own animation timer (cleaned up on unmount).

## No Test Suite

There is currently no testing framework configured.
