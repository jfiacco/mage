"""
Utility functions for XMage Gym

This module provides helper functions for common operations.
"""

from typing import Dict, List, Any
import numpy as np
from uuid import UUID

from mage_gym.enums import TurnPhase, PhaseStep, ManaType


def encode_phase_one_hot(phase: TurnPhase) -> np.ndarray:
    """
    Encode turn phase as one-hot vector
    
    Args:
        phase: Turn phase
        
    Returns:
        One-hot encoded vector
    """
    phases = list(TurnPhase)
    encoding = np.zeros(len(phases), dtype=np.float32)
    
    try:
        idx = phases.index(phase)
        encoding[idx] = 1.0
    except (ValueError, AttributeError):
        pass
    
    return encoding


def encode_step_one_hot(step: PhaseStep) -> np.ndarray:
    """
    Encode phase step as one-hot vector
    
    Args:
        step: Phase step
        
    Returns:
        One-hot encoded vector
    """
    steps = list(PhaseStep)
    encoding = np.zeros(len(steps), dtype=np.float32)
    
    try:
        idx = steps.index(step)
        encoding[idx] = 1.0
    except (ValueError, AttributeError):
        pass
    
    return encoding


def encode_color(color_string: str) -> np.ndarray:
    """
    Encode color string as vector
    
    Args:
        color_string: Color string (e.g., "WU" for white-blue)
        
    Returns:
        Binary vector [W, U, B, R, G, C]
    """
    encoding = np.zeros(6, dtype=np.float32)
    
    color_map = {
        'W': 0,  # White
        'U': 1,  # Blue
        'B': 2,  # Black
        'R': 3,  # Red
        'G': 4,  # Green
        'C': 5,  # Colorless
    }
    
    for char in color_string.upper():
        if char in color_map:
            encoding[color_map[char]] = 1.0
    
    return encoding


def parse_mana_cost(mana_cost: List[str]) -> Dict[str, int]:
    """
    Parse mana cost symbols into a dictionary
    
    Args:
        mana_cost: List of mana symbols (e.g., ["2", "U", "U"])
        
    Returns:
        Dictionary mapping mana type to count
    """
    result = {
        'generic': 0,
        'white': 0,
        'blue': 0,
        'black': 0,
        'red': 0,
        'green': 0,
        'colorless': 0,
    }
    
    for symbol in mana_cost:
        symbol = symbol.strip('{}').upper()
        
        if symbol.isdigit():
            result['generic'] += int(symbol)
        elif symbol == 'W':
            result['white'] += 1
        elif symbol == 'U':
            result['blue'] += 1
        elif symbol == 'B':
            result['black'] += 1
        elif symbol == 'R':
            result['red'] += 1
        elif symbol == 'G':
            result['green'] += 1
        elif symbol == 'C':
            result['colorless'] += 1
        # Handle hybrid and other complex symbols as needed
    
    return result


def calculate_total_mana(mana_pool: Dict[str, int]) -> int:
    """
    Calculate total mana available
    
    Args:
        mana_pool: Dictionary of mana by color
        
    Returns:
        Total mana count
    """
    return sum(mana_pool.values())


def normalize_observation(obs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Normalize observation values to reasonable ranges
    
    Args:
        obs: Observation dictionary
        
    Returns:
        Normalized observation dictionary
    """
    normalized = {}
    
    for key, value in obs.items():
        if key == "players":
            # Normalize player features
            normalized[key] = value / 100.0  # Simple normalization
        elif key == "hand" or key == "battlefield" or key == "stack":
            # Normalize card/permanent features
            normalized[key] = value / 20.0
        else:
            normalized[key] = value
    
    return normalized


def uuid_to_index(uuid: UUID, uuid_list: List[UUID]) -> int:
    """
    Convert UUID to index in list
    
    Args:
        uuid: UUID to find
        uuid_list: List of UUIDs
        
    Returns:
        Index of UUID, or -1 if not found
    """
    try:
        return uuid_list.index(uuid)
    except ValueError:
        return -1


def index_to_uuid(index: int, uuid_list: List[UUID]) -> UUID:
    """
    Convert index to UUID from list
    
    Args:
        index: Index in list
        uuid_list: List of UUIDs
        
    Returns:
        UUID at index, or None if out of bounds
    """
    if 0 <= index < len(uuid_list):
        return uuid_list[index]
    return None


def action_to_string(action: Dict[str, Any]) -> str:
    """
    Convert action dictionary to human-readable string
    
    Args:
        action: Action dictionary
        
    Returns:
        String representation
    """
    action_type = action.get("action_type", "UNKNOWN")
    target_id = action.get("target_id")
    value = action.get("value")
    
    parts = [f"Action: {action_type}"]
    
    if target_id is not None:
        parts.append(f"Target: {target_id}")
    
    if value is not None:
        if isinstance(value, np.ndarray):
            value = value.item()
        parts.append(f"Value: {value}")
    
    return ", ".join(parts)


def is_valid_deck(deck: List[str], min_size: int = 40, max_size: int = 250) -> bool:
    """
    Validate deck list
    
    Args:
        deck: List of card names
        min_size: Minimum deck size
        max_size: Maximum deck size
        
    Returns:
        True if deck is valid
    """
    if not deck:
        return False
    
    if len(deck) < min_size or len(deck) > max_size:
        return False
    
    # Check for basic lands to allow unlimited copies
    basic_lands = {"Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"}
    
    # Count non-basic cards
    card_counts = {}
    for card in deck:
        if card not in basic_lands:
            card_counts[card] = card_counts.get(card, 0) + 1
            if card_counts[card] > 4:
                return False
    
    return True


def format_game_state(game_state: Any) -> str:
    """
    Format game state for display
    
    Args:
        game_state: GameView object
        
    Returns:
        Formatted string
    """
    if game_state is None:
        return "No game state"
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"Turn {game_state.turn}")
    
    if game_state.phase:
        lines.append(f"Phase: {game_state.phase.name}")
    if game_state.step:
        lines.append(f"Step: {game_state.step.name}")
    
    lines.append("-" * 60)
    
    for player in game_state.players:
        marker = ">>> " if player.controlled else "    "
        lines.append(
            f"{marker}{player.name}: "
            f"Life={player.life}, "
            f"Hand={player.hand_count}, "
            f"Library={player.library_count}, "
            f"Battlefield={len(player.battlefield)}"
        )
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
