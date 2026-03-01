from utility_brain import UtilityBrain

def test_scenarios():
    brain = UtilityBrain('cards.json')

    print("Scenario 1: Defending against Hog Rider (Tank, Building-target)")
    enemy_threats = ["Hog Rider"]
    hand = ["Skeleton Army", "Dark Prince", "Baby Dragon", "Fireball"]
    best_card, zone, score = brain.evaluate_defense(enemy_threats, hand, 10)
    print(f"Hand: {hand}")
    print(f"Decision: Play {best_card} in {zone} (Score: {score})")
    assert best_card == "Skeleton Army", f"Expected Skeleton Army, got {best_card}"
    print("-" * 30)

    print("Scenario 2: Defending against Minions (Air, Swarm)")
    enemy_threats = ["Minions"]
    hand = ["Knight", "Dark Prince", "Witch", "Skeleton Army"]
    best_card, zone, score = brain.evaluate_defense(enemy_threats, hand, 10)
    print(f"Hand: {hand}")
    print(f"Decision: Play {best_card} in {zone} (Score: {score})")
    assert best_card == "Witch", f"Expected Witch, got {best_card}"
    print("-" * 30)

    print("Scenario 3: Defending against Skeleton Army (Ground, Swarm)")
    enemy_threats = ["Skeleton Army"]
    hand = ["Musketeer", "Dark Prince", "Knight", "Hog Rider"]
    best_card, zone, score = brain.evaluate_defense(enemy_threats, hand, 10)
    print(f"Hand: {hand}")
    print(f"Decision: Play {best_card} in {zone} (Score: {score})")
    assert best_card == "Dark Prince", f"Expected Dark Prince, got {best_card}"
    print("-" * 30)

    print("Scenario 4: Low Elixir")
    enemy_threats = ["Hog Rider"]
    hand = ["Skeleton Army", "Witch", "Musketeer", "Fireball"]
    # With only 3 elixir, only Skeleton Army should be playable
    best_card, zone, score = brain.evaluate_defense(enemy_threats, hand, 3)
    print(f"Elixir: 3, Hand: {hand}")
    print(f"Decision: Play {best_card} in {zone} (Score: {score})")
    assert best_card == "Skeleton Army", f"Expected Skeleton Army, got {best_card}"
    print("-" * 30)

if __name__ == "__main__":
    test_scenarios()
    print("All tests passed!")
