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
        cls.car = Car(cls.initialSpeed)
        cls.route = Route([cls.lane])
        cls.trafficlight = Trafficlight(Trafficlight.calculateMaxYellowTime(cls.initialSpeed), 2)
        cls.world = World()
        cls.world.addRoute(cls.route)
        cls.world.addTrafficlight(cls.trafficlight, cls.lane, 200)
        cls.world.addCar(cls.car, cls.route)

    def test_move_timestep(self):
        speedlimit = 60/3.6
        world = World()
        l0 = StraightLane(0, 0, 0, 150, 3, speedlimit)
        l1 = StraightLane.continueLane(l0, 100)
        l2 = StraightLane.continueLane(l1, 100)
        tl1 = Trafficlight(2,2.5,'red')
        tl2 = Trafficlight(2,2.5,'red')
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
        l0 = StraightLane(0, 0, 0, 150, 3, speedlimit)
        l1 = StraightLane.continueLane(l0, 100)
        l2 = StraightLane.continueLane(l1, 100)
        tl1 = Trafficlight(2,2.5,'red')
        tl2 = Trafficlight(2,2.5,'red')
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

    def test_addandremovecar(self):
        limit = 60/3.6
        world = World()
        lane = StraightLane(100,0,0,100,3,limit)
        route = Route([lane])
        world.addRoute(route)
        car = Car(limit)
        world.addCar(car, route)
        self.assertEqual(1, len(world.routes[route]['cars']))
        world.removeCar(car)
        self.assertEqual(0, len(world.routes[route]['cars']))

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
        trafficlight = Trafficlight(2,2.5,'green')
        world.addTrafficlight(trafficlight,lane2, 50)
        car = Car(limit)
        world.addCar(car, route)
        self.assertEqual(1, len(world.routes[route]['trafficlights']))
        trafficlightitems = world.routes[route]['trafficlights']
        self.assertTrue(trafficlight in [x for x,_,_ in trafficlightitems])

    def test_addroute(self):
        speedlimit = 60/3.6
        world = World()
        l0 = StraightLane(0, 0, 0, 1000, 3, speedlimit)
        l1 = StraightLane.continueLane(l0, 100)
        l2 = StraightLane.continueLane(l1, 100)
        route = Route([l0,l1,l2])
        world.addRoute(route)
        self.assertEqual(3, len(route.lanes))
        self.assertTrue(route in world.routes.keys())
        routes = world.routes.keys()
        pass

    def test_calculatenexttrafficlight(self):
        limit = 60/3.6
        world = World()
        lane1 = StraightLane(100,0,0,100,3,limit)
        lane2 = StraightLane.continueLane(lane1, 100)
        route = Route([lane1, lane2])
        world.addRoute(route)
        trafficlight = Trafficlight(2,2.5,'green')
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
