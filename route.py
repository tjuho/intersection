from lane import Lane
from functools import reduce
import uuid

def sumTwo(a, b):
    return a + b


class Route:
    def __init__(self, lanes: [Lane]):
        self.id = str(uuid.uuid4())
        self.lanes = lanes
        self.cars = []
        self.totalTravelDistance = sum([x.length for x in lanes])

    def to_dict(self):
        return {
            "id": self.id,
            "lanes": [lanes.to_dict() for lanes in self.lanes],
            "totalTravelDistance": self.totalTravelDistance,
        }

    def addLane(self, lane):
        if lane not in self.lanes:
            self.lanes.append(lane)
            self.totalTravelDistance = sum([x.length for x in self.lanes])

    def addCar(self, car):
        if car not in self.cars:
            print('add car', car)
            self.cars.append(car)
            print('all cars', self.cars)

    # returns the current lane and all the other remaining lanes
    def getLanesLeft(self, distanceCovered: float):
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

    def getCarsLocationsAndDirections(self):
        result = []
        for car in self.cars:
            x,y,d = self.getLocationAndDirection(car.distance)
            result.append((car, x,y,d))
        return result

    def getTrafficlightsLocationsAndDirections(self):
        result = []
        for lane in self.lanes:
            for tl in lane.trafficlights:
                x,y = lane.getLocation(tl.distanceFromLaneStart)
                d = lane.getDirection(tl.distanceFromLaneStart)
                result.append((tl, x, y, d))
        return result

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

    def getNextNonGreenTrafficlightAndDistance(self, distanceCovered):
        lanePosition = self.getCurrentLaneDistanceCovered(distanceCovered)
        lanes = self.getLanesLeft(distanceCovered)
        if len(lanes) == 0:
            return None, None
        if len(lanes) == 1:
            return lanes[0].getNextNonGreenTrafficlightAndDistance(lanePosition)
        tl, dist = lanes[0].getNextNonGreenTrafficlightAndDistance(lanePosition)
        if tl is not None:
            return tl, dist
        distance = lanes[0].length - lanePosition
        for i, lane in enumerate(lanes[1:]):
            tl, dist = lane.getNextNonGreenTrafficlightAndDistance(0)
            if tl is not None:
                return tl, dist + distance
        return None, None

    def getTotalDistance(self):
        ls = [x.length for x in self.lanes]
        return sum(ls)

    def __str__(self):
        return f"Route length {self.totalTravelDistance}"