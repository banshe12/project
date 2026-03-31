import sys
import os
import time
import random
import string
import struct
import threading
from dataclasses import dataclass
from typing import List, Optional
import pymem
import pymem.process
import keyboard
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QCheckBox, QLabel, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QObject, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

# Offsets provided
OFFSETS = {
    "dwEntityList": 38470232,
    "dwLocalPlayerPawn": 33991136,
    "dwViewMatrix": 36769552,
    "m_iHealth": 0x32C,
    "m_iTeamNum": 0x3CB,
    "m_vOldOrigin": 0x127C,
    "m_hPlayerPawn": 0x7E4,
    "dwWindowWidth": 9492888,
    "dwWindowHeight": 9492892
}

def generate_junk_code(length: int = 10):
    """
    Junk Code generator to randomize the binary signature.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def active_junk():
    """
    Active junk code to vary execution flow slightly.
    """
    _ = [random.randint(0, 255) for _ in range(5)]
    return sum(_)

class MemoryManager:
    def __init__(self, process_name="cs2.exe"):
        self.process_name = process_name
        self.pm = None
        self.client_base = None
        self.engine_base = None

    def attach(self):
        try:
            self.pm = pymem.Pymem(self.process_name)
            self.client_base = pymem.process.module_from_name(self.pm.process_handle, "client.dll").lpBaseOfDll
            self.engine_base = pymem.process.module_from_name(self.pm.process_handle, "engine2.dll").lpBaseOfDll
            return True
        except Exception as e:
            # print(f"Failed to attach: {e}")
            return False

    def read_int(self, address):
        try:
            return self.pm.read_int(address)
        except:
            return 0

    def read_float(self, address):
        try:
            return self.pm.read_float(address)
        except:
            return 0.0

    def read_uint64(self, address):
        try:
            return self.pm.read_ulonglong(address)
        except:
            return 0

    def read_vec3(self, address):
        try:
            data = self.pm.read_bytes(address, 12)
            return struct.unpack("3f", data)
        except:
            return (0.0, 0.0, 0.0)

    def read_matrix(self, address):
        try:
            data = self.pm.read_bytes(address, 64)
            return struct.unpack("16f", data)
        except:
            return [0.0] * 16

    def get_screen_resolution(self):
        try:
            width = self.read_int(self.engine_base + OFFSETS["dwWindowWidth"])
            height = self.read_int(self.engine_base + OFFSETS["dwWindowHeight"])
            return width, height
        except:
            return 1920, 1080

def world_to_screen(matrix, pos, width, height):
    """
    Transforms world coordinates to screen coordinates using the view matrix.
    Standard W2S logic for Source 2.
    """
    w = matrix[12] * pos[0] + matrix[13] * pos[1] + matrix[14] * pos[2] + matrix[15]
    if w < 0.001:
        return None

    x = matrix[0] * pos[0] + matrix[1] * pos[1] + matrix[2] * pos[2] + matrix[3]
    y = matrix[4] * pos[0] + matrix[5] * pos[1] + matrix[6] * pos[2] + matrix[7]

    nx = x / w
    ny = y / w

    sx = (width / 2) * nx + (width / 2)
    sy = -(height / 2) * ny + (height / 2)

    return (sx, sy)

class ESPOverlay(QMainWindow):
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.entities = []
        self.lock = threading.Lock()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.update_resolution()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(7) # ~144Hz

    def update_resolution(self):
        w, h = self.memory_manager.get_screen_resolution()
        self.screen_width = w
        self.screen_height = h
        self.setGeometry(0, 0, w, h)

    def update_data(self):
        # Periodically check resolution
        if random.random() < 0.01: # Check occasionally
            self.update_resolution()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Cyan accent
        pen = QPen(QColor(0, 206, 209), 2)
        painter.setPen(pen)

        with self.lock:
            for entity in self.entities:
                self.draw_esp(painter, entity)

    def draw_esp(self, painter, entity):
        if not entity.screen_pos:
            return

        active_junk()

        x, y = entity.screen_pos

        # Simple dynamic box sizing logic
        # Height based on distance or constant for simplicity
        h = 100
        w = 50

        # Snaplines
        if hasattr(self, 'main_menu') and self.main_menu.snaplines.isChecked():
            painter.drawLine(int(self.screen_width / 2), int(self.screen_height), int(x), int(y))

        # Master ESP check
        if hasattr(self, 'main_menu') and self.main_menu.master_esp.isChecked():
            painter.drawRect(int(x - w/2), int(y - h), int(w), int(h))

@dataclass
class Entity:
    pos: tuple
    health: int
    team: int
    screen_pos: Optional[tuple] = None

class MemoryThread(threading.Thread):
    def __init__(self, memory_manager, overlay):
        super().__init__()
        self.mm = memory_manager
        self.overlay = overlay
        self.running = True
        self.daemon = True

    def run(self):
        while self.running:
            try:
                active_junk()
                if not self.mm.pm:
                    time.sleep(1)
                    continue

                # View Matrix for W2S
                view_matrix = self.mm.read_matrix(self.mm.client_base + OFFSETS["dwViewMatrix"])

                # Local player info
                local_player = self.mm.read_uint64(self.mm.client_base + OFFSETS["dwLocalPlayerPawn"])
                if not local_player:
                    time.sleep(0.1)
                    continue
                local_team = self.mm.read_int(local_player + OFFSETS["m_iTeamNum"])

                # Entity List for players
                entity_list = self.mm.read_uint64(self.mm.client_base + OFFSETS["dwEntityList"])
                if not entity_list:
                    continue

                temp_entities = []
                for i in range(1, 64): # Basic player loop
                    try:
                        # 1. Get Controller from Entity List
                        list_entry = self.mm.read_uint64(entity_list + (8 * (i & 0x7FFF) >> 9) + 16)
                        if not list_entry: continue

                        controller_ptr = self.mm.read_uint64(list_entry + 120 * (i & 0x1FF))
                        if not controller_ptr: continue

                        # 2. Get Pawn handle from Controller
                        pawn_handle = self.mm.read_int(controller_ptr + OFFSETS["m_hPlayerPawn"])
                        if not pawn_handle: continue

                        # 3. Get Pawn pointer from handle
                        pawn_list_entry = self.mm.read_uint64(entity_list + (8 * (pawn_handle & 0x7FFF) >> 9) + 16)
                        if not pawn_list_entry: continue

                        pawn_ptr = self.mm.read_uint64(pawn_list_entry + 120 * (pawn_handle & 0x1FF))
                        if not pawn_ptr or pawn_ptr == local_player: continue

                        # 4. Read Pawn data
                        health = self.mm.read_int(pawn_ptr + OFFSETS["m_iHealth"])
                        if health <= 0 or health > 100: continue

                        team = self.mm.read_int(pawn_ptr + OFFSETS["m_iTeamNum"])
                        if team == local_team: continue # ESP only for enemies

                        origin = self.mm.read_vec3(pawn_ptr + OFFSETS["m_vOldOrigin"])

                        # Apply W2S
                        screen_pos = world_to_screen(view_matrix, origin, self.overlay.screen_width, self.overlay.screen_height)

                        temp_entities.append(Entity(pos=origin, health=health, team=team, screen_pos=screen_pos))
                    except:
                        continue

                with self.overlay.lock:
                    self.overlay.entities = temp_entities
                time.sleep(0.005) # ~200Hz
            except Exception as e:
                time.sleep(1)

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Silence Theme - " + generate_junk_code(8))
        self.setFixedSize(650, 420)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #0d1117; color: #ffffff;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(150)
        sidebar.setStyleSheet("background-color: #090c10; border-right: 1px solid #00ced1;")
        sidebar_layout = QVBoxLayout(sidebar)

        self.tabs = QStackedWidget()

        # Tab Buttons
        self.btn_aim = self.create_sidebar_button("AimBot", 0)
        self.btn_visuals = self.create_sidebar_button("Visuals", 1)
        self.btn_misc = self.create_sidebar_button("Misc", 2)

        sidebar_layout.addWidget(self.btn_aim)
        sidebar_layout.addWidget(self.btn_visuals)
        sidebar_layout.addWidget(self.btn_misc)
        sidebar_layout.addStretch()

        # Tabs Implementation
        self.setup_aimbot_tab()
        self.setup_visuals_tab()
        self.setup_misc_tab()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.tabs)

    def create_sidebar_button(self, name, index):
        btn = QPushButton(name)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                color: #00ced1;
            }
        """)
        btn.clicked.connect(lambda: self.tabs.setCurrentIndex(index))
        return btn

    def setup_aimbot_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("AimBot Settings"))
        layout.addStretch()
        self.tabs.addWidget(tab)

    def setup_visuals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.master_esp = QCheckBox("Master ESP")
        self.snaplines = QCheckBox("Snaplines")

        checkbox_style = """
            QCheckBox { spacing: 10px; color: #ffffff; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #00ced1; }
            QCheckBox::indicator:checked { background-color: #00ced1; }
        """
        self.master_esp.setStyleSheet(checkbox_style)
        self.snaplines.setStyleSheet(checkbox_style)

        layout.addWidget(self.master_esp)
        layout.addWidget(self.snaplines)
        layout.addStretch()
        self.tabs.addWidget(tab)

    def setup_misc_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Misc Settings"))
        layout.addStretch()
        self.tabs.addWidget(tab)

class KeyHandler(QObject):
    toggle_signal = pyqtSignal()

def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if os.name == 'nt' and not is_admin():
        print("Error: This script must be run as Administrator to access game memory.")
        sys.exit(1)

    app = QApplication(sys.argv)

    mm = MemoryManager()
    while not mm.attach():
        # print("Waiting for CS2...")
        time.sleep(2)

    overlay = ESPOverlay(mm)
    menu = MainMenu()
    overlay.main_menu = menu

    memory_thread = MemoryThread(mm, overlay)
    memory_thread.start()

    key_handler = KeyHandler()

    def on_toggle():
        if menu.isVisible():
            menu.hide()
        else:
            menu.show()
            menu.raise_()
            menu.activateWindow()

    key_handler.toggle_signal.connect(on_toggle)
    keyboard.add_hotkey('insert', lambda: key_handler.toggle_signal.emit())

    overlay.showFullScreen()
    menu.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
