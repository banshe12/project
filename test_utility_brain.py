from utility_brain import UtilityBrain

def test_prince_threat():
    brain = UtilityBrain()
    hand = ["Goblin Gang", "Hog Rider", "Dark Prince", "Musketeer"]
    threats = ["Prince"]
    elixir = 10

    result = brain.evaluate_defense(threats, hand, elixir)
    print(f"Test Prince Threat: Best card: {result['best_card']} (Score: {result['utility_score']})")
    # Goblin Gang is swarm, Prince is high_dps. Goblin Gang should score high.
    assert result['best_card'] == "Goblin Gang"

def test_minion_horde_threat():
    # Minion Horde is not in our json, but let's use "Minions" (swarm air)
    brain = UtilityBrain()
    hand = ["Dark Prince", "Hog Rider", "Fireball", "Musketeer"]
    threats = ["Minions"]
    elixir = 10

    result = brain.evaluate_defense(threats, hand, elixir)
    print(f"Test Minions Threat: Best card: {result['best_card']} (Score: {result['utility_score']})")
    # Fireball is splash, Minions are swarm. Fireball should score well.
    # Musketeer targets air. Dark Prince and Hog Rider don't.
    assert result['best_card'] in ["Fireball", "Musketeer"]

def test_elixir_constraint():
    brain = UtilityBrain()
    hand = ["P.E.K.K.A", "Musketeer", "Goblin Gang", "Dark Prince"]
    threats = ["Giant"]
    elixir = 3

    result = brain.evaluate_defense(threats, hand, elixir)
    print(f"Test Elixir Constraint (3): Best card: {result['best_card']}")
    # Only Goblin Gang costs 3 or less.
    assert result['best_card'] == "Goblin Gang"

if __name__ == "__main__":
    try:
        test_prince_threat()
        test_minion_horde_threat()
        test_elixir_constraint()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed!")
        exit(1)
