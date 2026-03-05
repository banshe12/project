import cv2
import numpy as np
import pyautogui
from PyQt6.QtCore import QRect

class RodTipDetector:
    def __init__(self):
        # Range for rod tip color (e.g., bright orange or green common in RF4)
        # These would be tuned for the specific rod tip in game
        self.lower_color = np.array([0, 100, 100])
        self.upper_color = np.array([10, 255, 255])

    def detect(self):
        # Take a screenshot of the main monitor
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour which we assume is the rod tip
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            # Add some padding
            padding = 10
            return QRect(x - padding, y - padding, w + 2*padding, h + 2*padding)

        return QRect(0, 0, 0, 0)
