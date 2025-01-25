from trafficlight import Trafficlight
import uuid
'''The logic how traffic lights switch in one intersection'''


class TrafficlightController:
    '''@systemmatrix shows which trafficlights are on or off at each state'''

    def __init__(self, trafficlights: [Trafficlight], systemsmatrix):
        self.id = str(uuid.uuid4())
        self.checkSystemMatreix(trafficlights, systemsmatrix)
        self.matrix = systemsmatrix
        self.trafficlights = trafficlights
        self.index = 0
        self.setIndex(0)

    def to_dict(self):
        return {
            "id": self.id,
            "matrix": self.matrix,
            "trafficlights": [trafficlights.to_dict() for trafficlights in self.trafficlights],
            "index": self.index,
        }

    def checkSystemMatreix(self, trafficlights, systemmatrix):
        for row in systemmatrix:
            assert (len(row) == len(trafficlights))
            for value in row:
                assert (value == 0 or value == 1)

    def cycle(self):
        if self.index == len(self.matrix) - 1:
            self.setIndex(0)
        else:
            self.setIndex(self.index + 1)

    def getStatesCount(self):
        return len(self.matrix)

    def setIndex(self, index: int):
        assert (index >= 0 and index < len(self.matrix))
        if len(self.matrix) <= index:
            self.index = 0
        else:
            self.index = index
        row = self.matrix[self.index]
        for i, value in enumerate(row):
            if value == 0:  # switch these to red
                self.trafficlights[i].turnRed()
            else:
                self.trafficlights[i].turnGreen()
