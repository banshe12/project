import time
from ai_brain import AIBrain

# --- Android 14 Service & Overlay (pyjnius skeleton) ---
class AICommanderService:
    def __init__(self):
        self.brain = AIBrain()
        self.is_running = False
        self.overlay_view = None
        self.window_manager = None
        self.layout_params = None

    def start(self):
        print("AI COMMANDER: Requesting Android 14 Service permissions...")
        # 1. Request MediaProjection
        # 2. Request System Alert Window
        self.create_floating_chat_box()
        self.run_loop()

    def create_floating_chat_box(self):
        """
        Using Android's WindowManager via pyjnius to create a visible,
        non-obtrusive floating chat box.
        """
        try:
            from jnius import autoclass
            Context = autoclass('android.content.Context')
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            PixelFormat = autoclass('android.graphics.PixelFormat')
            TextView = autoclass('android.widget.TextView')
            Color = autoclass('android.graphics.Color')
            Gravity = autoclass('android.view.Gravity')

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            self.window_manager = activity.getSystemService(Context.WINDOW_SERVICE)

            # Layout parameters for Overlay
            self.layout_params = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT,
                LayoutParams.TYPE_APPLICATION_OVERLAY, # API 26+ (Required for Android 14)
                LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT
            )
            self.layout_params.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL
            self.layout_params.y = 100

            # Create a simple TextView as the floating chat box
            self.overlay_view = TextView(activity)
            self.overlay_view.setText("AI Commander: System Online")
            self.overlay_view.setTextColor(Color.WHITE)
            self.overlay_view.setBackgroundColor(Color.argb(180, 0, 0, 0)) # Semi-transparent black
            self.overlay_view.setPadding(20, 10, 20, 10)

            self.window_manager.addView(self.overlay_view, self.layout_params)
            print("AI Commander: Floating Chat Box Created.")
        except Exception as e:
            print(f"Error creating overlay: {e}")

    def update_chat_box(self, message):
        if self.overlay_view and self.window_manager:
            try:
                self.overlay_view.setText(message)
                self.window_manager.updateViewLayout(self.overlay_view, self.layout_params)
            except Exception as e:
                print(f"Error updating overlay: {e}")

    def run_loop(self):
        self.is_running = True
        # Simulation of game loop
        hand = ["Goblin Gang", "Dark Prince", "Hog Rider", "Musketeer"]
        while self.is_running:
            # 1. capture screen frame (MediaProjection)
            # 2. process vision (OpenCV)
            # 3. get AI command
            threats = ["Prince"] # Simulating detected threat
            state = self.brain.update_match_state(threats, hand, 10, 1)

            # Update the visible chat box on Android
            self.update_chat_box(state['command'])

            time.sleep(2) # Update every 2 seconds

if __name__ == "__main__":
    service = AICommanderService()
    service.start()
