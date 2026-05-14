# GeoVIS

GeoVIS is a personal GeoGuessr post-game analytics and training companion. It captures completed game data, stores it locally, analyzes strengths and weaknesses, and recommends focused practice.

## Principles

- Personal analytics only
- No live hints during active rounds
- No auto-guessing or active-play overlays
- Passive capture from completed game and review flows when possible

## Stack

- **Extension:** Chrome Extension (Manifest V3)
- **Backend:** FastAPI + SQLite + SQLAlchemy
- **Dashboard:** React + Vite
- **Analytics:** pandas / scikit-learn later

## Repository layout

```text
geovis/
  extension/
    manifest.json
    src/
      background/
      content/
      parser/
      shared/
      storage/
  backend/
    requirements.txt
    app/
      main.py
      db.py
      models.py
      schemas.py
      routes/
      services/
  dashboard/
    package.json
    src/
      api/
      components/
      hooks/
      pages/
  data/
    geodata/
  notebooks/
```

## Phase 1 goals

- Capture completed game and round data
- Store local history in SQLite
- Show country performance statistics
- Show guessed-country vs actual-country confusion matrix
- Show recent games and score trend

## Quick start

### 1) Clone and initialize git

```bash
git init
git branch -M main
git add .
git commit -m "Initial GeoVIS scaffold"
```

### 2) Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

### 3) Run the dashboard

```bash
cd dashboard
npm install
npm run dev
```

Dashboard runs at `http://127.0.0.1:5173` by default.

### 4) Load the extension

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the `extension/` folder

## Current API endpoints

- `GET /health`
- `POST /api/ingest/game`
- `GET /api/games/recent`
- `GET /api/imports/recent`
- `GET /api/rounds/review`
- `PUT /api/rounds/{round_id}/note`
- `GET /api/rounds/review/options`
- `GET /api/training/review-queue`
- `GET /api/export/sqlite`
- `GET /api/analytics/country-performance`
- `GET /api/analytics/region-performance`
- `GET /api/analytics/confusion-matrix`
- `GET /api/analytics/region-confusion-matrix`
- `GET /api/analytics/score-trend`

Fixture payloads for repeatable completed-game ingest checks live in `backend/app/fixtures/`.
Region enrichment currently supports US states, Canadian provinces/territories, Brazilian states, Australian states/territories, and Japanese prefectures.

## Suggested next milestones

1. Implement robust result-page parsing in the extension
2. Add region enrichment for large countries
3. Add notes/tags for missed rounds
4. Add practice priority scoring
5. Add map/mode splits and trend analysis

## GitHub repo setup

After you create an empty GitHub repo:

```bash
git remote add origin https://github.com/<your-username>/geovis.git
git push -u origin main
```

If you prefer the assistant persona branding in the product later, keep the repo/app name **GeoVIS** and use **GeoJarvis** as the in-app coach persona.
