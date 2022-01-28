import math
from world import World
from route import Route
from trafficlight import Trafficlight
from car import Car, SpeedChange


class AI:
    '''Car logic'''

    def __init__(self, world: World):
        self.world = world
        self._carAiContainer = CarAIContainer()
        self.debug = {}
        self.debug['stack'] = {}
        self.debug['stack']['last added'] = ''

    def adjust(self):
        for route in self.world.getRoutes():
            self._adjustRoute(route)

    def _adjustRoute(self, route: Route):
        cars = self.world.getCars(route)
        for car in cars:
            self._adjustCar(car, route)

    def _adjustCar(self, car: Car, route: Route):
        currentspeed = car.getSpeed()
        carahead, distancetocarahead = self.world.getNextCarAheadAndDistance(car)
        trafficlight, distancetotrafficlightahead = self.world.getNextNonGreenTrafficlightAndDistance(car)
        reactiondistance = self._calculateReactionDistance(currentspeed)
        currentlane = route.getCurrentLane(car.distance)
        speedlimit = currentlane.getSpeedlimit()
        speedchangelist = []
        if carahead is not None and distancetocarahead < reactiondistance:
            previoustargetcarahead = self._carAiContainer.getTargetCar(car)
            previoustargettrafficlight = self._carAiContainer.getTargetTrafficlight(car)
            if carahead != previoustargetcarahead or carahead.timeFromLastSpeedChange <= car.timeFromLastSpeedChange or (
                    trafficlight is not None and trafficlight != previoustargettrafficlight and distancetotrafficlightahead < reactiondistance):
                speedchange = self._speedChangesToAdjustToCarAhead(carahead, currentspeed, speedlimit,
                                                                   distancetocarahead, car.preferredAcceleration,
                                                                   car.preferredDeceleration,
                                                                   car.calculateDistanceMargin)
                speedchangelist.append(speedchange)
            self._carAiContainer.setTargetCar(car, carahead)
        else:
            self._carAiContainer.setTargetCar(car, None)
        if trafficlight is not None and distancetotrafficlightahead < reactiondistance:
            if len(speedchangelist) > 0 or self._carAiContainer.getTargetTrafficlight(car) != trafficlight:
                if trafficlight.color == 'red':
                    speedchange = self._speedChangesToAdjustToTrafficlight(currentspeed, speedlimit,
                                                                           distancetotrafficlightahead,
                                                                           car.preferredAcceleration,
                                                                           car.preferredDeceleration,
                                                                           car.zeromargin)
                    speedchangelist.append(speedchange)
                elif trafficlight.color == 'yellow':
                    dtemp = []
                    dtemp.append(car.getTravelDistance(trafficlight.timeToNextColorChange))
                    if len(speedchangelist) > 0:
                        sc = min(speedchangelist)
                        dtemp.append(sc.getTravelDistance(trafficlight.timeToNextColorChange))
                    if min(dtemp) < distancetotrafficlightahead:
                        speedchange = self._speedChangesToAdjustToTrafficlight(currentspeed, speedlimit,
                                                                               distancetotrafficlightahead,
                                                                               car.preferredAcceleration,
                                                                               car.preferredDeceleration,
                                                                               car.zeromargin)
                        speedchangelist.append(speedchange)
            self._carAiContainer.setTargetTrafficlight(car, trafficlight)
        else:
            self._carAiContainer.setTargetTrafficlight(car, None)
        if len(speedchangelist) > 0:
            minspeedchange = min(speedchangelist)
            car.addSpeedChanges(minspeedchange)
            car.debug = self.debug['stack']['last added']
        if not (carahead is not None and distancetocarahead < reactiondistance) and not (
                trafficlight is not None and distancetotrafficlightahead < reactiondistance):
            car.setSpeed(speedlimit, 0.2)
        ok = car.testSpeedIntegrity()
        if not ok:
            msg = f'{car}\n['
            assert ()

    def _speedChangesToAdjustToCarAhead(self, carahead: Car, initialspeed: float, speedlimit: float, distance: float,
                                        preferredacceleration: float, preferreddeceleration: float, marginfunc):
        vt, dt, tt = carahead.getTargetSpeedAndDistanceAndTimeToIt()
        margin = marginfunc(vt)
        speedchange = self._speedChangeStack(initialspeed, vt, speedlimit, distance - margin - carahead.halflength, dt,
                                             tt, preferredacceleration, preferreddeceleration)
        speedintersectiontimes = carahead.calculateSpeedChangeSpeedIntersectionTimes(speedchange, False)
        starttime = 0.0
        speedintersectiontimes.sort()
        count = 0
        while len(speedintersectiontimes) > 0 and starttime < max(speedintersectiontimes):
            count += 1
            endtime = speedintersectiontimes.pop(0)
            if endtime <= starttime or math.isclose(endtime, starttime, abs_tol=1e-7):
                continue
            carbehindtraveldistance = speedchange.getTravelDistance(endtime, starttime)
            caraheadtraveldistance = carahead.getTravelDistance(endtime, starttime)
            vtcar = carahead.getSpeed(endtime)
            margin = marginfunc(vtcar)
            tempdist = distance + caraheadtraveldistance - carbehindtraveldistance - carahead.halflength - margin
            if tempdist >= 0:
                continue
            ttcar = endtime - starttime
            visc = speedchange.getSpeed(starttime)
            distancebetween = distance + carahead.getTravelDistance(starttime) - speedchange.getTravelDistance(
                starttime)
            speedchangefront = self._speedChangeStack(visc, vtcar, speedlimit,
                                                      distancebetween - margin - carahead.halflength,
                                                      caraheadtraveldistance, ttcar,
                                                      preferredacceleration, preferreddeceleration)
            speedchange.addSpeedChange(speedchangefront, starttime)
            vt, dt, tt = carahead.getTargetSpeedAndDistanceAndTimeToIt(endtime)
            margin = marginfunc(vt)
            vi = speedchange.getSpeed(endtime)
            distancebetween = distance + carahead.getTravelDistance(endtime) - speedchange.getTravelDistance(endtime)
            speedchangerear = self._speedChangeStack(vi, vt, speedlimit, distancebetween - margin - carahead.halflength,
                                                     dt, tt, preferredacceleration,
                                                     preferreddeceleration)
            speedchange.addSpeedChange(speedchangerear, endtime)
            tempitimes = carahead.calculateSpeedChangeSpeedIntersectionTimes(speedchange, False)
            speedintersectiontimes = list(filter(lambda x: x > endtime, tempitimes))
            speedintersectiontimes.sort()
            starttime = endtime
        return speedchange

    def _speedChangesToAdjustToTrafficlight(self, initialspeed: float, speedlimit: float,
                                            distance: float, preferredacceleration: float, preferreddeceleration: float,
                                            margin: float):

        speedchange = self._speedChangeStack(initialspeed, 0, speedlimit, distance - margin, 0, 0,
                                             preferredacceleration,
                                             preferreddeceleration)
        return speedchange

    def _speedChangeStack(self, vi, vt, vl, d, dt, tt, ap, an):
        vt = min(vl, vt)
        speedchange = SpeedChange(vi)
        if vt == vi and (math.isclose(vi * tt, dt + d, abs_tol=5e-3) or (d + dt < 0 and vt == 0)):
            speedchange.addAcceleration(0, tt)
            self._addDebugProfileStackCount('no change 1')
            return speedchange

        if vt == vi and d + dt < 0 and vt == 0:
            speedchange.addAcceleration(0, tt)
            self._addDebugProfileStackCount('no change 2')
            return speedchange

        vf = self._calculateFloorSpeed(vi, vt, d + dt, tt, ap, an)
        # seems that these two are not used at the moment
        if vf is not None and vf < vt and vf < vi and vf >= 0:
            t1 = (vf - vi) / an
            t2 = (vt - vf) / ap
            speedchange.addAcceleration(an, t1)
            speedchange.addAcceleration(ap, t2, tt - t2)
            self._addDebugProfileStackCount('_calculateFloorSpeed')
            return speedchange

        vr = self._calculateRoofSpeed(vi, vt, d + dt, tt, ap, an)
        if vr is not None and vr > vt and vr > vi and (math.isclose(vl, vr, abs_tol=1e-6) or vr < vl):
            t1 = (vr - vi) / ap
            t2 = (vt - vr) / an
            speedchange.addAcceleration(ap, t1)
            speedchange.addAcceleration(an, t2, tt - t2)
            self._addDebugProfileStackCount('_calculateRoofSpeed')
            return speedchange

        vm = self._calculateHighMidSpeed(vi, vt, dt + d, tt, ap, an)
        if vm is not None and vm > vi and vm > vt and (math.isclose(vl, vm, abs_tol=1e-6) or vm < vl):
            t1 = (vm - vi) / ap
            t2 = (vt - vm) / an
            tc = tt - t1 - t2
            speedchange.addAcceleration(ap, t1)
            speedchange.addAcceleration(an, t2, t1 + tc)
            self._addDebugProfileStackCount('_calculateHighMidSpeed')
            return speedchange

        vc = self._calculateMidSpeed(vi, vt, d + dt, tt, ap, an)
        if vc is not None and vc <= vl and vc > vt and vc > vi:
            t1 = (vc - vi) / ap
            t2 = (vt - vc) / an
            if tt <= t1 + t2:
                speedchange.addAcceleration(ap, t1)
                speedchange.addAcceleration(an, t2, t1)
                self._addDebugProfileStackCount('_calculateMidSpeed')
                return speedchange

        tc = self._calculateSpeedLimitedConstantSpeedTime(vi, vt, vl, d + dt, tt, ap, an)
        if tc is not None and tc > 0 and vi < vl:
            t1 = (vl - vi) / ap
            t2 = (vt - vl) / an
            speedchange.addAcceleration(ap, t1)
            speedchange.addAcceleration(an, t2, t1 + tc)
            self._addDebugProfileStackCount('_calculateSpeedLimitedConstantSpeedTime')
            return speedchange

        vm, t1, t2 = self._calculateLowMidSpeedWithEqualAccelerations(vi, vt, d + dt, tt)
        # this functions that don't take into account preferred accelerations might cause too high accelerations
        # These functions prevent crashes though
        if vm is not None and vm < vt - 1e-6 and vm < vi - 1e-6:
            a1 = (vm - vi) / t1
            a2 = (vt - vm) / t2
            speedchange.addAcceleration(a1, t1)
            speedchange.addAcceleration(a2, t2, t1)
            self._addDebugProfileStackCount('_calculateLowMidSpeedWithEqualAccelerations')
            return speedchange

        items = self._calculateANASpeeditems(vi, vt, dt + d, tt)
        if items is not None:
            speedchange.addSpeedItems(items)
            self._addDebugProfileStackCount('_calculateANASpeeditems')
            return speedchange

        items = self._calculateACASpeeditems(vi, vt, vl, d + dt, tt, ap, an)
        if items is not None:
            speedchange.addSpeedItems(items)
            self._addDebugProfileStackCount('_calculateACASpeeditems')
            return speedchange

        t1 = self._calculateLinearAccelerationTime(vi, vt, dt + d, tt)
        if t1 is not None and t1 > 0 and (t1 >= tt or math.isclose(tt, t1, abs_tol=1e-3)):
            a = (vt - vi) / t1
            speedchange.addAcceleration(a, t1)
            self._addDebugProfileStackCount('_calculateLinearAccelerationTime')
            return speedchange

        a = ap if vt > vi else an
        t1 = self._calculateTimeFromConstantSpeedToConstantAcceleration(vi, vt, a, dt + d, tt)
        if t1 is not None and t1 > 0:
            t2 = (vt - vi) / a
            speedchange.addAcceleration(a, t2, t1)
            t3 = tt - t1 - t2
            if t3 > 0:
                speedchange.addAcceleration(0, t3, t1 + t2)
            self._addDebugProfileStackCount('_calculateTimeFromConstantSpeedToConstantAcceleration')
            return speedchange

        if (vt >= vl or math.isclose(vt, vl, abs_tol=1e-5)) and vi < vl:
            t1 = (vl - vi) / ap
            speedchange.addAcceleration(ap, t1)
            self._addDebugProfileStackCount('vt >= vl')
            return speedchange

        self._addDebugProfileStackCount('no match no change')
        return speedchange

    '''
    Calculates the linear acceleration. The acceleration time needs to be same or higher with @timetotargetspeed
    '''

    def _calculateLinearAccelerationTime(self, currentspeed, targetspeed, distance, timetotargetspeed):
        if targetspeed == currentspeed: return 0
        accelerationtime = 2 * (distance - targetspeed * timetotargetspeed) / (currentspeed - targetspeed)
        return accelerationtime

    '''
    Calculates mid speed with equal acceleration and deceleration (a2 == -a1).
    The mid speed needs to be lower than initial speed and target speed. e.g. \/.
    vm < vi and vm < vt. 
    The resulting speed profile is of equal time as the time to target speed @t. This ensures that there is no
    overtaking when adjust to the car in front
    '''

    def _calculateLowMidSpeedWithEqualAccelerations(self, vi, vt, d, t):
        if t == 0: return None, None, None
        a = -2
        b = 4 * d / t
        c = vi * vi + vt * vt - 2 * d / t * (vi + vt)
        try:
            vm = (-b + math.sqrt(b * b - 4 * a * c)) * 0.5 / a
            vm2 = (-b - math.sqrt(b * b - 4 * a * c)) * 0.5 / a
            if vm > vi or vm > vt or vm < 0:
                return None, None, None
            try:
                t1 = t / (1 + (vt - vm) / (vi - vm))
                t2 = t - t1
                return vm, t1, t2
            except ZeroDivisionError:
                return None, None, None
        except ValueError:
            return None, None, None

    '''
    Calculates "acceleration stop acceleration" speed items.
    This profile might be unrealistic
    '''

    def _calculateANASpeeditems(self, vi, vt, d, t):
        if d == 0: return None
        if not vi > 0: return None
        a = (vi * vi + vt * vt) / (2 * d)
        t1 = vi / a
        t2 = vt / a
        ts = t - t1 - t2
        if ts < 0 or t1 < 0 or t2 < 0:
            return None
        if a > 8:
            print('fix too high acceleration')
        return [(0, t1, 0), (vt, t2, t1 + ts)]

    '''
    Calculates the speed items that have equal accelerations and limited constant speed.
    '''

    def _calculateSpeedItemTimesWithSpeedLimit(self, vi, vt, vl, d, t):
        try:
            a = (-2 * vl * vl - vi * vi - vt * vt + 2 * vi * vl + 2 * vt * vl) / (2 * d - 2 * vl * t)
            t1 = (vl - vi) / a
            t2 = (vl - vt) / a
            tc = t - t1 - t2
            td = 0.5 * (vl + vi) * t1 + (t - t1 - t2) * vl + 0.5 * (vl + vt) * t2
            # calculate extra constant speed time because limiting the mid speed cuts the total distance
            return t1, tc, t2
        except ZeroDivisionError:
            return -1, -1, -1

    '''
    Calculates the constant speed before acceleration to match the given time and distance.
    The time and distance need to be inside boundaries which need to be calculated first. 
    '''

    def _calculateTimeFromConstantSpeedToConstantAcceleration(self, vi, vt, a, d, tt):
        if vi == vt: return 0
        accelerationtime = (vt - vi) / a
        accelerationdistance = (vt * vt - vi * vi) / 2 / a
        timeleft = tt - accelerationtime
        distanceleft = d - timeleft * vt - accelerationdistance
        t1 = distanceleft / (vi - vt)
        return t1

    '''
    Calculates mid speed and duration in a rare case that the times for both profile to the target speed are same
    In this case timeToTargetSpeed @tt has to be the same as profile time (t1+tc+t2)
    '''

    def _calculateHighMidSpeed(self, vi, vt, d, tt, ap, an):
        try:
            try:
                a = 1 / an - 1 / ap
                b = 2 * tt + 2 * vi / ap - 2 * vt / an
                c = -2 * d - vi * vi / ap + vt * vt / an
                vc = 0.5 * (-b + math.sqrt(b * b - 4 * a * c)) / a
                r2 = 0.5 * (-b - math.sqrt(b * b - 4 * a * c)) / a
                if vc < 0: return None
                t1 = (vc - vi) / ap
                t2 = (vt - vc) / an
                tc = tt - t1 - t2
                return vc
            except ZeroDivisionError as e:
                return None
        except ValueError as e:
            return None

    def _calculateCASpeeditems(self, vi, vt, a, t, d):
        t2 = (vt - vi) / a
        tc = (d - 0.5 * (vi + vt) * t2) / vi
        tce = self._calculateExtraConstantSpeedTimeBetweenAccelerations(vt, vi, tc + t2, t)
        tc += tce
        if tc >= 0 and t2 > 0:
            return [(vt, t2, tc)]
        return None

    '''
    Calculates the speed items for profile that accelerates then constant speed and then acceleration again. 
    '''

    def _calculateACASpeeditems(self, vi, vt, vl, d, t, a1, a2):
        t1 = (vl - vi) / a1
        t2 = (vt - vl) / a2
        if t1 <= 0 or t2 <= 0:
            return None
            # raise Exception(f'input values: {vi} {vt} {vl} {d} {a1} {a2}')
        tc = (d - (vl * vl - vi * vi) * 0.5 / a1 - (vt * vt - vl * vl) * 0.5 / a2) / vl
        tce = self._calculateExtraConstantSpeedTimeBetweenAccelerations(vt, vl, t1 + t2 + tc, t)
        if tce is not None and tc + tce >= 0: return [(vl, t1, 0), (vt, t2, t1 + tc + tce)]
        # try to calculate mid speed with distance only first
        vm = self._calculateMidSpeedWithDistanceOnly(vi, vt, a1, a2, d)
        if vm is not None and vm <= vl:
            t1 = (vm - vi) / a1
            t2 = (vt - vm) / a2
            tc = self._calculateExtraConstantSpeedTimeBetweenAccelerations(vt, vm, t1 + t2, t)
            if tc is not None and t1 > 0 and t2 > 0 and tc >= 0:
                return [(vm, t1, 0), (vt, t2, t1 + tc)]
        # try to calculate constant speed with distance only
        return None

    '''
    Calculates the constant speed time for function that accelerates then constant speed and then acceleration again.
    The speed function may look like /-\. The max speed (speed limit) vl >= vt and vl >= vi
    '''

    def _calculateConstantSpeedTimeBetweenAccelerations(self, vi, vt, vl, d, a1, a2):
        t1 = (vl - vi) / a1
        t2 = (vt - vl) / a2
        if t1 < 0 or t2 < 0:
            return None
        tc = (d - (vl * vl - vi * vi) * 0.5 / a1 - (vt * vt - vl * vl) * 0.5 / a2) / vl
        return tc

    '''
    Calculates the constant speed time for function that accelerates then constant speed and then acceleration again.
    The speed function looks like /-\. The max speed (speed limit) vl >= vt and vl >= vi. 
    @t is time to target speed
    '''

    def _calculateConstantSpeedTimeBetweenAccelerationsWithTimeToTargetSpeed(self, vi, vt, vl, t, d, a1, a2):
        t1 = (vl - vi) / a1
        t2 = (vt - vl) / a2
        if t1 < 0 or t2 < 0:
            return None
        tc = (d - (vl * vl - vi * vi) * 0.5 / a1 - (vt * vt - vl * vl) * 0.5 / a2) / vl
        tce = self._calculateExtraConstantSpeedTimeBetweenAccelerations(vt, vl, t1 + t2 + tc, t)
        return tc + tce

    '''
    Calculates the extra constant speed at vl so that the follower catches the car in front. 
    Should be used with other function e.g. _calculateConstantSpeedTimeBetweenAccelerations.
    @tp is the profile total time. Function assumes that equal acceleration and deceleration is used e.g. a1 == -a2
    '''

    def _calculateExtraConstantSpeedTimeBetweenAccelerations(self, vt, vl, tp, t):
        if vl == vt:
            return 0
        if vl < vt:
            return 0
        return vt * (tp - t) / (vl - vt)

    '''
    Calculates the constant speed at speed limit. 
    '''

    def _calculateSpeedLimitedConstantSpeedTime(self, vi, vt, vl, d, tt, ap, an):
        if vi > vl or vt >= vl: return None
        t1 = (vl - vi) / ap
        t2 = (vt - vl) / an
        d1 = 0.5 * t1 * (vl + vi)
        d2 = 0.5 * t2 * (vt + vl)
        tc = (vt * (t1 + t2 - tt) + d - d1 - d2) / (vl - vt)
        if tc < 0: return None
        return tc

    '''
    Not useful I guess
    '''

    def _calculateMidSpeedAndConstantSpeedTime(self, vi, vt, vl, ap, an, d):
        vm = self._calculateMidSpeedWithDistanceOnly(vi, vt, ap, an, d)
        if vm is None or vm <= 0: return None, None
        if vm <= vl: return vm, 0
        vdiff = vm - vl
        ta = vdiff / ap
        td = vdiff / an
        ddiff = 0.5 * (vm + vl) * (ta + td)
        tm = ddiff / (vl - vt)
        return vm, tm

    '''
    Calculates midspeed without time. E.g. stopping at trafficlight.
    '''

    def _calculateMidSpeedWithDistanceOnly(self, vi, vt, a1, a2, d):
        # result = math.sqrt((2 * a1 * a2 * d + a2 * vi * vi - a1 * vt * vt) / (a2 - a1))
        if a1 == a2: return None
        try:
            try:
                vm = math.sqrt((d + vi * vi / (2 * a1) - vt * vt / (2 * a2)) / (1 / (2 * a1) - 1 / (2 * a2)))
                if vm < 0: return None
                return vm
            except ZeroDivisionError as e:
                return None
        except ValueError as e:
            return None

    '''
    Calculates midspeed.
    @t is time to target speed for the car ahead. offset time that may be required if the car ahead has not reached the target time yet
    '''

    def _calculateMidSpeed(self, vi, vt, d, t, a1, a2):
        try:
            try:
                a = 0.5 * (1 / a1 - 1 / a2)
                b = vt * (-1 / a1 + 1 / a2)
                c = -0.5 * vi * vi / a1 + 0.5 * vt * vt / a2 + vt * vi / a1 - vt * vt / a2 - d + vt * t
                r1 = 0.5 * (-b + math.sqrt(b * b - 4 * a * c)) / a
                r2 = 0.5 * (-b - math.sqrt(b * b - 4 * a * c)) / a
                if r1 < 0: return None
                return r1
            except ZeroDivisionError as e:
                return None
        except ValueError as e:
            return None

    '''
    Calculates the max distance to objects that the car reacts to 
    '''

    def _calculateReactionDistance(self, speed) -> float:
        refspeed = 16.7
        refdistance = 120
        a = 6 if speed < refspeed else 2
        result = (speed * speed - refspeed * refspeed) / (2 * a) + refdistance
        return result

    '''
    Calculates constant low speed for profile \_/ 
    Value error might indicate that you need to stop
    '''

    def _calculateFloorSpeed(self, vi, vt, d, t, ap, an):
        try:
            a = 0.5 * (1.0 / ap - 1.0 / an)
            b = t + vi / an - vt / ap
            c = 0.5 * vt * vt / ap - 0.5 * vi * vi / an - d
            r1 = 0.5 * (-b + math.sqrt(b * b - 4 * a * c)) / a
        #            r2 = 0.5*(-b-math.sqrt(b*b-4*a*c))/a
        except ValueError:
            return None
        return r1

    '''
    Calculates constant high speed for profile /-\
    '''

    def _calculateRoofSpeed(self, vi, vt, d, t, ap, an):
        a = 0.5 * (1.0 / an - 1.0 / ap)
        b = t + vi / ap - vt / an
        c = 0.5 * vt * vt / an - 0.5 * vi * vi / ap - d
        try:
            r1 = 0.5 * (-b + math.sqrt(b * b - 4 * a * c)) / a
            #        r2 = 0.5*(-b-math.sqrt(b*b-4*a*c))/a
            return r1
        except ValueError:
            return None

    def _calculateMaxMinAccelerations(self, items, startSpeed):
        min = 0
        max = 0
        for speed, time, _ in items:
            if time > 0:
                a = (speed - startSpeed) / time
                if a > max:
                    max = a
                if a < min:
                    min = a
            startSpeed = speed
        return max, min

    def _addDebugProfileStackCount(self, key):
        if key not in self.debug['stack'].keys():
            self.debug['stack'][key] = 0
        self.debug['stack'][key] += 1
        self.debug['stack']['last added'] = key


class CarAIContainer:
    def __init__(self):
        self.targetCarDict = {}  # type is {Car: Car}
        self.targetTrafficlightDict = {}  # {Car: Trafficlight}
        self.spottedTrafficlightDict = {}
        self.spottedCarDict = {}
        self.currentTarget = {}  # type is {Car: Object}

    def setCurrentTarget(self, car: Car, target):
        self.currentTarget[car] = target

    def getCurrentTarget(self, car: Car):
        try:
            return self.currentTarget[car]
        except KeyError:
            return None

    def setTargetCar(self, car: Car, targetCar: Car):
        self.targetCarDict[car] = targetCar

    def getTargetCar(self, car: Car):
        try:
            return self.targetCarDict[car]
        except KeyError:
            return None

    def setTargetTrafficlight(self, car: Car, trafficlight: Trafficlight):
        self.targetTrafficlightDict[car] = trafficlight

    def getTargetTrafficlight(self, car: Car):
        try:
            result = self.targetTrafficlightDict[car]
            return result
        except KeyError:
            return None
