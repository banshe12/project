from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock
import random

class GlitchButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self.start_glitch)

    def start_glitch(self, *args):
        # Multiple rapid animations to simulate a glitch
        for i in range(5):
            Clock.schedule_once(lambda dt: self._apply_glitch(), i * 0.05)
        Clock.schedule_once(self._reset_glitch, 0.3)

    def _apply_glitch(self, *args):
        self.background_color = [random.random(), random.random(), random.random(), 1]
        self.pos = (self.pos[0] + random.uniform(-5, 5), self.pos[1] + random.uniform(-5, 5))
        self.color = [random.random(), random.random(), random.random(), 1]

    def _reset_glitch(self, *args):
        self.background_color = [0, 0, 0, 0]
        # Assuming original pos is managed by layout, reset is tricky,
        # but in most Kivy layouts, pos is recalculated.
        self.color = [0, 1, 0.5, 1]

if __name__ == "__main__":
    print("GlitchButton loaded")
