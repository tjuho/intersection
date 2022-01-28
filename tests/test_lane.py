import unittest
from lane import *


class MyTestCase(unittest.TestCase):
    def test_boundingboxofxurvedlane(self):
        lane = CurvedLane(1,2,180, 0, 1, 1, False)
        xmax, ymax, xmin, ymin = lane.getBoundingBox()
        #print(xmax, ymax, xmin, ymin)
        self.assertAlmostEqual(1,xmax)
        self.assertAlmostEqual(2,ymax)
        self.assertAlmostEqual(0, xmin)
        self.assertAlmostEqual(0, ymin)

        lane = CurvedLane(1,2,0, 180, 1, 1, True)
        xmax, ymax, xmin, ymin = lane.getBoundingBox()
        #print(xmax, ymax, xmin, ymin)
        self.assertAlmostEqual(2,xmax)
        self.assertAlmostEqual(2,ymax)
        self.assertAlmostEqual(1, xmin)
        self.assertAlmostEqual(0, ymin)

        lane = CurvedLane(1,2,0, 180, 1, 1, False)
        xmax, ymax, xmin, ymin = lane.getBoundingBox()
        #print(xmax, ymax, xmin, ymin)
        self.assertAlmostEqual(2,xmax)
        self.assertAlmostEqual(4,ymax)
        self.assertAlmostEqual(1, xmin)
        self.assertAlmostEqual(2, ymin)

        print(10e-9)