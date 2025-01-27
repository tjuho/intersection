from world import World
from ai import AI
from lane import *
from trafficlight import Trafficlight
from car import Car
from trafficlightcontroller import TrafficlightController
from route import Route
import utils
import random
'''Simulations that control the traffic lights and car spawning'''


class Simulation:
    def __init__(self):
        self.world = World()
        self.ai = AI(self.world)
        self.trafficlightControllers = []

    def to_dict(self):
        return {
            "world": self.world.to_dict(),
            "ai": self.ai.to_dict(),
            "trafficlightControllers": [controller.to_dict() for controller in self.trafficlightControllers],
        }

    def moveTimestep(self, timestep):
        self.updateWorldState(timestep)
        self.ai.adjust()
        self.world.moveTimestep(timestep)

    '''
    here we put how to update the world.
    Spawn new cars and change trafficlight color
    '''

    def updateWorldState(self, timestep):
        pass

class DummylightsTwoCrossings(Simulation):
    def __init__(self):
        super().__init__()
        self.timeToTrafficlightControllerStateChange = [random.randint(15, 60), random.randint(15, 60)]
        self.routeCarSpawn = {}
        self.setup()

    def to_dict(self):
        # Start with the base class's dictionary
        base_dict = super().to_dict()

        # Create a serializable version of routeCarSpawn with string keys
        serializable_routeCarSpawn = {
            route.id: spawn_info for route, spawn_info in self.routeCarSpawn.items()
        }

        # Update the base dictionary with subclass-specific data
        base_dict.update({
            "timeToTrafficlightControllerStateChange": self.timeToTrafficlightControllerStateChange,
            "routeCarSpawn": serializable_routeCarSpawn,
        })

        return base_dict

    def setup(self):
        redtogreendelay = 9
        yellowtime = 8
        inputsensorfromtrafficlight = 200
        outputsensorfromtrafficlight = 0
        lanelength = 400
        trafficlightmargin = 3
        cx = lanelength * 0.5
        cy = lanelength * 0.5
        startx1 = 0
        starty2 = 0
        lanewidth = 3

        lane1a1 = StraightLane(startx1, cy - lanewidth * 0.5, 0, lanelength, lanewidth, 60 / 3.6)
        lane1a2 = StraightLane.continueLane(lane1a1, lanelength)
        lane1b1 = StraightLane(startx1 + lanelength * 2, cy + lanewidth * 0.5, 180, lanelength, lanewidth, 60 / 3.6)
        lane1b2 = StraightLane.continueLane(lane1b1, lanelength)
        lane2a = StraightLane(cx + lanewidth * 0.5, starty2, 90, lanelength, lanewidth, 60 / 3.6)
        lane2b = StraightLane(cx - lanewidth * 0.5, starty2 + lanelength, 270, lanelength, lanewidth, 60 / 3.6)
        lane3a = StraightLane(cx + lanewidth * 0.5 + lanelength, starty2, 90, lanelength, lanewidth, 60 / 3.6)
        lane3b = StraightLane(cx - lanewidth * 0.5 + lanelength, starty2 + lanelength, 270, lanelength, lanewidth,
                              60 / 3.6)

        route1a = Route([lane1a1, lane1a2], 8)
        route1b = Route([lane1b1, lane1b2], 8)
        route2a = Route([lane2a],8)
        route2b = Route([lane2b], 8)
        route3a = Route([lane3a], 8)
        route3b = Route([lane3b], 8)

        self.world.addRoute(route1a)
        self.world.addRoute(route1b)
        self.world.addRoute(route2a)
        self.world.addRoute(route2b)
        self.world.addRoute(route3a)
        self.world.addRoute(route3b)

        tl1a1 = Trafficlight(redtogreendelay, yellowtime, 'green', lanelength * 0.5 - trafficlightmargin)
        tl1a2 = Trafficlight(redtogreendelay, yellowtime, 'green', lanelength * 0.5 - trafficlightmargin)
        tl1b1 = Trafficlight(redtogreendelay, yellowtime, 'green', lanelength * 0.5 - trafficlightmargin)
        tl1b2 = Trafficlight(redtogreendelay, yellowtime, 'green', lanelength * 0.5 - trafficlightmargin)
        tl2a = Trafficlight(redtogreendelay, yellowtime, 'red', lanelength * 0.5 - trafficlightmargin)
        tl2b = Trafficlight(redtogreendelay, yellowtime, 'red', lanelength * 0.5 - trafficlightmargin)
        tl3a = Trafficlight(redtogreendelay, yellowtime, 'red', lanelength * 0.5 - trafficlightmargin)
        tl3b = Trafficlight(redtogreendelay, yellowtime, 'red', lanelength * 0.5 - trafficlightmargin)
        self.trafficlightControllers.append(
            TrafficlightController([tl1a1, tl1b2, tl2a, tl2b], [[1, 1, 0, 0], [0, 0, 1, 1]]))
        self.trafficlightControllers.append(
            TrafficlightController([tl1a2, tl1b1, tl3a, tl3b], [[1, 1, 0, 0], [0, 0, 1, 1]]))
        lane1a1.addTrafficlight(tl1a1)
        lane1a2.addTrafficlight(tl1a2)
        lane1b1.addTrafficlight(tl1b1)
        lane1b2.addTrafficlight(tl1b2)
        lane2a.addTrafficlight(tl2a)
        lane2b.addTrafficlight(tl2b)
        lane3a.addTrafficlight(tl3a)
        lane3b.addTrafficlight(tl3b)
        self.setupSpawntimes()

    def setupSpawntimes(self):
        carsperminute = [25, 15]
        avgspawnrate = 7
        spawnValues = calculateCarSpawnDistribution(avgspawnrate, carsperminute, 6)
        routes = self.world.getRoutes()
        for route in routes:
            spawntimes = [60.0 / x for x in spawnValues]
            if route not in self.routeCarSpawn.keys():
                self.routeCarSpawn[route] = {}
            self.routeCarSpawn[route]['spawntimes'] = spawntimes
            nextspawntime = spawntimes[random.randint(0, len(self.routeCarSpawn[route]['spawntimes']) - 1)]
            self.routeCarSpawn[route]['spawntime'] = nextspawntime

    def updateWorldState(self, timestep):
        # spawn car
        for route in self.world.routes:
            if utils.shouldTriggerEvent(timestep, route.carSpawnRate):
                route.carSpawnQueue += 1
            lastCar, minDistance  = route.getNewestCarAndDistance()
            speed = route.getSpeedLimit() if lastCar is None else lastCar.getSpeed()
            margin = utils.calculateDistanceMargin(speed)
            if route.carSpawnQueue > 0 and (lastCar is None or minDistance >= margin):
                route.addCar(Car(speed))
                route.carSpawnQueue -= 1
        # the trafficlights cycle in constant time periods
        for i, time in enumerate(self.timeToTrafficlightControllerStateChange):
            newtime = time - timestep
            if newtime <= 0:
                newtime = random.randint(15, 60)
                self.trafficlightControllers[i].cycle()
            self.timeToTrafficlightControllerStateChange[i] = newtime

'''
Calculates the tail of the discrete distribution for spawning the cars. The values can be cars per second or minute. 
The values to be calculated are for the tail of the distribution as the front of the distribution is provided with 
@initialSpawnTimeList. The discrete values of the tail of the distribution are equal
'''


def calculateCarSpawnDistribution(avgSpawnTime, initialSpawnTimeList, newSpawnTimeCount):
    y = (avgSpawnTime * (len(initialSpawnTimeList) + newSpawnTimeCount) - sum(initialSpawnTimeList)) / newSpawnTimeCount
    assert (y > 0)
    for i in range(newSpawnTimeCount):
        initialSpawnTimeList.append(y)
    return initialSpawnTimeList


def calculateTimeToNextCarSpawn(spawnTimesDistribution):
    return spawnTimesDistribution[random.randint(0, len(spawnTimesDistribution) - 1)]


def getUnityMatrix(size):
    result = []
    for r in range(size):
        row = []
        for c in range(size):
            if c == r:
                row.append(1)
            else:
                row.append(0)
        result.append(row)
    return result
