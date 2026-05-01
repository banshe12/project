import cv2
import numpy as np
import pyautogui
import time
import random

try:
    import winsound
except ImportError:
    winsound = None

# --- Configuration ---
# Keys
KEY_INTERACT = 'e'
KEY_FORWARD = 'w'
KEY_LEFT = 'a'
KEY_RIGHT = 'd'
KEY_FINISH = 'r'

# Timing
MIN_DELAY = 0.1
MAX_DELAY = 0.4

# HSV Color Ranges (Placeholder values, need calibration in-game)
# Cyan/Blue for navigation arrows
LOWER_CYAN = np.array([80, 100, 100])
UPPER_CYAN = np.array([130, 255, 255])

# Green for finish pillar
LOWER_GREEN = np.array([40, 100, 100])
UPPER_GREEN = np.array([80, 255, 255])

# Thresholds
STUCK_THRESHOLD_SECONDS = 10
PRICE_THRESHOLD = 3000

# OCR/Template Regions (Placeholders)
# Coordinates depend on screen resolution
PRICE_ROI = (100, 100, 200, 50) # (x, y, w, h)
# UI Button Positions (Example for 1920x1080)
ACCEPT_BUTTON_COORD = (960, 600)
CANCEL_BUTTON_COORD = (100, 900)
ORDER_LIST_POS = (960, 400)

def random_sleep(min_s=MIN_DELAY, max_s=MAX_DELAY):
    """Adds a random delay to simulate human behavior."""
    time.sleep(random.uniform(min_s, max_s))

def press_key(key, duration=None):
    """Presses a key with optional duration and random sleep."""
    if duration:
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
    else:
        pyautogui.press(key)
    random_sleep()

class TruckerBot:
    def __init__(self):
        self.is_running = True
        self.last_move_time = time.time()
        self.last_frame = None
        # Track key states to avoid jitter
        self.key_states = {
            KEY_FORWARD: False,
            KEY_LEFT: False,
            KEY_RIGHT: False
        }

    def _set_key(self, key, state):
        """Sets the key state and only calls pyautogui if state changed."""
        if self.key_states.get(key) != state:
            if state:
                pyautogui.keyDown(key)
            else:
                pyautogui.keyUp(key)
            self.key_states[key] = state

    def capture_screen(self, region=None):
        """Captures a screenshot and converts it to OpenCV BGR format."""
        try:
            screenshot = pyautogui.screenshot(region=region)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def play_beep(self):
        """Triggers a loud beep sound."""
        if winsound:
            winsound.Beep(1000, 1000)
        else:
            print("\a") # PC speaker beep fallback

    def get_navigation_direction(self):
        """Analyzes the screen center to find blue/cyan navigation arrows."""
        frame = self.capture_screen()
        h, w, _ = frame.shape
        center_x = w // 2

        # Region of Interest: Middle third of the screen horizontally and vertically
        roi = frame[h//3:2*h//3, :]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_CYAN, UPPER_CYAN)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < 100:
            return None

        M = cv2.moments(largest_contour)
        if M["m00"] == 0: return None
        cX = int(M["m10"] / M["m00"])

        tolerance = 60 # Pixels from center to be considered 'Forward'

        if cX < center_x - tolerance:
            return "LEFT"
        elif cX > center_x + tolerance:
            return "RIGHT"
        else:
            return "CENTER"

    def get_order_price(self):
        """
        Detects the price of the order in the menu using OCR or Template Matching.
        """
        roi_frame = self.capture_screen(region=PRICE_ROI)
        gray_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

        # Method 1: OCR (Requires pytesseract)
        try:
            import pytesseract
            # Convert to grayscale and threshold for better OCR
            _, thresh = cv2.threshold(gray_roi, 150, 255, cv2.THRESH_BINARY_INV)
            text = pytesseract.image_to_string(thresh, config='--psm 7 digits')
            # Extract numbers only
            price_str = ''.join(filter(str.isdigit, text))
            if price_str:
                return int(price_str)
        except (ImportError, Exception):
            pass

        # Method 2: Template Matching (Fallback/Native Stack)
        # Note: In a real environment, you would have small image files for digits '0'-'9'
        # This implementation shows how to use cv2.matchTemplate
        try:
            detected_price = ""
            # Placeholder: loop through digit templates 0-9
            # for digit in range(10):
            #     template = cv2.imread(f'templates/{digit}.png', 0)
            #     res = cv2.matchTemplate(gray_roi, template, cv2.TM_CCOEFF_NORMED)
            #     ... logic to find digit positions and reconstruct the price ...

            # Simple threshold check for "> 3000" if full OCR is too complex
            # Check for specific price patterns if they are static
            pass
        except Exception:
            pass

        return 0 # Default if detection fails

    def is_finish_available(self):
        """Checks for the green light pillar or 'Hold R to finish' text."""
        frame = self.capture_screen()

        # Color-based detection for the green light pillar
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_green = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
        green_count = cv2.countNonZero(mask_green)

        # Logic: if enough green pixels are found, assume we reached the finish
        if green_count > 1000:
            return True
        return False

    def reroll_orders(self):
        """Finds a profitable order or rerolls by accepting and cancelling."""
        while self.is_running:
            print("Opening menu...")
            press_key(KEY_INTERACT)
            time.sleep(1.5) # Wait for UI animation

            price = self.get_order_price()
            print(f"Order price detected: {price}")

            if price > PRICE_THRESHOLD:
                print("Profitable order found! Accepting...")
                pyautogui.click(ACCEPT_BUTTON_COORD)
                random_sleep()
                return True
            else:
                print("Price too low. Rerolling (Take -> Cancel -> Retry)...")
                # Step 1: Click on any order to select it
                pyautogui.click(ORDER_LIST_POS)
                random_sleep(0.2, 0.4)
                # Step 2: Click Accept
                pyautogui.click(ACCEPT_BUTTON_COORD)
                random_sleep(1.0, 1.5)

                print("Cancelling current order to reset menu...")
                # Step 3: Click Cancel/Abandon in the menu
                pyautogui.click(CANCEL_BUTTON_COORD)
                random_sleep(0.5, 1.0)

                # Loop continues to press 'E' again

    def board_truck(self):
        """Sequence to enter the vehicle: hold W for 1s while spamming E."""
        print("Boarding the truck...")
        pyautogui.keyDown(KEY_FORWARD)
        start_time = time.time()
        while time.time() - start_time < 1.0:
            pyautogui.press(KEY_INTERACT)
            time.sleep(0.05)
        pyautogui.keyUp(KEY_FORWARD)
        random_sleep()

    def steer(self):
        """Converts visual navigation cues into keyboard inputs."""
        direction = self.get_navigation_direction()

        if direction == "LEFT":
            print("Steering: LEFT")
            self._set_key(KEY_RIGHT, False)
            self._set_key(KEY_LEFT, True)
            self._set_key(KEY_FORWARD, True)
        elif direction == "RIGHT":
            print("Steering: RIGHT")
            self._set_key(KEY_LEFT, False)
            self._set_key(KEY_RIGHT, True)
            self._set_key(KEY_FORWARD, True)
        elif direction == "CENTER":
            print("Steering: FORWARD")
            self._set_key(KEY_LEFT, False)
            self._set_key(KEY_RIGHT, False)
            self._set_key(KEY_FORWARD, True)
        else:
            print("No navigation data. Idling...")
            self._set_key(KEY_LEFT, False)
            self._set_key(KEY_RIGHT, False)
            self._set_key(KEY_FORWARD, False)

    def check_stuck(self, current_frame):
        """Anti-Stuck: Checks if the visual stream is static while moving."""
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        if self.last_frame is None:
            self.last_frame = gray
            self.last_move_time = time.time()
            return False

        # Calculate difference between frames
        diff = cv2.absdiff(self.last_frame, gray)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        change_ratio = np.sum(thresh) / thresh.size

        if change_ratio > 0.005: # Movement detected
            self.last_frame = gray
            self.last_move_time = time.time()
            return False

        # If no movement for STUCK_THRESHOLD_SECONDS
        if time.time() - self.last_move_time > STUCK_THRESHOLD_SECONDS:
            return True
        return False

    def detect_obstacle(self, frame):
        """
        Detects obstacles in front of the vehicle.
        Uses Canny edge detection to find sudden large vertical edges or blocks.
        """
        h, w, _ = frame.shape
        # ROI: Lower-middle part of the screen where obstacles (walls, cars) appear
        roi = frame[h//2:3*h//4, w//4:3*w//4]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # If too many edges are detected in front, it might be an obstacle
        edge_density = np.sum(edges > 0) / edges.size
        if edge_density > 0.05: # Threshold for 'blocked'
            return True
        return False

    def finish_delivery(self):
        """Finalizes the delivery by holding R."""
        print("Finish point reached! Completing delivery...")
        self._set_key(KEY_FORWARD, False)
        self._set_key(KEY_LEFT, False)
        self._set_key(KEY_RIGHT, False)

        print("Holding R to finish...")
        press_key(KEY_FINISH, duration=5.0)
        print("Delivery complete.")

    def run(self):
        """Main operational loop."""
        print("Trucker Bot starting in 5 seconds. Switch to Roblox!")
        time.sleep(5)

        try:
            while self.is_running:
                if self.reroll_orders():
                    self.board_truck()

                    driving = True
                    self.last_frame = None
                    self.last_move_time = time.time()

                    while driving:
                        frame = self.capture_screen()

                        # Check for delivery finish
                        if self.is_finish_available():
                            self.finish_delivery()
                            driving = False
                            continue

                        # Anti-Stuck & Obstacle check
                        if self.check_stuck(frame) or self.detect_obstacle(frame):
                            print("Я застрял, помоги!")
                            self.play_beep()
                            # Stop movement to wait for help
                            self._set_key(KEY_FORWARD, False)
                            self._set_key(KEY_LEFT, False)
                            self._set_key(KEY_RIGHT, False)
                            time.sleep(5)
                            self.last_move_time = time.time()
                            continue

                        # Navigation
                        self.steer()
                        random_sleep(0.1, 0.2)

        except KeyboardInterrupt:
            print("Bot stopped by user.")
        finally:
            # Safety cleanup: release all keys
            for key in [KEY_FORWARD, KEY_LEFT, KEY_RIGHT, KEY_FINISH]:
                pyautogui.keyUp(key)

if __name__ == "__main__":
    bot = TruckerBot()
    # bot.run() # Uncomment to run
    print("Trucker Bot ready.")
