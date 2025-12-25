from fastapi.testclient import TestClient
from app.main import app
from io import BytesIO

client = TestClient(app)

def test_csv_upload_valid():
    """Test valid CSV upload"""
    csv_content = b"""id,name,street,city,postal_code
1,Office,123 Main St,Delhi,110001
2,Stop1,456 Second St,Delhi,110002
3,Stop2,789 Third St,Delhi,110003
"""
    files = {"file": ("addresses.csv", BytesIO(csv_content), "text/csv")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["parsed_successfully"] == 3
    assert len(data["addresses"]) == 3

def test_csv_upload_with_coordinates():
    """Test CSV with coordinates"""
    csv_content = b"""id,name,street,city,latitude,longitude
1,Office,123 Main,Delhi,28.6139,77.2090
2,Stop1,456 Second,Delhi,28.6145,77.2100
"""
    files = {"file": ("addresses.csv", BytesIO(csv_content), "text/csv")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["parsed_successfully"] == 2

def test_csv_upload_missing_columns():
    """Test CSV with missing required columns"""
    csv_content = b"""id,name,street
1,Office,123 Main
2,Stop1,456 Second
"""
    files = {"file": ("addresses.csv", BytesIO(csv_content), "text/csv")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 400
    assert "Missing columns" in response.json()["detail"]

def test_csv_upload_non_csv_file():
    """Test upload with non-CSV file"""
    content = b"not a csv file"
    files = {"file": ("addresses.txt", BytesIO(content), "text/plain")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 400
    assert "Only CSV files" in response.json()["detail"]

def test_csv_upload_parse_errors():
    """Test CSV with some parsing errors"""
    csv_content = b"""id,name,street,city
invalid,Office,123 Main,Delhi
2,Stop1,456 Second,Delhi
"""
    files = {"file": ("addresses.csv", BytesIO(csv_content), "text/csv")}
    response = client.post("/api/upload/csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["failed"] == 1
    assert len(data["errors"]) > 0
