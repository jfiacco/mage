"""
mage_gym: Python Gymnasium Environment for XMage Server

This package provides a Gymnasium-compatible environment for interacting with
the XMage (Magic Another Game Engine) server for reinforcement learning applications.
"""

from mage_gym.env import XMageEnv
from mage_gym.connection import XMageConnection
from mage_gym.game_state_manager import XMageGameStateManager
from mage_gym.models import (
    GameView,
    PlayerView,
    CardView,
    PermanentView,
    GameObservation,
)
from mage_gym.enums import (
    PlayerAction,
    ActionType,
    PlayerType,
    TurnPhase,
    PhaseStep,
    ManaType,
    ClientCallbackMethod,
)

__version__ = "0.1.0"

__all__ = [
    "XMageEnv",
    "XMageConnection",
    "XMageGameStateManager",
    "GameView",
    "PlayerView",
    "CardView",
    "PermanentView",
    "GameObservation",
    "PlayerAction",
    "ActionType",
    "PlayerType",
    "TurnPhase",
    "PhaseStep",
    "ManaType",
    "ClientCallbackMethod",
]
