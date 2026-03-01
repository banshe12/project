import os
import requests
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window

# --- UI Screens ---
Builder.load_string("""
<WelcomeScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.2, 1
        Rectangle:
            size: self.size
            pos: self.pos
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 30
        Label:
            text: "Ultimate Mega AI Commander"
            font_size: '32sp'
            bold: True
            color: 0, 0.8, 1, 1
        Button:
            id: start_btn
            text: "START AI COMMANDER"
            font_size: '22sp'
            bold: True
            background_normal: ''
            background_color: 0.1, 0.6, 0.9, 1
            size_hint: (0.8, 0.2)
            pos_hint: {'center_x': 0.5}
            on_press: root.animate_button(self)
            on_release: root.start_commander()

<DashboardScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Label:
            text: "COMMANDER ACTIVE"
            font_size: '24sp'
        Button:
            text: "STOP"
            on_release: root.manager.current = 'welcome'
""")

class WelcomeScreen(Screen):
    def animate_button(self, btn):
        anim = Animation(background_color=(0, 1, 0.5, 1), duration=0.1) + \
               Animation(background_color=(0.1, 0.6, 0.9, 1), duration=0.2)
        anim.start(btn)

    def start_commander(self):
        print("Launching Clash Royale and Background Service...")
        self.start_service()
        self.launch_clash_royale()
        # Navigate to dashboard after short delay
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 1)

    def start_service(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Context = autoclass('android.content.Context')
            activity = PythonActivity.mActivity

            service_intent = Intent(activity, autoclass('org.kivy.android.PythonService'))
            service_intent.putExtra('PYTHON_SERVICE_ARG', '')
            service_intent.putExtra('PYTHON_SERVICE_CLASS', 'org.test.megacommander.ServiceAicommander')
            activity.startForegroundService(service_intent)
        except Exception as e:
            print(f"Error starting service: {e}")

    def launch_clash_royale(self):
        """
        Using pyjnius to launch the game package: com.supercell.clashroyale
        """
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            PackageManager = autoclass('android.content.pm.PackageManager')
            pm = activity.getPackageManager()
            intent = pm.getLaunchIntentForPackage('com.supercell.clashroyale')
            if intent:
                activity.startActivity(intent)
            else:
                print("Clash Royale not found!")
        except Exception as e:
            print(f"Error launching game: {e}")

class DashboardScreen(Screen):
    pass

class MegaAIApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    MegaAIApp().run()
