# PolarSync — Production Deployment Guide (SIH26062)

This guide documents the exact configuration and deployment steps for launching **PolarSync** to production on **Render** (FastAPI Backend + Python Simulation Engine) and **Vercel** (React Command Center Frontend).

---

## 🏗️ Architecture Topology

```
┌─────────────────────────────────────────────────────────────┐
│                       Vercel (Frontend)                     │
│         React 19 + Vite + Leaflet GIS + IndexedDB           │
│                   https://polarsync.vercel.app              │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS API Calls (VITE_API_BASE_URL)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Render (Backend Gateway)                 │
│         FastAPI + Uvicorn + IntelligenceService             │
│            https://polarsync-api.onrender.com/api/v1        │
└──────────────────────────────┬──────────────────────────────┘
                               │ In-Process Execution
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Python Simulation Kernel                   │
│          (src/core, src/models, configs/scenarios)          │
│               Authoritative Source of Truth                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 1. Backend Deployment on Render

### Step 1.1: Create Render Web Service
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your GitHub repository (`PolarSync` / `polar-simulator`).

### Step 1.2: Configure Service Settings
- **Name**: `polarsync-api`
- **Region**: Closest to your users (e.g., *Singapore / Frankfurt / Ohio*)
- **Branch**: `main`
- **Root Directory**: `.` *(Leave as repository root so it can access `src/` and `configs/`)*
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r polarsync-platform/backend/requirements.txt
  ```
- **Start Command**:
  ```bash
  python -m uvicorn app.main:app --app-dir polarsync-platform/backend --host 0.0.0.0 --port $PORT
  ```

### Step 1.3: Set Render Environment Variables
Add the following key-value pairs in the **Environment Variables** section on Render:

| Variable Key | Suggested Value | Description |
|---|---|---|
| `PYTHONPATH` | `.` | Ensures Python finds root `src` package |
| `BACKEND_CORS_ORIGINS` | `https://<YOUR_VERCEL_APP>.vercel.app,http://localhost:5175,http://localhost:5173` | Allowed frontend domains (comma-separated or JSON list) |
| `PROJECT_NAME` | `PolarSync API` | API display name in Swagger docs |
| `SECRET_KEY` | `generate-a-secure-random-string-here` | App secret key |
| `SIMULATOR_ROOT` | *(Optional, auto-detected)* | Path to simulation root containing `src` and `configs` |
| `DATABASE_URL` | *(Optional)* | PostgreSQL connection string if persistent DB is connected |

Click **Create Web Service**. Once deployed, copy your Render URL (e.g. `https://polarsync-api.onrender.com`).

---

## ⚡ 2. Frontend Deployment on Vercel

### Step 2.1: Import Project to Vercel
1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository.

### Step 2.2: Configure Project Settings
- **Project Name**: `polarsync`
- **Framework Preset**: `Vite`
- **Root Directory**: `polarsync-platform/frontend` *(Important: click Edit and select `polarsync-platform/frontend`)*
- **Build Command**: `npm run build` *(auto-detected)*
- **Output Directory**: `dist` *(auto-detected)*
- **Install Command**: `npm install` *(auto-detected)*

### Step 2.3: Set Vercel Environment Variables
Add the following in the **Environment Variables** section on Vercel:

| Variable Key | Value | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `https://polarsync-api.onrender.com/api/v1` | Your live Render backend API URL (with `/api/v1` suffix) |
| `VITE_APP_TITLE` | `PolarSync Command Center` | Web app header title |
| `VITE_SIH_PROBLEM_CODE` | `SIH26062` | Hackathon Problem Statement code |

Click **Deploy**.

---

## 🔄 3. Update Backend CORS After Frontend Deploy

Once Vercel finishes deployment and provides your production URL (e.g. `https://polarsync.vercel.app`):
1. Go back to Render Dashboard $\rightarrow$ **Environment Variables**.
2. Update `BACKEND_CORS_ORIGINS` to include your live Vercel URL:
   ```
   BACKEND_CORS_ORIGINS=https://polarsync.vercel.app,https://polarsync-git-main-*.vercel.app,http://localhost:5175
   ```
3. Render will automatically apply the changes without downtime.

---

## 🧪 4. Production Verification Checklist

1. **Health Probe**:
   Visit `https://<YOUR_RENDER_APP>.onrender.com/api/v1/health`
   - Expected: `{"status":"ok","service":"polarsync-api","simulation_engine":"connected"}`
2. **Scenario Intelligence API**:
   Visit `https://<YOUR_RENDER_APP>.onrender.com/api/v1/intelligence/summary?scenario_id=1`
   - Expected: `HTTP 200 OK` with 4-pillar explainability JSON.
3. **Frontend SPA Navigation**:
   Open `https://<YOUR_VERCEL_APP>.vercel.app/`
   - Verify Scenario Selector changes state across Scenarios 1 to 5.
   - Navigate directly to `/inventory` and refresh the browser — verify no 404 error occurs.
   - Disconnect internet — verify **IndexedDB Offline Mode** displays cached data with timestamps.
