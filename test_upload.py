import requests

url = "http://localhost:8000/upload"
files = {'file': open('test_air_quality.csv', 'rb')}

try:
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
