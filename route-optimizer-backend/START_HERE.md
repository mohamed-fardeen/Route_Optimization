# 🚀 START HERE - How to Run RouteOptimizer

## In 3 Steps:

### Step 1: Open Terminal
```bash
cd "d:\User\Documents\Route optimization - Copy\route-optimizer-backend"
```

### Step 2: Start Everything with Docker
```bash
docker-compose up
```

Wait for message: **"Application started"** (takes ~30 seconds)

### Step 3: Open Your Browser
Go to: **http://localhost:8000/api/docs**

You'll see interactive API documentation. Click "Try it out" on any endpoint to test!

---

## Quick Test (Optional)

After server starts, in a NEW terminal:
```bash
cd "d:\User\Documents\Route optimization - Copy\route-optimizer-backend"
python test_api.py
```

This will:
- ✓ Test health checks
- ✓ Test route optimization
- ✓ Test CSV upload
- ✓ Show you real results

---

## What You Can Do Now

### 1. Optimize a Route (Main Feature)
Send addresses → Get optimized route with cost savings

### 2. Upload Addresses
Upload CSV file → Get all addresses parsed

### 3. View History
Check past optimizations (with API key)

### 4. See Analytics
Dashboard stats on costs saved, distances, monthly stats

---

## Example: Optimize a Route

Open http://localhost:8000/api/docs

Click on **POST /api/optimize** → Click "Try it out"

Paste this:
```json
{
  "addresses": [
    {"street": "123 Main St", "city": "Delhi", "postal_code": "110001"},
    {"street": "456 Park Ave", "city": "Delhi", "postal_code": "110002"},
    {"street": "789 Market St", "city": "Delhi", "postal_code": "110003"}
  ]
}
```

Click "Execute" → See optimized route + cost savings!

---

## Expected Results

**For 3 addresses:** 
- Takes ~20ms (very fast ⚡)
- Shows: distance km, cost in ₹, time saved, sequence

**For 100 addresses:**
- Takes ~80ms (still very fast ⚡)
- Shows optimized stops for delivery

---

## Stop the Server

Press `CTRL+C` in the terminal

---

## Need Help?

- 📖 **Full docs:** Read `QUICK_START.md`
- 🔍 **See code:** Open `app/` folder
- 📊 **Architecture:** Read `PROJECT_INDEX.md`

---

**That's it! You now have a fully working route optimization system running locally.**

Go to http://localhost:8000/api/docs and start testing! 🎉
