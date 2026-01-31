import httpx
import os
import sys

# Ensure server is running (or we could use TestClient, but integration test is better here)
# For this script we will use TestClient for simplicity as before
from fastapi.testclient import TestClient
from src.api.main import app

def verify_ingestion():
    client = TestClient(app)
    
    raw_file = "raw_results.csv"
    if not os.path.exists(raw_file):
        print("Error: raw_results.csv not found for testing.")
        return

    print(f"--- Testing Ingestion Pipeline ---")
    
    # 1. Upload
    print(f"1. Uploading {raw_file}...")
    with open(raw_file, "rb") as f:
        files = {"file": ("test_upload.csv", f, "text/csv")}
        response = client.post("/api/v1/datasets/upload", files=files)
        
    if response.status_code != 200:
        print(f"FAILED: {response.status_code} {response.text}")
        return
        
    data = response.json()
    dataset_id = data["dataset_id"]
    print(f"SUCCESS. Dataset ID: {dataset_id}")
    
    # 2. Process
    print(f"2. Processing dataset {dataset_id}...")
    response = client.post(f"/api/v1/datasets/{dataset_id}/process")
    
    if response.status_code != 200:
        print(f"FAILED: {response.status_code} {response.text}")
        return
        
    data = response.json()
    print(f"SUCCESS. Message: {data['message']}")
    print(f"Records loaded: {data['records']}")

    # 3. Verify Data is Active
    print(f"3. Verifying Health Check...")
    response = client.get("/")
    print(f"Health Status: {response.json()}")
    
    if response.json()["records_loaded"] > 0:
        print("VERIFICATION COMPLETE: Ingestion pipeline working.")
    else:
        print("VERIFICATION FAILED: Data not loaded active.")

if __name__ == "__main__":
    verify_ingestion()
