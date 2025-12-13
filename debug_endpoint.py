import urllib.request
import urllib.error

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()
URL = "http://localhost:8000/teams/my-invitations"

req = urllib.request.Request(URL)
req.add_header("Authorization", f"Bearer {TOKEN}")
req.add_header("Accept", "application/json")

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
