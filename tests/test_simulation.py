import unittest
from simulation import *
import random

class A:
    def __init__(self):
        self.t = 't'
    def call(self):
        self.back()

    def back(self):
        print('A')

class B(A):
    def __init__(self):
        super().__init__()

    def back(self):
        print('B')
        print(self.t)

class MyTestCase(unittest.TestCase):
    def test_spawnratedistribution(self):
        avg = 12
        tailsize = 6
        distribution = [30, 25, 20]
        distribution = calculateCarSpawnDistribution(avg, distribution, tailsize)
        print(avg , distribution)
        time = 0
        count = 0
        for value in distribution:
            time += value
            count += 1
        self.assertAlmostEqual(avg, time/count)

    def test_inheritance(self):
        b = B()
        b.back()

    def test_listslicing(self):
        a = [1,23,4,56,7,8]
        print(a[-4:])

    def test_dummysimulation(self):
        x = 100000
        failurelist = []
        for i in range(10):
            found = False
            dum = Dummylights()
            for c in range(x):
                dum.moveTimestep(.2)
                routes = dum.world.getRoutes()
                for route in routes:
                    cars = dum.world.getCars(route)
                    for car in cars:
                        carAhead, distance = dum.world.getNextCarAheadAndDistance(car)
                        if carAhead:
                            msg = f'timestep #{i}'
                            found =  (car.halflength + carAhead.halflength > distance)
                            if found:
                                failurelist.append(f'{i}\n{c}')
                                break
                            self.assertLess(car.halflength + carAhead.halflength, distance, msg=msg)
                        if found: break
                    if found: break
                if found: break
        print(failurelist)
        self.assertEqual(0, len(failurelist))


    def test_dummysimulation1(self):
        x = 10000
        failurelist = []
        for i in range(10):
            print('now',i)
            found = False
            dum = Dummylights()
            for c in range(x):
                dum.moveTimestep(.2)
                routes = dum.world.getRoutes()
                for route in routes:
                    cars = dum.world.getCars(route)
                    for car in cars:
                        carAhead, distance = dum.world.getNextCarAheadAndDistance(car)
                        if carAhead:
                            msg = f'timestep #{c}'
                            found =  (car.halflength + carAhead.halflength > distance)
                            if found:
                                print(i,c)
                                carAhead.name = 'ahead'
                                print(carAhead)
                                print(car)
                                failurelist.append(f'{car}\n{carAhead}')
                            self.assertLess(car.halflength + carAhead.halflength, distance, msg=msg)

        print(len(failurelist))
        self.assertEqual(0, len(failurelist))
        
        


if __name__ == '__main__':
    unittest.main()
