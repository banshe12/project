import asyncio
import random
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.factory import Factory

# Import custom components
from particle_background import ParticleBackground
from spiderweb_graph import SpiderwebGraph
from glitch_button import GlitchButton
from scanning_laser import ScanningLaser
from result_transitions import animate_fade_slide_up
from username_checker import UsernameChecker
from ip_lookup import IPLookup
from exif_extractor import EXIFExtractor

KV = """
<GlassCard@BoxLayout>:
    orientation: 'vertical'
    padding: 15
    spacing: 10
    opacity: 0
    size_hint_y: None
    height: 150
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 0.6
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,]
        # Neon Border
        Color:
            rgba: 0, 1, 0.5, 0.3
        Line:
            width: 1.2
            rounded_rectangle: self.x, self.y, self.width, self.height, 15

<CyberInput@TextInput>:
    background_color: 0, 0, 0, 0.5
    foreground_color: 0, 1, 0.5, 1
    cursor_color: 0, 1, 0.5, 1
    padding: [10, 10]
    multiline: False
    canvas.after:
        Color:
            rgba: 0, 1, 0.5, 0.5
        Line:
            width: 1.2
            rectangle: self.x, self.y, self.width, self.height

<OSINTAppWidget>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.02, 0.02, 0.02, 1
        Rectangle:
            pos: self.pos
            size: self.size

    FloatLayout:
        id: main_container

        # High-performance Particle Background
        ParticleBackground:
            id: particle_bg
            size_hint: (1, 1)

        # Scanning Laser (Initial position off-screen)
        ScanningLaser:
            id: scanning_laser
            size_hint: (1, 1)

        # Main UI Overlay
        BoxLayout:
            orientation: 'vertical'
            padding: [20, 20, 20, 20]
            spacing: 20

            Label:
                text: "DEEP CYBERPUNK OSINT TOOL"
                font_size: '24sp'
                bold: True
                color: 0, 1, 0.5, 1
                size_hint_y: None
                height: 50

            BoxLayout:
                size_hint_y: None
                height: 50
                spacing: 10
                CyberInput:
                    id: search_input
                    hint_text: "Enter Username, IP, or Image Path"
                    hint_text_color: 0, 1, 0.5, 0.5

                GlitchButton:
                    text: "SCAN"
                    size_hint_x: 0.3
                    on_release: app.run_scan(search_input.text)
                    background_color: 0, 0, 0, 0
                    color: 0, 1, 0.5, 1
                    bold: True
                    canvas.before:
                        Color:
                            rgba: 0, 1, 0.5, 1
                        Line:
                            width: 1.5
                            rectangle: self.x, self.y, self.width, self.height

            # Graph Visualization Area
            SpiderwebGraph:
                id: spiderweb_graph
                size_hint: (1, 1)

            # Results View
            ScrollView:
                size_hint_y: 0.4
                BoxLayout:
                    id: results_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: 10
                    spacing: 15
"""

class OSINTAppWidget(BoxLayout):
    pass

class MainApp(App):
    def build(self):
        Builder.load_string(KV)
        self.root_widget = OSINTAppWidget()
        self.username_checker = UsernameChecker()
        self.ip_lookup = IPLookup()
        self.exif_extractor = EXIFExtractor()
        return self.root_widget

    def add_result_card(self, title, content):
        container = self.root_widget.ids.results_container
        card = Factory.GlassCard()

        title_label = Label(text=title, bold=True, color=[0, 1, 0.5, 1], size_hint_y=None, height=30, halign='left', text_size=(container.width - 40, None))
        content_label = Label(text=content, color=[1, 1, 1, 1], size_hint_y=None, height=100, halign='left', valign='top', text_size=(container.width - 40, None))

        card.add_widget(title_label)
        card.add_widget(content_label)
        container.add_widget(card)

        # Animation: Fade-in and Slide-up
        animate_fade_slide_up(card)

    def run_scan(self, query):
        if not query:
            return

        self.root_widget.ids.results_container.clear_widgets()
        self.root_widget.ids.spiderweb_graph.clear_graph()
        self.root_widget.ids.scanning_laser.start()

        # Async logic
        asyncio.create_task(self.perform_scan(query))

    async def perform_scan(self, query):
        # Determine query type (very simple heuristic)
        if query.replace('.', '').isdigit() or (query.count('.') == 3 and all(p.isdigit() for p in query.split('.'))): # Likely IP
            result = await self.ip_lookup.lookup(query)
            if result['status'] == 'Found':
                data = result['data']
                content = f"ISP: {data.get('isp')}\nLocation: {data.get('city')}, {data.get('country')}\nLat/Lon: {data.get('lat')}, {data.get('lon')}"
                self.add_result_card("IP LOOKUP FOUND", content)
                self.root_widget.ids.spiderweb_graph.add_data(f"IP: {query}", {
                    "ISP": data.get('isp'),
                    "Country": data.get('country'),
                    "City": data.get('city'),
                    "Lat/Lon": f"{data.get('lat')}, {data.get('lon')}"
                })
            else:
                self.add_result_card("IP LOOKUP ERROR", result.get('message', 'Unknown error'))
        elif '.' in query and (query.lower().endswith('.jpg') or query.lower().endswith('.jpeg')): # Likely Image Path
             result = self.exif_extractor.extract(query)
             if result['status'] == 'Found':
                 meta = result['metadata']
                 content = "\n".join([f"{k}: {v[:30]}..." for k, v in list(meta.items())[:5]])
                 if result['coords']:
                     content += f"\nCOORDS: {result['coords']}"
                 self.add_result_card("EXIF DATA EXTRACTED", content)
                 graph_data = {k: v[:20] for k, v in list(meta.items())[:4]}
                 if result['coords']:
                     graph_data["COORDS"] = str(result['coords'])
                 self.root_widget.ids.spiderweb_graph.add_data("EXIF SOURCE", graph_data)
             else:
                 self.add_result_card("EXIF ERROR", result.get('message', 'File not found or no EXIF'))
        else: # Default to Username
            found = await self.username_checker.check_username(query)
            if found:
                content = "\n".join([f"{res['platform']}: {res['url']}" for res in found[:5]])
                self.add_result_card(f"USERNAME FOUND: {query}", content)
                graph_data = {res['platform']: res['url'] for res in found[:6]}
                self.root_widget.ids.spiderweb_graph.add_data(f"USER: {query}", graph_data)
            else:
                self.add_result_card("SEARCH COMPLETE", f"No public data found for '{query}'")

        self.root_widget.ids.scanning_laser.stop()

if __name__ == '__main__':
    # Use Kivy's async_run
    async def main():
        app = MainApp()
        await app.async_run()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
