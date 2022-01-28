import unittest
from speedchange import SpeedChange

class MyTestCase(unittest.TestCase):
    def test_indexrelated(self):
        offset = 0.5
        vi = 60/3.6
        sc = SpeedChange(vi)
        sc.addAcceleration(1,2)
        sc.addAcceleration(1,1,2)
        sc.addAcceleration(-1,1,3)
        changetimes = sc.getUpcommingSpeedChangeTimes(offset)
        tds = sc.getSpeedChangeTimesAndDistances(offset)
        print(changetimes)
        print(tds)

    def test_getIndexAndDurationRemaining(self):
        vi = 60/3.6
        sc = SpeedChange(vi)
        sc.addAcceleration(1,2)
        sc.addAcceleration(1,1,2)
        sc.addAcceleration(-1,1,3)
        changetimes = sc._getIndexAndDurationRemaining(2.1)
        print(changetimes)

    def test_customspeedchange(self):
        acc = [(-1, 1.9014566196709999), (0, 5.1478150704935), (2, 0.9507283098354999)]
        sc = SpeedChange(5)
        sc.accelerations = acc
        tds = sc.getSpeedChangeTimesAndDistances()

    def test_getAcceleration(self):
        sc = SpeedChange(10)
        sc.addAcceleration(1,1)
        sc.addAcceleration(-1,1,1)
        a = sc.getAcceleration(0)
        self.assertEqual(1,a)
        a = sc.getAcceleration(1)
        self.assertEqual(-1,a)
        a = sc.getAcceleration(2)
        self.assertEqual(0,a)
        a = sc.getAcceleration(20)
        self.assertEqual(0,a)

    def test_getIndexAndDurationRemaining(self):
        sc = SpeedChange(10)
        sc.addAcceleration(1,1)
        sc.addAcceleration(-1,1,1)
        a,_ = sc._getIndexAndDurationRemaining(0)
        self.assertEqual(0,a)
        a,_ = sc._getIndexAndDurationRemaining(1)
        self.assertEqual(1,a)
        a,_ = sc._getIndexAndDurationRemaining(2)
        print(a, sc.accelerations)
        self.assertEqual(2,a)
        a,_ = sc._getIndexAndDurationRemaining(20)
        self.assertEqual(2,a)

    def test_gettraveldistance(self):
        sc = SpeedChange(10)
        sc.addAcceleration(1,1)
        sc.addAcceleration(-1,1,1)
        self.assertEqual(0, sc.getTravelDistance(0))

    def test_speeditemcount(self):
        sc = SpeedChange(10)
        sc.addAcceleration(1,1)
        sc.addAcceleration(-1,1,1)
        sc.addAcceleration(-0.5,1,1)
        print(sc.accelerations)

    def test_addspeedchangetoanother(self):
        sc = SpeedChange(10)
        sc.addAcceleration(1,1)
        sc1 = SpeedChange(101)
        sc1.addAcceleration(-1,1,1)
        sc1.addAcceleration(-0.5,1,1)
        sc.addSpeedChange(sc1,1)
        sc.addSpeedChange(sc1,1)
        sc.addSpeedChange(sc1,1)
        print(sc.accelerations)




if __name__ == '__main__':
    unittest.main()
