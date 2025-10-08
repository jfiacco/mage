"""
Configuration for XMage Gym

This module provides configuration classes and default values.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """Server connection configuration"""
    host: str = "localhost"
    port: int = 17171
    username: str = "player"
    password: str = "password"
    timeout: int = 30


@dataclass
class EnvironmentConfig:
    """Environment configuration"""
    max_turns: int = 50
    max_hand_size: int = 20
    max_battlefield_size: int = 50
    max_stack_size: int = 20
    max_players: int = 4
    
    # Feature sizes
    player_features: int = 15
    card_features: int = 30
    permanent_features: int = 35
    stack_features: int = 25
    
    # Action space size
    num_actions: int = 1000
    
    # Reward shaping
    life_reward_weight: float = 0.01
    board_reward_weight: float = 0.1
    card_advantage_weight: float = 0.01
    
    # Rendering
    render_mode: Optional[str] = None


@dataclass
class TrainingConfig:
    """Training configuration"""
    num_episodes: int = 1000
    learning_rate: float = 0.0003
    discount_factor: float = 0.99
    batch_size: int = 32
    buffer_size: int = 10000
    
    # Exploration
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay: float = 0.995
    
    # Checkpointing
    save_interval: int = 100
    checkpoint_dir: str = "./checkpoints"
    
    # Logging
    log_interval: int = 10
    tensorboard_dir: str = "./runs"


# Default configurations
DEFAULT_SERVER_CONFIG = ServerConfig()
DEFAULT_ENV_CONFIG = EnvironmentConfig()
DEFAULT_TRAINING_CONFIG = TrainingConfig()
