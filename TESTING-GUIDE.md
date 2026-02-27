# Testing Guide - Dataset-Agnostic DataSage

## 🧪 Testing the Refactored System

### Test 1: Original Telco Dataset (Regression Test)

**Dataset:** Telco Customer Churn
**Columns:** customerID, gender, SeniorCitizen, Partner, tenure, MonthlyCharges, Churn

**Test Queries:**

1. "What is the churn rate by gender?"
   - ✅ Should detect "Churn" as binary column
   - ✅ Should group by "gender"
   - ✅ Should show bar chart

2. "Show average monthly charges by contract type"
   - ✅ Should calculate average of "MonthlyCharges"
   - ✅ Should group by "Contract"
   - ✅ Should show bar chart

3. "How many customers are there?"
   - ✅ Should return simple count
   - ✅ Should show KPI card

**Expected Result:** All queries work exactly as before

---

### Test 2: Sales Dataset

**Create Test CSV:** `sales_data.csv`

```csv
Date,Revenue,Cost,Region,Product,Status
2024-01-01,5000,3000,North,Widget,Completed
2024-01-02,3000,2000,South,Gadget,Completed
2024-01-03,7000,4000,East,Widget,Pending
2024-01-04,4500,2500,West,Gadget,Completed
2024-01-05,6000,3500,North,Gadget,Completed
```

**Upload and Check:**

1. ✅ Upload succeeds
2. ✅ Suggested questions appear:
   - "What is the average Revenue by Region?"
   - "Show Revenue trend over Date"
   - "What is the Status rate?"

**Test Queries:**

1. "What is the completion rate?"
   - ✅ Should detect "Status" as binary (Completed/Pending)
   - ✅ Should calculate rate
   - ✅ Formula: `count(Completed) / total * 100`

2. "Show average Revenue by Region"
   - ✅ Should calculate average Revenue
   - ✅ Should group by Region
   - ✅ Should show bar chart

3. "Compare Revenue across Products"
   - ✅ Should compare Widget vs Gadget
   - ✅ Should show comparison chart

**Expected Result:** All queries work without any code changes

---

### Test 3: Air Quality Dataset

**Create Test CSV:** `air_quality.csv`

```csv
Date,City,State,AQI,PM2.5,Temperature
2024-01-01,Delhi,Delhi,350,180,22
2024-01-02,Mumbai,Maharashtra,120,50,28
2024-01-03,Bangalore,Karnataka,80,30,25
2024-01-04,Chennai,Tamil Nadu,95,40,30
2024-01-05,Kolkata,West Bengal,200,100,27
```

**Upload and Check:**

1. ✅ Upload succeeds
2. ✅ Suggested questions appear:
   - "What is the average AQI by City?"
   - "Show AQI trend over Date"
   - "What is the distribution of State?"

**Test Queries:**

1. "Which city has the highest AQI?"
   - ✅ Should find Delhi
   - ✅ Should sort by AQI descending

2. "Show average PM2.5 by State"
   - ✅ Should calculate average PM2.5
   - ✅ Should group by State

3. "What is the AQI trend over time?"
   - ✅ Should detect Date column
   - ✅ Should show line chart

**Expected Result:** System adapts to air quality domain

---

### Test 4: E-commerce Conversion Dataset

**Create Test CSV:** `ecommerce.csv`

```csv
Customer,Product,Price,Converted,Channel,SignupDate
John,Laptop,1200,Yes,Email,2024-01-01
Jane,Phone,800,No,Social,2024-01-02
Mike,Tablet,600,Yes,Search,2024-01-03
Sarah,Laptop,1200,Yes,Email,2024-01-04
Tom,Phone,800,No,Social,2024-01-05
```

**Upload and Check:**

1. ✅ Upload succeeds
2. ✅ Suggested questions appear:
   - "What is the average Price by Product?"
   - "What is the Converted rate?"
   - "Show Price trend over SignupDate"

**Test Queries:**

1. "What is the conversion rate by Channel?"
   - ✅ Should detect "Converted" as binary (Yes/No)
   - ✅ Should group by "Channel"
   - ✅ Should calculate rate for each channel

2. "Compare Price across Products"
   - ✅ Should show average/total price by Product
   - ✅ Should show bar chart

3. "How many customers converted?"
   - ✅ Should count where Converted='Yes'
   - ✅ Should show KPI card

**Expected Result:** System handles conversion analytics

---

### Test 5: Banking Loan Dataset

**Create Test CSV:** `loans.csv`

```csv
LoanID,CustomerAge,Income,LoanAmount,CreditScore,Approved,AppliedDate
L001,35,75000,200000,720,Yes,2024-01-01
L002,42,120000,350000,780,Yes,2024-01-02
L003,28,45000,150000,620,No,2024-01-03
L004,55,200000,500000,800,Yes,2024-01-04
L005,31,60000,180000,650,No,2024-01-05
```

**Upload and Check:**

1. ✅ Upload succeeds
2. ✅ Suggested questions appear:
   - "What is the average LoanAmount by CreditScore?"
   - "What is the Approved rate?"
   - "Show Income trend over AppliedDate"

**Test Queries:**

1. "What is the approval rate?"
   - ✅ Should detect "Approved" as binary (Yes/No)
   - ✅ Should calculate approval rate

2. "Show average loan amount by approval status"
   - ✅ Should calculate average LoanAmount
   - ✅ Should group by "Approved"

3. "Compare income across age groups"
   - ✅ Should handle numeric grouping
   - ✅ Should show comparison

**Expected Result:** System handles financial data

---

## 🔴 Error Handling Tests

### Test 6: Missing Column Error

**Dataset:** sales_data.csv (from Test 2)

**Query:** "What is the churn rate?"

**Expected Response:**

```
❌ Error: Column 'churn' not found in dataset.
Available columns: Date, Revenue, Cost, Region, Product, Status
```

---

### Test 7: Invalid Operation Error

**Dataset:** sales_data.csv (from Test 2)

**Query:** "What is the average of Region?" (Region is categorical)

**Expected Response:**

```
❌ Error: No numeric columns found for average calculation
```

---

### Test 8: Empty Dataset Error

**Upload:** Empty CSV file

**Expected Response:**

```
❌ Error: Failed to parse CSV: Empty dataset
```

---

## 📋 Test Checklist

### Upload Tests

- [x] Telco dataset uploads successfully
- [x] Sales dataset uploads successfully
- [x] Air quality dataset uploads successfully
- [x] E-commerce dataset uploads successfully
- [x] Banking dataset uploads successfully
- [x] Empty file is rejected
- [x] Non-CSV file is rejected

### Schema Detection Tests

- [x] Numeric columns detected correctly
- [x] Categorical columns detected correctly
- [x] Date columns detected correctly
- [x] Boolean/binary columns detected correctly
- [x] Suggested questions generated correctly

### Query Tests

- [x] Count operations work
- [x] Average operations work
- [x] Sum operations work
- [x] Rate/percentage calculations work
- [x] Grouping operations work
- [x] Comparison queries work
- [x] Trend/time series queries work

### Visualization Tests

- [x] Bar charts generated correctly
- [x] Pie charts generated correctly
- [x] Doughnut charts generated correctly
- [x] KPI cards generated correctly
- [x] Line charts generated correctly (if date column exists)

### Error Handling Tests

- [x] Missing column error shown clearly
- [x] Invalid operation error shown clearly
- [x] Empty dataset rejected
- [x] Parse errors handled gracefully

---

## 🚀 Quick Testing Commands

### Start Backend

```bash
cd backend
python main.py
# Server runs on http://localhost:8000
```

### Test Upload

```bash
# Using curl (Windows PowerShell)
curl -X POST "http://localhost:8000/upload" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@sales_data.csv"
```

### Test Query

```bash
curl -X POST "http://localhost:8000/query" `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What is the completion rate by region?\", \"context\": []}'
```

---

## ✅ Success Criteria

A successful test means:

1. ✅ Upload works for ALL datasets
2. ✅ Schema detected correctly for each dataset
3. ✅ Suggested questions make sense for the dataset
4. ✅ Queries work without hardcoded column assumptions
5. ✅ Rate calculations work for ANY binary column
6. ✅ Visualizations are appropriate for result type
7. ✅ All numbers come from Pandas calculations
8. ✅ Clear error messages when operations fail
9. ✅ No crashes or unhandled exceptions

---

## 📊 Expected Performance

- Upload time: < 2 seconds for 10k rows
- Query response: < 1 second for most queries
- Schema detection: < 500ms
- Suggested questions: Instant (generated during schema analysis)

---

## 🐛 Known Limitations

1. **Date Parsing**: May not detect all date formats
   - Workaround: Ensure dates are in standard formats (YYYY-MM-DD)

2. **Large Files**: Files > 50MB may be slow
   - Recommendation: Sample data or use chunking

3. **Complex Queries**: Multi-step aggregations not yet supported
   - Example: "Show average of maximum by group" requires multiple passes

4. **Natural Language**: Very complex phrasings may not parse correctly
   - Recommendation: Use clear, direct questions

---

## 🎯 Testing Summary

This guide ensures DataSage works with:

- ✅ ANY structured CSV dataset
- ✅ ANY column names
- ✅ ANY business domain
- ✅ ANY combination of numeric/categorical/date columns

**No code changes required between datasets!** 🎉
