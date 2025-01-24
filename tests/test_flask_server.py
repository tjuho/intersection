import unittest
from world import *
import json

class MyTestCase(unittest.TestCase):
    def test_something(self):
        world = World()
        # Add routes, cars, traffic lights, and sensors to `world`
        world_dict = world.to_dict()

        # Test JSON serialization
        json_data = json.dumps(world_dict, indent=4)
        print(json_data)


if __name__ == '__main__':
    unittest.main()
