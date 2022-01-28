from lane import Lane
from functools import reduce


def sumTwo(a, b):
    return a + b


class Route:
    def __init__(self, lanes: [Lane]):
        self.lanes = lanes
        self.totalTravelDistance = sum([x.length for x in lanes])

    def addLane(self, lane):
        if lane not in self.lanes:
            self.lanes.append(lane)
            self.totalTravelDistance = sum([x.length for x in self.lanes])

    def getLanesLeft(self, distanceCovered: float):
        # returns the current lane and all the other remaining lanes
        totalDistance = 0
        result = []
        for lane in self.lanes:
            totalDistance += lane.length
            if distanceCovered < totalDistance:
                result.append(lane)
        return result

    def _getCurrentLaneIndexAndLaneDistanceCovered(self, distanceCovered: float):
        runningLanesLength = 0
        idx = 0
        laneDistanceCovered = 0
        for lane in self.lanes:
            if distanceCovered <= lane.length + runningLanesLength:
                laneDistanceCovered = distanceCovered - runningLanesLength
                break
            runningLanesLength += lane.length
            idx += 1
        return idx, laneDistanceCovered

    def getPastLanes(self, distanceCovered: float):
        laneDistance = 0
        result = []
        for lane in self.lanes:
            laneDistance += lane.length
            result.append(lane)
            if distanceCovered <= laneDistance:
                break
        return result

    def getCurrentLane(self, distanceCovered: float) -> Lane:
        return self.getLaneFromDistance(distanceCovered)

    def getLocationAndDirection(self, distanceCovered: float):
        i, d = self._getCurrentLaneIndexAndLaneDistanceCovered(distanceCovered)
        x, y = self.lanes[i].getLocation(d)
        return x, y, self.lanes[i].getDirection(d)

    def getDistanceToLaneStart(self, lane: Lane, distanceCovered: float):
        if lane not in self.lanes:
            return None
        i = self.lanes.index(lane)
        if i == 0: return 0 - distanceCovered
        return reduce(sumTwo, [x.length for x in self.lanes[:i]]) - distanceCovered

    def getCurrentLaneDistanceCovered(self, distanceCovered: float):
        result = distanceCovered
        for lane in self.lanes:
            if result <= lane.length:
                return result
            result -= lane.length
        return None

    def getSpeedLimit(self, distance=0):
        lane = self.getLaneFromDistance(distance)
        return lane.speedLimit

    def getLaneFromDistance(self, distance):
        if distance > self.totalTravelDistance: return None
        total = 0
        for lane in self.lanes:
            total += lane.length
            if distance <= total:
                return lane
        return None
