import requests
import json

def test_api():
    url = "https://remotive.com/api/remote-jobs?category=software-dev&limit=5"
    response = requests.get(url)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        jobs = response.json().get('jobs', [])
        print(f"Found {len(jobs)} jobs")
        if jobs:
            print(f"First job: {jobs[0]['title']} at {jobs[0]['company_name']}")

if __name__ == "__main__":
    test_api()
