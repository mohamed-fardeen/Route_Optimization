#!/usr/bin/env python3
"""
Run RouteOptimizer without Docker (local development)
This starts the server with a local database (SQLite as fallback)
"""

import os
import sys
import subprocess
from pathlib import Path

# Add app to path
app_path = Path(__file__).parent
sys.path.insert(0, str(app_path))

def main():
    print("=" * 60)
    print("RouteOptimizer - Local Development Server")
    print("=" * 60)
    
    # Create .env if it doesn't exist
    env_file = app_path / ".env"
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        env_file.write_text("""# Local Development
APP_NAME=RouteOptimizer
DEBUG=True
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Database (optional - uses in-memory if not available)
DATABASE_URL=sqlite:///./route_optimizer.db
REDIS_URL=redis://localhost:6379/0

# External APIs
GOOGLE_MAPS_API_KEY=

# Optimization
ALGORITHM_TIMEOUT=30
MAX_ADDRESSES=1000
""")
        print("✓ Created .env file")
    
    print("\n🚀 Starting RouteOptimizer API...")
    print("   Access at: http://localhost:8000")
    print("   Docs at: http://localhost:8000/api/docs")
    print("   Press CTRL+C to stop\n")
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
