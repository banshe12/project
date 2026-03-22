import random
import math
import asyncio
import aiohttp
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Point, Line, Rectangle, Bezier, InstructionGroup, PushMatrix, PopMatrix, Scale
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import NumericProperty

class Particle:
    def __init__(self, width, height):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.size = random.uniform(1, 3)

    def move(self, width, height):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > width: self.vx *= -1
        if self.y < 0 or self.y > height: self.vy *= -1

class ParticleSystem(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = [Particle(Window.width, Window.height) for _ in range(60)]
        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 1) # True Black Background
            Rectangle(pos=self.pos, size=self.size)

            for i, p in enumerate(self.particles):
                p.move(self.width, self.height)
                Color(0.5, 0.5, 0.5, 0.5)
                Point(points=[p.x, p.y], pointsize=p.size)

                # Connect nearby particles
                for j in range(i + 1, len(self.particles)):
                    p2 = self.particles[j]
                    dist = math.hypot(p.x - p2.x, p.y - p2.y)
                    if dist < 150:
                        alpha = 1 - (dist / 150)
                        Color(0.5, 0.5, 0.5, alpha * 0.3)
                        Line(points=[p.x, p.y, p2.x, p2.y], width=1)

class GraphNode(Widget):
    scale_val = NumericProperty(0.5)
    def __init__(self, text, is_center=False, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint = (None, None)
        self.size = (dp(150), dp(50))
        self.opacity = 0
        self.scale_val = 0.5

        with self.canvas.before:
            PushMatrix()
            self.scale_instr = Scale(self.scale_val, self.scale_val, 1, origin=self.center)
        with self.canvas.after:
            PopMatrix()

        with self.canvas:
            self.color = Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=dp(1.5))

        self.label = Label(text=f"[b]{self.text}[/b]", markup=True, color=(1,1,1,1),
                           pos=self.pos, size=self.size)
        self.add_widget(self.label)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.rectangle = (self.x, self.y, self.width, self.height)
        self.label.pos = self.pos
        self.label.size = self.size
        self.scale_instr.origin = self.center

    def on_scale_val(self, instance, value):
        self.scale_instr.x = value
        self.scale_instr.y = value

    def animate_in(self):
        anim = Animation(opacity=1, scale_val=1, duration=0.6, t='out_expo')
        anim.start(self)

class BezierConnection(Widget):
    def __init__(self, start_pos, end_pos, **kwargs):
        super().__init__(**kwargs)
        self.start_pos = start_pos
        self.end_pos = end_pos

        # Calculate control points for S-shape
        mid_x = (start_pos[0] + end_pos[0]) / 2
        cp1 = [mid_x, start_pos[1]]
        cp2 = [mid_x, end_pos[1]]

        with self.canvas:
            Color(1, 1, 1, 0.4)
            self.line = Bezier(points=[*start_pos, *cp1, *cp2, *end_pos], segments=30)

class OSINTApp(App):
    def build(self):
        root = Widget()

        # Background Particle System
        self.ps = ParticleSystem(size=Window.size)
        root.add_widget(self.ps)

        # UI Overlay
        self.ui_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10), size=Window.size)

        self.input_field = TextInput(
            hint_text='Target Username',
            multiline=False,
            size_hint=(1, None),
            height=dp(50),
            background_color=(0, 0, 0, 0.5),
            foreground_color=(1, 1, 1, 1),
            padding=[dp(10), dp(13)]
        )
        # Neon Border for Input
        with self.input_field.canvas.after:
            Color(0, 1, 1, 0.8) # Cyan Neon
            self.neon_line = Line(rectangle=(self.input_field.x, self.input_field.y, self.input_field.width, self.input_field.height), width=dp(1.2))

        self.scan_btn = Button(
            text='DEEP SCAN',
            size_hint=(1, None),
            height=dp(50),
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            bold=True
        )
        with self.scan_btn.canvas.before:
            Color(1, 0, 1, 0.8) # Magenta Glitch Base
            self.btn_bg = Rectangle(pos=self.scan_btn.pos, size=self.scan_btn.size)

        self.scan_btn.bind(on_press=self.start_scan)
        Clock.schedule_interval(self.update_glitch, 0.1)

        self.ui_layout.add_widget(Widget()) # Spacer
        self.ui_layout.add_widget(self.input_field)
        self.ui_layout.add_widget(self.scan_btn)

        root.add_widget(self.ui_layout)

        # Graph Layer
        self.graph_layer = Widget()
        root.add_widget(self.graph_layer)

        return root

    def start_scan(self, instance):
        username = self.input_field.text
        if not username: return

        self.graph_layer.canvas.clear()
        self.graph_layer.clear_widgets()

        # Central Node
        center_x, center_y = Window.width / 2, Window.height / 2 + dp(100)
        self.center_node = GraphNode(text=username, pos=(center_x - dp(75), center_y))
        self.graph_layer.add_widget(self.center_node)
        self.center_node.animate_in()

        self.found_count = 0
        asyncio.ensure_future(self.perform_osint_scan(username))

    async def perform_osint_scan(self, username):
        platforms = [
            ("GitHub", f"https://github.com/{username}"),
            ("Instagram", f"https://www.instagram.com/{username}/"),
            ("Telegram", f"https://t.me/{username}"),
            ("VK", f"https://vk.com/{username}"),
            ("Steam", f"https://steamcommunity.com/id/{username}"),
            ("Reddit", f"https://www.reddit.com/user/{username}"),
            ("Twitter", f"https://twitter.com/{username}"),
            ("Medium", f"https://medium.com/@{username}"),
            ("Facebook", f"https://www.facebook.com/{username}"),
            ("Pinterest", f"https://www.pinterest.com/{username}"),
            ("Tumblr", f"https://{username}.tumblr.com"),
            ("Spotify", f"https://open.spotify.com/user/{username}"),
            ("SoundCloud", f"https://soundcloud.com/{username}"),
            ("Twitch", f"https://www.twitch.tv/{username}"),
            ("TikTok", f"https://www.tiktok.com/@{username}"),
            ("DeviantArt", f"https://www.deviantart.com/{username}"),
            ("Behance", f"https://www.behance.net/{username}"),
            ("Dribbble", f"https://dribbble.com/{username}"),
            ("Vimeo", f"https://vimeo.com/{username}"),
            ("Etsy", f"https://www.etsy.com/people/{username}"),
            ("DailyMotion", f"https://www.dailymotion.com/{username}"),
            ("Slack", f"https://{username}.slack.com"),
            ("Bitbucket", f"https://bitbucket.org/{username}"),
            ("CodePen", f"https://codepen.io/{username}"),
            ("GitLab", f"https://gitlab.com/{username}"),
            ("HackerNews", f"https://news.ycombinator.com/user?id={username}"),
            ("ProductHunt", f"https://www.producthunt.com/@{username}"),
            ("Quora", f"https://www.quora.com/profile/{username}"),
            ("Snapchat", f"https://www.snapchat.com/add/{username}"),
            ("Wikipedia", f"https://en.wikipedia.org/wiki/User:{username}"),
            ("Last.fm", f"https://www.last.fm/user/{username}"),
            ("Letterboxd", f"https://letterboxd.com/{username}"),
            ("MyAnimeList", f"https://myanimelist.net/profile/{username}"),
            ("Roblox", f"https://www.roblox.com/user.aspx?username={username}"),
            ("Chess.com", f"https://www.chess.com/member/{username}"),
            ("Duolingo", f"https://www.duolingo.com/profile/{username}"),
            ("AllTrails", f"https://www.alltrails.com/members/{username}"),
            ("Strava", f"https://www.strava.com/athletes/{username}"),
            ("Flickr", f"https://www.flickr.com/photos/{username}"),
            ("ArtStation", f"https://www.artstation.com/{username}"),
            ("Goodreads", f"https://www.goodreads.com/user/show/{username}"),
            ("Bandcamp", f"https://bandcamp.com/{username}"),
            ("SpeakerDeck", f"https://speakerdeck.com/{username}"),
            ("Wattpad", f"https://www.wattpad.com/user/{username}"),
            ("Archive.org", f"https://archive.org/details/@{username}"),
            ("Codecademy", f"https://www.codecademy.com/profiles/{username}"),
            ("Disqus", f"https://disqus.com/by/{username}"),
            ("IFTTT", f"https://ifttt.com/p/{username}"),
            ("Instructables", f"https://www.instructables.com/member/{username}"),
            ("Keybase", f"https://keybase.io/{username}"),
            ("Kaggle", f"https://www.kaggle.com/{username}"),
            ("OpenStreetMap", f"https://www.openstreetmap.org/user/{username}"),
        ]

        async with aiohttp.ClientSession() as session:
            tasks = [self.check_platform(session, name, url) for name, url in platforms]
            await asyncio.gather(*tasks)

        # Simulated Deep Trace
        await asyncio.sleep(1)
        self.add_node("Leak DB: Found (2021)", self.found_count)
        self.found_count += 1

    async def check_platform(self, session, name, url):
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    text = await response.text()
                    # Basic extraction simulation
                    info = f"{name}: Found"
                    if "location" in text.lower():
                        info += "\n(Location meta)"

                    # Update UI from async thread
                    Clock.schedule_once(lambda dt: self.add_node(info, self.found_count), 0)
                    self.found_count += 1
        except:
            pass

    def update_glitch(self, dt):
        if random.random() > 0.8:
            # Glitch the button
            self.btn_bg.pos = (self.scan_btn.x + random.uniform(-2, 2), self.scan_btn.y + random.uniform(-2, 2))
        else:
            self.btn_bg.pos = self.scan_btn.pos

    def add_node(self, text, index):
        angle = math.radians(index * 60 + 150) # Distribute around center
        dist = dp(200)
        target_x = self.center_node.center_x + math.cos(angle) * dist - dp(75)
        target_y = self.center_node.center_y + math.sin(angle) * dist - dp(25)

        node = GraphNode(text=text, pos=(target_x, target_y))

        # Draw connection first so it's behind the node
        conn = BezierConnection(self.center_node.center, node.center)
        self.graph_layer.add_widget(conn)

        self.graph_layer.add_widget(node)
        node.animate_in()

if __name__ == '__main__':
    OSINTApp().run()
