import requests

def test_nominatim(country):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "county": "Nioro",
        "state": "Kayes",
        "country": country,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "test-agent"}
    r = requests.get(url, params=params, headers=headers)
    print(f"Testing with country='{country}':")
    print(r.status_code)
    print(r.json())

test_nominatim("MLI")
test_nominatim("Mali")
test_nominatim("ML")
