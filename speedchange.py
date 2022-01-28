'''Halds the possible speed change for a cars'''


class SpeedChange:

    def __init__(self, initialspeed: float):
        # (acceleraiton, duration)
        self.accelerations = []
        self.initialspeed = initialspeed
        pass

    def addAcceleration(self, acceleration, duration, offsettime=0.0):
        duration = max(duration, 0)
        idx = 0
        totalduration = 0
        for acc, dur in self.accelerations:
            totalduration += dur
            diff = offsettime - totalduration
            if diff == 0:
                self.accelerations = self.accelerations[:idx + 1]
                break
            if diff < 0:
                self.accelerations = self.accelerations[:idx + 1]
                lacc, ldur = self.accelerations[-1]
                self.accelerations[-1] = (lacc, ldur + diff)
                break
            idx += 1
        if offsettime - totalduration > 0:
            self.accelerations.append((0, offsettime - totalduration))
        self.accelerations.append((acceleration, duration))

    def addDelay(self, time):
        self.accelerations.insert(0, (0, time))

    def getAcceleration(self, offsettime=0.0) -> float:
        i, _ = self._getIndexAndDurationRemaining(offsettime)
        if i == len(self.accelerations):
            return 0.0
        return self.accelerations[i][0]

    def getSpeed(self, offsettime):
        speed = self.initialspeed
        totalduration = 0
        for acc, dur in self.accelerations:
            totalduration += dur
            diff = totalduration - offsettime
            if diff >= 0:
                speed += acc * (dur - diff)
                break
            speed += acc * dur
        return speed

    def getTargetSpeed(self):
        speed = self.initialspeed
        for acc, dur in self.accelerations:
            speed += acc * dur
        return speed

    def getTravelDistance(self, timestep: float, offsettime=0.0):
        if timestep == 0.0: return 0.0
        distance = 0.0
        currentspeed = self.getSpeed(offsettime)
        idx1, timeremain1 = self._getIndexAndDurationRemaining(offsettime)
        idx2, timeremain2 = self._getIndexAndDurationRemaining(timestep + offsettime)
        accelerations = self.accelerations[idx1:idx2 + 1]
        if len(accelerations) == 0:
            return timestep * currentspeed
        totalduration = 0
        for acc, dur in accelerations:
            duration = dur
            if timeremain1 > 0:
                duration = timeremain1
                nextspeed = acc * duration + currentspeed
            else:
                nextspeed = acc * duration + currentspeed
            if idx1 == idx2:
                duration = duration - timeremain2
                nextspeed = acc * duration + currentspeed
            distance += 0.5 * (currentspeed + nextspeed) * duration
            timeremain1 = 0
            idx1 += 1
            currentspeed = nextspeed
            totalduration += duration
        if timestep > totalduration:
            distance += (timestep - totalduration) * self.getTargetSpeed()
        return distance

    def _getIndexAndDurationRemaining(self, time):
        diff = 0
        idx = 0
        totalduration = 0
        for acc, dur in self.accelerations:
            totalduration += dur
            diff = totalduration - time
            if diff > 0:
                break
            idx += 1
        return idx, diff

    def getUpcommingSpeedChangeTimes(self, offsettime=0.0):
        result = []
        i, timeremaining = self._getIndexAndDurationRemaining(offsettime)
        first = True
        currentspeed = self.initialspeed
        for acc, dur in self.accelerations[i:]:
            targetspeed = currentspeed + acc * dur
            if first:
                time = timeremaining
                first = False
            else:
                time += dur
            currentspeed = targetspeed
            result.append(time)
        return result

    def getSpeedChangeTimesAndDistances(self, offsettime=0.0):
        result = []
        i, timeremaining = self._getIndexAndDurationRemaining(offsettime)
        distance = 0
        time = 0
        first = True
        currentspeed = self.initialspeed
        for acc, dur in self.accelerations[i:]:
            if first:
                time = timeremaining
                first = False
            else:
                time += dur
            targetspeed = currentspeed + acc * dur
            distance += 0.5 * (currentspeed + targetspeed) * dur
            currentspeed = targetspeed
            result.append((time, distance))
        return result

    def getTimeToTargetSpeed(self):
        time = 0.0
        for _, dur in self.accelerations:
            time += dur
        return time

    def addSpeedChange(self, speedchange, offsettime=0.0):
        for acc, dur in speedchange.accelerations:
            self.addAcceleration(acc, dur, offsettime)
            offsettime += dur

    def addSpeedItems(self, speeditems):
        currentspeed = self.initialspeed
        for targetspeed, changetime, offsettime in speeditems:
            if changetime == 0: continue
            self.addAcceleration((targetspeed - currentspeed) / changetime, changetime, offsettime)
            currentspeed = targetspeed

    def getMaxMinSpeed(self):
        max = self.initialspeed
        min = self.initialspeed
        currentspeed = self.initialspeed
        for acc, dur in self.accelerations:
            currentspeed += acc * dur
            if max < currentspeed:
                max = currentspeed
            if min > currentspeed:
                min = currentspeed
        return max, min

    def __str__(self):
        msg = ','.join([f'({x[0]}, {x[1]})' for x in self.accelerations])
        return 'acc, dur' + msg

    def __add__(self, other):
        acc1 = self.accelerations
        acc1.extend(other.accelerations)
        result = SpeedChange(self.initialspeed)
        result.accelerations = acc1
        return result

    def __lt__(self, other):
        t1 = 0
        t2 = 0
        for acc, dur in self.accelerations:
            t1 += dur
        for acc, dur in other.accelerations:
            t2 += dur
        mt = max(t1, t2)
        d1 = self.getTravelDistance(mt)
        d2 = other.getTravelDistance(mt)
        if d1 < d2:
            return True
        v1 = self.getSpeed(mt)
        v2 = self.getSpeed(mt)
        if v1 < v2: return True
        return False
