import sys
import asyncio
from pymem import Pymem
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from pc_esp import ESPOverlay
from smart_reel import ReelController
from bot_handler import TelegramReporter
from vision import RodTipDetector

class RF4Bot:
    def __init__(self, telegram_token=None, telegram_chat_id=None):
        self.pm = None
        self.process_name = "rf4_x64.exe"

        # Components
        self.reel_controller = ReelController()
        self.detector = RodTipDetector()
        self.reporter = None
        if telegram_token and telegram_chat_id:
            self.reporter = TelegramReporter(telegram_token, telegram_chat_id)

        # Memory Addresses (Placeholders)
        self.addr_fish_name = 0x0
        self.addr_weight = 0x0
        self.addr_tension = 0x0
        self.addr_distance = 0x0
        self.addr_fatigue = 0x0
        self.addr_is_caught = 0x0

        self.last_caught_state = False

    def attach(self):
        try:
            self.pm = Pymem(self.process_name)
            print(f"Attached to {self.process_name}")
            return True
        except Exception as e:
            print(f"Could not attach to {self.process_name}: {e}")
            return False

    def read_game_data(self):
        if not self.pm:
            # Return dummy/mock data if not attached for development/testing
            return {
                "name": "Common Carp (Simulated)",
                "weight": 12.5,
                "tension": 45,
                "distance": 25.0,
                "fatigue": 30,
                "is_caught": False
            }

        try:
            # In production, these addresses must be updated via memory scanning
            data = {
                "name": self.pm.read_string(self.addr_fish_name) if self.addr_fish_name != 0 else "Unknown",
                "weight": self.pm.read_float(self.addr_weight) if self.addr_weight != 0 else 0.0,
                "tension": self.pm.read_int(self.addr_tension) if self.addr_tension != 0 else 0,
                "distance": self.pm.read_float(self.addr_distance) if self.addr_distance != 0 else 0.0,
                "fatigue": self.pm.read_int(self.addr_fatigue) if self.addr_fatigue != 0 else 0,
                "is_caught": self.pm.read_bool(self.addr_is_caught) if self.addr_is_caught != 0 else False
            }
            return data
        except Exception as e:
            print(f"Error reading memory: {e}")
            return None

    async def run_loop(self, overlay):
        print("Bot loop started.")
        while True:
            game_data = self.read_game_data()

            # 1. Computer Vision: Find rod tip
            try:
                rod_tip_rect = self.detector.detect()
            except:
                rod_tip_rect = None

            # 2. Update Overlay
            overlay.update_data(
                game_data['name'],
                game_data['weight'],
                game_data['tension'],
                game_data['distance'],
                rod_tip_rect
            )

            # 3. AI Reel Logic
            self.reel_controller.update(game_data['tension'], game_data['fatigue'])

            # 4. Telegram Reporting
            if game_data['is_caught'] and not self.last_caught_state:
                if self.reporter:
                    await self.reporter.report_catch({
                        "name": game_data['name'],
                        "weight": game_data['weight'],
                        "dist": game_data['distance'],
                        "fatigue": game_data['fatigue'],
                        "is_trophy": game_data['weight'] > 10.0
                    })

            self.last_caught_state = game_data['is_caught']
            await asyncio.sleep(0.05)

def main():
    # User should set these via environment variables or direct input
    import os
    TELEGRAM_TOKEN = os.getenv("RF4_TG_TOKEN", "YOUR_TOKEN_HERE")
    TELEGRAM_CHAT_ID = os.getenv("RF4_TG_CHAT_ID", "YOUR_CHAT_ID_HERE")

    app = QApplication(sys.argv)

    # Use qasync for the event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    overlay = ESPOverlay()
    overlay.show()

    bot = RF4Bot(telegram_token=TELEGRAM_TOKEN, telegram_chat_id=TELEGRAM_CHAT_ID)
    bot.attach()

    with loop:
        loop.create_task(bot.run_loop(overlay))
        loop.run_forever()

if __name__ == "__main__":
    main()
