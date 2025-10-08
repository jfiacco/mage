"""
Tests for Gymnasium environment
"""

import pytest
import numpy as np
from gymnasium import spaces

from mage_gym.env import XMageEnv
from mage_gym.models import DeckCardLists


class TestXMageEnv:
    """Test XMageEnv class"""
    
    def test_initialization(self):
        """Test environment initialization"""
        env = XMageEnv()
        assert env.server_host == "localhost"
        assert env.server_port == 17171
        assert env.max_turns == 50
    
    def test_custom_initialization(self):
        """Test environment with custom parameters"""
        deck = DeckCardLists(main_deck=["Mountain"] * 60)
        env = XMageEnv(
            server_host="example.com",
            server_port=12345,
            username="testuser",
            deck_list=deck,
            max_turns=100
        )
        
        assert env.server_host == "example.com"
        assert env.server_port == 12345
        assert env.username == "testuser"
        assert env.max_turns == 100
    
    def test_default_deck_creation(self):
        """Test default deck is created"""
        env = XMageEnv()
        assert env.deck_list is not None
        assert len(env.deck_list.main_deck) > 0
    
    def test_action_space(self):
        """Test action space is valid"""
        env = XMageEnv()
        assert isinstance(env.action_space, spaces.Dict)
        assert "action_type" in env.action_space.spaces
        assert "target_id" in env.action_space.spaces
        assert "value" in env.action_space.spaces
    
    def test_observation_space(self):
        """Test observation space is valid"""
        env = XMageEnv()
        assert isinstance(env.observation_space, spaces.Dict)
        assert "turn_number" in env.observation_space.spaces
        assert "phase" in env.observation_space.spaces
        assert "players" in env.observation_space.spaces
        assert "hand" in env.observation_space.spaces
        assert "battlefield" in env.observation_space.spaces
    
    def test_observation_space_shapes(self):
        """Test observation space shapes"""
        env = XMageEnv()
        
        # Check player space shape
        assert env.observation_space.spaces["players"].shape == (4, 15)
        
        # Check hand space shape
        assert env.observation_space.spaces["hand"].shape == (20, 30)
        
        # Check battlefield space shape
        assert env.observation_space.spaces["battlefield"].shape == (50, 35)
    
    def test_action_space_sampling(self):
        """Test action space can be sampled"""
        env = XMageEnv()
        action = env.action_space.sample()
        
        assert "action_type" in action
        assert "target_id" in action
        assert "value" in action
    
    def test_create_empty_observation(self):
        """Test creating empty observation"""
        env = XMageEnv()
        obs = env._create_empty_observation()
        
        assert "turn_number" in obs
        assert "phase" in obs
        assert "players" in obs
        
        # Check shapes
        assert obs["turn_number"].shape == (1,)
        assert obs["players"].shape == (4, 15)
        assert obs["hand"].shape == (20, 30)
    
    def test_calculate_reward_no_state(self):
        """Test reward calculation with no state"""
        env = XMageEnv()
        reward = env._calculate_reward()
        assert reward == 0.0
    
    def test_is_game_over_no_state(self):
        """Test game over check with no state"""
        env = XMageEnv()
        assert env._is_game_over() is False
    
    def test_get_info_no_state(self):
        """Test getting info with no state"""
        env = XMageEnv()
        info = env._get_info()
        
        assert "episode_step" in info
        assert "episode_reward" in info
    
    def test_close_without_connection(self):
        """Test closing env without connection"""
        env = XMageEnv()
        # Should not raise exception
        env.close()
    
    def test_metadata(self):
        """Test environment metadata"""
        env = XMageEnv()
        assert "render_modes" in env.metadata
        assert "human" in env.metadata["render_modes"]
        assert "rgb_array" in env.metadata["render_modes"]
    
    def test_render_modes(self):
        """Test render modes"""
        # Human mode
        env = XMageEnv(render_mode="human")
        assert env.render_mode == "human"
        
        # RGB mode
        env = XMageEnv(render_mode="rgb_array")
        assert env.render_mode == "rgb_array"
    
    def test_render_rgb_array(self):
        """Test RGB rendering"""
        env = XMageEnv(render_mode="rgb_array")
        result = env._render_rgb()
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (480, 640, 3)
        assert result.dtype == np.uint8
