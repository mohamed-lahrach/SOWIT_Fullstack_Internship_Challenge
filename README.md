# Sowit Fullstack Challenge - User Guide

## What this app does
- Draw farm plots (polygons) on a map.
- Save plots to a PostGIS-backed API.
- List saved plots and zoom to a selected plot.

## Prerequisites
- Docker Desktop (running).
- `make` and `docker compose` available in terminal.
- A valid Mapbox token in `.env` as `VITE_MAPBOX_TOKEN`.

## 1) Start the app
From the project root:

```bash
make up
```

Open:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/plots/`

## 2) Use the app (UI flow)
1. Open `http://localhost:5173`.
2. Draw a polygon with the draw tool (top-left on the map).
3. Enter a value in **Plot Name**.
4. Click **Save Drawn Polygon**.
5. Use **Saved Plots** dropdown to select a plot and auto-zoom to it.

## 3) Useful day-to-day commands
```bash
make status                 # show container status
make logs SERVICE=backend   # stream backend logs
make logs SERVICE=frontend  # stream frontend logs
make test                   # run backend tests
make down                   # stop containers
```

## API quick reference
- `GET /api/plots/` -> list plots as GeoJSON.
- `POST /api/plots/` -> create a plot (GeoJSON feature).

Example `POST`:

```bash
curl -X POST http://localhost:8000/api/plots/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-6.84, 34.02],
        [-6.83, 34.02],
        [-6.83, 34.01],
        [-6.84, 34.01],
        [-6.84, 34.02]
      ]]
    },
    "properties": { "name": "Farm A" }
  }'
```

## Troubleshooting
- If the map is blank, verify `VITE_MAPBOX_TOKEN` in `.env`, then restart: `make restart`.
- If frontend cannot reach API, verify `VITE_API_URL=http://localhost:8000`.
- If database state is broken and you want a full reset:
  - `make clean-reset`
  - `make up`
  - `make migrate`
