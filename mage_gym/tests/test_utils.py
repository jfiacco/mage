"""
Tests for utility functions
"""

import pytest
import numpy as np
from uuid import uuid4

from mage_gym.utils import (
    encode_phase_one_hot,
    encode_step_one_hot,
    encode_color,
    parse_mana_cost,
    calculate_total_mana,
    normalize_observation,
    uuid_to_index,
    index_to_uuid,
    action_to_string,
    is_valid_deck,
    format_game_state,
)
from mage_gym.enums import TurnPhase, PhaseStep
from mage_gym.models import GameView, PlayerView


class TestEncodingFunctions:
    """Test encoding functions"""
    
    def test_encode_phase_one_hot(self):
        """Test phase one-hot encoding"""
        encoding = encode_phase_one_hot(TurnPhase.COMBAT)
        assert isinstance(encoding, np.ndarray)
        assert encoding.sum() == 1.0
        assert encoding[2] == 1.0  # Combat is 3rd phase
    
    def test_encode_step_one_hot(self):
        """Test step one-hot encoding"""
        encoding = encode_step_one_hot(PhaseStep.DECLARE_ATTACKERS)
        assert isinstance(encoding, np.ndarray)
        assert encoding.sum() == 1.0
    
    def test_encode_color(self):
        """Test color encoding"""
        # Single color
        encoding = encode_color("W")
        assert encoding[0] == 1.0
        assert encoding.sum() == 1.0
        
        # Multicolor
        encoding = encode_color("WU")
        assert encoding[0] == 1.0
        assert encoding[1] == 1.0
        assert encoding.sum() == 2.0
        
        # Empty
        encoding = encode_color("")
        assert encoding.sum() == 0.0


class TestManaParsing:
    """Test mana parsing functions"""
    
    def test_parse_simple_mana_cost(self):
        """Test parsing simple mana cost"""
        cost = parse_mana_cost(["1", "U"])
        assert cost["generic"] == 1
        assert cost["blue"] == 1
    
    def test_parse_multicolor_cost(self):
        """Test parsing multicolor cost"""
        cost = parse_mana_cost(["2", "W", "B"])
        assert cost["generic"] == 2
        assert cost["white"] == 1
        assert cost["black"] == 1
    
    def test_parse_complex_cost(self):
        """Test parsing complex cost"""
        cost = parse_mana_cost(["3", "R", "R", "G"])
        assert cost["generic"] == 3
        assert cost["red"] == 2
        assert cost["green"] == 1
    
    def test_calculate_total_mana(self):
        """Test calculating total mana"""
        pool = {
            'generic': 0,
            'white': 2,
            'blue': 3,
            'black': 0,
            'red': 1,
            'green': 0,
            'colorless': 0,
        }
        total = calculate_total_mana(pool)
        assert total == 6


class TestNormalization:
    """Test normalization functions"""
    
    def test_normalize_observation(self):
        """Test observation normalization"""
        obs = {
            "players": np.array([[20, 7, 53, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0]], dtype=np.float32),
            "hand": np.ones((20, 30), dtype=np.float32),
            "turn_number": np.array([5], dtype=np.int32),
        }
        
        normalized = normalize_observation(obs)
        
        # Players should be normalized by 100
        assert normalized["players"][0][0] == 20 / 100.0
        
        # Turn number should stay the same
        assert normalized["turn_number"][0] == 5


class TestUUIDHelpers:
    """Test UUID helper functions"""
    
    def test_uuid_to_index(self):
        """Test UUID to index conversion"""
        uuid_list = [uuid4() for _ in range(5)]
        
        # Test existing UUID
        idx = uuid_to_index(uuid_list[2], uuid_list)
        assert idx == 2
        
        # Test non-existing UUID
        idx = uuid_to_index(uuid4(), uuid_list)
        assert idx == -1
    
    def test_index_to_uuid(self):
        """Test index to UUID conversion"""
        uuid_list = [uuid4() for _ in range(5)]
        
        # Test valid index
        result = index_to_uuid(2, uuid_list)
        assert result == uuid_list[2]
        
        # Test invalid index
        result = index_to_uuid(10, uuid_list)
        assert result is None
        
        # Test negative index
        result = index_to_uuid(-1, uuid_list)
        assert result is None


class TestActionFormatting:
    """Test action formatting"""
    
    def test_action_to_string_simple(self):
        """Test simple action to string"""
        action = {"action_type": "PASS_PRIORITY"}
        result = action_to_string(action)
        assert "PASS_PRIORITY" in result
    
    def test_action_to_string_with_target(self):
        """Test action with target to string"""
        target = uuid4()
        action = {
            "action_type": "SELECT_TARGET",
            "target_id": target
        }
        result = action_to_string(action)
        assert "SELECT_TARGET" in result
        assert "Target" in result
    
    def test_action_to_string_with_value(self):
        """Test action with value to string"""
        action = {
            "action_type": "SELECT_AMOUNT",
            "value": np.array([5])
        }
        result = action_to_string(action)
        assert "SELECT_AMOUNT" in result
        assert "Value: 5" in result


class TestDeckValidation:
    """Test deck validation"""
    
    def test_valid_deck(self):
        """Test valid deck"""
        deck = ["Lightning Bolt"] * 4 + ["Mountain"] * 36
        assert is_valid_deck(deck) is True
    
    def test_deck_too_small(self):
        """Test deck too small"""
        deck = ["Mountain"] * 30
        assert is_valid_deck(deck) is False
    
    def test_deck_too_large(self):
        """Test deck too large"""
        deck = ["Mountain"] * 300
        assert is_valid_deck(deck) is False
    
    def test_too_many_copies(self):
        """Test too many copies of non-basic"""
        deck = ["Lightning Bolt"] * 5 + ["Mountain"] * 35
        assert is_valid_deck(deck) is False
    
    def test_basic_lands_unlimited(self):
        """Test basic lands can have unlimited copies"""
        deck = ["Mountain"] * 60
        assert is_valid_deck(deck) is True
    
    def test_empty_deck(self):
        """Test empty deck"""
        assert is_valid_deck([]) is False


class TestGameStateFormatting:
    """Test game state formatting"""
    
    def test_format_none_state(self):
        """Test formatting None state"""
        result = format_game_state(None)
        assert "No game state" in result
    
    def test_format_game_state(self):
        """Test formatting game state"""
        player1 = PlayerView(
            player_id=uuid4(),
            name="Player1",
            controlled=True,
            is_human=True,
            life=20,
            hand_count=7,
            library_count=53
        )
        
        game = GameView(
            players=[player1],
            turn=5,
            phase=TurnPhase.COMBAT
        )
        
        result = format_game_state(game)
        assert "Turn 5" in result
        assert "Player1" in result
        assert "Life=20" in result
        assert "COMBAT" in result
