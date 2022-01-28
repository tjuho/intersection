from lane import Lane
from car import Car
from route import Route
from trafficlight import Trafficlight

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
        self.routes = {}
        self.sensorsFired = []
        self.sensorRouteDistances = {}  # indexing a bit here

    def moveTimestep(self, timestep):
        carsToRemove = []
        for route in self.routes.keys():
            dic = self.routes[route]
            if 'trafficlights' in self.routes[route].keys():
                for trafficlight, _, _ in self.routes[route]['trafficlights']:
                    trafficlight.moveTimestep(timestep)
            if 'cars' in self.routes[route].keys():
                for car in self.routes[route]['cars']:
                    d1 = car.distance
                    car.moveTimestep(timestep)
                    d2 = car.distance
                    if car.distance >= route.totalTravelDistance:
                        carsToRemove.append(car)
                    if 'sensors' in self.routes[route].keys():
                        for sensor, sensorroutedistance in self.routes[route]['sensors']:
                            if sensorroutedistance <= d1 and sensorroutedistance > d2:
                                speed1 = car.getSpeed(-timestep)
                                speed2 = car.getSpeed()
                                sensor.addDetection(0.5 * (speed1 + speed2), (speed2 - speed1) / timestep, car.length)
        for car in carsToRemove:
            self.removeCar(car)
        for route in self.routes.keys():
            dic = self.routes[route]
            if 'sensors' in self.routes[route].keys():
                for sensor, _ in self.routes[route]['sensors']:
                    sensor.resetDetections()

    def addRoute(self, route):
        self.routes[route] = {}
        self.routes[route]['cars'] = []
        self.routes[route]['trafficlights'] = []
        self.routes[route]['sensors'] = []

    def addSensor(self, sensor, lane, distancefromlanestart):
        # first check that the lane is in some route
        routefound = False
        for route in self.routes.keys():
            routedistance = self.calculateRouteDistanceFromLaneDistance(route, lane, distancefromlanestart)
            if routedistance is not None:
                newsensors = [(sensor, routedistance)]
                if 'sensors' not in self.routes[route].keys():
                    self.routes[route]['sensors'] = []
                for tsensor, distance in self.routes[route]['sensors']:
                    if sensor != tsensor:
                        newsensors.append((tsensor, distance))
                self.routes[route]['sensors'] = newsensors

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
        route = self.getCarRoute(car)
        assert (route in self.routes.keys())
        remaining = [x for x in self.routes[route]['cars'] if x is not car]
        self.routes[route]['cars'] = remaining

    def getCarRoute(self, car: Car):
        for route in self.routes.keys():
            if 'cars' in self.routes[route].keys():
                if car in self.routes[route]['cars']:
                    return route

    def getRoutes(self):
        if self.routes.keys() is None: return []
        return list(self.routes.keys())

    def getCars(self, route: Route):
        routedict = self.routes[route]
        if routedict is None: return []
        if 'cars' not in routedict: return []
        return routedict['cars']

    def getLanes(self):
        result = []
        for route in self.routes.keys():
            temp = [x for x in route.lanes if x not in result]
            result.extend(temp)
        return result

    def getSensorsLocations(self):
        result = []
        for route in self.routes.keys():
            if 'sensors' not in self.routes[route].keys(): continue
            sensors = self.routes[route]['sensors']
            for sensor in sensors:
                x, y, a = route.getLocationAndDirection(sensor.distance)
                if x is None or y is None:
                    print('problem with car', sensor)
                else:
                    result.append((sensor, x, y, a))
        return result

    def getNextNonGreenTrafficlightAndDistance(self, car: Car):
        route = self.getCarRoute(car)
        try:
            trafficlightitems = self.routes[route]['trafficlights']
            distance = None
            trafficlight = None
            for tl, tld, _ in trafficlightitems:
                delta = tld - car.distance
                if delta >= 0 and (distance is None or distance > delta) and tl.color != 'green':
                    distance = delta
                    trafficlight = tl
            return trafficlight, distance
        except KeyError:
            return None, None

    def getRoutesWithCommonLane(self, route: Route):
        result = []
        for temp in self.routes.keys():
            if temp != route and any(item in temp.lanes for item in route.lanes):
                result.append(temp)
        return result

    '''
    Gets the next car ahead.
    Assumes that the next car is placed to the route just before this one (e.g. cars at the same route can't overtake. 
    This might not be true in the future because routes might share lanes in the future.
    '''

    def getNextCarAheadAndDistance(self, car: Car) -> (Car, float):
        for route in self.routes.keys():
            if 'cars' in self.routes[route].keys():
                cars = self.routes[route]['cars']
                if car in cars:
                    i = cars.index(car)
                    if i > 0:
                        ahead = cars[i - 1]
                        distance = ahead.distance - car.distance
                        #                assert (distance > 0)
                        return ahead, distance
                    elif i == 0:
                        return None, None
        return None, None

    def getCarsLocationsAndDirections(self):
        result = []
        for route in self.routes.keys():
            if 'cars' not in self.routes[route].keys(): continue
            cars = self.routes[route]['cars']
            for car in cars:
                x, y, a = route.getLocationAndDirection(car.distance)
                if x is None or y is None:
                    print('problem with car', car)
                else:
                    result.append((car, x, y, a))
        return result

    def getTrafficlightsLocationsAndDirections(self):
        result = []
        for route in self.routes.keys():
            if 'trafficlights' not in self.routes[route].keys():
                continue
            trafficlightitems = self.routes[route]['trafficlights']
            for trafficlight, distance, location in trafficlightitems:
                x, y, direction = location
                result.append((trafficlight, x, y, direction))
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

