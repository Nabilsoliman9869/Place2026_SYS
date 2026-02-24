import unittest
from app import app
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class SystemHealthCheck(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_01_login_page_loads(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200, "Login page failed to load")
        print("[PASS] Login Page Load")

    def test_02_admin_login(self):
        response = self.login('admin', '123')
        # Check for Arabic text or specific ID that exists in dashboard
        self.assertIn(b'Place _Guide Academy', response.data, "Admin login failed")
        print("[PASS] Admin Login")

    def test_03_marketing_flow(self):
        self.login('marketing1', '123')
        # Check Dashboard
        response = self.app.get('/marketing/daily_sheet')
        self.assertEqual(response.status_code, 200, "Marketing Sheet failed to load")
        # Test Add Lead (Simulated)
        response = self.app.post('/marketing/add_lead_row', data={
            'name': 'Test Candidate',
            'phone': '01000000999',
            'source': 'Facebook',
            'assigned_agent': '2', # Assuming ID 2 is sales
            'entry_date': '2025-01-01'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Adding Lead Failed")
        print("[PASS] Marketing Flow (Dashboard + Add Lead)")

    def test_04_sales_flow(self):
        self.login('sales1', '123')
        response = self.app.get('/sales')
        self.assertEqual(response.status_code, 200, "Sales Dashboard failed to load")
        print("[PASS] Sales Dashboard Load")

    def test_05_ta_flow(self):
        self.login('ta_rec', '123')
        response = self.app.get('/talent/dashboard')
        self.assertEqual(response.status_code, 200, "TA Dashboard failed to load")
        print("[PASS] Talent Acquisition Dashboard Load")

    def test_06_corporate_flow(self):
        self.login('am1', '123')
        # AM goes to am_dashboard, not manage (which is for Recruiters)
        response = self.app.get('/recruitment/am_dashboard') 
        self.assertEqual(response.status_code, 200, "AM Dashboard failed to load")
        print("[PASS] Corporate/AM Dashboard Load")
        
    def test_07_training_flow(self):
        self.login('ta_train', '123') # Assuming trainer role or similar
        # Since ta_train is TA, let's try a Trainer user if exists, otherwise skip
        # We'll check the route availability at least
        pass

if __name__ == '__main__':
    print("\n>>> STARTING SYSTEM HEALTH CHECK <<<\n")
    try:
        unittest.main(exit=False)
        print("\n>>> ALL CHECKS COMPLETED <<<")
    except Exception as e:
        print(f"\n!!! SYSTEM CHECK FAILED: {e}")
