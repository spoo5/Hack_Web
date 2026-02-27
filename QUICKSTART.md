# 🚀 Quick Start Guide - DataSage

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.8 or higher
- ✅ Node.js 16 or higher
- ✅ npm (comes with Node.js)

---

## 🎯 Method 1: Automated Startup (Windows)

### One-Command Launch

Double-click: **`start-all.bat`**

This will:

1. Create Python virtual environment (if needed)
2. Install Python dependencies
3. Start FastAPI backend on port 8000
4. Install Node dependencies (if needed)
5. Start React frontend on port 3000

### Individual Servers

- **Backend only:** Double-click `start-backend.bat`
- **Frontend only:** Double-click `start-frontend.bat`

---

## 🛠 Method 2: Manual Setup

### Backend Setup

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

✅ Backend running at: **http://localhost:8000**

### Frontend Setup

Open a **new terminal** window:

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

---

## 📊 Testing the Application

### Step 1: Open Frontend

Navigate to **http://localhost:3000** in your browser

### Step 2: Upload Dataset

1. You'll see the landing page with upload interface
2. Drag & drop a CSV file or click to browse
3. Wait for schema analysis
4. Click "Analyze Dataset"

### Step 3: Ask Questions

Example questions to try:

- "What is the total number of records?"
- "Show distribution by category"
- "What is the churn rate by gender?"
- "Calculate average revenue"

### Step 4: View Results

You'll see 4 sections:

1. **Natural Language Answer** - Plain English response
2. **SQL Query Logic** - Generated query
3. **Derivation** - How the answer was computed
4. **Visualization** - Dynamic chart

---

## 🧪 Sample Dataset

Don't have a CSV? Create a simple test file:

**customers.csv**

```csv
customerID,name,gender,age,region,revenue,churn
1,Alice,Female,25,North,1200,No
2,Bob,Male,30,South,1500,Yes
3,Charlie,Male,35,East,1800,No
4,Diana,Female,28,West,1300,Yes
5,Eve,Female,32,North,1600,No
```

Upload this and try:

- "What is the churn rate by gender?"
- "Show average revenue by region"

---

## 📡 API Testing

Backend API is available at **http://localhost:8000**

### Interactive API Docs

Visit: **http://localhost:8000/docs**

This opens FastAPI's built-in Swagger UI where you can test all endpoints.

---

## ❗ Troubleshooting

### Backend Issues

**Error:** `Python was not found`
**Fix:** Install Python from [python.org](https://python.org)

**Error:** `No module named 'fastapi'`
**Fix:** Make sure virtual environment is activated and run `pip install -r requirements.txt`

**Error:** `Address already in use`
**Fix:** Port 8000 is busy. Change port in `main.py`:

```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### Frontend Issues

**Error:** `npm: command not found`
**Fix:** Install Node.js from [nodejs.org](https://nodejs.org)

**Error:** `EADDRINUSE: address already in use`
**Fix:** Port 3000 is busy. Vite will automatically suggest another port.

**Error:** `Failed to fetch`
**Fix:** Make sure backend is running on port 8000

### CORS Errors

If you see CORS errors in browser console:

1. Check that backend is running
2. Verify CORS middleware in `backend/main.py` includes:
   ```python
   allow_origins=["*"]
   ```

---

## 🎨 Features to Explore

1. **Dark Theme** - Premium black & gold design
2. **Animations** - Smooth Framer Motion transitions
3. **Glassmorphic Cards** - Modern UI effects
4. **Suggested Questions** - Auto-generated based on schema
5. **Confidence Scoring** - Visual confidence indicators
6. **Data Grounding** - Verification badges

---

## 📦 Production Deployment

### Backend

```bash
cd backend
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

```bash
cd frontend
npm run build
# Deploy 'dist' folder to Netlify/Vercel/AWS
```

---

## 🔐 Security Notes

For production:

1. Change CORS `allow_origins` from `["*"]` to specific domains
2. Add authentication middleware
3. Implement rate limiting
4. Use HTTPS
5. Validate file uploads (size limits, type checking)

---

## 📞 Getting Help

- Check `README.md` for detailed documentation
- Review `backend/README.md` for API details
- Review `frontend/README.md` for UI components

---

## ✅ Success Checklist

After running the application, verify:

- [ ] Backend responds at http://localhost:8000
- [ ] Frontend loads at http://localhost:3000
- [ ] CSV upload works
- [ ] Schema detection shows columns
- [ ] Query submission returns results
- [ ] Charts render correctly
- [ ] Confidence badges appear
- [ ] No console errors

---

**You're all set! 🎉**

Start exploring your data with natural language queries!
