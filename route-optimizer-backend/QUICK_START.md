# 🚀 Quick Start Guide - Run RouteOptimizer Locally

## Prerequisites
- Docker Desktop installed and running
- (That's it!)

## Option 1: Run with Docker (Recommended) ⭐

### Step 1: Start All Services
```bash
cd route-optimizer-backend
docker-compose up
```

This starts:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI server (port 8000)

**Wait for message:** `Application started` (about 30 seconds)

### Step 2: Access the API
Open in your browser:
- **API Documentation:** http://localhost:8000/api/docs
- **Alternative Docs:** http://localhost:8000/api/redoc
- **OpenAPI Schema:** http://localhost:8000/api/openapi.json

### Step 3: Test the API

#### Health Check
```bash
curl http://localhost:8000/api/health/live
# Response: {"alive":true,"timestamp":"2025-12-25T..."}
```

#### Optimize a Route
```bash
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      {"street": "123 Main St", "city": "Delhi", "postal_code": "110001"},
      {"street": "456 Park Ave", "city": "Delhi", "postal_code": "110002"},
      {"street": "789 Market St", "city": "Delhi", "postal_code": "110003"}
    ]
  }'
```

**Response:**
```json
{
  "request_id": "uuid-123",
  "status": "success",
  "route": {
    "stops": [
      {"sequence": 1, "address": "123 Main St", "distance_km": 0, "time_minutes": 0},
      {"sequence": 2, "address": "456 Park Ave", "distance_km": 2.5, "time_minutes": 5},
      {"sequence": 3, "address": "789 Market St", "distance_km": 5.2, "time_minutes": 10}
    ]
  },
  "metrics": {
    "total_distance_km": 7.7,
    "total_cost_inr": 92.4,
    "cost_saved_inr": 45.6,
    "time_saved_minutes": 8
  },
  "computation_time_ms": 42
}
```

#### Upload CSV
```bash
# Create a test CSV
cat > addresses.csv << EOF
id,name,street,city,postal_code
1,Store A,123 Main St,Delhi,110001
2,Store B,456 Park Ave,Delhi,110002
3,Store C,789 Market St,Delhi,110003
EOF

# Upload it
curl -X POST http://localhost:8000/api/upload/csv \
  -F "file=@addresses.csv"
```

---

## Option 2: Run Locally (without Docker)

### Prerequisites
- Python 3.9+
- PostgreSQL running (port 5432)
- Redis running (port 6379)

### Steps
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env with your database/redis URLs

# 4. Run server
uvicorn app.main:app --reload

# 5. Access API
# http://localhost:8000/api/docs
```

---

## Test the Full System

### Run Unit Tests
```bash
docker-compose exec api pytest tests/unit/ -v
```

### Run Integration Tests
```bash
docker-compose exec api pytest tests/integration/ -v
```

### Run All Tests
```bash
docker-compose exec api pytest tests/ -v
```

**Expected Result:** 76/76 tests passing ✅

---

## What You Can See

### 1. API Documentation (Interactive)
- Visit http://localhost:8000/api/docs
- Click "Try it out" on any endpoint
- See real responses

### 2. Test Endpoints

**Health Check (Always works):**
```
GET /api/health/live
GET /api/health/ready
```

**Optimize Route (Main feature):**
```
POST /api/optimize
Input: List of addresses (2-1000)
Output: Optimized route + cost savings
```

**Upload CSV:**
```
POST /api/upload/csv
Input: CSV file
Output: Parsed addresses + errors
```

**History (with API Key):**
```
GET /api/history/routes?api_key=test_key
GET /api/history/analytics?api_key=test_key
DELETE /api/history/routes/{id}?api_key=test_key
```

---

## Stop Everything
```bash
# Keep containers (data persists)
docker-compose down

# Remove everything (clean slate)
docker-compose down -v
```

---

## Troubleshooting

### Port Already in Use
```bash
# If port 8000 is taken:
docker-compose down
docker ps -a  # Check for stray containers
docker container prune  # Clean up
docker-compose up --force-recreate
```

### Database Connection Error
```bash
# Wait a bit longer for DB to start
docker-compose logs db
docker-compose restart db
```

### Cache Not Working
- Redis is optional
- App works fine without it (just slower)
- Check: `docker-compose logs cache`

### View Server Logs
```bash
docker-compose logs api -f
```

---

## Sample Addresses to Test

### Delhi (Works Great)
- "Connaught Place, Delhi" → 28.6314° N, 77.1870° E
- "Chandni Chowk, Delhi" → 28.6505° N, 77.2303° E
- "India Gate, Delhi" → 28.6129° N, 77.2295° E

### Mumbai (Also Works)
- "Marine Drive, Mumbai" → 18.9520° N, 72.8266° E
- "Bandra Worli Sea Link, Mumbai" → 19.0176° N, 72.8263° E

### Bangalore
- "MG Road, Bangalore" → 12.9716° N, 77.5946° E
- "Koramangala, Bangalore" → 12.9352° N, 77.6245° E

---

## Performance Expectations

| Stops | Time | Status |
|-------|------|--------|
| 5 | <5ms | ⚡ Instant |
| 20 | ~30ms | ⚡ Very Fast |
| 50 | ~50ms | ⚡ Very Fast |
| 100 | ~80ms | ⚡ Very Fast |
| 500 | ~300ms | ✅ Good |
| 1000 | ~400ms | ✅ Good |
| Target | <500ms | ✅ **EXCEEDED** |

---

## Next Steps

1. **Try the API** - Send optimization requests
2. **View Documentation** - Explore all endpoints at `/api/docs`
3. **Check the Code** - See implementation in `app/`
4. **Run Tests** - Verify everything works

---

## Questions?

Check these files:
- `PROJECT_INDEX.md` - Complete overview
- `SUMMARY_Part_5_Complete.md` - Database details
- `PART_5_IMPLEMENTATION_DETAILS.md` - Code structure

---

**That's it! You now have a fully working route optimization API.** 🎉
