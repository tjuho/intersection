import unittest
from lane import Lane, StraightLane, CurvedLane
from car import Car
from route import Route
from trafficlight import Trafficlight
from world import World

class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.initialSpeed = 60 / 3.6
        cls.lane = StraightLane(0, 0, 0, 1000, 3, cls.initialSpeed)
        cls.trafficlight = Trafficlight(Trafficlight.calculateMaxYellowTime(cls.initialSpeed), 2, 'green', 200)
        cls.lane.addTrafficlight(cls.trafficlight)
        cls.car = Car(cls.initialSpeed)
        cls.route = Route([cls.lane])
        cls.world = World()
        cls.world.addRoute(cls.route)
        cls.route.addCar(cls.car)

    def test_move_timestep(self):
        speedlimit = 60/3.6
        world = World()
        l0 = StraightLane(0, 0, 0, 150, 3, speedlimit)
        l1 = StraightLane.continueLane(l0, 100)
        l2 = StraightLane.continueLane(l1, 100)
        tl1 = Trafficlight(2,2.5,'red',50)
        tl2 = Trafficlight(2,2.5,'red',50)
        route = Route([l0,l1,l2])
        world.addRoute(route)
        car = Car(speedlimit)
        world.addCar(car, route)
        world.addTrafficlight(tl1, l1,50)
        world.addTrafficlight(tl2, l2,50)
        self.assertEqual(3, len(route.lanes))
        self.assertTrue(route in world.routes.keys())
        tl, d = world.getNextNonGreenTrafficlightAndDistance(car)
        self.assertEqual(tl1, tl)
        self.assertEqual(200, d)
        tl1.color = 'green'
        car.distance = 100
        tl, d = world.getNextNonGreenTrafficlightAndDistance(car)
        self.assertEqual(tl2, tl)
        self.assertEqual(200, d)
        world.moveTimestep(1)
        pass

    def test_getNextNonGreenTrafficLightAndDistance(self):
        speedlimit = 60/3.6
        world = World()
        l0 = StraightLane(0, 0, 0, 50, 3, speedlimit)
        l1 = StraightLane.continueLane(l0, 100)
        l2 = StraightLane.continueLane(l1, 150)
        tl1 = Trafficlight(2,2.5,'red',50)
        tl2 = Trafficlight(2,2.5,'red',50)
        route = Route([l0,l1,l2])
        world.addRoute(route)
        car = Car(speedlimit)
        world.addCar(car, route)
        world.addTrafficlight(tl1, l1,50)
        world.addTrafficlight(tl2, l2,50)
        self.assertEqual(3, len(route.lanes))
        self.assertTrue(route in world.routes)
        tl, d = world.getNextNonGreenTrafficlightAndDistance(car)
        self.assertEqual(tl1, tl)
        self.assertEqual(100, d)
        tl1.color = 'green'
        tl, d = world.getNextNonGreenTrafficlightAndDistance(car)
        self.assertEqual(tl2, tl)
        self.assertEqual(200, d)

    def test_addandremovecar(self):
        limit = 60/3.6
        world = World()
        lane = StraightLane(100,0,0,100,3,limit)
        route = Route([lane])
        world.addRoute(route)
        car = Car(limit)
        world.addCar(car, route)
        self.assertEqual(1, len(world.getCarsLocationsAndDirections()))
        world.removeCar(car)
        self.assertEqual(0, len(world.getCarsLocationsAndDirections()))

    def test_getNextCarAheadAndDistance(self):
        limit = 1
        world = World()
        lane = StraightLane(100,0,0,100,3,limit)
        route = Route([lane])
        world.addRoute(route)
        car = Car(limit)
        world.addCar(car, route)
        world.moveTimestep(10)
        car1 = Car(limit)
        world.addCar(car1, route)
        self.assertEqual(2, len(world.getCarsLocationsAndDirections()))
        ahead, dist  = world.getNextCarAheadAndDistance(car1)
        self.assertEqual(car, ahead)
        self.assertEqual(10, dist)

    def test_routedistancefromlanedistance(self):
        limit = 60/3.6
        world = World()
        lane1 = StraightLane(100,0,0,100,3,limit)
        lane2 = StraightLane.continueLane(lane1, 100)
        route = Route([lane1, lane2])
        world.addRoute(route)
        self.assertEqual(150, world.calculateRouteDistanceFromLaneDistance(route, lane2, 50))


    def test_addtrafficlight(self):
        limit = 60/3.6
        world = World()
        lane1 = StraightLane(100,0,0,100,3,limit)
        lane2 = StraightLane.continueLane(lane1, 100)
        route = Route([lane1, lane2])
        world.addRoute(route)
        trafficlight = Trafficlight(2,2.5,'green', 50)
        world.addTrafficlight(trafficlight,lane2, 50)
        car = Car(limit)
        world.addCar(car, route)
        self.assertEqual(1, len(world.getTrafficlightsLocationsAndDirections()))

    def test_addroute(self):
        speedlimit = 60/3.6
        world = World()
        l0 = StraightLane(0, 0, 0, 1000, 3, speedlimit)
        l1 = StraightLane.continueLane(l0, 100)
        l2 = StraightLane.continueLane(l1, 100)
        route = Route([l0,l1,l2])
        world.addRoute(route)
        self.assertEqual(3, len(route.lanes))
        self.assertTrue(route in world.routes)

    def test_calculatenexttrafficlight(self):
        limit = 60/3.6
        world = World()
        lane1 = StraightLane(100,0,0,100,3,limit)
        lane2 = StraightLane.continueLane(lane1, 100)
        route = Route([lane1, lane2])
        world.addRoute(route)
        trafficlight = Trafficlight(2,2.5,'green', 50)
        world.addTrafficlight(trafficlight,lane2, 50)
        car = Car(limit)
        world.addCar(car, route)
        tl, d = world.getNextNonGreenTrafficlightAndDistance(car)

    def test_getters(self):
        limit  =10
        world = World()
        r = world.getRoutes()
        self.assertListEqual(r, [])
        lane1 = StraightLane(100,0,0,100,3,limit)
        lane2 = StraightLane.continueLane(lane1, 100)
        route = Route([lane1, lane2])
        world.addRoute(route)
        r = world.getRoutes()
        self.assertListEqual(r, [route])
        r = world.getCarsLocationsAndDirections()
        self.assertListEqual(r, [])
        r = world.getRoutesWithCommonLane(route)
        self.assertListEqual(r, [])
        r = world.getTrafficlightsLocationsAndDirections()
        self.assertListEqual(r, [])

    def test_carsetget(self):
        limit  =10
        world = World()
        r = world.getRoutes()
        self.assertListEqual(r, [])
        lane1 = StraightLane(100,0,0,100,3,limit)
        lane2 = StraightLane.continueLane(lane1, 100)
        route = Route([lane1, lane2])
        world.addRoute(route)

        r = world.getCars(route)
        self.assertListEqual(r, [])
        car1 = Car(limit)
        car2 = Car(limit)
        world.addCar(car1,route)
        r = world.getCars(route)
        self.assertListEqual(r, [car1])
        world.removeCar(car1)
        r = world.getCars(route)
        self.assertListEqual(r, [])
        world.addCar(car1,route)
        world.addCar(car2,route)
        r = world.getCars(route)
        self.assertListEqual(r, [car1, car2])
        world.removeCar(car1)
        r = world.getCars(route)
        self.assertListEqual(r, [car2])

        res =  world.getCarsLocationsAndDirections()
        self.assertEqual(1, len(res))

        world.removeCar(car2)
        res =  world.getCarsLocationsAndDirections()
        self.assertEqual(0, len(res))


if __name__ == '__main__':
    unittest.main()
