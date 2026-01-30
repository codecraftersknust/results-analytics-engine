from fastapi.testclient import TestClient
from src.api.main import app
import sys

# Need to ensure startup event runs or manually load data for TestClient
# TestClient runs startup events by default in recent versions

def verify_api():
    print("Initializing Test Client...")
    
    # We use the context manager to ensure startup/shutdown events run
    with TestClient(app) as client:
        
        # 1. Health Check
        print("\n--- Testing Health Check ---")
        response = client.get("/")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
        if response.status_code != 200:
            print("FAILED")
            return

        # 2. Student Summary
        print("\n--- Testing Student Summary (ID: 110001) ---")
        response = client.get("/api/v1/students/110001/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"Overall Average: {data['overall_average']}")
            print(f"Insight Count: {len(data['insights'])}")
            if len(data['insights']) > 0:
                print(f"Sample Insight: {data['insights'][0]}")
        else:
            print(f"Failed: {response.status_code} {response.text}")

        # 3. Cohort Trends
        print("\n--- Testing Cohort Trends ---")
        response = client.get("/api/v1/cohort/trends")
        if response.status_code == 200:
            data = response.json()
            print(f"Trend Data Points: {len(data['trends'])}")
        else:
            print(f"Failed: {response.status_code} {response.text}")

        # 4. Correlations
        print("\n--- Testing Correlations ---")
        response = client.get("/api/v1/cohort/correlations")
        if response.status_code == 200:
            data = response.json()
            print(f"Heatmap Data Points: {len(data['heatmap_data'])}")
            print(f"Insight Count: {len(data['insights'])}")
        else:
            print(f"Failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    verify_api()
