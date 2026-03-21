from kivy.uix.label import Label
from kivy.graphics import Color, Line, Rectangle
from kivy.properties import StringProperty, ListProperty

class OSINTNode(Label):
    background_color = ListProperty([0, 0, 0, 1])
    border_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bold = True
        self.font_size = "14sp"
        self._dragging = False
        self.padding = (10, 5)
        self.size_hint = (None, None)
        self.halign = "center"
        self.valign = "middle"
        # Minimum size, will update after texture is ready
        self.size = (120, 40)
        self.bind(texture_size=self.setter("size"))
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Black fill
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)
            # White border
            Color(*self.border_color)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._dragging = True
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self._dragging = False
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

if __name__ == "__main__":
    from kivy.app import App
    class NodeApp(App):
        def build(self):
            return OSINTNode(text="USERNAME: test")
    # NodeApp().run()
    print("OSINTNode loaded")
