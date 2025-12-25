# RouteOptimizer Backend

AI-powered route optimization for Indian delivery businesses.

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+

### Setup

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd route-optimizer-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run development server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/api/docs`

## Project Structure

```
app/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── routers/             # API endpoints
├── services/            # Business logic
├── models/              # Pydantic models
├── database/            # Database layer
└── utils/               # Utilities and helpers
tests/                   # Test suites
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health/live` - Liveness check
- `GET /api/health/ready` - Readiness check
- `POST /api/optimize/routes` - Optimize delivery routes
- `POST /api/upload/addresses` - Upload addresses

## Docker

```bash
docker build -t route-optimizer .
docker-compose up
```

## Development

- **Code Format**: Black
- **Linting**: Flake8
- **Testing**: Pytest
- **Async**: asyncio with FastAPI

```bash
black .
flake8 .
pytest
```
