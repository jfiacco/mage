"""
Basic usage example for mage_gym

This example demonstrates how to use the XMageEnv to interact with
the XMage server for reinforcement learning.
"""

import sys
sys.path.insert(0, '..')

from mage_gym import XMageEnv
from mage_gym.models import DeckCardLists


def main():
    """Run a simple game with random actions"""
    
    print("=" * 60)
    print("XMage Gym - Basic Usage Example")
    print("=" * 60)
    print()
    
    # Create a simple deck
    deck = DeckCardLists(
        main_deck=(
            ["Mountain"] * 20 +
            ["Lightning Bolt"] * 4 +
            ["Shock"] * 4 +
            ["Lava Spike"] * 4 +
            ["Rift Bolt"] * 4 +
            ["Monastery Swiftspear"] * 4 +
            ["Goblin Guide"] * 4 +
            ["Eidolon of the Great Revel"] * 4 +
            ["Skullcrack"] * 4 +
            ["Searing Blaze"] * 4
        ),
        sideboard=["Pyroblast"] * 4 + ["Smash to Smithereens"] * 4
    )
    
    print(f"Deck: {len(deck.main_deck)} cards in main, {len(deck.sideboard)} in sideboard")
    print()
    
    # Create environment
    print("Creating environment...")
    env = XMageEnv(
        server_host="localhost",
        server_port=17171,
        username="rl_agent",
        password="password",
        deck_list=deck,
        opponent_type="ai",
        max_turns=50,
        render_mode="human",
    )
    
    print(f"Action space: {env.action_space}")
    print(f"Observation space: {env.observation_space}")
    print()
    
    # Run a few episodes
    num_episodes = 3
    
    for episode in range(num_episodes):
        print("=" * 60)
        print(f"Episode {episode + 1}/{num_episodes}")
        print("=" * 60)
        
        # Reset environment
        observation, info = env.reset()
        episode_reward = 0
        step = 0
        done = False
        
        print(f"Initial state: {info}")
        print()
        
        # Run episode
        while not done and step < 100:  # Limit steps for demo
            # Select random action
            action = env.action_space.sample()
            
            # Execute action
            observation, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            step += 1
            done = terminated or truncated
            
            # Print progress every 10 steps
            if step % 10 == 0:
                print(f"Step {step}: Reward={episode_reward:.2f}, Info={info}")
            
            # Render
            if step % 20 == 0:
                env.render()
        
        print()
        print(f"Episode finished after {step} steps")
        print(f"Total reward: {episode_reward:.2f}")
        print(f"Terminated: {terminated}, Truncated: {truncated}")
        print()
    
    # Clean up
    env.close()
    print("Environment closed")
    print()
    print("Demo completed!")


if __name__ == "__main__":
    main()
