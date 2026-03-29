import json
from utility_brain import UtilityBrain

class ElixirTracker:
    def __init__(self):
        self.enemy_elixir = 5.0 # Starting elixir (estimated)
        self.last_update = 0

    def card_played(self, card_cost):
        self.enemy_elixir -= card_cost
        if self.enemy_elixir < 0:
            self.enemy_elixir = 0

    def passive_gain(self, seconds, rate=0.35):
        # 1 elixir every ~2.8 seconds in single elixir (approx 0.35/sec)
        self.enemy_elixir += seconds * rate
        if self.enemy_elixir > 10:
            self.enemy_elixir = 10

class CounterPickEngine:
    def __init__(self, cards_file='cards.json'):
        with open(cards_file, 'r') as f:
            self.cards = json.load(f)

    def get_hard_counter(self, card_name):
        # Simple hardcoded counter-picks for demonstration
        counters = {
            "Hog Rider": "Cannon",
            "Prince": "Goblin Gang",
            "Minion Horde": "Fireball",
            "Goblin Barrel": "Log", # Log not in json, placeholder
            "Giant": "P.E.K.K.A",
            "P.E.K.K.A": "Minions",
            "Witch": "Dark Prince"
        }
        return counters.get(card_name)

class CommandGenerator:
    def __init__(self):
        self.states = ["DEFENSE", "ATTACK", "WAITING"]
        self.current_state = "WAITING"

    def generate_command(self, elixir_info, threats, recommendation):
        if threats:
            self.current_state = "DEFENSE"
            return f"🔴 DEFENSE: Play {recommendation['best_card']} in {recommendation['recommended_zone']}!"

        if elixir_info.enemy_elixir < 3:
            self.current_state = "ATTACK"
            return "🟢 ENEMY LOW ELIXIR - PUSH RIGHT LANE!"

        self.current_state = "WAITING"
        return "⚪ WAITING FOR ENEMY MOVE..."

class AIBrain:
    def __init__(self, cards_file='cards.json'):
        self.utility_brain = UtilityBrain(cards_file)
        self.elixir_tracker = ElixirTracker()
        self.counter_engine = CounterPickEngine(cards_file)
        self.command_gen = CommandGenerator()

    def update_match_state(self, enemy_threats, hand, current_elixir, time_delta):
        # Update elixir estimate
        self.elixir_tracker.passive_gain(time_delta)

        # Get defense recommendation from utility brain
        recommendation = self.utility_brain.evaluate_defense(enemy_threats, hand, current_elixir)

        # Generate tactical command
        command = self.command_gen.generate_command(self.elixir_tracker, enemy_threats, recommendation)

        return {
            "command": command,
            "enemy_elixir_est": round(self.elixir_tracker.enemy_elixir, 1),
            "recommendation": recommendation
        }

    def process_vision(self, frame):
        """
        Skeleton for OpenCV zone recognition.
        frame: numpy array from screen capture.
        """
        # 1. Detect cards played (template matching)
        # 2. Map coordinates to game zones
        # 3. Update elixir_tracker.card_played() if enemy card detected
        pass

if __name__ == "__main__":
    brain = AIBrain()
    hand = ["Goblin Gang", "Dark Prince", "Hog Rider", "Musketeer"]
    threats = ["Prince"]
    state = brain.update_match_state(threats, hand, 10, 5) # 5 seconds later
    print(f"Command: {state['command']}")
    print(f"Enemy Elixir Estimate: {state['enemy_elixir_est']}")
