import unittest
from app import app

class TestSimulationAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_simulation(self):
        response = self.client.get('/api/simulation')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('ai', data)
        self.assertIn('world', data)

if __name__ == '__main__':
    unittest.main()
