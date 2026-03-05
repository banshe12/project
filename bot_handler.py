import asyncio
import pyautogui
import os
from telegram import Bot

class TelegramReporter:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=self.token)

    async def report_catch(self, fish_data):
        """
        On every successful catch:
        Take a high-quality screenshot.
        Send to Telegram with caption.
        """
        screenshot_path = "catch_screenshot.png"
        pyautogui.screenshot(screenshot_path)

        caption = (
            f"🐟 Name: {fish_data['name']} | ⚖️ Weight: {fish_data['weight']:.2f} kg\n"
            f"📏 Dist: {fish_data['dist']:.2f}m | 🔋 Fatigue: {fish_data['fatigue']}%\n"
            f"🏆 Status: {'TROPHY' if fish_data['is_trophy'] else 'Regular'}"
        )

        try:
            with open(screenshot_path, 'rb') as photo:
                await self.bot.send_photo(chat_id=self.chat_id, photo=photo, caption=caption)
            print("[Telegram] Catch report sent successfully.")
        except Exception as e:
            print(f"[Telegram] Error sending report: {e}")
        finally:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

if __name__ == "__main__":
    # Example usage (requires token and chat_id)
    # reporter = TelegramReporter("TOKEN", "CHAT_ID")
    # asyncio.run(reporter.report_catch({"name": "Carp", "weight": 5.4, "dist": 20.0, "fatigue": 10, "is_trophy": False}))
    pass
