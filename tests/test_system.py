import unittest
from world import World
from ai import AI
from car import Car
from speedchange import SpeedChange
from lane import CurvedLane, StraightLane
from trafficlight import Trafficlight
from route import Route
import random

class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        initialSpeed = 60 / 3.6
        cls.lane = StraightLane(0, 0, 0, 1000, 3, initialSpeed)
        cls.route = Route([cls.lane])
        cls.world = World()
        cls.ai = AI(cls.world)



    def test_carinemptyroad(self):
        world = World()
        ai = AI(world)
        lane = StraightLane(0,0,0,1000,2, 60/3.6)
        route = Route([lane])
        world.addRoute(route)
        carb = Car(60/3.6)
        cara = Car(60/3.6)
        world.addCar(cara, route)
        world.moveTimestep(3)
        world.addCar(carb, route)
        for i in range(19):
            world.moveTimestep(1)
            ai._adjustCar(carb, route)

    def test_stopAtTrafficlight(self):
        world = World()
        ai = AI(world)
        lane = StraightLane(0,0,0,1000,2, 60/3.6)
        route = Route([lane])
        world.addRoute(route)
        world.addTrafficlight(Trafficlight(2, 2.5,'red'),lane, 100)
        car = Car(60/3.6)
        world.addCar(car, route)
        for i in range(21):
            world.moveTimestep(1)
            ai.adjust()
            dt = car.getDistanceToTargetSpeed()
            self.assertAlmostEqual(dt, 100-car.distance-car.zeromargin)
        self.assertAlmostEqual(100, car.distance+car.zeromargin, delta=0.1)

    def test_stopAtTrafficlight2(self):
        cerr = 3
        ierr = 50
        timefromspeedchange = 6
        carname = '38'
        random.seed(1)
        timestep = 1
        speedlimit = 60/3.6
        tld = 200
        trafficlight = Trafficlight(2, 2.5, 'red')
        lane = StraightLane(0,0,0,1000,2, speedlimit)
        for c in range(100):
            world = World()
            ai = AI(world)
            route = Route([lane])
            world.addRoute(route)
            world.addTrafficlight(trafficlight,lane, tld)
            timetospawn = 0
            iserror = False
            for i in range(59):
                if timetospawn <= 0:
                    world.addCar(Car(speedlimit, name=str(i)), route)
                    timetospawn = random.randint(5,15)
                cars = world.getCars(route)
                for car in cars:
                    ahead, d = world.getNextCarAheadAndDistance(car)
                    if i == ierr-timefromspeedchange and c == cerr and car.name == carname:
                        print(car.timeFromLastSpeedChange, car.debug, ahead.timeFromLastSpeedChange, car.distance)
                        print(car.speedItems)
                        print()
                        pass
                    if c == cerr and car.name == carname:
                        print(car.timeFromLastSpeedChange, car.debug, ahead.timeFromLastSpeedChange)
                        print()
                        pass
                    ai._adjustCar(car, route)
                    if ahead is not None:
                        iserror = d - car.length <= 0
                        if iserror:
                            print(c, i, car.timeFromLastSpeedChange, car.name)
                            print(car.debug)
                            print(car.distance, ahead.distance)
                            print(car.speedItems)
                            self.assertGreaterEqual(d, car.halflength + ahead.halflength)
                    if iserror: break
                if iserror: break
                world.moveTimestep(timestep)
                timetospawn -= timestep

    def test_stopAndStartAtTrafficlightWithTwoCars(self):
        world = World()
        ai = AI(world)
        lane = StraightLane(0,0,0,1000,2, 60/3.6)
        route = Route([lane])
        world.addRoute(route)
        trafficlight = Trafficlight(1, 1.5, 'red')
        world.addTrafficlight(trafficlight,lane, 100)
        carAhead = Car(60/3.6)
        world.addCar(carAhead, route)
        for i in range(20):
            if i == 2:
                carFollowing = Car(60/3.6)
                world.addCar(carFollowing, route)
            world.moveTimestep(1)
            ai.adjust()
        self.assertAlmostEqual(100, carAhead.distance + carAhead.calculateDistanceMargin(0) + carAhead.halflength, delta=3)
        self.assertGreaterEqual(100, carAhead.distance)
        self.assertGreaterEqual(carAhead.distance, carFollowing.distance)
        margin = carAhead.calculateDistanceMargin(carAhead.getSpeed())
        self.assertAlmostEqual(carFollowing.distance, carAhead.distance - margin - carAhead.halflength)
        self.assertAlmostEqual(0, carAhead.getTargetSpeed(), delta=1e-3)
        self.assertAlmostEqual(0, carAhead.getSpeed(), delta=1e-3)
        trafficlight.switch()
        world.moveTimestep(1)
        world.moveTimestep(1)
        ai.adjust()
        world.moveTimestep(1)
        ai.adjust()
        ai._adjustCar(carFollowing, route)
        self.assertGreater(carAhead.getSpeed(), 0)
        self.assertGreater(carAhead.getTargetSpeed(), 0)
        self.assertLess(carAhead.timeFromLastSpeedChange, 3)
        world.moveTimestep(1)
        self.assertGreater(carFollowing.getSpeed(), 0)
        self.assertAlmostEqual(carFollowing.getTargetSpeed(), carAhead.getTargetSpeed(), delta=1e-3)
        self.assertLess(carFollowing.timeFromLastSpeedChange, 3)
        #self.assertGreater(carFollowing.getSpeed(), 0)
        for i in range(12):
            world.moveTimestep(1)
            ai.adjust()

    def test_stopAndStartAtTrafficlightWithTwoCars1(self):
        world = World()
        ai = AI(world)
        lane = StraightLane(0,0,0,1000,2, 60/3.6)
        route = Route([lane])
        world.addRoute(route)
        trafficlight = Trafficlight(1, 1.5, 'red')
        world.addTrafficlight(trafficlight,lane, 200)
        carAhead = Car(60/3.6)
        world.addCar(carAhead, route)
        ai.adjust()
        world.moveTimestep(1)
        carBehind = Car(60/3.6)
        world.addCar(carBehind, route)
        ai._adjustCar(carBehind, route)
        ai._adjustCar(carAhead, route)
        world.moveTimestep(1)
        ai._adjustCar(carBehind, route)
        ai._adjustCar(carAhead, route)
        for i in range(25):
            world.moveTimestep(1)
            ai._adjustCar(carBehind, route)
            ai._adjustCar(carAhead, route)
        print(carAhead.distance, carBehind.distance)
        margin = carAhead.calculateDistanceMargin(carAhead.getSpeed())
        self.assertLessEqual(carBehind.distance, carAhead.distance - margin - carBehind.halflength)

    def test_stopAndStartAtTrafficlightWithTwoCars2(self):
        world = World()
        ai = AI(world)
        lane = StraightLane(0,0,0,1000,2, 60/3.6)
        route = Route([lane])
        world.addRoute(route)
        trafficlight = Trafficlight(3, 3, 'green')
        world.addTrafficlight(trafficlight,lane, 500)
        for i in range(10000):
            if i % 100 == 0:
                car = Car(60/3.6)
                world.addCar(car, route)
            if i % 1000 == 0:
                print(f'{i} trafficlightswitch')
                trafficlight.switch()
            ai.adjust()
            cars = world.getCars(route)
            for c, car in enumerate(cars):
                ai._adjustCar(car, route)
            world.moveTimestep(0.2)
            cars = world.getCars(route)
            for c, car in enumerate(cars):
                ahead, d = world.getNextCarAheadAndDistance(car)
                if ahead is not None and ahead.distance < car.distance + ahead.halflength + car.zeromargin - 1e-6:
                    print(f'{i} crash')
                    self.assertGreaterEqual(ahead.distance, car.distance + ahead.halflength + car.zeromargin - 1e-6)


    def test_speedup(self):
        world = World()
        ai = AI(world)
        lane = StraightLane(0,0,0,1000,2, 20)
        route = Route([lane])
        world.addRoute(route)
        ahead = Car(20)
        ahead.addAcceleration(-20, 1, 4.5)
        world.addCar(ahead, route)
        world.moveTimestep(10)
        print(ahead.distance)
        behind = Car(20)
        world.addCar(behind, route)
        for i in range(9):
            ai._adjustCar(behind, route)
            world.moveTimestep(1)
            print(behind.distance)
        ahead.addAcceleration(1,10, 0)
        for i in range(10):
            ai._adjustCar(behind, route)
            world.moveTimestep(1)
            print(ahead.distance - behind.distance)
            self.assertGreater(ahead.distance, behind.distance + ahead.length)




    def test_startFollowingCarWhenLeadingCarSpeedsUp(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0,0,0,2000,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        carAhead = Car(2)
        world.addCar(carAhead, route)
        carAhead.addAcceleration(-1, 2)
        world.moveTimestep(2)
        carFollowing = Car(0)
        world.addCar(carFollowing, route)
        ai._adjustCar(carAhead, route)
        ai._adjustCar(carFollowing, route)
        world.moveTimestep(1)
        ai._adjustCar(carFollowing, route)
        self.assertGreater(carAhead.getTargetSpeed(), 0)
        self.assertGreater(carFollowing.getTargetSpeed(), 0)
        self.assertAlmostEqual(carAhead.getTargetSpeed(),carFollowing.getTargetSpeed())
        pass

    def test_stopBehindCarInTrafficlight(self):
        world = World()
        ai = AI(world)
        distance = 1000
        lane1 = StraightLane(0,0,0,2000,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        trafficlight = Trafficlight(2, 2.5, color='red')
        world.addTrafficlight(trafficlight, lane1, distance)
        car1 = Car(60/3.6)
        world.addCar(car1, route)
        for a in range(500):
            ai.adjust()
            world.moveTimestep(1)
        car2 = Car(60/3.6)
        world.addCar(car2, route)
        for a in range(200):
            ai.adjust()
            world.moveTimestep(1)
        carahead, dist = world.getNextCarAheadAndDistance(car2)
        margin = carahead.calculateDistanceMargin(carahead.getSpeed())
        self.assertAlmostEqual(car2.distance, carahead.distance - margin - carahead.halflength)

    def test_stopBehindCarInTrafficlight1(self):
        world = World()
        ai = AI(world)
        distance = 1000
        lane1 = StraightLane(0,0,0,distance*2,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        trafficlight = Trafficlight(2, 2.5, color='red')
        world.addTrafficlight(trafficlight, lane1, distance)
        car1 = Car(60/3.6, color='blue')
        world.addCar(car1, route)
        for a in range(500):
            ai.adjust()
            world.moveTimestep(.5)
        car2 = Car(60/3.6)
        world.addCar(car2, route)
        for a in range(200):
            ai.adjust()
            world.moveTimestep(.5)
        carahead, dist = world.getNextCarAheadAndDistance(car2)
        margin = car1.calculateDistanceMargin(carahead.getSpeed())
        self.assertAlmostEqual(car2.distance, carahead.distance - margin - carahead.halflength)

    def test_QueueAtTrafficlight(self):
        world = World()
        ai = AI(world)
        distance = 100
        lane1 = StraightLane(0,0,0,2000,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        trafficlight = Trafficlight(2, 2.5, color='red')
        world.addTrafficlight(trafficlight, lane1, distance)
        cars = [Car(60/3.6) for x in range(5)]
        for i, car in enumerate(cars):
            world.addCar(car, route)
            ai._adjustCar(car, route)
            for a in range(10):
                ai.adjust()
                world.moveTimestep(1)
        for car in cars:
            self.assertLess(car.distance, distance)
            ahead, d = world.getNextCarAheadAndDistance(car)
            if ahead is not None:
                self.assertAlmostEqual(ahead.distance, car.distance + ahead.halflength + car.zeromargin)
            distance = car.distance
            print(distance)


    def test_detectCarInFront(self):
        world = World()
        ai = AI(world)
        distance = 100
        lane1 = StraightLane(0,0,0,2000,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        trafficlight = Trafficlight(2, 2.5, color='red')
        world.addTrafficlight(trafficlight, lane1, distance)
        cars = [Car(60/3.6) for x in range(5)]
        prev = None
        for i, car in enumerate(cars):
            world.addCar(car, route)
            ai._adjustCar(car, route)
            for a in range(10):
                ai.adjust()
                world.moveTimestep(1)
            ahead, _ = world.getNextCarAheadAndDistance(car)
            if prev:
                self.assertEqual(prev, ahead)
            prev = car

    def test_slowDownAccordingToCarAhead(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0,0,0,20000,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        car = Car(60/3.6/2)
        world.addCar(car, route)
        world.moveTimestep(10)
        car1 = Car(60/3.6)
        world.addCar(car1, route)
        for i in range(150):
            ai._adjustCar(car1, route)
            world.moveTimestep(1)
        ahead, d = world.getNextCarAheadAndDistance(car1)
        margin = car.calculateDistanceMargin(car.getSpeed())
        self.assertAlmostEqual(margin + ahead.halflength, d, delta=1)
        self.assertEqual(car, ahead)
        self.assertAlmostEqual(car.getSpeed(), car1.getSpeed(), delta=1e-4)
        car.addAcceleration(4,(60/3.6-60/3.6/2)/4)
        ai._adjustCar(car1, route)
        self.assertAlmostEqual(car.getTargetSpeed(), car1.getTargetSpeed(), delta=1e-4)
        for i in range(150):
            ai._adjustCar(car1, route)
            world.moveTimestep(1)
        ahead, d = world.getNextCarAheadAndDistance(car1)
        self.assertEqual(car, ahead)
        margin = car.calculateDistanceMargin(car.getSpeed())
        self.assertAlmostEqual(car.getSpeed(), car1.getSpeed(), delta=1e-4)
        self.assertLessEqual(margin + car.halflength, d)

    def test_slowDownAccordingToCarAhead(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0,0,0,20000,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        car = Car(60/3.6/2)
        world.addCar(car, route)
        world.moveTimestep(10)
        car1 = Car(60/3.6)
        world.addCar(car1, route)
        for i in range(150):
            ai._adjustCar(car1, route)
            world.moveTimestep(1)
            self.assertGreater(car.distance, car1.distance + car.halflength + car1.halflength)
    def test_speedUpWithCarAhead(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0,0,0,20000,2, 60/3.6)
        route = Route([lane1])
        world.addRoute(route)
        car = Car(60/3.6/2)
        world.addCar(car, route)
        world.moveTimestep(0.5)
        car1 = Car(60/3.6/2)
        world.addCar(car1, route)
        car.addAcceleration(4,(60/3.6-60/3.6/2)/4)
        ai._adjustCar(car1, route)
        self.assertAlmostEqual(car.getTargetSpeed(), car1.getTargetSpeed(), delta=1e-4)
        for i in range(150):
            ai._adjustCar(car1, route)
            world.moveTimestep(1)
        ahead, d = world.getNextCarAheadAndDistance(car1)
        self.assertEqual(car, ahead)
        margin = car.calculateDistanceMargin(60 / 3.6)
        self.assertGreaterEqual(d, margin)
        self.assertAlmostEqual(car.getSpeed(), car1.getSpeed(), delta=1e-4)

    def test_speedUpWithCarAhead1(self):
        world = World()
        ai = AI(world)
        vl = 20
        lane1 = StraightLane(0,0,0,20000,2, vl)
        route = Route([lane1])
        world.addRoute(route)
        car = Car(10)
        world.addCar(car, route)
        world.moveTimestep(0.5)
        car1 = Car(10)
        world.addCar(car1, route)
        car.addAcceleration(2,(vl-10)/2)
        ai._adjustCar(car1, route)
        self.assertAlmostEqual(vl, car1.getTargetSpeed(), delta=1e-4)
        world.moveTimestep(1)
        ai._adjustCar(car1, route)
        for i in range(150):
            world.moveTimestep(1)
            ahead, d = world.getNextCarAheadAndDistance(car1)
            self.assertEqual(car, ahead)
        ahead, d = world.getNextCarAheadAndDistance(car1)
        self.assertEqual(car, ahead)
        margin = car.calculateDistanceMargin(car.getTargetSpeed())
        self.assertAlmostEqual(d, margin + car.halflength, delta=1)
        self.assertAlmostEqual(car.getSpeed(), car1.getSpeed(), delta=1e-4)

    def test_speedUpWithCarAheadWithDelayedSpeedUp2(self):
        world = World()
        ai = AI(world)
        vl = 20
        an = -2
        lane1 = StraightLane(0,0,0,20000,2, vl)
        route = Route([lane1])
        world.addRoute(route)
        car = Car(10)
        world.addCar(car, route)
        world.moveTimestep(1.5)
        car1 = Car(10)
        world.addCar(car1, route)
        car.setSpeed(0)
        ai._adjustCar(car1, route)
        world.moveTimestep(1)
        ai._adjustCar(car1, route)
        for i in range(10):
            world.moveTimestep(1)
            ahead, d = world.getNextCarAheadAndDistance(car1)
            self.assertEqual(car, ahead)
            self.assertGreaterEqual(d, car.zeromargin + car.halflength)
        car.setSpeed(vl, 3)
        for i in range(20):
            ai._adjustCar(car1, route)
            world.moveTimestep(1)
            ahead, d = world.getNextCarAheadAndDistance(car1)
            print(d)
            self.assertEqual(car, ahead)
            self.assertGreaterEqual(d, car.zeromargin + car.halflength)
        ahead, d = world.getNextCarAheadAndDistance(car1)
        self.assertEqual(car, ahead)
        margin = car.calculateDistanceMargin(car.getTargetSpeed())
        self.assertAlmostEqual(d, margin + car.halflength, delta=1)
        self.assertAlmostEqual(car.getSpeed(), car1.getSpeed(), delta=1e-4)

    def test_stopAtSecondTrafficlight(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0,0,0,100,2, 60/3.6)
        lane2 = StraightLane.continueLane(lane1,2000)
        trafficlight = Trafficlight(2, 2.5,'red')
        trafficlight1 = Trafficlight(2, 2.5, 'red')
        route = Route([lane1, lane2])
        world.addRoute(route)
        car = Car(10)
        world.addCar(car, route)
        world.addTrafficlight(trafficlight, lane1, 100)
        world.addTrafficlight(trafficlight1, lane2, 50)
        for i in range(100):
            ai._adjustCar(car, route)
            world.moveTimestep(1)
        t, d = world.getNextNonGreenTrafficlightAndDistance(car)
        self.assertAlmostEqual(car.zeromargin, d)
        self.assertEqual(t, trafficlight)
        trafficlight.switch()
        world.moveTimestep(3)
        ai._adjustCar(car, route)
        world.moveTimestep(2)
        self.assertLess(0, car.getSpeed())
        for i in range(100):
            ai._adjustCar(car, route)
            world.moveTimestep(1)
        t, d = world.getNextNonGreenTrafficlightAndDistance(car)
        self.assertEqual(t, trafficlight1)
        self.assertAlmostEqual(car.zeromargin, d)

    '''
    red trafficlight that switches to green followed by red trafficlight
    '''
    def test_stopAtTrafficlightWhenOtherCarsOnTheNextTrafficlight(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0, 0, 0, 100, 2, 10)
        lane2 = StraightLane.continueLane(lane1, 2000)
        trafficlight1 = Trafficlight(2, 0, 'red')
        trafficlight2 = Trafficlight(2, 0, 'red')
        route = Route([lane1, lane2])
        world.addRoute(route)
        car = Car(10)
        world.addCar(car, route)
        world.addTrafficlight(trafficlight1, lane1, 50)
        world.addTrafficlight(trafficlight2, lane2, 50)
        for i in range(60):
            world.moveTimestep(1)
            ai.adjust()
            if i == 30:
                trafficlight1.switch()
            if i > 40:
                t, d = world.getNextNonGreenTrafficlightAndDistance(car)
                self.assertEqual(trafficlight2, t)
            if i < 30:
                t, d = world.getNextNonGreenTrafficlightAndDistance(car)
                self.assertEqual(trafficlight1, t)

    def test_stopWhenYellowIsTooShort(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0, 0, 0, 100, 2, 10)
        lane2 = StraightLane.continueLane(lane1, 2000)
        trafficlight = Trafficlight(2, 2.5, 'green')
        route = Route([lane1, lane2])
        world.addRoute(route)
        car = Car(10)
        world.addCar(car, route)
        world.addTrafficlight(trafficlight, lane1, 52)
        trafficlight.switch(0)
        for i in range(30):
            ai._adjustCar(car, route)
            world.moveTimestep(1)
        t, d = world.getNextNonGreenTrafficlightAndDistance(car)
        self.assertEqual(t, trafficlight)
        self.assertAlmostEqual(car.zeromargin, d, delta=0.1)

    def test_removecarwhenfinished(self):
        world = World()
        ai = AI(world)
        lane1 = StraightLane(0, 0, 0, 100, 2, 10)
        lane2 = StraightLane.continueLane(lane1, 100)
        trafficlight = Trafficlight(2, 'green')
        route = Route([lane1, lane2])
        world.addRoute(route)
        car = Car(10)
        world.addCar(car, route)
        world.addTrafficlight(trafficlight, lane1, 52)
        for i in range(300):
            ai._adjustCar(car, route)
            world.moveTimestep(1)
        res = world.getCarsLocationsAndDirections()
        self.assertEqual(0,len(res))
        res = world.getCars(route)
        self.assertEqual(0,len(res))

    def test_stopattrafficlight(self):
        world = World()
        ai = AI(world)
        vl = 10
        lane = StraightLane(0, 0, 0, 1000, 2, vl)
        tfd = 200
        trafficlight = Trafficlight(2,2.5, 'red')
        world.addTrafficlight(trafficlight,lane, tfd)
        car = Car(vl)
        route = Route([lane])
        world.addRoute(route)
        world.addCar(car, route)
        for i in range(50):
            ai.adjust()
            world.moveTimestep(1)

    def test_rewindcars(self):
        world = World()
        ai = AI(world)
        vl = 60/3.6
        lane = StraightLane(0, 0, 0, 2000, 2, vl)
        route = Route([lane])
        world.addRoute(route)

        ahead = Car(vl)
        world.addCar(ahead, route)

        speed = 3.943246027810658
        ahead.distance = 386.536719800151
        ahead.speedItems = [(0, 16.666666666666668, 0), (16.199999999999974, 16.666666666666668, 269.9999999999996),
                            (16.799999999999972, 15.915915915915923, 279.77477477477436),
                            (29.520000000000017, -1.7763568394002505e-15, 381.0),
                            (40.00000000000003, -1.7763568394002505e-15, 381.0),
                            (40.20000000000003, 0.2749385431491808, 381.0274938543149),
                            (40.400000000000034, 0.4550426141922384, 381.10049197004906),
                            (41.32398914322818, 1.0908674521030872, 381.81469402888104),
                            (51.56820030028747, 16.666666666666668, 472.7706585995621)]
        ahead.time = 43.200000000000074
        ahead.timeFromLastSpeedChange = 2.8000000000000003

        ahead.timeFromLastSpeedChange = round(ahead.timeFromLastSpeedChange, 12)

        car = Car(vl)
        world.addCar(car, route)

        speed = 6.428020694515624
        car.distance = 382.6795067171358
        car.speedItems = [(0, 16.666666666666668, 0), (15.799999999999976, 16.666666666666668, 263.333333333333),
                          (16.99999999999997, 15.174129353233841, 282.4378109452732),
                          (24.999999999999943, 5.223880597015, 364.02985074626827),
                          (25.199999999999942, 5.302825370923535, 365.0825213430621),
                          (25.39999999999994, 5.3780547158770515, 366.15060935174216),
                          (25.59999999999994, 5.45333213638262, 367.2337480369681),
                          (32.169625666126365, 7.916154816378911, 411.1500103508704),
                          (38.041037402225044, 16.666666666666668, 483.3179436318567)]
        car.time = 28.199999999999932
        car.timeFromLastSpeedChange = 2.6

        th = car.time - car.timeFromLastSpeedChange

        car.timeFromLastSpeedChange = round(car.timeFromLastSpeedChange, 12)
        world.moveTimestep(-1*car.timeFromLastSpeedChange)
        car.timeFromLastSpeedChange = 99
        car.speedItems = [x for x in car.speedItems if x[0] < th]
        print(car.speedItems)
        ai._adjustCar(car, route)
        print(car.speedItems)
        count = 0
        xstep = 0.7282458007194501
        world.moveTimestep(xstep)
        a,d = world.getNextCarAheadAndDistance(car)
        print(str(round(count,1)),str(round(d, 4)), car.getAcceleration(), ahead.getAcceleration())
        print()
        world.moveTimestep(-xstep)
        t = .1
        for i in range(100):
            count += 0.1
            world.moveTimestep(t)
            a,d = world.getNextCarAheadAndDistance(car)
            print(str(round(count,1)),str(round(d, 4)), car.getAcceleration(), ahead.getAcceleration())


if __name__ == '__main__':
    unittest.main()
