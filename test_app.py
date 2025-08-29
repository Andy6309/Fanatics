import unittest
from fastapi.testclient import TestClient
from app.main import app
import json

class TestMachineAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.machine_data = {
            "name": "Test Machine",
            "location": "Test Location"
        }
        
        # Register a test machine
        response = self.client.post("/api/machines", json=self.machine_data)
        self.machine = response.json()
        
    def test_register_machine(self):
        response = self.client.post("/api/machines", json={
            "name": "New Machine",
            "location": "New Location"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "New Machine")
        self.assertEqual(data["location"], "New Location")
    
    def test_log_status(self):
        status_data = {
            "status": "running"
        }
        response = self.client.post(
            f"/api/machines/{self.machine['id']}/status",
            json=status_data
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "running")
        self.assertIn("timestamp", data)
    
    def test_list_machines(self):
        response = self.client.get("/api/machines")
        self.assertEqual(response.status_code, 200)
        machines = response.json()
        self.assertIsInstance(machines, list)
        self.assertGreater(len(machines), 0)
    
    def test_get_machine_details(self):
        # First log a status to have some history
        self.client.post(
            f"/api/machines/{self.machine['id']}/status",
            json={"status": "running"}
        )
        
        response = self.client.get(f"/api/machines/{self.machine['id']}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.machine["id"])
        self.assertIn("current_status", data)
        self.assertIn("status_history", data)
        self.assertEqual(len(data["status_history"]), 1)

if __name__ == "__main__":
    unittest.main()
