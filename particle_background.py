import random
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.clock import Clock
from kivy.properties import ListProperty

class Particle:
    def __init__(self, width, height):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.size = 2

    def update(self, width, height):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > width: self.vx *= -1
        if self.y < 0 or self.y > height: self.vy *= -1

class ParticleBackground(Widget):
    particles = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_particles = 60
        # Initialize particles after some delay to ensure size is set
        Clock.schedule_once(self.init_particles, 0)
        Clock.schedule_interval(self.update_canvas, 1/60.)

    def init_particles(self, dt):
        self.particles = [Particle(self.width, self.height) for _ in range(self.num_particles)]

    def update_canvas(self, dt):
        if not self.particles:
            return

        for p in self.particles:
            p.update(self.width, self.height)

        self.canvas.clear()
        with self.canvas:
            # Drawing connections first (semi-transparent)
            for i in range(len(self.particles)):
                p1 = self.particles[i]
                for j in range(i + 1, len(self.particles)):
                    p2 = self.particles[j]
                    dist_sq = (p1.x - p2.x)**2 + (p1.y - p2.y)**2
                    if dist_sq < 100**2:  # 100 pixels max connection distance
                        alpha = 1.0 - (dist_sq**0.5 / 100.0)
                        Color(0, 1, 0.5, alpha * 0.3)  # Neon Green alpha
                        Line(points=[p1.x, p1.y, p2.x, p2.y], width=0.5)

            # Drawing nodes
            Color(0, 1, 0.5, 0.8)
            for p in self.particles:
                Ellipse(pos=(p.x - p.size/2, p.y - p.size/2), size=(p.size, p.size))

if __name__ == "__main__":
    from kivy.app import App
    class TestApp(App):
        def build(self):
            return ParticleBackground()
    # TestApp().run()
    print("ParticleBackground loaded")
