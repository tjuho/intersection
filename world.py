from lane import Lane
from car import Car
from route import Route
from trafficlight import Trafficlight
import uuid
'''Stores all the stuff in the world'''


class World:
    def __init__(self):
        '''
        Routes are stored this way:
        Route: {
        'cars': [Car],
        'trafficlights': [(Trafficlight, distanceFromStart, (x,y,direction))],
        'sensors': [(Sensor, distanceFromStart)]}
        '''
        self.id = str(uuid.uuid4())
        self.routes = []

    def to_dict(self):
        return {
            "id": self.id,
            "routes": [route.to_dict() for route in self.routes],
            "lanes": [lane.to_dict() for lane in self.getLanes()],
            "trafficlightsLocationsAndDirections": self.getTrafficlightsLocationsAndDirections(),
            "carsLocationsAndDirections": self.getCarsLocationsAndDirections(),
            "sensorsFired": [sensor.to_dict() for sensor in self.sensorsFired],
        }

    def moveTimestep(self, timestep):
        carsToRemove = []
        for route in self.routes:
            temp = route.getTrafficlightsLocationsAndDirections()
            for tl, _, _, _ in temp:
                tl.moveTimestep(timestep)
            for car in route.cars:
                car.moveTimestep(timestep)
                if car.distance >= route.totalTravelDistance:
                    carsToRemove.append(car)
        for car in carsToRemove:
            self.removeCar(car)

    def addRoute(self, route):
        if route not in self.routes:
            self.routes.append()

    '''
    Adds traffic light to given lane. If the yellowtime is None then we calculate it from the lane's speed limit.
    At the moment a lane can have only one trafficlight.
    '''

    def addTrafficlight(self, trafficlight: Trafficlight, lane: Lane, distancefromlanestart: float):
        for route in self.routes.keys():
            routedistance = self.calculateRouteDistanceFromLaneDistance(route, lane, distancefromlanestart)
            if routedistance is not None:
                x, y = lane.getLocation(distancefromlanestart)
                d = lane.getDirection(distancefromlanestart)
                newitem = (trafficlight, routedistance, (x, y, d))
                newtrafficlights = [newitem]
                if 'trafficlights' not in self.routes[route].keys():
                    self.routes[route]['trafficlights'] = []
                for ttrafficlight, distance, location in self.routes[route]['trafficlights']:
                    if trafficlight != ttrafficlight:
                        newtrafficlights.append((ttrafficlight, distance, location))
                self.routes[route]['trafficlights'] = newtrafficlights

    def addCar(self, car: Car, route: Route):
        car.timeFromLastSpeedChange = -1e-10  # this is some bug fix
        car.maxSpeed = route.getSpeedLimit()
        assert (route in self.routes.keys())
        if 'cars' not in self.routes[route].keys():
            self.routes[route]['cars'] = [car]
        else:
            cars = self.routes[route]['cars']
            cars.append(car)
            self.routes[route]['cars'] = cars

    def calculateRouteDistanceFromLaneDistance(self, route, lane, distancefromlanestart):
        if lane not in route.lanes:
            return None
        result = 0
        for tlane in route.lanes:
            if tlane == lane:
                result += distancefromlanestart
                break
            result += tlane.length
        return result

    def getOldestCar(self, route):
        assert (route in self.routes.keys())
        cars = self.routes[route]['cars']
        if len(cars) > 0:
            return self.routes[route]['cars'][0]
        return None

    def getNewestCar(self, route):
        assert (route in self.routes.keys())
        cars = self.routes[route]['cars']
        if len(cars) > 0:
            return self.routes[route]['cars'][-1]
        return None

    def removeCar(self, car: Car):
        for route in self.routes:
            if car in route.cars:
                route.cars.pop(car)
                break

    def getCarRoute(self, car: Car):
        for route in self.routes:
            if car in route.cars:
                return route

    def getRoutes(self):
        return self.routes

    def getCars(self, route: Route):
        return route.cars

    def getLanes(self):
        result = []
        for route in self.routes:
            result.extend(route.lanes)
        return result

    # def getSensorsLocations(self):
    #     result = []
    #     for route in self.routes.keys():
    #         if 'sensors' not in self.routes[route].keys(): continue
    #         sensors = self.routes[route]['sensors']
    #         for sensor in sensors:
    #             x, y, a = route.getLocationAndDirection(sensor.distance)
    #             if x is None or y is None:
    #                 print('problem with car', sensor)
    #             else:
    #                 result.append((sensor, x, y, a))
    #     return result

    def getNextNonGreenTrafficlightAndDistance(self, car: Car):
        route = self.getCarRoute(car)
        return route.getNextNonGreenTrafficlightAndDistance(car.distance)

    # def getNextNonGreenTrafficlightAndDistance(self, car: Car):
    #     route = self.getCarRoute(car)
    #     try:
    #         distance = route.getCurrentLane(car.distance)
    #         lanes = route.getLanesLeft(distance)
    #         lanePosition = route.getCurrentLaneDistanceCovered(distance)
    #         trafficlightitems = self.routes[route]['trafficlights']
    #         distance = None
    #         trafficlight = None
    #         for tl, tld, _ in trafficlightitems:
    #             delta = tld - car.distance
    #             if delta >= 0 and (distance is None or distance > delta) and tl.color != 'green':
    #                 distance = delta
    #                 trafficlight = tl
    #         return trafficlight, distance
    #     except KeyError:
    #         return None, None

    def getRoutesWithCommonLane(self, route: Route):
        result = []
        for aroute in self.routes:
            if route != aroute:
                if bool(set(route.lanes) & set(aroute.lanes)):
                    result.append(aroute)
        return result

    '''
    Gets the next car ahead.
    Assumes that the next car is placed to the route just before this one (e.g. cars at the same route can't overtake. 
    This might not be true in the future because routes might have common.
    '''

    def getNextCarAheadAndDistance(self, car: Car) -> (Car, float):
        route = self.getCarRoute(car)
        commonRoutes = self.getRoutesWithCommonLane(route) # not implemented yet
        cars = self.getCars(route)
        cars.pop(car)
        minDistance = None
        result = None
        for acar in cars:
            diff = acar.distance - car.distance
            if diff > 0 and (minDistance is not None or minDistance > diff):
                result = acar
                minDistance = diff
        return result, minDistance

    def getCarsLocationsAndDirections(self):
        result = []
        for route in self.routes:
            result.extend(route.getCarsLocationsAndDirections())
        return result

    def getTrafficlightsLocationsAndDirections(self):
        result = []
        for route in self.routes:
            result.extend(route.getTrafficlightsLocationsAndDirections())
        return result

    def getBoundingBox(self):
        #
        lanes = self.getLanes()
        if len(lanes) == 0:
            return None, None, None, None
        xmax = -1e9
        ymax = -1e9
        xmin = 1e9
        ymin = 1e9
        for lane in self.getLanes():
            ux, uy, lx, ly = lane.getBoundingBox()
            if ux < lx:
                temp = ux
                ux = lx
                lx = temp
            if uy < ly:
                temp = uy
                uy = ly
                ly = temp
            xmax = max(xmax, ux)
            ymax = max(ymax, uy)
            xmin = min(xmin, lx)
            ymin = min(ymin, ly)
        return xmax, ymax, xmin, ymin

