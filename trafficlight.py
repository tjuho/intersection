class Trafficlight:
    def __init__(self, yellowTime: float, redtogreendelay: float, color='green'):
        self.color = color
        self.timeToNextColorChange = None
        self.yellowTime = yellowTime
        self.redToGreenDelay = redtogreendelay

    def turnRed(self):
        if self.color == 'green':
            self.switch()
        elif self.color == 'red':
            self.timeToNextColorChange = None
        elif self.color == 'red delay':
            self.color = 'red'
            self.timeToNextColorChange = None

    def turnGreen(self):
        if self.color == 'yellow':
            self.color = 'green'
            self.timeToNextColorChange = None
        elif self.color == 'red':
            self.switch()
        elif self.color == 'green':
            self.timeToNextColorChange = None

    def switch(self, offsetTime=0):
        self.timeToNextColorChange = offsetTime

    def moveTimestep(self, timestep):
        if self.timeToNextColorChange or self.timeToNextColorChange == 0:
            self.timeToNextColorChange -= timestep
            if self.timeToNextColorChange <= 0:
                if self.color == 'green':
                    if self.timeToNextColorChange + self.yellowTime <= 0:
                        self.color = 'red'
                        self.timeToNextColorChange = None
                    else:
                        self.color = 'yellow'
                        self.timeToNextColorChange = self.yellowTime
                elif self.color == 'yellow':
                    self.color = 'red'
                    self.timeToNextColorChange = None
                elif self.color == 'red' and self.timeToNextColorChange * -1 >= self.redToGreenDelay:
                    self.color = 'green'
                    self.timeToNextColorChange = None

    @classmethod
    def calculateMaxYellowTime(self, speed):
        times = [3, 6]  # seconds
        speeds = [11.11111111111111, 27.77777777777778]  # same as [40, 100] kmh
        k = 0.18  # k and b calculated from numbers above
        b = 1
        # k = (times[-1] - times[0])/(speeds[-1]- speeds[0])
        # b = times[0] - k * speeds[0]
        if speed <= speeds[0]:
            return times[0]
        elif speed >= speeds[-1]:
            return times[-1]
        return k * speed + b

    def __str__(self):
        return f'{self.color} change in {self.timeToNextColorChange}'
