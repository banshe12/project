import json
import os

class UtilityBrain:
    def __init__(self, cards_file='cards.json'):
        self.cards = self._load_cards(cards_file)

    def _load_cards(self, cards_file):
        if not os.path.exists(cards_file):
            return {}
        with open(cards_file, 'r') as f:
            return json.load(f)

    def _calculate_score(self, card_name, threat_name):
        if card_name not in self.cards or threat_name not in self.cards:
            return 0

        card = self.cards[card_name]
        threat = self.cards[threat_name]
        score = 0

        # 1. Elixir Trade
        # Positive trade is good.
        score += (threat['cost'] - card['cost'])

        # 2. Type Matching
        if threat['type'] == 'air':
            if card['target'] in ['ground', 'buildings']:
                score -= 20 # Useless against air
            elif card['target'] == 'ground_air':
                score += 10

        if card['type'] == 'air' and threat['target'] == 'ground':
            score += 7 # Safe from ground-only threat

        # 3. Trait Counters
        c_traits = card.get('traits', [])
        t_traits = threat.get('traits', [])

        if "swarm" in t_traits and "splash" in c_traits:
            score += 15
        if "high_dps" in t_traits and "swarm" in c_traits:
            score += 12
        if "tank" in t_traits and "high_dps" in c_traits:
            score += 12
        if "tank" in t_traits and "swarm" in c_traits:
            score += 8
        if "splash" in t_traits and "swarm" in c_traits:
            score -= 10 # Swarm is bad against splash

        return score

    def _determine_zone(self, card_name, threat_name):
        card = self.cards[card_name]
        # threat = self.cards[threat_name] # Could be used for more complex logic

        if card['type'] == 'spell':
            return "ON_THREAT"
        if card['type'] == 'building':
            return "CENTER_KITE"
        if "tank" in card.get('traits', []):
            return "BRIDGE_BLOCK"
        if "swarm" in card.get('traits', []):
            return "ON_THREAT"
        if card_name in ["Witch", "Musketeer"]:
            return "BEHIND_KING"

        return "CENTER_KITE"

    def evaluate_defense(self, enemy_threats, hand, current_elixir):
        """
        enemy_threats: list of card names
        hand: list of card names (size 4)
        current_elixir: float
        """
        if not enemy_threats:
            return {"best_card": None, "recommended_zone": None, "utility_score": 0}

        best_card = None
        best_score = -float('inf')
        best_zone = "CENTER_KITE"

        for card_name in hand:
            if card_name not in self.cards:
                continue

            card_data = self.cards[card_name]
            if card_data['cost'] > current_elixir:
                continue

            total_card_score = 0
            # For multiple threats, we sum the scores but might want to weight them
            for threat_name in enemy_threats:
                total_card_score += self._calculate_score(card_name, threat_name)

            if total_card_score > best_score:
                best_score = total_card_score
                best_card = card_name
                # Zone is determined by the first threat for simplicity,
                # or we could find the 'most dangerous' threat
                best_zone = self._determine_zone(card_name, enemy_threats[0])

        return {
            "best_card": best_card,
            "recommended_zone": best_zone if best_card else None,
            "utility_score": round(best_score, 2) if best_card else 0
        }

if __name__ == "__main__":
    brain = UtilityBrain()
    # Example usage
    sample_hand = ["Goblin Gang", "Dark Prince", "Fireball", "Musketeer"]
    sample_threats = ["Prince"]
    result = brain.evaluate_defense(sample_threats, sample_hand, 10)
    print(f"Threats: {sample_threats}")
    print(f"Best card: {result['best_card']} in zone {result['recommended_zone']} (Score: {result['utility_score']})")
