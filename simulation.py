from world import World
from ai import AI
from lane import *
from trafficlight import Trafficlight
from car import Car
from trafficlightcontroller import TrafficlightController
from route import Route
from random import randint

'''Simulations that control the traffic lights and car spawning'''


class Simulation:
    def __init__(self):
        self.world = World()
        self.ai = AI(self.world)
        self.trafficlightControllers = []
        self.laneInputs = []
        self.sensors = []

    def to_dict(self):
        return {
            "world": self.world.to_dict(),
            "ai": self.ai.to_dict(),
            "trafficlightControllers": [controller.to_dict() for controller in self.trafficlightControllers],
            "laneInputs": self.laneInputs,
            "sensors": self.sensors,
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

    # simulation.py

class DummylightsTwoCrossings(Simulation):
    def __init__(self):
        super().__init__()
        self.timeToTrafficlightControllerStateChange = [randint(15, 60), randint(15, 60)]
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
        # Existing setup code...
        # When adding to routeCarSpawn, use route objects as keys
        # This will be converted to string keys in to_dict()
        redtogreendelay = 3
        yellowtime = 4
        inputsensorfromtrafficlight = 200
        outputsensorfromtrafficlight = 0
        lanelength = 600
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

        route1a = Route([lane1a1, lane1a2])
        route1b = Route([lane1b1, lane1b2])
        route2a = Route([lane2a])
        route2b = Route([lane2b])
        route3a = Route([lane3a])
        route3b = Route([lane3b])

        self.world.addRoute(route1a)
        self.world.addRoute(route1b)
        self.world.addRoute(route2a)
        self.world.addRoute(route2b)
        self.world.addRoute(route3a)
        self.world.addRoute(route3b)

        # Initialize traffic lights and controllers as before...

        self.setupSpawntimes()

    def setupSpawntimes(self):
        carsperminute = [25, 15]
        avgspawnrate = 8
        spawnValues = calculateCarSpawnDistribution(avgspawnrate, carsperminute, 6)
        routes = self.world.getRoutes()
        for route in routes:
            spawntimes = [60.0 / x for x in spawnValues]
            if route not in self.routeCarSpawn.keys():
                self.routeCarSpawn[route] = {}
            self.routeCarSpawn[route]['spawntimes'] = spawntimes
            nextspawntime = spawntimes[randint(0, len(self.routeCarSpawn[route]['spawntimes']) - 1)]
            self.routeCarSpawn[route]['spawntime'] = nextspawntime

    def updateWorldState(self, timestep):
        # does not change the trafficlight state
        # spawn car
        for route in self.routeCarSpawn.keys():
            tospawn = self.routeCarSpawn[route]['spawntime']
            tospawn -= timestep
            if tospawn > 0:
                self.routeCarSpawn[route]['spawntime'] = tospawn
            else:  # create a new car to the route
                lastcar = self.world.getNewestCar(route)
                if lastcar is not None and lastcar.distance < 10:
                    continue
                nextspawntime = self.routeCarSpawn[route]['spawntimes'][
                    randint(0, len(self.routeCarSpawn[route]['spawntimes']) - 1)]
                self.routeCarSpawn[route]['spawntime'] = nextspawntime + tospawn
                speed = route.getSpeedLimit()
                if lastcar is not None:
                    lspeed = lastcar.getSpeed()
                    speed = min(speed,
                                math.sqrt(lspeed * lspeed - 2 * lastcar.preferredDeceleration * lastcar.distance))
                car = Car(speed)
                self.world.addCar(car, route)
                carahead, dist = self.world.getNextCarAheadAndDistance(car)
                if dist is not None:
                    distmargin = car.calculateDistanceMargin(speed)
                    if dist < distmargin:
                        # maybe we should stop the simulation
                        print('too close to car ahead')
                        pass
                    elif dist < distmargin * 1.5 and car.getSpeed() * 0.99 > carahead.getSpeed():
                        # here the car ahead speed already drops so the queue end is near
                        pass
        # the trafficlights are constant time controlled
        for i, time in enumerate(self.timeToTrafficlightControllerStateChange):
            newtime = time - timestep
            if newtime <= 0:
                newtime = randint(15, 60)
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
    return spawnTimesDistribution[randint(0, len(spawnTimesDistribution) - 1)]


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
