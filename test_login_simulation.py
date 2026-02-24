import requests
import time
import threading
import sys
import os

# Ensure the app is running first!
# This script simulates a login request

URL = "http://127.0.0.1:5000/login"

def test_login(username, password):
    print(f"Testing login for {username}...")
    try:
        # Create a session to handle cookies
        s = requests.Session()
        
        # Get the login page first (to get any potential CSRF token if used, though not in this app)
        r = s.get(URL)
        if r.status_code != 200:
            print(f"FAILED to reach login page. Status: {r.status_code}")
            return False
            
        # Post login data
        payload = {'username': username, 'password': password}
        r = s.post(URL, data=payload, allow_redirects=True)
        
        # Check if we were redirected to dashboard
        if "/dashboard" in r.url:
            print(f"SUCCESS: {username} logged in! Redirected to {r.url}")
            return True
        elif "/corporate/dashboard" in r.url:
            print(f"SUCCESS: {username} logged in! Redirected to {r.url}")
            return True
        elif "/training" in r.url:
            print(f"SUCCESS: {username} logged in! Redirected to {r.url}")
            return True
        elif "/sales" in r.url:
            print(f"SUCCESS: {username} logged in! Redirected to {r.url}")
            return True
        else:
            print(f"FAILURE: {username} could not login. Current URL: {r.url}")
            if "Invalid username" in r.text:
                print("Reason: Invalid username or Database not initialized")
            elif "Invalid password" in r.text:
                print("Reason: Invalid password")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("--- Login Simulation ---")
    users = [
        ('manager', '123'),
        ('sales', '123'),
        ('corp', '123'),
        ('trainer', '123'),
        ('dev', '123'),
        ('wronguser', '123'),
        ('manager', 'wrongpass')
    ]
    
    for u, p in users:
        test_login(u, p)
        print("-" * 20)
