from simulation import *
import arcade
import math
from lane import Lane

UPDATE_RATE = 0.1
SPEEDMULTIPLIER = 2
ZOOM = 2
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Intersection   author Juho Taipale"
colors = [arcade.color.BLEU_DE_FRANCE, arcade.color.WHITE,
          arcade.color.ORANGE, arcade.color.OLIVE]
carColors = ['blue', 'white', 'orange', 'olive']
colorConversion = {'yellow': arcade.color.YELLOW, 'green': arcade.color.GREEN, 'red': arcade.color.RED,
                   'blue': arcade.color.BLUE, 'orange': arcade.color.ORANGE, 'lane': arcade.color.COOL_GREY}
LANE_COLOR = colorConversion['lane']


class Graphics(arcade.Window):
    '''Graphics for the simulation.'''

    def __init__(self):
        self.simulation = DummylightsTwoCrossings()
        self._setZoomParameters(SCREEN_WIDTH, SCREEN_HEIGHT)
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=UPDATE_RATE, resizable=True)
        arcade.set_background_color(arcade.color.BLACK)
        self.debugTextOffsets = [0 for x in range(10)]
        self.lanes = self.simulation.world.getLanes()
        self.lanewidth =self.lanes[0].width # useful when drawing traffic lights
        self.laneShapeElementList = self.getLaneShapesElementList(self.lanes)
        pass

    def setup(self):
        arcade.draw_point(100,100, arcade.color.ORANGE, 50)
        pass

    def on_draw(self):
        arcade.start_render()
        self.laneShapeElementList.draw()
        clds = self.simulation.world.getCarsLocationsAndDirections()
        shapeelementlist = arcade.ShapeElementList()
        for car, x, y, d in clds:
            shapeelementlist.append(self.getCarShape(x, y, d, car))
        tlds = self.simulation.world.getTrafficlightsLocationsAndDirections()
        for trafficlight, x, y, d in tlds:
            shapeelementlist.append(self.getTrafficlightShape(x, y, d, trafficlight))
        shapeelementlist.draw()

    def on_update(self, delta_time: float):
        self.simulation.moveTimestep(delta_time * SPEEDMULTIPLIER)
        arcade.pause(delta_time / 50)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self._setZoomParameters(width, height)
        self.laneShapeElementList = self.getLaneShapesElementList(self.lanes)


    def _setZoomParameters(self, width, height):
        ux, uy, lx, ly = self.simulation.world.getBoundingBox()
        self.offsetx = lx
        self.offsety = ly
        self.screenwidth = ux - lx
        self.sreenheight = uy - ly
        self.zoom = min(width / (ux - lx), height / (uy - ly))

    def getStraightShapeWithCoordinationChange(self, startx, starty, endx, endy, linewidth, color):
        return arcade.create_line((startx - self.offsetx) * self.zoom, (starty - self.offsety) * self.zoom,
                                  (endx - self.offsetx) * self.zoom, (endy - self.offsety) * self.zoom, color,
                                  linewidth)


    def getRectangleShapeWithCoordinationChange(self, centerx, centery, width, height, color, direction):
        return arcade.create_rectangle_filled((centerx - self.offsetx) * self.zoom,
                                              (centery - self.offsety) * self.zoom, width * self.zoom,
                                              height * self.zoom, color, direction)

    def getLaneShape(self, lane: Lane):
        if lane.type == 'line':
            return self.getStraightShapeWithCoordinationChange(lane.startx, lane.starty, lane.endx, lane.endy,
                                                               lane.width * self.zoom, LANE_COLOR)
        elif lane.type == 'arc':
            ''' arc is approximated with several lines because there is no way to create arc primitive'''
            laneShapeList = []
            straights = lane.getStraightApproximationCoordinateList()
            for straight in straights:
                laneShapeList.append(
                    self.getStraightShapeWithCoordinationChange(straight[0], straight[1], straight[2], straight[3],
                                                                lane.width, LANE_COLOR)
                )
            return laneShapeList

    def getLaneShapesElementList(self, lanes):
        elementList = arcade.ShapeElementList()
        for lane in lanes:
            result = self.getLaneShape(lane)
            if type(result) is list:
                for shape in result:
                    elementList.append(shape)
            else:
                elementList.append(result)
        return elementList

    def getCarShape(self, x, y, d, car):
        color = colorConversion[car.color]
        d = (d + math.pi / 2) / math.pi * 180
        return self.getRectangleShapeWithCoordinationChange(x, y, car.width, car.length, color, d)

    def getTrafficlightShape(self, x, y, d, trafficlight):
        a = d - math.pi * .5
        b = d + math.pi * .5
        o = d + math.pi
        w = self.lanewidth*0.5
        offset = w
        x1 = x + w * math.cos(a) - offset * math.cos(d)
        y1 = y + w * math.sin(a) - offset * math.sin(d)
        x2 = x + w * math.cos(b) - offset * math.cos(d)
        y2 = y + w * math.sin(b) - offset * math.sin(d)
        color = colorConversion[trafficlight.color]
        return self.getStraightShapeWithCoordinationChange(x1, y1, x2, y2, w*3, color)


def main():
    window = Graphics()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
