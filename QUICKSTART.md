# 🚀 Quick Start – DataSage (Frontend + Backend)

> **TL;DR** – you need **two terminals**: one for the Python backend, one for the
> React frontend. Open both, follow the steps below, then visit
> **http://localhost:3000** in your browser.

---

## How the pieces fit together

```
Browser (http://localhost:3000)
        │
        │  /api/*  ──proxy──►  FastAPI backend (http://localhost:8000)
        │                              │
        │                         DuckDB + pandas
        │                         (optional) Mistral AI LLM
        │
   React / Vite frontend
```

- **Frontend** (React + Vite) – lives in `frontend/`, runs on port **3000**.
- **Backend** (FastAPI + DuckDB) – lives in `backend/`, runs on port **8000**.
- Vite automatically forwards every request that starts with `/api` to the
  backend, so the browser never has to talk to two different origins.

---

## Prerequisites

| Tool | Minimum version | Download |
|------|----------------|---------|
| Python | 3.8 | https://python.org |
| Node.js + npm | 16 | https://nodejs.org |

Check you have them:

```bash
python3 --version   # or  python --version  on Windows
node --version
npm --version
```

---

## ⚡ Fastest way – one-command launch

### Mac / Linux

```bash
# Clone the repo (skip if you already have it)
git clone https://github.com/spoo5/Hack_Web.git
cd Hack_Web

# Make the script executable (first time only)
chmod +x start-all.sh

# Run both servers
./start-all.sh
```

### Windows

Double-click **`start-all.bat`** in the repo root.

Both servers start in separate windows automatically.

---

## 🛠 Step-by-step (manual) setup

### Terminal 1 – Backend

```bash
cd backend

# Create a virtual environment (first time only)
python3 -m venv venv          # Mac/Linux
# python -m venv venv         # Windows

# Activate it
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# (Optional) enable Mistral AI for richer NL answers
# export MISTRAL_API_KEY=sk-...   # Mac/Linux
# set MISTRAL_API_KEY=sk-...      # Windows

# Start the API server
python main.py
```

✅ You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2 – Frontend

```bash
cd frontend

# Install Node packages (first time only)
npm install

# Start the dev server
npm run dev
```

✅ You should see:
```
  VITE v5.x.x  ready in ...ms
  ➜  Local:   http://localhost:3000/
```

---

## 🌐 Open the app

Navigate to **http://localhost:3000** in your browser.

---

## 📋 Using the app – step by step

1. **Landing page** – click **Get Started** or **Sign In** (uses mock auth, any
   email/password works).
2. **Department selection** – pick the analytics focus closest to your data.
3. **Upload a CSV** – drag-and-drop or click the upload area. Any CSV works.
4. **Ask questions** in plain English, or click a suggested question.
5. **Read the 4-section response:**
   - ① Data-backed answer
   - ② Executed SQL query
   - ③ How the answer was derived
   - ④ Auto-generated chart

---

## 🧪 No CSV handy? Use the included sample

A sample dataset is included at the repo root:

```bash
# it's already there:
ls sample-dataset.csv
```

Upload `sample-dataset.csv` and try questions like:

- *"How many total records are there?"*
- *"What is the average salary by department?"*
- *"Show the distribution of job titles"*

---

## 🤖 Optional – Mistral AI (LLM) integration

Without an API key the backend still works fully using its built-in
rule-based query parser and DuckDB engine.

To enable **richer natural-language answers and smarter SQL generation**:

1. Get a free API key at https://console.mistral.ai
2. Set it before starting the backend:

```bash
# Mac / Linux
export MISTRAL_API_KEY=sk-your-key-here
python main.py

# Windows (Command Prompt)
set MISTRAL_API_KEY=sk-your-key-here
python main.py
```

---

## 🔗 Useful URLs once both servers are running

| URL | What it is |
|-----|-----------|
| http://localhost:3000 | React frontend – main app |
| http://localhost:8000 | FastAPI backend root |
| http://localhost:8000/docs | Interactive Swagger API docs |
| http://localhost:8000/health | Backend health check |

---

## ❗ Troubleshooting

### "python3: command not found"
Install Python 3.8+ from https://python.org. On Windows use `python` instead of `python3`.

### "No module named 'fastapi'" (or any other module)
Your virtual environment is not activated. Run:
```bash
source backend/venv/bin/activate   # Mac/Linux
backend\venv\Scripts\activate      # Windows
```
Then re-run `pip install -r requirements.txt`.

### "Port 8000 already in use"
Kill the process using port 8000, or change the port in `backend/main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```
Then update `frontend/vite.config.js` proxy target to match.

### "npm: command not found"
Install Node.js from https://nodejs.org.

### "Failed to fetch" / network error in the browser
Make sure the **backend** is running. The frontend cannot work without it.
Check http://localhost:8000/health — it should return `{"status":"healthy",...}`.

### CORS errors in browser console
The backend already has `allow_origins=["*"]`. If you still see CORS errors,
confirm the backend is actually running (it may have crashed on startup).

---

## 📦 Individual launcher scripts

| Script | OS | What it does |
|--------|----|-------------|
| `start-all.sh` | Mac / Linux | Starts both backend + frontend |
| `start-backend.sh` | Mac / Linux | Starts backend only |
| `start-frontend.sh` | Mac / Linux | Starts frontend only |
| `start-all.bat` | Windows | Starts both backend + frontend |
| `start-backend.bat` | Windows | Starts backend only |
| `start-frontend.bat` | Windows | Starts frontend only |

---

## ✅ Everything working? Verify with this checklist

- [ ] `http://localhost:8000/health` returns `{"status":"healthy",...}`
- [ ] `http://localhost:3000` loads the DataSage landing page
- [ ] Signing in (any email/password) reaches the department selection screen
- [ ] Uploading a CSV shows row count, column count, and suggested questions
- [ ] Submitting a question returns all four response sections
- [ ] A chart is rendered for distribution/average queries
- [ ] No red errors in the browser developer console (`F12 → Console`)

---

**You're all set! 🎉**  Upload any CSV and start asking questions in plain English.
