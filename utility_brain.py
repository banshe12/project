import json
import os

class UtilityBrain:
    def __init__(self, card_db_path='cards.json'):
        self.cards = self._load_cards(card_db_path)

    def _load_cards(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Card database not found at {path}")
        with open(path, 'r') as f:
            return json.load(f)

    def evaluate_defense(self, enemy_threats, hand, current_elixir):
        """
        Evaluates the best card to play from hand against enemy threats.

        :param enemy_threats: List of enemy card names currently on board.
        :param hand: List of 4 card names in the user's hand.
        :param current_elixir: Current elixir available.
        :return: (best_card, recommended_zone, utility_score)
        """
        if not enemy_threats or not hand:
            return None, "WAIT", 0.0

        best_card = None
        best_zone = "WAIT"
        max_score = 0.0

        for card_name in hand:
            if card_name not in self.cards:
                continue

            card_data = self.cards[card_name]

            # Skip if we don't have enough elixir
            if card_data['cost'] > current_elixir:
                continue

            total_score = 0
            found_threats = 0

            for threat_name in enemy_threats:
                if threat_name not in self.cards:
                    continue

                threat_data = self.cards[threat_name]
                score = self._calculate_score(card_name, card_data, threat_name, threat_data)
                total_score += score
                found_threats += 1

            if found_threats == 0:
                avg_score = 0
            else:
                # Average score per threat
                avg_score = total_score / found_threats

            if best_card is None or avg_score > max_score:
                max_score = avg_score
                best_card = card_name
                best_zone = self._recommend_zone(card_data, enemy_threats)

        return best_card, best_zone, round(float(max_score), 2)

    def _calculate_score(self, card_name, card_data, threat_name, threat_data):
        score = 0

        # 1. Elixir Trade
        elixir_diff = threat_data['cost'] - card_data['cost']
        score += elixir_diff * 10

        # 2. Type Matching
        # If threat is air but card cannot hit air
        if threat_data['type'] == 'air' and 'air' not in card_data['target']:
            score -= 50
        # If card is air and threat cannot hit air
        elif card_data['type'] == 'air' and 'air' not in threat_data['target']:
            score += 20

        # 3. Trait Counters
        card_traits = card_data.get('traits', [])
        threat_traits = threat_data.get('traits', [])

        # Swarm vs Single Target (assume lack of splash means single/low target)
        if 'swarm' in card_traits and 'splash' not in threat_traits:
            score += 30

        # Splash vs Swarm
        if 'splash' in card_traits and 'swarm' in threat_traits:
            score += 40

        # High DPS vs Tank
        if 'high_dps' in card_traits and 'tank' in threat_traits:
            score += 30

        # Tank vs High DPS (to distract)
        if 'tank' in card_traits and 'high_dps' in threat_traits:
            score += 15

        return score

    def _recommend_zone(self, card_data, enemy_threats):
        # Very basic zone recommendation
        if 'tank' in card_data['traits']:
            return "BRIDGE_BLOCK"
        if card_data['type'] == 'spell':
            return "ON_THREAT"
        if 'high_dps' in card_data['traits'] or 'swarm' in card_data['traits']:
            return "CENTER_KITE"
        return "BEHIND_KING"
