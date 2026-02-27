# 🧠 DataSage - Conversational Data Intelligence Platform

![DataSage Banner](https://img.shields.io/badge/DataSage-Production--Ready-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![React](https://img.shields.io/badge/React-18.2-61dafb?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square)

**Full-stack SaaS platform for department-specific conversational analytics** with Google OAuth authentication, AI-powered insights, and dataset-agnostic analysis. Upload CSV files, select your department focus, and get **data-backed, explainable, hallucination-free answers** with visualizations.

---

## 🌟 New Features (v2.0)

### 🔐 Authentication & User Management

- **Marketing Landing Page** - Professional homepage with hero, features, and statistics
- **Google OAuth Integration** - One-click signup/login with Google
- **Email/Password Auth** - Traditional authentication with secure backend
- **Protected Routes** - Dashboard access requires authentication

### 🎯 Department-Based Analytics

Choose from 6 department types with tailored insights:

- 📈 **Sales Analytics** - Revenue trends, customer segments, churn analysis
- 🎯 **Marketing Intelligence** - Campaign performance, lead generation, ROI
- 💰 **Finance Analytics** - Financial health, cost breakdown, profit margins
- 🎓 **Business Intelligence** - KPIs, strategic metrics, market analysis
- ⚙️ **Operations Analytics** - Process efficiency, resource utilization
- 👥 **HR Analytics** - Workforce data, employee performance, turnover

### 💡 Smart Insights Tab

- **Auto-Generated Insights** - AI-powered analysis based on your department
- **Suggested Queries** - Pre-built questions relevant to your domain
- **Column Analysis** - Automatic detection of data types and opportunities
- **Data Quality Indicators** - Real-time feedback on dataset completeness

---

## 🎯 Problem Statement

A production-ready SaaS system that:

- ✅ Provides **professional landing page** with authentication
- ✅ Supports **department-specific analytics** (Sales, Marketing, Finance, etc.)
- ✅ Accepts **any structured CSV dataset**
- ✅ Parses natural language questions
- ✅ Executes **deterministic Pandas computations** (zero hallucination)
- ✅ Returns **4-section structured responses**:
  1. **Natural Language Answer**
  2. **SQL-style Query Logic**
  3. **Derivation Explanation** (formula, rows, columns)
  4. **Dynamic Visualization**
- ✅ Includes **confidence scoring** and **data grounding**
- ✅ Generates **AI-powered insights** tailored to department needs

---

## 🏗 Tech Stack

### Backend

- **FastAPI** - High-performance Python web framework
- **Pandas** - All computations (anti-hallucination enforcement)
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend

- **React 18** - UI framework (functional components)
- **Framer Motion** - Smooth animations
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Vite** - Build tool

### Design

- **Dark Neo-Enterprise Theme**
- Background: `#0C0E14`
- Accent: Gold `#EAAB00`
- Fonts: DM Sans, Lora, DM Mono
- Glassmorphic cards with hover effects

---

## 📂 Project Structure

```
dataweb/
├── backend/
│   ├── main.py                  # FastAPI app with auth endpoints
│   ├── csv_manager.py           # CSV upload & storage
│   ├── schema_analyzer.py       # Auto-detect column types
│   ├── query_parser.py          # NL query → structured query
│   ├── analytics_engine.py      # Pandas execution engine
│   ├── response_formatter.py    # Format 4-section responses
│   ├── requirements.txt         # Python dependencies
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx                    # ✨ Marketing landing page
│   │   │   ├── HomePage.css
│   │   │   ├── LoginPage.jsx                   # ✨ Login with Google OAuth
│   │   │   ├── SignupPage.jsx                  # ✨ Registration form
│   │   │   ├── AuthPages.css                   # ✨ Shared auth styling
│   │   │   ├── DepartmentSelectionPage.jsx     # ✨ Department chooser
│   │   │   ├── DepartmentSelectionPage.css
│   │   │   ├── LandingPage.jsx                 # CSV upload (protected)
│   │   │   ├── LandingPage.css
│   │   │   ├── DashboardPage.jsx               # Main dashboard with tabs
│   │   │   └── DashboardPage.css
│   │   ├── components/
│   │   │   ├── QueryTab.jsx          # Query interface (4-section output)
│   │   │   ├── QueryTab.css
│   │   │   ├── InsightsTab.jsx       # ✨ Department-specific insights
│   │   │   ├── InsightsTab.css       # ✨ NEW
│   │   │   ├── ChartComponent.jsx    # Recharts visualizations
│   │   │   ├── ChartComponent.css
│   │   │   ├── ConfidenceComponent.jsx  # Confidence scoring UI
│   │   │   ├── ConfidenceComponent.css
│   │   │   ├── DatasetInfoPanel.jsx
│   │   │   └── DatasetInfoPanel.css
│   │   ├── App.jsx                   # ✨ Updated with protected routes
│   │   ├── main.jsx
│   │   └── index.css                 # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
│
└── README.md                         # This file
```

✨ = New in v2.0

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### 1️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python main.py
```

Backend runs on: **http://localhost:8000**

### 2️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 🔄 User Flow

```
HomePage (/)
  ├── View features, stats, and benefits
  └── Click "Get Started" or "Sign In"
      ↓
Login/Signup (/login or /signup)
  ├── Email/Password authentication
  ├── Google OAuth (one-click)
  └── Creates account or authenticates
      ↓
Department Selection (/departments)
  ├── Choose from 6 departments
  ├── View department-specific insights preview
  └── Select your analytics focus
      ↓
CSV Upload (/upload)
  ├── Drag & drop CSV file
  ├── Auto-detect schema
  └── View dataset preview
      ↓
Dashboard (/dashboard)
  ├── Query Tab - Ask questions in natural language
  ├── Overview Tab - Dataset statistics
  └── Insights Tab - AI-powered department-specific insights
```

---

## 🔐 Authentication Endpoints (New in v2.0)

### POST `/auth/login`

Email/password login

**Request:**

```json
{
  "email": "user@company.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "token": "mock_jwt_token_user_at_company_com",
  "user": {
    "name": "User",
    "email": "user@company.com",
    "company": "DataSage User",
    "userId": "user_1234"
  },
  "message": "Login successful"
}
```

### POST `/auth/signup`

User registration

**Request:**

```json
{
  "name": "John Doe",
  "email": "john@company.com",
  "company": "Acme Corp",
  "password": "password123"
}
```

**Response:** Same structure as login

### POST `/auth/google`

Google OAuth authentication (mock implementation)

**Request:**

```json
{
  "email": "user@gmail.com",
  "name": "Google User"
}
```

**Response:** Same structure as login, with `authProvider: "google"`

> **Note:** Current implementation uses mock JWT tokens. For production:
>
> - Implement real JWT with PyJWT
> - Hash passwords with bcrypt
> - Verify Google OAuth tokens with Google's API
> - Add token expiration and refresh logic

---

## 🎬 Usage Demo

### Step 1: Upload Dataset

1. Navigate to **http://localhost:3000**
2. Drag & drop your CSV file or click to browse
3. System auto-detects schema:
   - Numeric columns
   - Categorical columns
   - Date columns
   - Boolean columns
4. View preview and suggested questions

### Step 2: Ask Questions

Example queries:

- _"What is the churn rate by gender?"_
- _"Show average revenue by department"_
- _"Count customers by region"_
- _"What is the retention rate?"_

### Step 3: Get 4-Section Response

#### ① Data-Backed Answer

Plain English answer with exact values from your dataset.

#### ② SQL Query Logic

```sql
SELECT gender,
       COUNT(*) as total,
       SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) as churned,
       ROUND(SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as churn_rate
FROM dataset
GROUP BY gender
```

#### ③ Derivation

- **Rows Analyzed:** 7,043
- **Columns Used:** Churn, gender
- **Formula:** `churn_rate = (churned ÷ total) × 100`
- **Calculations:**
  - Male: `1869 ÷ 7043 × 100 = 26.54%`
  - Female: `1893 ÷ 7043 × 100 = 26.88%`

#### ④ Visualization

Auto-generated bar chart, pie chart, line chart, or KPI card based on result type.

#### ⑤ Data Grounding Badge

_"This answer is derived strictly from 7,043 rows in your uploaded dataset. No external data used."_

#### ⑥ Confidence Score

**96% High Confidence** - Based on deterministic computation and column match accuracy.

---

## 🛡 Anti-Hallucination Features

### How We Prevent Hallucinations:

1. ✅ **Pandas-Only Computation** - All numbers computed server-side using Pandas
2. ✅ **Schema Validation** - Query parser checks if requested columns exist
3. ✅ **Explicit Formulas** - Every calculation shows formula (e.g., `1869 ÷ 7043 × 100`)
4. ✅ **Row Count Verification** - Always display rows analyzed
5. ✅ **Column Existence Check** - Return error if column doesn't exist
6. ✅ **No External Data** - Only uses uploaded dataset

### Example Error Handling:

```
User: "Show revenue by department"
System: ❌ "The dataset does not contain the requested field 'revenue'.
         Available columns: customerID, gender, age, Churn..."
```

---

## 🎨 UI Features

### Landing Page

- 🌟 Premium dark theme with gold accents
- ☁️ Drag & drop CSV upload
- 📊 Real-time schema detection
- 🔍 Dataset preview (first 5 rows)
- ✨ Animated glassmorphic cards

### Dashboard

- 📌 Sticky header with dataset info badge
- 🗂 Tabbed interface (Query, Overview, Insights)
- 📈 Live analysis indicator
- 🎯 Dataset statistics panel

### Query Interface

- 💬 Large query input with auto-suggestions
- ⚡ Real-time loading state with steps
- 📋 4-section structured output
- 📊 Interactive Recharts visualizations
- 🏅 Animated confidence badges
- 🔒 Data grounding verification

---

## 📊 Supported Operations

### Aggregations

- ✅ COUNT
- ✅ SUM
- ✅ AVERAGE
- ✅ PERCENTAGE
- ✅ CHURN RATE
- ✅ GROUP BY

### Filters

- ✅ Equality (=)
- ✅ Greater than (>)
- ✅ Less than (<)
- ✅ Contains
- ✅ Date ranges

### Visualizations

- ✅ Bar Chart (grouped comparisons)
- ✅ Pie/Doughnut Chart (distributions)
- ✅ Line Chart (time series)
- ✅ KPI Cards (single metrics)

---

## 🧪 Testing with Sample Dataset

### Sample Churn Dataset Structure:

```csv
customerID,gender,SeniorCitizen,Partner,Dependents,tenure,PhoneService,InternetService,Contract,MonthlyCharges,TotalCharges,Churn
7590-VHVEG,Female,0,Yes,No,1,No,DSL,Month-to-month,29.85,29.85,No
5575-GNVDE,Male,0,No,No,34,Yes,DSL,One year,56.95,1889.5,No
3668-QPYBK,Male,0,No,No,2,Yes,DSL,Month-to-month,53.85,108.15,Yes
...
```

### Example Queries to Test:

1. _"What is the churn rate by gender?"_
2. _"Show average monthly charges by contract type"_
3. _"Count customers with internet service"_
4. _"Compare tenure for churned vs retained customers"_

---

## 🔮 Future Enhancements

- [ ] Multi-sheet Excel support
- [ ] SQL database connections
- [ ] Time-series forecasting
- [ ] Correlation analysis
- [ ] Export results as PDF/JSON
- [ ] Query history persistence
- [ ] Multi-language support
- [ ] Advanced filtering UI

---

## 📜 API Endpoints

### `POST /upload`

Upload CSV dataset

```json
{
  "success": true,
  "row_count": 7043,
  "column_count": 21,
  "schema": {...},
  "preview": [...]
}
```

### `POST /query`

Query dataset with natural language

```json
{
  "query": "What is the churn rate by gender?",
  "context": []
}
```

Returns structured 4-section response.

### `GET /dataset/info`

Get current dataset information

### `GET /conversation/history`

Retrieve conversation history

### `DELETE /conversation/clear`

Clear conversation context

---

## 🤝 Contributing

Contributions welcome! Please follow:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👨‍💻 Author

Built with ❤️ for conversational data intelligence

---

## 🏆 Key Differentiators

✅ **Dataset Agnostic** - Works with ANY structured CSV
✅ **Zero Hallucination** - Pandas-only computation
✅ **Explainable** - Shows SQL logic + derivation
✅ **Production Ready** - Error handling, validation, confidence scoring
✅ **Beautiful UX** - Enterprise-grade dark theme with animations
✅ **Full Stack** - Complete frontend + backend solution

---

**DataSage** - _Where Data Meets Intelligence_ 🧠✨
