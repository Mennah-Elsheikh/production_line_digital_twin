# Vercel Deployment Instructions

## Prerequisites
1. Install Vercel CLI: `npm install -g vercel`
2. Create a Vercel account at https://vercel.com

## Deployment Steps

### 1. Login to Vercel
```bash
vercel login
```

### 2. Deploy to Production
```bash
vercel --prod
```

### 3.# Deployment Guide 🚀

## 1. Local Development (Full Features)
Running locally provides the full experience: Real Simulation + Web Dashboard + Streamlit.

**Prerequisites:**
- Python 3.8+

**Setup:**
1. Install local dependencies:
   ```bash
   pip install -r requirements-local.txt
   ```

2. Run the services (in separate terminals):

   **Backend API (FastAPI):**
   ```bash
   uvicorn api.index:app --reload
   ```

   **Web Dashboard:**
   ```bash
   python -m http.server 8080 --directory public
   ```
   *Access: http://localhost:8080*

   **Streamlit App:**
   ```bash
   streamlit run app_launcher.py
   ```
   *Access: http://localhost:8501*

---

## 2. Streamlit Cloud (Full Simulation)
Hosts the Python-heavy simulation and data science interface.

- **Config:** Uses `requirements.txt` (Full dependencies including matplotlib, simpy, plotly).
- **Entry Point:** `app_launcher.py`
- **Python Version:** 3.10+ (Recommended)

---

## 3. Vercel (Web Dashboard Demo)
Hosts the modern web dashboard with a lightweight demo API.

**Why distinct?** Vercel Serverless has size limits (250MB). We deploy a simplified "Demo API" for Vercel that doesn't import heavy `src/` modules.

- **Config:** `vercel.json`
- **Dependencies:** `api/requirements.txt` (Minimal: fastapi, numpy, pydantic only).
- **Structure:**
    - `public/`: Static HTML/JS frontend
    - `api/`: Lightweight FastAPI backend

**Steps to Deploy:**
1. Push to GitHub.
2. Import project in Vercel.
3. Vercel automatically detects `vercel.json` and builds.
- Keep `SIM_TIME` under 300 minutes for web deployment
- The frontend automatically calls `/api/simulate` endpoint
