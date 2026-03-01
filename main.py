import os
import requests
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

# --- Auto-Fetch Logic ---
CARDS_URL = "https://raw.githubusercontent.com/RoyaleAPI/cr-api-data/master/json/cards.json"
CARDS_PATH = "cards.json"

def auto_fetch_cards():
    if not os.path.exists(CARDS_PATH):
        print("Fetching card database...")
        try:
            response = requests.get(CARDS_URL, timeout=10)
            if response.status_code == 200:
                with open(CARDS_PATH, 'wb') as f:
                    f.write(response.content)
                print("Card database downloaded successfully.")
            else:
                print(f"Failed to fetch cards: {response.status_code}")
        except Exception as e:
            print(f"Error fetching cards: {e}")

# --- UI Screens ---
Builder.load_string("""
<WelcomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label:
            text: "Welcome to Clash AI Trainer"
            font_size: '24sp'
        Button:
            text: "Next"
            size_hint_y: 0.2
            on_release: root.manager.current = 'tutorial'

<TutorialScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label:
            text: "How it works:\\n1. Grant permissions.\\n2. Start the service.\\n3. Open the game. The AI will show green zones for perfect defense."
            text_size: self.width, None
            halign: 'center'
        Button:
            text: "Next"
            size_hint_y: 0.2
            on_release: root.manager.current = 'permissions'

<PermissionsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Label:
            text: "The app needs Overlay and Screen Capture permissions to function."
        Button:
            text: "Grant Permissions"
            size_hint_y: 0.2
            on_release: root.grant_permissions()
        Button:
            text: "Next"
            size_hint_y: 0.2
            on_release: root.manager.current = 'dashboard'

<DashboardScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        Button:
            text: "START AI OVERLAY"
            font_size: '20sp'
            background_color: 0, 1, 0, 1
            on_release: root.start_service()
""")

class WelcomeScreen(Screen):
    pass

class TutorialScreen(Screen):
    pass

class PermissionsScreen(Screen):
    def grant_permissions(self):
        print("Requesting Android permissions: SYSTEM_ALERT_WINDOW, MediaProjection")
        # In a real Android environment, pyjnius would be used here to trigger intent
        pass

class DashboardScreen(Screen):
    def start_service(self):
        print("Starting Background AI Service...")
        # Code to launch service.py via pyjnius/Android service

class ClashAIApp(App):
    def build(self):
        auto_fetch_cards()
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(TutorialScreen(name='tutorial'))
        sm.add_widget(PermissionsScreen(name='permissions'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    ClashAIApp().run()
