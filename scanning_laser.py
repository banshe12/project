from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.animation import Animation
from kivy.properties import NumericProperty

class ScanningLaser(Widget):
    laser_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, laser_y=self.update_canvas)
        self.opacity = 0

    def update_canvas(self, *args):
        self.canvas.clear()
        if self.opacity <= 0:
            return

        with self.canvas:
            Color(0, 1, 0.5, 0.8)
            # Main laser line
            Line(points=[self.x, self.y + self.laser_y, self.right, self.y + self.laser_y], width=1.5)
            # Faded glow lines
            for i in range(1, 4):
                Color(0, 1, 0.5, 0.8 / (i + 1))
                Line(points=[self.x, self.y + self.laser_y - (i * 2), self.right, self.y + self.laser_y - (i * 2)], width=1)
                Line(points=[self.x, self.y + self.laser_y + (i * 2), self.right, self.y + self.laser_y + (i * 2)], width=1)

    def start(self):
        self.opacity = 1
        self.laser_y = self.height
        anim = Animation(laser_y=0, duration=1.5) + Animation(laser_y=self.height, duration=1.5)
        anim.repeat = True
        anim.start(self)

    def stop(self):
        Animation.cancel_all(self)
        self.opacity = 0
        self.canvas.clear()

if __name__ == "__main__":
    print("ScanningLaser loaded")
