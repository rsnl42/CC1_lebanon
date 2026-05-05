import requests
import json
import os

def load_env(filepath):
    """Simple manual .env loader since python-dotenv isn't installed."""
    env_vars = {}
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return None
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    return env_vars

def fetch_acled_lebanon():
    # 1. Load Credentials
    env = load_env('April 28/.env')
    if not env: return

    email = env.get('ACLED_EMAIL')
    password = env.get('ACLED_PASSWORD')

    if email == 'your_email@example.com':
        print("Error: Please update April 28/.env with your actual myACLED credentials.")
        return

    print(f"🔑 Authenticating with ACLED as {email}...")

    # 2. Get OAuth Token
    auth_url = "https://acleddata.com/oauth/token"
    auth_payload = {
        "grant_type": "password",
        "client_id": "acled",
        "username": email,
        "password": password
    }

    try:
        auth_res = requests.post(auth_url, data=auth_payload)
        auth_res.raise_for_status()
        token = auth_res.json().get('access_token')
        print("✅ Authentication successful. Token received.")
    except Exception as e:
        print(f"❌ Auth Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return

    # 3. Fetch Sample Data (Lebanon)
    # Filter: country=Lebanon, limit=5
    data_url = "https://acleddata.com/api/acled/read"
    params = {
        "country": "Lebanon",
        "limit": 5,
        "_format": "json"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    print("\n🛰️ Fetching sample events for Lebanon...")
    try:
        data_res = requests.get(data_url, params=params, headers=headers)
        data_res.raise_for_status()
        dataset = data_res.json()
        
        # ACLED response usually has a 'data' key
        events = dataset.get('data', [])
        
        # 4. Save to file
        output_file = 'April 28/lebanon_conflict_sample.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
            
        print(f"✅ Success! Fetched {len(events)} events.")
        print(f"💾 Saved to {output_file}")

        # Quick Preview
        if events:
            print("\n--- SAMPLE EVENT ---")
            sample = events[0]
            print(f"Date:     {sample.get('event_date')}")
            print(f"Type:     {sample.get('event_type')}")
            print(f"Location: {sample.get('location')}, {sample.get('admin1')}")
            print(f"Actors:   {sample.get('actor1')} vs {sample.get('actor2')}")
            print(f"Notes:    {sample.get('notes')[:100]}...")

    except Exception as e:
        print(f"❌ Data Fetch Failed: {e}")

if __name__ == "__main__":
    fetch_acled_lebanon()
