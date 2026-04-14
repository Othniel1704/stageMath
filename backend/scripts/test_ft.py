import requests

def test_ft_api():
    token = "06714d7966bed3bd45ed93d7a1d06080ed413f35c21956862fe2292944b324e6"
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search?motsCles=developpeur"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    print("Testing France Travail API...")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_ft_api()
