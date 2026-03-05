import unittest
from smart_reel import ReelController
from unittest.mock import MagicMock, patch
import time

class TestSmartReel(unittest.TestCase):
    def setUp(self):
        self.controller = ReelController()
        # Mocking the actual key presses
        self.controller.start_reeling = MagicMock()
        self.controller.stop_reeling = MagicMock()
        self.controller.lower_friction = MagicMock()
        self.controller.raise_friction = MagicMock()

    def test_high_tension_release(self):
        self.controller.is_reeling = True
        self.controller.update(tension=95, fatigue=20)
        self.controller.stop_reeling.assert_called_once()
        self.controller.lower_friction.assert_called_once()

    def test_low_tension_pumping(self):
        self.controller.is_reeling = False
        self.controller.last_tension = 40
        self.controller.last_update_time = time.time() - 1.0
        self.controller.update(tension=40, fatigue=60)
        self.controller.start_reeling.assert_called_once()

    def test_normal_reeling(self):
        self.controller.is_reeling = False
        self.controller.last_tension = 70
        self.controller.last_update_time = time.time() - 1.0
        self.controller.update(tension=70, fatigue=20)
        self.controller.start_reeling.assert_called_once()

    def test_sudden_jerk_release(self):
        self.controller.is_reeling = True
        self.controller.last_tension = 10
        self.controller.last_update_time = time.time() - 0.1
        # Tension jumped from 10 to 60 in 0.1s -> jerk = 500
        self.controller.update(tension=60, fatigue=20)
        self.controller.stop_reeling.assert_called_once()
        self.controller.lower_friction.assert_called_once()

if __name__ == "__main__":
    unittest.main()
