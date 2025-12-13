import urllib.request
import urllib.error
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
USER_EMAIL = "scanner_test@example.com"
USER_PASS = "password123"

def make_request(url, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = None
    if data:
        encoded_data = json.dumps(data).encode('utf-8')
        
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 204: # No content
                return json.loads(response.read().decode('utf-8'))
            return {}
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def login(email, password):
    print(f"Logging in as {email}...")
    result = make_request(f"{BASE_URL}/login", method="POST", data={"email": email, "contrasena": password})
    if result and "access_token" in result:
        return result["access_token"]
    print("Login failed.")
    return None

def test_team_events(token):
    print("\nTesting GET /teams/events...")
    events = make_request(f"{BASE_URL}/teams/events", method="GET", token=token)
    
    if events is not None:
        print(f"Success! Found {len(events)} events.")
        for e in events:
            print(f"- Event: {e.get('nombre')} (ID: {e.get('id')})")
        return events
    else:
        print("Failed to get events.")
        return []

def test_scan_ticket(token, ticket_code):
    print(f"\nTesting SCAN ticket {ticket_code}...")
    result = make_request(f"{BASE_URL}/tickets/scan/{ticket_code}", method="POST", token=token)
    
    if result:
        print(f"Scan Result: {result}")
        if result.get('status') == 'error' and 'NO AUTORIZADO' in result.get('message', ''):
             print("FAILED: User is not authorized to scan this ticket.")
        elif result.get('status') == 'success':
             print("SUCCESS: Ticket scanned and valid.")
        else:
             print(f"Result: {result.get('message')}")
    else:
        print("Request failed.")

def main():
    # 1. Login as Admin to set up Team
    print("--- STEP 1: Admin Setup ---")
    admin_token = login("admin@njoy.com", "admin123")
    if not admin_token:
        return

    # Create Team
    print("Creating Team...")
    import random
    team_name = f"Test Team {random.randint(1000, 9999)}"
    team_res = make_request(f"{BASE_URL}/teams/", method="POST", data={"name": team_name}, token=admin_token)
    if not team_res or "id" not in team_res:
        print("Failed to create team (maybe name taken).")
        # Try to continue if we can't create (maybe already exists?)
    else:
        team_id = team_res["id"]
        print(f"Team '{team_name}' created (ID: {team_id})")

        # Invite Juan
        print(f"Inviting Juan to Team {team_id}...")
        invite_res = make_request(f"{BASE_URL}/teams/{team_id}/invite", method="POST", data={"email": "juan@example.com"}, token=admin_token)
        print(f"Invite Response: {invite_res}")

    # 2. Login as Juan (The Scanner)
    print("\n--- STEP 2: Juan (Member) Actions ---")
    juan_token = login("juan@example.com", "password123")
    if not juan_token:
        return

    # Check Invitations
    print("Checking invitations...")
    invites = make_request(f"{BASE_URL}/teams/my-invitations", method="GET", token=juan_token)
    if invites:
        for inv in invites:
            print(f"Found invite for team {inv['team_id']}: {inv['status']}")
            if inv['status'] == 'pending':
                print("Accepting invitation...")
                # Note: params not supported in my simple make_request for POST, need to fix or use query string
                # Fixing make_request call for query param:
                url = f"{BASE_URL}/teams/invitations/{inv['id']}/respond?status_update=accepted"
                resp = make_request(url, method="POST", token=juan_token)
                print(f"Respond result: {resp}")

    # 3. Get Team Events
    print("\nGetting Team Events...")
    events = test_team_events(juan_token)
    
    # 4. Simulate Scan
    # We need a valid ticket code. Admin likely has created some events.
    # In seed data, Admin created "Primavera Sound 2025" etc.
    # We can try to purchase a ticket as Juan or just use a dummy if we accept 404 but "Authorized"
    print("\nSimulating Scan...")
    test_scan_ticket(juan_token, "RANDOM-CODE-TEST")


if __name__ == "__main__":
    main()
