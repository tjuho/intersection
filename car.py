from speedchange import SpeedChange
import math

'''Car state and movement'''


class Car:
    def __init__(self, initialspeed=0.0, color='orange', width=1.8, length=4, preferredAcceleration=1.7,
                 preferredDeceleration=-1.9, maxSpeedKmh=170, name='car'):
        self.maxSpeed = maxSpeedKmh / 3.6
        self.width = width
        self.length = length
        self.halflength = length * 0.5
        self.color = color
        self.name = name
        self.preferredAcceleration = preferredAcceleration
        self.preferredDeceleration = preferredDeceleration
        self.initialSpeed = initialspeed
        # self.speedItemIndex = 0
        self.time = 0.0
        self.distance = 0.0
        self.timeFromLastSpeedChange = 0.0
        self.zeromargin = self.calculateDistanceMargin(0)
        self.speedItems = [(0, initialspeed, 0)]
        '''speed item type is (startTime, speed, distance)'''

        self.debug = None

    def moveTimestep(self, timestep):
        if timestep == 0: return
        self.distance += self.getTravelDistance(timestep)
        self.time += timestep
        self.timeFromLastSpeedChange += timestep

    def changeSpeed(self, targetSpeed, changeTime, offsettime=0.0):
        #        if not (changeTime == 0 and math.isclose(targetSpeed, self.getSpeed(offsettime), abs_tol=1e-10)) and (
        #                changeTime <= 0 or math.isclose(0, changeTime, abs_tol=1e-15)): return
        assert (offsettime >= 0.0)
        targetSpeed = min(self.maxSpeed, targetSpeed)
        startspeed = self.getSpeed(offsettime)
        starttime = self.time + offsettime
        i = self._getSpeedItemIndex(starttime)
        self.speedItems = self.speedItems[:i + 1]
        lstarttime, lspeed, ldistance = self.speedItems[-1]
        startdistance = 0.5 * (lspeed + startspeed) * (starttime - lstarttime) + ldistance
        if starttime > 1e10: return
        if starttime > lstarttime:
            self.speedItems.append((starttime, startspeed, startdistance))
        enddistance = 0.5 * (targetSpeed + startspeed) * changeTime + startdistance
        if changeTime > 1e10: return
        self.speedItems.append((starttime + changeTime, targetSpeed, enddistance))
        self.timeFromLastSpeedChange = 0.0
        if len(self.speedItems) > 1:
            if self.speedItems[-1][0] == self.speedItems[-2][0]:
                self.speedItems.pop()

    def addSpeedChanges(self, speedchange: SpeedChange, offsettime: float = 0.0):
        for acc, dur in speedchange.accelerations:
            self.addAcceleration(acc, dur, offsettime)
            offsettime += dur

    def addSpeedItems(self, speeditems):
        for targetspeed, changetime, offsettime in speeditems:
            self.changeSpeed(targetspeed, changetime, offsettime)

    def addConstantSpeed(self, duration: float, offsettime=0.0):
        self.addAcceleration(0, duration, offsettime)

    def addAcceleration(self, acceleration: float, duration: float, offsettime=0.0):
        speed = self.getSpeed(offsettime)
        targetSpeed = speed + acceleration * duration
        self.changeSpeed(targetSpeed, duration, offsettime)

    def getTravelDistance(self, timestep, offsettime=0.0):
        if timestep == 0.0: return 0.0
        starttime = self.time + offsettime
        endtime = starttime + timestep
        return self._getDistance(endtime) - self._getDistance(starttime)

    def getDistance(self, offsettime):
        return self._getDistance(self.time + offsettime)

    def _getDistance(self, time):
        if time < 0: return 0
        j = self._getSpeedItemIndex(time)
        speed = self.getSpeed(time - self.time)
        itemtime, itemspeed, itemdistance = self.speedItems[j]
        return itemdistance + 0.5 * (speed + itemspeed) * (time - itemtime)

    def _getSpeedItemIndex(self, time):
        starttime, _, _ = self.speedItems[-1]
        if time > starttime: return len(self.speedItems) - 1
        l = 0
        r = len(self.speedItems) - 1
        m = 0
        m = int((l + r) / 2)
        while l <= r:
            starttime, _, _ = self.speedItems[m]
            if starttime < time:
                if l == r: return m
                l = m + 1
            elif starttime > time:
                if l == r: return m - 1
                r = m - 1
            else:
                return m
            m = int((l + r) / 2)
        return m

    def getAcceleration(self, offsettime=0.0) -> float:
        i = self._getSpeedItemIndex(self.time + offsettime)
        if i == len(self.speedItems) - 1:
            return 0.0
        t1, v1, _ = self.speedItems[i]
        t2, v2, _ = self.speedItems[i + 1]
        if t1 == t2:
            print(self)
        return (v2 - v1) / (t2 - t1)

    def getSpeed(self, offsettime=0.0):
        time = self.time + offsettime
        i = self._getSpeedItemIndex(time)
        starttime, startspeed, _ = self.speedItems[i]
        if i == len(self.speedItems) - 1: return startspeed
        nstarttime, nstartspeed, _ = self.speedItems[i + 1]
        temp = (nstarttime - starttime)
        if temp != 0.0:
            speed = (time - starttime) / temp * (nstartspeed - startspeed) + startspeed
            return speed
        else:
            return startspeed

    def getTargetSpeedAndDistanceAndTimeToIt(self, offsettime=0.0):
        if len(self.speedItems) == 0:
            return self.initialSpeed, 0, 0
        s = self.getTargetSpeed()
        d = self.getDistanceToTargetSpeed(offsettime)
        t = self.getTimeToTargetSpeed()
        return s, d, max(0, t - offsettime)

    def getTargetSpeed(self):
        return self.speedItems[-1][1]

    def getDistanceToTargetSpeed(self, offsettime=0.0):
        return self._getDistanceToTargetSpeed(self.time + offsettime)

    def _getDistanceToTargetSpeed(self, time):
        t, _, d = self.speedItems[-1]
        return max(0.0, d - self._getDistance(time))

    def getTimeToNextSpeedChange(self, offsettime=0.0):
        i = self._getSpeedItemIndex(self.time + offsettime)
        if i == len(self.speedItems) - 1:
            return None
        else:
            return self.speedItems[i + 1][0] - self.time - offsettime

    def getTimeToTargetSpeed(self):
        if len(self.speedItems) == 0:
            return 0
        t, _, _ = self.speedItems[-1]
        return max(0.0, t - self.time)

    def getMaxSpeed(self):
        return max([x[1] for x in self.speedItems])

    def getMaxMinSpeed(self, offsettime=0.0):
        speed = self.getSpeed(offsettime)
        min = speed
        max = speed
        i = self._getSpeedItemIndex(self.time + offsettime)
        for time, speed, distance in self.speedItems[i:]:
            if min > speed:
                min = speed
            if max < speed:
                max = speed
        return max, min

    def getUpcommingSpeedChangeTimes(self, offsettime=0.0):
        i = self._getSpeedItemIndex(self.time + offsettime)
        result = []
        for time, speed, distance in self.speedItems[i + 1:]:
            time = time - self.time - offsettime
            result.append(time)
        return result

    def getSpeedChangeTimesAndDistances(self, offsettime=0.0):
        i = self._getSpeedItemIndex(self.time + offsettime)
        dnow = self._getDistance(self.time + offsettime)
        result = []
        for time, speed, distance in self.speedItems[i + 1:]:
            time = time - self.time - offsettime
            distance = distance - dnow
            result.append((time, distance))
        return result

    def setSpeed(self, speed, offsettime=0.0):
        targetspeed = self.getTargetSpeed()
        if not math.isclose(targetspeed, speed):
            initialspeed = self.getSpeed(offsettime)
            if speed > initialspeed:
                self.changeSpeed(speed, (speed - initialspeed) / self.preferredAcceleration, offsettime)
            else:
                self.changeSpeed(speed, (speed - initialspeed) / self.preferredDeceleration, offsettime)

    '''
    Calculates distance margin for the car. So That with higher speeds the car stays further away from the car in front
    '''

    def calculateDistanceMargin(self, speed: float) -> float:
        speeds = [0.0, 40 / 3.6, 60 / 3.6, 80 / 3.6, 120 / 3.6]
        distances = [2.0, 5.0, 10.0, 16.0, 32.0]
        minIndex = None
        maxIndex = None
        for i, referenceSpeed in enumerate(speeds):
            if speed <= referenceSpeed:
                minIndex = i - 1
                maxIndex = i
                break
        if minIndex is not None and maxIndex is not None:
            k = (distances[maxIndex] - distances[minIndex]) / (speeds[maxIndex] - speeds[minIndex])
            b = distances[minIndex] - k * speeds[minIndex]
            return k * speed + b + self.halflength
        result = distances[-1]
        return result + self.halflength

    def makesFaster(self, speedchange: SpeedChange) -> bool:
        tspeed1 = self.getTargetSpeed()
        tspeed2 = speedchange.getTargetSpeed()
        if tspeed1 < tspeed2:
            return True
        t1 = self.getTimeToTargetSpeed()
        t2 = speedchange.getTimeToTargetSpeed()
        t = max(t1, t2)
        d1 = self.getTravelDistance(t)
        d2 = speedchange.getTravelDistance(t)
        if d1 < d2: return True
        return False

    def calculateSpeedChangeSpeedIntersectionTimes(self, speedchange: SpeedChange, caraccelerationhigher=False,
                                                   offsettime=0.0):
        result = []
        changetimes = self.getUpcommingSpeedChangeTimes(offsettime)
        changetimes.extend(speedchange.getUpcommingSpeedChangeTimes(offsettime))
        changetimes = list(set(changetimes))
        changetimes.sort()
        starttime = 0
        if math.isclose(speedchange.getSpeed(offsettime), self.getSpeed(offsettime), abs_tol=1e-12) and len(
                changetimes) > 0:
            result.append(changetimes[0])
        for endtime in changetimes:
            acc = self.getAcceleration(starttime + offsettime)
            scacc = speedchange.getAcceleration(starttime + offsettime)
            if acc != scacc:
                ispeed = self.getSpeed(0)
                iscspeed = speedchange.getSpeed(9)
                speed = self.getSpeed(starttime + offsettime)
                scspeed = speedchange.getSpeed(starttime + offsettime)
                deltaspeed = scspeed - speed
                crossingtime = deltaspeed / (acc - scacc)
                if (crossingtime > 0 or math.isclose(0, deltaspeed,
                                                     abs_tol=1e-12)) and crossingtime <= endtime - starttime:
                    if caraccelerationhigher:
                        if acc > scacc:
                            result.append(starttime + crossingtime)
                    else:
                        result.append(starttime + crossingtime)
            starttime = endtime
        return result

    def testSpeedIntegrity(self):
        pt = None
        pv = None
        pd = None

        for t, v, d in self.speedItems:
            if pt == t:
                return False
            pt = t
        return True

    def __lt__(self, other):
        tspeed1 = self.getTargetSpeed()
        tspeed2 = other.getTargetSpeed()
        if tspeed1 < tspeed2:
            return True
        tdist1 = self.getDistanceToTargetSpeed()
        tdist2 = other.getDistanceToTargetSpeed()
        if tspeed1 == tspeed2 and tdist1 < tdist2:
            return True
        ttime1 = self.getTimeToTargetSpeed()
        ttime2 = other.getTimeToTargetSpeed()
        if tspeed1 == tspeed2 and tdist1 == tdist2 and ttime1 > ttime2:
            return True
        return False

    def __gt__(self, other):
        tspeed1 = self.getTargetSpeed()
        tspeed2 = other.getTargetSpeed()
        if tspeed1 > tspeed2:
            return True
        tdist1 = self.getDistanceToTargetSpeed()
        tdist2 = other.getDistanceToTargetSpeed()
        if tspeed1 == tspeed2 and tdist1 > tdist2:
            return True
        ttime1 = self.getTimeToTargetSpeed()
        ttime2 = other.getTimeToTargetSpeed()
        if tspeed1 == tspeed2 and tdist1 == tdist2 and ttime1 < ttime2:
            return True
        return False

    def __str__(self):
        items = ','.join([f'({x[0]}, {x[1]}, {x[2]})' for x in self.speedItems])
        vt, dt, tt = self.getTargetSpeedAndDistanceAndTimeToIt()
        additionalinfo = f'target speed: {vt:.1f} t.distance: {dt:.1f} t.time: {tt:.1f} debug {self.debug}'
        res = f'speed={self.getSpeed()} time={self.time} from speed change={self.timeFromLastSpeedChange} distance={self.distance} {additionalinfo} speedItems=[{items}]'
        res = f'speed={self.getSpeed()}\n{self.name}.distance={self.distance}\n{self.name}.speedItems={self.speedItems}\n{self.name}.time={self.time}\n{self.name}.timeFromLastSpeedChange={self.timeFromLastSpeedChange}'
        return res
