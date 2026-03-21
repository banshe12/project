from kivy.graphics import Color, Bezier
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty

class BezierConnection(Widget):
    node_start = ObjectProperty(None)
    node_end = ObjectProperty(None)
    line_color = ListProperty([1, 1, 1, 0.6])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        if self.node_start:
            self.node_start.bind(pos=self.update_canvas, size=self.update_canvas)
        if self.node_end:
            self.node_end.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_node_start(self, instance, value):
        if value:
            value.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_node_end(self, instance, value):
        if value:
            value.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        if not self.node_start or not self.node_end:
            return

        self.canvas.clear()
        with self.canvas:
            Color(*self.line_color)

            x1, y1 = self.node_start.center
            x2, y2 = self.node_end.center

            # Control points for S-shaped curve
            cx1 = x1 + (x2 - x1) * 0.5
            cy1 = y1
            cx2 = x1 + (x2 - x1) * 0.5
            cy2 = y2

            Bezier(points=[x1, y1, cx1, cy1, cx2, cy2, x2, y2], segments=30, width=1.2)

if __name__ == "__main__":
    print("BezierConnection loaded")
