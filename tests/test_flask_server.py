import unittest
from world import *
from ai import AI
import json
from car import Car
from lane import Lane
from route import Route
from simulation import Simulation
from speedchange import SpeedChange
from trafficlight import Trafficlight
from trafficlightcontroller import TrafficlightController


class MyTestCase(unittest.TestCase):
    def test_something(self):
        world = World()
        ai = AI(world)
        # Add routes, cars, traffic lights, and sensors to `world`
        world_dict = world.to_dict()

        # Test JSON serialization
        json_data = json.dumps(world_dict, indent=4)
        print(json_data)
        ai_dict = ai.to_dict()

        # Test JSON serialization
        json_data = json.dumps(ai_dict, indent=4)
        print(json_data)
        car = Car()
        car_dict = car.to_dict()

        # Test JSON serialization
        json_data = json.dumps(car_dict, indent=4)
        print(json_data)
        lane = Lane(1,2,3,4,5,6,7,8,9,0,9)
        lane_dict = lane.to_dict()

        # Test JSON serialization
        json_data = json.dumps(lane_dict, indent=4)
        print(json_data)
        route = Route([lane])
        route_dict = route.to_dict()

        # Test JSON serialization
        json_data = json.dumps(route_dict, indent=4)
        print(json_data)
        simulation = Simulation()
        simulation_dict = simulation.to_dict()

        # Test JSON serialization
        json_data = json.dumps(simulation_dict, indent=4)
        print(json_data)
        speedChange = SpeedChange(1)
        speedChange_dict = speedChange.to_dict()

        # Test JSON serialization
        json_data = json.dumps(speedChange_dict, indent=4)
        print(json_data)
        trafficlight = Trafficlight(1,1)
        trafficlight_dict = trafficlight.to_dict()

        # Test JSON serialization
        json_data = json.dumps(trafficlight_dict, indent=4)
        print(json_data)
        trafficlightController = TrafficlightController([trafficlight], [[1]])
        trafficlightController_dict = trafficlightController.to_dict()

        # Test JSON serialization
        json_data = json.dumps(trafficlightController_dict, indent=4)
        print(json_data)



if __name__ == '__main__':
    unittest.main()
