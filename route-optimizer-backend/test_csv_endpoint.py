from fastapi.testclient import TestClient
from app.main import app
from io import BytesIO

client = TestClient(app)

csv_content = b"""id,name,street,city
1,Office,123 Main,Delhi
2,Stop1,456 Second,Delhi
"""

files = {"file": ("addresses.csv", BytesIO(csv_content), "text/csv")}
r = client.post("/api/upload/csv", files=files)
print(f"Status: {r.status_code}")
print(f"Parsed: {r.json()['parsed_successfully']}/{r.json()['total_rows']}")
print(f"Response: {r.json()}")
