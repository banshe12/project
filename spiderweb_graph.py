import math
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty
from osint_node import OSINTNode
from bezier_connection import BezierConnection

class SpiderwebGraph(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nodes = []
        self.connections = []

    def clear_graph(self):
        self.clear_widgets()
        self.nodes = []
        self.connections = []

    def add_data(self, root_text, data_points):
        self.clear_graph()

        # Central node
        root_node = OSINTNode(text=root_text)
        root_node.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.add_widget(root_node)
        self.nodes.append(root_node)

        num_points = len(data_points)
        radius = 200 # Fixed radius for radial layout

        for i, (key, value) in enumerate(data_points.items()):
            node_text = f"{key.upper()}:\n{value}"
            node = OSINTNode(text=node_text)
            # Start at root center for "shooting out" animation effect
            node.center = root_node.center
            node.opacity = 0
            self.add_widget(node)
            self.nodes.append(node)

            # Connection
            conn = BezierConnection(node_start=root_node, node_end=node)
            conn.opacity = 0
            self.add_widget(conn)
            self.connections.append(conn)

        # Trigger initial layout update once size is known
        self.bind(size=self.update_layout)

    def update_layout(self, *args):
        if not self.nodes:
            return

        root_node = self.nodes[0]
        root_node.center = self.center

        child_nodes = self.nodes[1:]
        num_points = len(child_nodes)
        radius = min(self.width, self.height) * 0.3

        for i, node in enumerate(child_nodes):
            angle = (2 * math.pi * i) / num_points if num_points > 0 else 0
            target_x = root_node.center_x + radius * math.cos(angle)
            target_y = root_node.center_y + radius * math.sin(angle)

            # Animate shooting out
            from kivy.animation import Animation
            anim = Animation(center_x=target_x, center_y=target_y, opacity=1, duration=0.8, t='out_back')
            anim.start(node)

            # Find and animate corresponding connection
            for conn in self.connections:
                if conn.node_end == node:
                    anim_conn = Animation(opacity=1, duration=1.0)
                    anim_conn.start(conn)

    def update_layout_static(self, *args):
        if not self.nodes:
            return

        root_node = self.nodes[0]
        # Recenter root
        root_node.center = self.center

        child_nodes = self.nodes[1:]
        num_points = len(child_nodes)
        radius = min(self.width, self.height) * 0.3

        for i, node in enumerate(child_nodes):
            angle = (2 * math.pi * i) / num_points if num_points > 0 else 0
            node.center_x = root_node.center_x + radius * math.cos(angle)
            node.center_y = root_node.center_y + radius * math.sin(angle)

if __name__ == "__main__":
    print("SpiderwebGraph loaded")
