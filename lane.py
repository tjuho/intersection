import math


class Lane:
    def __init__(self, startx: float, starty: float, endx: float, endy: float,
                 centerx: float, centery: float, length: float, width: float, startDirection: float,
                 endDirection: float, speedLimit: float):
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy
        self.centerx = centerx
        self.centery = centery
        self.length = length
        self.width = width
        self.startDirection = startDirection
        self.endDirection = endDirection
        self.type = None
        self.speedLimit = speedLimit

    def coordinates(self, distance):
        if distance > self.length:
            return None, None
        x = distance / self.length * (self.endx - self.startx) + self.startx
        y = distance / self.length * (self.endy - self.starty) + self.starty
        return x, y

    def inLane(self, x: float, y: float):
        return False

    def getStraightApproximationCoordinateList(self):
        return [(self.startx, self.starty, self.endx, self.endy)]

    def getDirection(self, travel=0):
        if travel > self.length or travel < 0:
            return None
        return self.startDirection

    def getLocation(self, travel=0):
        if travel > self.length or travel < 0:
            return None, None
        x = self.startx + (self.endx - self.startx) * travel / self.length
        y = self.starty + (self.endy - self.starty) * travel / self.length
        return x, y

    def getBoundingBox(self):
        return self.startx, self.starty, self.endx, self.endy

    def getSpeedlimit(self):
        return self.speedLimit

    def __str__(self):
        return 'Lane: startx {:.2f} starty {:.2f} endx {:.2f} endy {:.2f} length {:.2f} width {:.2f} start direction {:.4f} end direction {:.4f}' \
               ''.format(self.startx, self.starty, self.endx, self.endy, self.length, self.width, self.startDirection,
                         self.endDirection)


class CurvedLane(Lane):
    def __init__(self, startx, starty, startDirection, endDirection, radius, width, isClockwise, speedLimit=60 / 3.6):
        if (startDirection >= math.pi * 2 or endDirection >= math.pi * 2):
            startDirection = startDirection / 180 * math.pi
            endDirection = endDirection / 180 * math.pi
        assert (startDirection != endDirection)
        self.startAngle = self._getAngleFromDirection(startDirection, isClockwise)
        self.endAngle = self._getAngleFromDirection(endDirection, isClockwise)
        self.radians = self._getArcRadians(self.startAngle, self.endAngle, isClockwise)
        self.isClockwise = isClockwise
        self.radius = radius
        length = math.fabs(self.radians * radius)
        centerx = startx - radius * math.cos(self.startAngle)
        centery = starty - radius * math.sin(self.startAngle)
        endx = centerx + radius * math.cos(self.endAngle)
        endy = centery + radius * math.sin(self.endAngle)
        super().__init__(startx, starty, endx, endy, centerx, centery, length, width, startDirection, endDirection,
                         speedLimit)
        self.type = 'arc'

    @classmethod
    def continueLane(cls, lane: Lane, endDirection, radius, isClockwise, speedLimit=None):
        return cls(lane.endx, lane.endy, lane.endDirection, endDirection, radius, lane.width, isClockwise,
                   speedLimit if speedLimit else lane.speedLimit)

    def getStraightApproximationCoordinateList(self):
        result = []
        count = int(self.radians / (math.pi / 10))
        deltaAngle = 0 - self.radians / count if self.isClockwise else self.radians / count
        for i in range(count):
            startAngle = self.startAngle + deltaAngle * i
            endAngle = self.startAngle + deltaAngle * (i + 1)
            startx = self.centerx + self.radius * math.cos(startAngle)
            starty = self.centery + self.radius * math.sin(startAngle)
            endx = self.centerx + self.radius * math.cos(endAngle)
            endy = self.centery + self.radius * math.sin(endAngle)
            result.append((startx, starty, endx, endy))
        return result

    def getDirection(self, travel=0):
        if travel > self.length or travel < 0:
            return None
        travelAngle = travel / self.radius
        result = self.startDirection - travelAngle if self.isClockwise else self.startDirection + travelAngle
        if result < 0:
            return 2 * math.pi + result
        elif result > 2 * math.pi:
            return result - 2 * math.pi
        return result

    def getLocation(self, travel=0):
        if travel > self.length or travel < 0:
            return None, None
        deltaangle = travel / self.radius
        angle = self.startAngle - deltaangle if self.isClockwise else self.startAngle + deltaangle
        x = self.centerx + self.radius * math.cos(angle)
        y = self.centery + self.radius * math.sin(angle)
        return x, y

    def getBoundingBox(self):
        squad = quadrant(self.startAngle)
        assert (squad >= 0)
        equad = quadrant(self.endAngle)
        assert (equad >= 0)
        xmin = min(self.startx, self.endx)
        ymin = min(self.starty, self.endy)
        xmax = max(self.startx, self.endx)
        ymax = max(self.starty, self.endy)
        if self.isClockwise:
            temp = squad
            squad = equad
            equad = temp
        while squad != equad:
            axleAngle = squad * math.pi * 0.5
            x = self.centerx + self.radius * math.cos(axleAngle)
            y = self.centery + self.radius * math.sin(axleAngle)
            xmin = min(xmin, x)
            ymin = min(ymin, y)
            xmax = max(xmax, x)
            ymax = max(ymax, y)
            squad += 1
            squad = squad % 5
        return xmax, ymax, xmin, ymin

    def _getAngleFromDirection(self, direction: float, isClockwise: bool):
        angle = (direction + math.pi * 0.5) if isClockwise else (direction + math.pi * 1.5)
        modulo = int(angle / (2 * math.pi))
        if modulo >= 1:
            angle -= modulo * 2 * math.pi
        return angle

    def _getArcRadians(self, startAngle, endAngle, isClockwise):
        if not isClockwise:
            return endAngle - startAngle if startAngle <= endAngle else 2 * math.pi - (startAngle - endAngle)
        return 2 * math.pi - (endAngle - startAngle) if endAngle > startAngle else startAngle - endAngle


class StraightLane(Lane):
    def __init__(self, startx, starty, direction, length, width, speedLimit=60 / 3.6):
        if (direction >= math.pi * 2):
            direction = direction / 180 * math.pi
        endx = startx + length * math.cos(direction)
        endy = starty + length * math.sin(direction)
        centerx = (endx + startx) * 0.5
        centery = (endy + starty) * 0.5
        super().__init__(startx, starty, endx, endy, centerx, centery, length, width, direction, direction, speedLimit)
        self.limitingLines = []
        self.type = 'line'

    @classmethod
    def continueLane(cls, lane: Lane, length, speedLimit=None):
        return cls(lane.endx, lane.endy, lane.endDirection, length, lane.width,
                   speedLimit if speedLimit else lane.speedLimit)

    def inLane(self, x: float, y: float):
        a = self.endy - self.starty
        b = self.startx - self.endx
        # here we calculate lines that represent the all four sides of the lanes
        c1 = a * self.startx + b * self.starty


def quadrant(angle):
    if angle >= 0.0 and angle < math.pi / 2.0:
        return 1
    if angle >= math.pi / 2.0 and angle < math.pi:
        return 2
    if angle >= math.pi and angle < math.pi * 3.0 / 2.0:
        return 3
    if angle >= math.pi * 3.0 / 2.0 and angle < math.pi * 2:
        return 4
    return -1
