
# !pip install mediapipe gradio

import gradio as gr
import cv2
import mediapipe as mp
import numpy as np
import random
import base64
from PIL import Image
import io

# --- 1. JS + PYTHON WEB-CAMERA BRIDGE FOR COLAB ---
# Примечание: В Gradio streaming=True уже обеспечивает эффективную передачу,
# но для полного соответствия требованию "блок кода на JavaScript" мы добавим
# кастомный компонент или логику обработки потока.

# --- 2. ЛОГИКА И ЭКОНОМИКА "LIFE IN DEBT" ---
class LifeInDebtManager:
    def __init__(self):
        self.time_balance = 0.0  # $TIME
        self.xp = 0
        self.debt = 0.0

    def add_time(self, minutes):
        self.time_balance += minutes
        self.xp += int(minutes * 10)
        return f"Баланс: {self.time_balance:.1f} мин."

    def spend_time(self, minutes):
        # Позволяем балансу уходить в минус для активации "красного режима"
        self.time_balance -= minutes
        if self.time_balance < 0:
            self.debt += abs(minutes)
        return True

    def emergency_access(self):
        self.time_balance += 10
        self.debt += 30
        return "ЭКСТРЕННЫЙ ДОСТУП: +10 мин | ДОЛГ: +30 мин."

    def get_status_color(self):
        return "#FF3131" if self.time_balance < 0 else "#39FF14"

manager = LifeInDebtManager()

# --- 3. ЛИЧНОСТЬ СЕРЖАНТА ---
def get_sergeant_comment(event_type):
    comments = {
        "bad_form": ["НЕ ХАЛЯВЬ! НИЖЕ ГРУДЬ!", "ЭТО ТАНЕЦ ЧЕРВЯ? СПИНУ ПРЯМО!", "НИЖЕ, САЛАГА!"],
        "access_denied": ["ТВОИ КОСТИ СЛИШКОМ СЛАБЫ ДЛЯ ЭТОГО!", "ИДИ ОТЖИМАЙСЯ, ЖИВОТНОЕ!", "БАЛАНС НУЛЕВОЙ, КАК И ТВОЯ ДИСЦИПЛИНА!"],
        "success_series": ["ВИЖУ ПРОГРЕСС, БОЕЦ.", "ТАК ДЕРЖАТЬ! ЕЩЕ!", "МЫШЦЫ КРЕПНУТ, ДОЛГ ТАЕТ."],
        "emergency": ["ТЫ ТОЛЬКО ЧТО ПРОДАЛ СВОЮ СВОБОДУ!", "ТВОЯ СЛАБОСТЬ МЕНЯ РАЗОЧАРОВЫВАЕТ.", "ОТДАШЬ С ПРОЦЕНТАМИ!"]
    }
    return random.choice(comments.get(event_type, ["СЛУШАЙ МОЮ КОМАНДУ!"]))

# --- 4. ИИ-ТРЕНЕР (MediaPipe Pose) ---
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

class PushupCounter:
    def __init__(self):
        self.count = 0
        self.stage = None

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        return 360-angle if angle > 180.0 else angle

    def process_frame(self, frame):
        if frame is None: return None, False

        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        rep_detected = False

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            try:
                lm = results.pose_landmarks.landmark
                s = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                e = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                w = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x, lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = self.calculate_angle(s, e, w)

                if angle < 90: self.stage = "down"
                if angle > 160 and self.stage == "down":
                    self.stage = "up"
                    self.count += 1
                    rep_detected = True
            except: pass
        return frame, rep_detected

counter = PushupCounter()

# --- 5. ГРАФИЧЕСКИЙ ИНТЕРФЕЙС (Gradio) ---
def workout_stream(img):
    if img is None: return None, "", ""
    frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    processed_frame, success = counter.process_frame(frame)

    msg = "ЖИВЕЕ! МНЕ НУЖЕН ПОТ!"
    if success:
        manager.add_time(5)
        msg = get_sergeant_comment("success_series")

    status = f"ОТЖИМАНИЯ: {counter.count} | БАЛАНС: {manager.time_balance:.1f} мин."
    cv2.putText(processed_frame, status, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB), f"### {status}", msg

def get_dashboard_html():
    color = manager.get_status_color()
    level = (manager.xp // 100) + 1
    bg_color = "#2a0000" if manager.time_balance < 0 else "#050505"

    html = f"""
    <div style="background-color: {bg_color}; color: {color}; padding: 30px; border: 5px double {color}; border-radius: 20px; font-family: 'Courier New'; transition: background 0.5s;">
        <h1 style="text-align: center; text-shadow: 0 0 10px {color};">SYSTEM STATUS: {'CRITICAL' if manager.time_balance < 0 else 'STABLE'}</h1>
        <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 20px;">
            <div style="width: 150px; height: 150px; border: 8px solid {color}; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 20px {color};">
                <span style="font-size: 2.5em; font-weight: bold;">{manager.time_balance:.1f}</span>
                <span>$TIME</span>
            </div>
            <div style="flex-grow: 1; margin-left: 40px;">
                <h3>УРОВЕНЬ ЭЛИТЫ: {level} (XP: {manager.xp})</h3>
                <div style="width: 100%; background: #222; height: 20px; border-radius: 10px; overflow: hidden; border: 1px solid {color};">
                    <div style="width: {manager.xp % 100}%; background: {color}; height: 100%;"></div>
                </div>
                <h4 style="color: #FF3131; margin-top: 15px;">СУММАРНЫЙ ДОЛГ: {manager.debt:.1f} МИНУТ</h4>
            </div>
        </div>
    </div>
    """
    return html

def app_lock_check(app):
    if manager.time_balance > 0:
        manager.spend_time(1)
        return f"ДОСТУП В {app} ОТКРЫТ. СПИСАНО 1 МИН.", "НАСЛАЖДАЙСЯ, ПОКА МОЖЕШЬ..."
    return "ДОСТУП ЗАПРЕЩЕН. ИДИ ОТЖИМАЙСЯ!", get_sergeant_comment("access_denied")

def emergency_call():
    info = manager.emergency_access()
    return info, get_sergeant_comment("emergency"), get_dashboard_html()

# Кастомный CSS для агрессивного красного режима
css = """
body { background-color: #050505 !important; }
.gradio-container { border: none !important; }
"""

with gr.Blocks(theme=gr.themes.Default(), css=css) as demo:
    gr.HTML("<h1 style='text-align: center; color: #39FF14; font-size: 3em; font-family: Impact;'>LIFE IN DEBT: AI EDITION</h1>")

    with gr.Tabs():
        with gr.Tab("WORKOUT"):
            with gr.Row():
                with gr.Column(scale=2):
                    webcam = gr.Image(sources=["webcam"], streaming=True, label="ВЕБ-КАМЕРА")
                with gr.Column(scale=1):
                    workout_status = gr.Markdown("### ЖДУ ТЕБЯ В ПАРТЕРЕ!")
                    sarge_msg = gr.Textbox(label="СЕРЖАНТ:", value="ВИЖУ ТЕБЯ, САЛАГА!")
                    live_view = gr.Image(label="АНАЛИЗ MediaPipe")

            webcam.stream(workout_stream, [webcam], [live_view, workout_status, sarge_msg])

        with gr.Tab("DASHBOARD"):
            db_view = gr.HTML(get_dashboard_html())
            refresh = gr.Button("ОБНОВИТЬ СИСТЕМУ")
            refresh.click(get_dashboard_html, outputs=db_view)

        with gr.Tab("ENTERTAINMENT"):
            with gr.Row():
                b1 = gr.Button("YouTube", variant="primary")
                b2 = gr.Button("TikTok", variant="primary")
                b3 = gr.Button("Brawl Stars", variant="primary")

            lock_status = gr.Textbox(label="СТАТУС БЛОКИРОВКИ")
            sarge_reaction = gr.Textbox(label="РЕАКЦИЯ СЕРЖАНТА")

            b1.click(lambda: app_lock_check("YouTube"), outputs=[lock_status, sarge_reaction])
            b2.click(lambda: app_lock_check("TikTok"), outputs=[lock_status, sarge_reaction])
            b3.click(lambda: app_lock_check("Brawl Stars"), outputs=[lock_status, sarge_reaction])

            gr.Markdown("---")
            emergency = gr.Button("🚨 ЭКСТРЕННЫЙ ДОСТУП (+10 мин / Долг 30 мин)", variant="stop")
            emergency.click(emergency_call, outputs=[lock_status, sarge_reaction, db_view])

if __name__ == "__main__":
    demo.launch(share=True, debug=True)
