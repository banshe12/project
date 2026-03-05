import sys
import time

# Mocking pydirectinput for non-Windows environments
class MockPyDirectInput:
    FAILSAFE = True
    def keyDown(self, key): pass
    def keyUp(self, key): pass
    def mouseDown(self, button): pass
    def mouseUp(self, button): pass
    def press(self, key): pass

try:
    import pydirectinput
except (AttributeError, ImportError, KeyError):
    pydirectinput = MockPyDirectInput()

class ReelController:
    def __init__(self):
        pydirectinput.FAILSAFE = True
        self.is_reeling = False
        self.last_tension = 0
        self.last_update_time = time.time()
        self.friction_level = 20 # Assume starting friction

    def update(self, tension, fatigue):
        """
        Algorithm:
        - If Tension > 90% OR Sudden Jerk -> Release reel instantly.
        - If Tension < 60% AND FishFatigue > 50% -> Forced reeling (pumping).
        """
        current_time = time.time()
        dt = current_time - self.last_update_time

        # 1. Sudden Jerk Detection
        jerk = 0
        if dt > 0:
            jerk = (tension - self.last_tension) / dt

        # 2. Release Reel if tension is too high OR sudden jerk
        if tension > 90 or jerk > 100: # Threshold for jerk
            if self.is_reeling:
                self.stop_reeling()
                print(f"[AI] {'High Tension' if tension > 90 else 'Sudden Jerk'}! Releasing reel.")

            # Reduce friction
            self.lower_friction()

        # 3. Forced reeling (pumping)
        elif tension < 60 and fatigue > 50:
            if not self.is_reeling:
                self.start_reeling()
                print("[AI] Low tension & high fatigue. Pumping...")
            # Pumping often involves raising the rod too, but here we focus on reeling

        # 4. Maintain reeling in normal conditions
        elif tension < 85:
             if not self.is_reeling:
                self.start_reeling()

             # Increase friction if tension is too low
             if tension < 30:
                 self.raise_friction()

        self.last_tension = tension
        self.last_update_time = current_time

    def start_reeling(self):
        pydirectinput.keyDown('shift')
        pydirectinput.mouseDown(button='left')
        self.is_reeling = True

    def stop_reeling(self):
        pydirectinput.keyUp('shift')
        pydirectinput.mouseUp(button='left')
        self.is_reeling = False

    def lower_friction(self):
        # In RF4, friction is often adjusted with mouse wheel or specific keys
        # We simulate the 'R' key as requested
        print("[AI] Lowering friction (R)")
        pydirectinput.press('r')
        # Here we could add logic to scroll down while R is held if that's the game mechanic

    def raise_friction(self):
        print("[AI] Raising friction (R)")
        # Placeholder for raising friction logic
        pass

if __name__ == "__main__":
    controller = ReelController()
    controller.update(95, 20)
    time.sleep(0.1)
    controller.update(40, 60)
