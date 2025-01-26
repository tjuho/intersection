import unittest
from simulation import *
import random
from car import Car


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

    def test_dummysimulation(self):
        x = 100000
        failurelist = []
        for i in range(10):
            found = False
            dum = DummylightsTwoCrossings()
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

    def test_dummysimulation11(self):
        dum = DummylightsTwoCrossings()
        print('')
        print(dum.world.routes)
        print(len(dum.world.getCarsLocationsAndDirections()))
        route = dum.world.routes[0]
        dum.world.addCar(Car(1),route)
        for i in range(1):
            dum.world.moveTimestep(1)
        self.assertEqual(1, len(dum.world.getCarsLocationsAndDirections()))




    def test_dummysimulation1(self):
        x = 10000
        failurelist = []
        for i in range(10):
            print('now',i)
            found = False
            dum = DummylightsTwoCrossings()
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
