import sys
import time

class MockPymem:
    def __init__(self, process_name):
        self.process_name = process_name
    def read_string(self, addr): return "Mock Fish"
    def read_float(self, addr): return 5.5
    def read_int(self, addr): return 45
    def read_bool(self, addr): return False

def get_mock_game_data(counter):
    """Simulates game states based on a counter."""
    # Simulation:
    # 0-10: normal reeling
    # 11-15: high tension
    # 16-20: low tension, high fatigue
    # 21: catch

    data = {
        "name": "Common Carp",
        "weight": 12.5,
        "tension": 45,
        "distance": 25.0,
        "fatigue": 30,
        "is_caught": False
    }

    if 11 <= counter <= 15:
        data["tension"] = 95
    elif 16 <= counter <= 20:
        data["tension"] = 40
        data["fatigue"] = 60
    elif counter >= 21:
        data["is_caught"] = True

    return data
