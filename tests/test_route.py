import unittest
from route import Route
from lane import StraightLane, CurvedLane


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



if __name__ == '__main__':
    unittest.main()
