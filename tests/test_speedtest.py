import unittest
from speedchange import SpeedChange


class MyTestCase(unittest.TestCase):
    def test_distance(self):
        s = SpeedChange(60/3.6)
        s.addAcceleration(1.7,0)
        d = s.getTravelDistance(3)
        self.assertGreater(d,0)

    def test_getspeed(self):
        s = SpeedChange(60/3.6)
        s.addAcceleration(1.7,0)
        v = s.getSpeed(0)
        self.assertGreater(v,0)


if __name__ == '__main__':
    unittest.main()
