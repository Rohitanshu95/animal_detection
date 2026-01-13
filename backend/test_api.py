import requests

# Test the backend API
base_url = "http://localhost:8000"

def test_health():
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health check: {response.status_code}")
        print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_incidents():
    try:
        response = requests.get(f"{base_url}/incidents?limit=5")
        print(f"Incidents endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Number of incidents returned: {len(data)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Incidents test failed: {e}")
        return False

def test_filters():
    try:
        response = requests.get(f"{base_url}/incidents/filters")
        print(f"Filters endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Filter keys: {list(data.keys())}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Filters test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend API...")
    health_ok = test_health()
    incidents_ok = test_incidents()
    filters_ok = test_filters()

    if health_ok and incidents_ok and filters_ok:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
