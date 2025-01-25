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

    def test_move_timestep(self):
        response = self.client.get('/api/simulation')
        initial_state = response.get_json()
        self.client.post('/api/simulation/update')
        response = self.client.get('/api/simulation')
        updated_state = response.get_json()
        self.assertNotEqual(initial_state, updated_state)

if __name__ == '__main__':
    unittest.main()
