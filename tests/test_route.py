import unittest
from route import Route
from lane import StraightLane, CurvedLane
from trafficlight import Trafficlight


class MyTestCase(unittest.TestCase):
    def test_getDistanceToLaneStart(self):
        l1 = StraightLane(0,0,0,100,2)
        l2 = StraightLane.continueLane(l1, 100)
        l3 = StraightLane.continueLane(l2, 100)
        route = Route([l1,l2,l3])
        self.assertEqual(route.getDistanceToLaneStart(l1, 50), -50)
        self.assertEqual(route.getDistanceToLaneStart(l1, 150), -150)
        self.assertEqual(route.getDistanceToLaneStart(l2, 50), 50)
        self.assertEqual(route.getDistanceToLaneStart(l3, 50), 150)

    def test_getDistanceToTrafficlight(self):
        l1 = StraightLane(0,0,0,100,2)
        l2 = StraightLane.continueLane(l1, 100)
        l3 = StraightLane.continueLane(l2, 100)
        route = Route([l1,l2,l3])
        tl1 = Trafficlight(1,2,'red', 20)
        tl2 = Trafficlight(1,2,'red', 40)
        tl3 = Trafficlight(1,2,'red', 20)
        l2.trafficlights.append(tl1)
        l2.trafficlights.append(tl2)
        l3.trafficlights.append(tl3)
        tl, dist = route.getNextNonGreenTrafficlightAndDistance(10)
        self.assertEqual(tl, tl1)
        self.assertEqual(dist, 110)
        tl, dist = route.getNextNonGreenTrafficlightAndDistance(130)
        self.assertEqual(tl, tl2)
        self.assertEqual(dist, 10)


if __name__ == '__main__':
    unittest.main()
