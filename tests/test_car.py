import unittest
from car import Car
from speedchange import SpeedChange
import copy
import math
class MyTestCase(unittest.TestCase):

    def test_append_acceleration(self):
        sp = Car(1)
        sp.changeSpeed(2,1)
        speed = sp.getSpeed()
        offsetspeed = sp.getSpeed(1)
        self.assertEqual(1, speed)
        sp.moveTimestep(1)
        speed = sp.getSpeed()
        self.assertEqual(2, speed)
        self.assertEqual(speed, offsetspeed)

    def test_distance(self):
        sp = Car()
        sp.changeSpeed(1,1,0)
        sp.changeSpeed(3,1,1)
        self.assertEqual(2.5, sp.getTravelDistance(2))
        self.assertEqual(5.5, sp.getTravelDistance(3))
        sp.moveTimestep(2)
        self.assertEqual(2.5, sp.distance)
        sp.moveTimestep(1)
        self.assertEqual(5.5, sp.distance)

    def test_move_forward_with_initial_speed(self):
        sp = Car(10)
        sp.moveTimestep(1)
        self.assertEqual(10, sp.distance)

    def test_move_forward_with_initial_speed_and_acceleration(self):
        sp = Car(10)
        sp.changeSpeed(11,1,1)
#        sp.addAcceleration(1, 1, 1)
        sp.moveTimestep(1)
        sp.moveTimestep(1)
        self.assertEqual(sp.distance, 20.5)

    def test_move_forward_and_backward_at_initial_speed(self):
        sp = Car(10)
        sp.moveTimestep(.5)
        sp.moveTimestep(.5)
        self.assertEqual(10, sp.distance)
        sp.moveTimestep(-1)
        self.assertEqual(0, sp.distance)
        sp.moveTimestep(1)
        self.assertEqual(10, sp.distance)
        sp.moveTimestep(-.5)
        self.assertEqual(5, sp.distance)
        sp.moveTimestep(-1.5)
        self.assertEqual(0, sp.distance)
        sp.moveTimestep(.5)
        self.assertEqual(0, sp.distance)
        sp.moveTimestep(-.5)
        self.assertEqual(0, sp.distance)
        sp.moveTimestep(1.5)
        self.assertEqual(5, sp.distance)

    def test_time_reduction(self):
        sp = Car(10)
        sp.moveTimestep(1)
        self.assertEqual(sp.distance, 10)
        sp.moveTimestep(-1)
        self.assertEqual(sp.distance, 0)
        sp.moveTimestep(1)
        self.assertEqual(sp.distance, 10)
        sp.moveTimestep(-.25)
        self.assertEqual(sp.distance, 7.5)

    def test_time_forwward_and_backward_by_multiple_speeditems_when_accelerating(self):
        # /-\
        sp = Car(1)
        sp.changeSpeed(2,1,0)
        sp.changeSpeed(1,1,2)
        sp.moveTimestep(1)
        self.assertEqual(1.5, sp.distance)
        sp.moveTimestep(-1)
        self.assertEqual(0, sp.distance)
        sp.moveTimestep(3)
        self.assertEqual(5, sp.distance)
        sp.moveTimestep(-3)
        self.assertEqual(0, sp.distance)

    def test_time_forwward_and_backward_by_multiple_speeditems_when_accelerating1(self):
        sp = Car(1)
        sp.changeSpeed(2, 1, 0)
        sp.changeSpeed(1, 1, 2)
        sp.moveTimestep(3)
        self.assertEqual(5, sp.distance)
        sp.moveTimestep(-4)
        self.assertEqual(0, sp.distance)
        sp.moveTimestep(4/3)
        sp.moveTimestep(4/3)
        sp.moveTimestep(4/3)
        self.assertAlmostEqual(5, sp.distance)
        sp.moveTimestep(-4/3)
        sp.moveTimestep(-4/3)
        sp.moveTimestep(-4/3)
        self.assertAlmostEqual(0, sp.distance)

    def test_travelDistanceFunctions(self):
        sp = Car(0)
        sp.changeSpeed(1,1,0)
        sp.changeSpeed(0,1,2)
        sp.changeSpeed(5,5,3)
        d1 = sp.getTravelDistance(-1.8, 3)
        d2 = sp.getTravelDistance(1.8,1.2)
        self.assertAlmostEqual(-d1,d2)

    def test_copy(self):
        sp = Car(0)
        sp.changeSpeed(1,1,0)
        sp.changeSpeed(0,1,2)
        sp.changeSpeed(5,5,3)
        d1 = sp.getTravelDistance(-1.8, 3)
        sp1 = copy.deepcopy(sp)
        d2 = sp1.getTravelDistance(1.8,1.2)
        self.assertAlmostEqual(-d1,d2)

    def test_addAccelerationToReplace(self):
        sp = Car(0)
        sp.changeSpeed(1,1,0)
        sp.changeSpeed(0,1,2)
        sp.changeSpeed(5,5,3)
        self.assertEqual(5,len(sp.speedItems))
        sp.addAcceleration(0,1,1)
        self.assertEqual(3,len(sp.speedItems))
        sp.addAcceleration(0, 1, 0.5)
        self.assertEqual(3,len(sp.speedItems))

    def test_addMultipleSpeeditemsWithSameStartTime(self):
        sp = Car(0)
        sp.changeSpeed(1,1,0)
        sp.changeSpeed(1,1,0)
        sp.changeSpeed(1,1,0)
        self.assertEqual(2,len(sp.speedItems))
        sp.changeSpeed(-1,1,2)
        sp.changeSpeed(-1,1,2)
        sp.changeSpeed(-1,1,2)
        self.assertEqual(4,len(sp.speedItems))

    def test_getSpeedItemIndex(self):
        sp = Car(0)
        sp.changeSpeed(1,1,0)
        sp.changeSpeed(0,1,2)
        sp.changeSpeed(5,5,3)
        self.assertEqual(0, sp._getSpeedItemIndex(0))
        self.assertEqual(0, sp._getSpeedItemIndex(0.999))
        self.assertEqual(1, sp._getSpeedItemIndex(1.999))

    def test_speedItemIndexAndSpeeds(self):
        sp = Car(0)
        speed= -1707.907683408471
        sp.time= 4.286636226628616
        sp.distance= 86.93166310234722
        sp.speedItems= [(0, 16.666666666666668, 0), (4.245104914725703, 16.666666666666668, 70.75174857876172),
                (7.456666666666666, 3.8204196589028108, 103.64952000471754),
                (7.480457240638014, 16.666666666666668, 122.21036217191725)]
        time=4.286636226628616
        self.assertEqual(1,sp._getSpeedItemIndex(time))
        self.assertAlmostEqual(sp.getSpeed(4.245104914725703-10e-7), sp.getSpeed(4.245104914725703))
        count = 20000
        step = 10/count
        time = 0
        for i in range(count):
            self.assertLessEqual(0, sp.getSpeed(time))
            time += step

    def test_speedchange(self):
        sc = SpeedChange(0)
        sc.addAcceleration(1,1)
        sc.addAcceleration(1,1,1)
        d = sc.getTravelDistance(0.5, 0)
        temp = sc.getSpeed(0.5)
        self.assertAlmostEqual(0.5*(temp)*0.5, d )


    def test_speedchangegetspeed(self):
        sc = SpeedChange(2)
        sc.addAcceleration(1,1)
        sc.addAcceleration(1,1,1)
        sc.addAcceleration(1,1,2)
        sc.addAcceleration(-1,2,3)
        v1 = sc.getSpeed(1)
        v2 = sc.getSpeed(3)
        v3 = sc.getSpeed(4)
        d1 = 0.5*(v1+v2)*2
        d2 = 0.5*(v3+v2)*1
        dx = sc.getTravelDistance(3,1)
        self.assertAlmostEqual(d1+d2,dx)

    def test_speedchangeplus(self):
        sc1 = SpeedChange(0)
        sc2 = SpeedChange(0)
        sc1.addAcceleration(1,1,1)
        sc2.addAcceleration(2,2)
        temp = sc1 +sc2
        print(temp)

    def test_speedchangecomparison(self):
        sc1 = SpeedChange(0)
        sc2 = SpeedChange(0)
        sc1.accelerations = [(1.7, 0.0), (0, 0.2940350877192972), (-1.9, 8.771929824561404)]
        sc2.accelerations = [(1.7, 0.0), (0, 0.3540350877192972), (-1.9, 8.771929824561404)]
        self.assertTrue(sc1 < sc2)

    def test_makesFaster(self):
        vi = 10
        car = Car(vi)
        sc = SpeedChange(vi-0.5)
        sc.addAcceleration(0.1, 10)
        self.assertTrue(car.makesFaster(sc))
        sc = SpeedChange(vi-1)
        sc.addAcceleration(0.1, 10)
        self.assertFalse(car.makesFaster(sc))


    def test_premade(self):
        offsettime = -2
        cara =Car(60/3.6)
        cara.time = 48.60000000000015
        cara.distance = 371.2014985909131
        cara.speedItems=[(0, 16.666666666666668, 0),(15.399999999999977, 16.666666666666668, 256.6666666666663),(15.599999999999977, 16.666666666666668, 259.9999999999996),(15.799999999999976, 16.666666666666668, 263.3333333333329),(15.999999999999975, 16.666666666666668, 266.66666666666623),(16.199999999999974, 16.666666666666668, 269.99999999999955),(16.399999999999974, 16.666666666666668, 273.33333333333286),(16.599999999999973, 16.666666666666668, 276.6666666666662),(16.799999999999972, 16.666666666666668, 279.9999999999995),(17.7540350877193, 16.666666666666668, 295.9005847953216),(26.525964912280703, 0.0, 369.0),(45.0000000000001, 0.0, 369.0),(45.2000000000001, 0.0, 369.0),(45.400000000000105, 0.2373506087345055, 369.02373506087343),(45.528158623013134, 0.0, 369.0389443244668),(45.60000000000011, 0.0, 369.0389443244668),(45.80000000000011, 0.25159900816821035, 369.06410422528364),(45.95887871767732, 0.0, 369.084091089177),(46.96470683276213, 0.0, 369.084091089177),(46.96470683276214, 0.0, 369.084091089177),(57.48930566656672, 16.666666666666668, 456.78908137088183)]
        carb = Car(60 / 3.6)
        carb.time = 33.59999999999994
        carb.distance = 367
        carb.speedItems=[(0, 16.666666666666668, 0),(14.999999999999979, 16.666666666666668, 249.99999999999966),(15.199999999999978, 16.666666666666668, 253.33333333333297),(15.399999999999977, 16.666666666666668, 256.6666666666663),(15.599999999999977, 16.666666666666668, 259.9999999999996),(15.799999999999976, 16.666666666666668, 263.3333333333329),(15.999999999999975, 16.666666666666668, 266.66666666666623),(16.199999999999974, 16.666666666666668, 269.99999999999955),(16.399999999999974, 16.666666666666668, 273.33333333333286),(16.599999999999973, 16.666666666666668, 276.6666666666662),(16.799999999999972, 16.666666666666668, 279.9999999999995),(17.3940350877193, 16.666666666666668, 289.9005847953216),(26.165964912280703, 0.0, 363.0),(29.999999999999925, 0.0, 363.0),(30.199999999999925, 0.0, 363.0),(30.399999999999924, 0.222164140094092, 363.0222164140094),(30.507169675696264, 0.0, 363.03412104343204),(30.599999999999923, 0.0, 363.03412104343204),(30.799999999999923, 0.2346093438603781, 363.0575819778181),(30.93465475247487, 0.0, 363.073377609381),(30.999999999999922, 0.0, 363.073377609381),(44.41272688175304, 16.666666666666668, 474.8461016239903)]
        distance = cara.getDistance(offsettime) - carb.getDistance(offsettime)
        tds = cara.getSpeedChangeTimesAndDistances(offsettime)
        tds.extend(carb.getSpeedChangeTimesAndDistances(offsettime))
        tds.sort(key=lambda y: y[0])
        for t,d in tds:
            distance = cara.getDistance(offsettime+t) - carb.getDistance(offsettime+t)
            print(t,d, distance)
        for t in range(1200):
            t /= 10
            distance = cara.getDistance(offsettime+t) - carb.getDistance(offsettime+t-.2)
            print(t, distance)

    def test_getSpeedItemIndex(self):
        car = Car(10)
        car.addAcceleration(1,1)
        car.addAcceleration(-1,1,1)
        i = car._getSpeedItemIndex(0)
        self.assertEqual(0,i)
        i = car._getSpeedItemIndex(1)
        self.assertEqual(1,i)
        i = car._getSpeedItemIndex(2)
        self.assertEqual(2,i)
        i = car._getSpeedItemIndex(20)
        self.assertEqual(2,i)

    def test_calculateSpeedChangeSpeedIntersectionTimes(self):
        car = Car(10)
        car.addAcceleration(1, 1)
        car.addAcceleration(-1, 1, 1)
        sc = SpeedChange(10.5)
        res = car.calculateSpeedChangeSpeedIntersectionTimes(sc)
        self.assertEqual(2, len(res))
        res = car.calculateSpeedChangeSpeedIntersectionTimes(sc,1)
        self.assertEqual(1, len(res))

    def test_calculateSpeedChangeSpeedIntersectionTimes1(self):
        car = Car(0)
        car.addAcceleration(2, 1)
        car.addAcceleration(0.5, 2, 1)
        car.addAcceleration(2, 1, 3)
        sc = SpeedChange(1)
        sc.addAcceleration(2,1,1)
        sc.addAcceleration(0.5,2,2)
        res = car.calculateSpeedChangeSpeedIntersectionTimes(sc)
        self.assertEqual(3, len(res))
        res = car.calculateSpeedChangeSpeedIntersectionTimes(sc, True)
        self.assertEqual(2, len(res))
        res = car.calculateSpeedChangeSpeedIntersectionTimes(sc,offsettime=1)
        self.assertEqual(2, len(res))
        res = car.calculateSpeedChangeSpeedIntersectionTimes(sc, True, offsettime=1)
        self.assertEqual(1, len(res))
        print(res)

    def test_speeditemscount(self):
        car = Car(10)
        car.addAcceleration(1, 1, 0)
        car.addAcceleration(1, 1, 1)
        car.addAcceleration(0.5, 1, 1)
        car.addAcceleration(0.5, 1, 1)
        car.addAcceleration(0.5, 1, 1)
        car.addAcceleration(0.5, 1, 1)
        car.changeSpeed(5,5,1)
        car.changeSpeed(5,5,1)
        car.changeSpeed(5,5,1)
        car.changeSpeed(5,5,1)
        car.changeSpeed(5,5,1)
        self.assertEqual(3, len(car.speedItems))

    def test_speeditemswithsamestartspeed(self):
        car = Car(10)
        car.initialSpeed = 16.666666666666668
        car.time = 34.59999999999995
        car.distance = 375.0
        car.timeFromLastSpeedChange = 0.0
        car.speedItems = [(0, 16.666666666666668, 0), (15.799999999999976, 16.666666666666668, 263.333333333333),
                          (15.999999999999975, 16.417910447761198, 266.64179104477574),
                          (16.146327187591428, 16.666666666666668, 269.06237760567916),
                          (16.199999999999974, 16.666666666666668, 269.9569244791549),
                          (16.399999999999974, 16.402224887519928, 273.2638136345736),
                          (16.55555398773335, 16.666666666666668, 275.8358126101617),
                          (16.599999999999973, 16.666666666666668, 276.5765794812721),
                          (16.799999999999972, 16.384439350938578, 279.88169008303265),
                          (16.96601606807532, 16.666666666666668, 282.6251974163248),
                          (18.122539310815128, 16.666666666666668, 301.9005847953216), (26.894469135376532, 0.0, 375.0),
                          (35.799999999999955, 0.0, 375.0), (41.18711484593834, 9.158095238095258, 399.6678554088303)]
        vt = 16.666666666666668
        tt = 4.416806722689064
        offsettime = 6.5871148459383875
        car.changeSpeed(vt,tt,offsettime)
        print(car.speedItems)

    def test_speeditemswithsamestartspeed1(self):
        car = Car(10)
        car.changeSpeed(5,5)
        car.changeSpeed(5,5)
        car.changeSpeed(10,5,5)
        car.changeSpeed(5,5,10)
        print(car.speedItems)

    def test_calculateDistanceIntegralCrossingTime(self):
        va = 1
        vb = 2
        d = 20
        vt = 15
        tt = 41
        car = Car(va)
        car.changeSpeed(vt,tt)
        speedchange = SpeedChange(vb)
        tx = 2*d/(vb-va)
        vx = car.getAcceleration()*tx+va
        print(tx)
        speedchange.addAcceleration((vx-vb)/tx, tx)
        step = 0
        for i in range(100):
            step += 0.1
            da = car.getTravelDistance(step)
            db = speedchange.getTravelDistance(step)
            print(step, da+d, db)
        self.assertAlmostEqual(car.getTravelDistance(tx)+d, speedchange.getTravelDistance(tx))

        #res = car.calculateDistanceIntegralCrossingTime(speedchange, 20)
        #print(res)






def func(sc: SpeedChange, d, a, o):
    sc.addAcceleration(d,a, o)

if __name__ == '__main__':
    unittest.main()
