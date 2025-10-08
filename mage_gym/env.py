"""
Gymnasium Environment for XMage

This module implements the main Gymnasium environment interface
for interacting with the XMage server.
"""

from typing import Tuple, Dict, Any, Optional
from uuid import UUID
import logging

import gymnasium as gym
from gymnasium import spaces
import numpy as np

from mage_gym.connection import XMageConnection
from mage_gym.game_state_manager import XMageGameStateManager
from mage_gym.models import MatchOptions, DeckCardLists
from mage_gym.enums import PlayerType

logger = logging.getLogger(__name__)


class XMageEnv(gym.Env):
    """
    Gymnasium environment for XMage
    
    This environment wraps the XMage server connection and game state
    to provide a standard RL interface.
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    
    def __init__(
        self,
        server_host: str = "localhost",
        server_port: int = 17171,
        username: str = "player",
        password: str = "password",
        deck_list: Optional[DeckCardLists] = None,
        opponent_type: str = "ai",
        render_mode: Optional[str] = None,
        max_turns: int = 50,
    ):
        """
        Initialize XMage environment
        
        Args:
            server_host: XMage server hostname
            server_port: XMage server port
            username: Player username
            password: Player password
            deck_list: Deck configuration
            opponent_type: Type of opponent ("ai" or "human")
            render_mode: Rendering mode ("human" or "rgb_array")
            max_turns: Maximum turns before episode ends
        """
        super().__init__()
        
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.password = password
        self.deck_list = deck_list or self._create_default_deck()
        self.opponent_type = opponent_type
        self.max_turns = max_turns
        self.render_mode = render_mode
        
        # Initialize connection (lazy)
        self.connection: Optional[XMageConnection] = None
        self.game_state_manager: Optional[XMageGameStateManager] = None
        
        # Current episode state
        self.current_game_id: Optional[UUID] = None
        self.episode_step: int = 0
        self.episode_reward: float = 0.0
        
        # Define action and observation spaces
        self.action_space = self._create_action_space()
        self.observation_space = self._create_observation_space()
    
    def _create_default_deck(self) -> DeckCardLists:
        """Create a simple default deck for testing"""
        # Simple mono-red aggro deck
        main_deck = (
            ["Mountain"] * 20 +
            ["Shock"] * 4 +
            ["Lightning Bolt"] * 4 +
            ["Goblin Guide"] * 4 +
            ["Monastery Swiftspear"] * 4 +
            ["Lava Spike"] * 4
        )
        
        return DeckCardLists(main_deck=main_deck, sideboard=[])
    
    def _create_action_space(self) -> gym.Space:
        """Create action space definition"""
        # Discrete action space with type and parameters
        return spaces.Dict({
            "action_type": spaces.Discrete(20),  # 20 action types
            "target_id": spaces.Discrete(1000),  # Target object index
            "value": spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
        })
    
    def _create_observation_space(self) -> gym.Space:
        """Create observation space definition"""
        return spaces.Dict({
            # Scalar values
            "turn_number": spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
            "phase": spaces.Box(low=0, high=10, shape=(1,), dtype=np.int32),
            "step": spaces.Box(low=0, high=15, shape=(1,), dtype=np.int32),
            "is_my_turn": spaces.Box(low=0, high=1, shape=(1,), dtype=np.int32),
            "have_priority": spaces.Box(low=0, high=1, shape=(1,), dtype=np.int32),
            
            # Player information
            "players": spaces.Box(
                low=-100, high=10000,
                shape=(4, 15),
                dtype=np.float32
            ),
            
            # Hand
            "hand": spaces.Box(
                low=0, high=100,
                shape=(20, 30),
                dtype=np.float32
            ),
            
            # Battlefield
            "battlefield": spaces.Box(
                low=0, high=100,
                shape=(50, 35),
                dtype=np.float32
            ),
            
            # Stack
            "stack": spaces.Box(
                low=0, high=100,
                shape=(20, 25),
                dtype=np.float32
            ),
            
            # Action mask
            "action_mask": spaces.MultiBinary(1000),
        })
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[Dict, Dict]:
        """
        Reset environment to initial state (start new game)
        
        Args:
            seed: Random seed
            options: Additional options
            
        Returns:
            observation: Initial observation
            info: Additional information
        """
        super().reset(seed=seed)
        
        # Connect to server if not connected
        if self.connection is None or not self.connection.is_connected():
            self._connect()
        
        # Create or join a game
        self.current_game_id = self._create_game()
        
        # Wait for game to start
        self._wait_for_game_start()
        
        # Get initial observation
        observation = self._get_observation()
        info = self._get_info()
        
        self.episode_step = 0
        self.episode_reward = 0.0
        
        return observation, info
    
    def step(
        self,
        action: Dict
    ) -> Tuple[Dict, float, bool, bool, Dict]:
        """
        Execute action in environment
        
        Args:
            action: Action to execute
            
        Returns:
            observation: New observation after action
            reward: Reward for this step
            terminated: Whether episode is done (win/loss)
            truncated: Whether episode was truncated (time limit)
            info: Additional information
        """
        self.episode_step += 1
        
        # Translate and send action to server
        self._send_action(action)
        
        # Wait for game state update
        self._wait_for_update()
        
        # Get new observation
        observation = self._get_observation()
        
        # Calculate reward
        reward = self._calculate_reward()
        self.episode_reward += reward
        
        # Check if game is over
        terminated = self._is_game_over()
        truncated = self.episode_step >= self.max_turns * 10  # Approximate steps per turn
        
        # Get additional info
        info = self._get_info()
        
        if terminated or truncated:
            self._cleanup_game()
        
        return observation, reward, terminated, truncated, info
    
    def render(self):
        """Render the environment"""
        if self.render_mode == "human":
            self._render_text()
        elif self.render_mode == "rgb_array":
            return self._render_rgb()
        return None
    
    def close(self):
        """Close the environment and disconnect"""
        if self.connection is not None:
            if self.current_game_id is not None:
                self._cleanup_game()
            
            if self.game_state_manager:
                self.game_state_manager.stop_callback_processing()
            
            self.connection.disconnect()
            self.connection = None
    
    def _connect(self):
        """Establish connection to XMage server"""
        logger.info(f"Connecting to XMage server at {self.server_host}:{self.server_port}")
        
        self.connection = XMageConnection()
        success = self.connection.connect(
            self.server_host,
            self.server_port,
            self.username,
            self.password
        )
        
        if not success:
            raise ConnectionError("Failed to connect to XMage server")
        
        self.game_state_manager = XMageGameStateManager(self.connection)
        self.game_state_manager.start_callback_processing()
        
        logger.info("Connected to XMage server")
    
    def _create_game(self) -> UUID:
        """Create a new game on the server"""
        logger.info("Creating new game")
        
        # Get main room
        room_id = self.connection.get_main_room_id()
        
        # Create table with match options
        match_options = MatchOptions(
            name=f"RL Game {self.username}",
            game_type="Two Player Duel",
            free_mulligans=1,
        )
        
        table_view = self.connection.create_table(room_id, match_options)
        
        # Join the table with our deck
        self.connection.join_table(
            room_id,
            table_view.table_id,
            self.username,
            PlayerType.HUMAN,
            skill=5,
            deck_list=self.deck_list,
            password=""
        )
        
        # Add opponent if needed
        if self.opponent_type == "ai":
            self._add_ai_opponent(room_id, table_view.table_id)
        
        # Start the match
        self.connection.start_match(room_id, table_view.table_id)
        
        logger.info(f"Game created with ID: {table_view.game_id}")
        
        return table_view.game_id
    
    def _add_ai_opponent(self, room_id: UUID, table_id: UUID):
        """Add AI opponent to the game"""
        # In a real implementation, this would add a computer player
        logger.info("Adding AI opponent")
    
    def _wait_for_game_start(self, timeout: float = 30.0):
        """Wait for game to start"""
        logger.info("Waiting for game to start")
        # In a real implementation, wait for START_GAME callback
        import time
        time.sleep(1.0)  # Simulate wait
    
    def _send_action(self, action: Dict):
        """Send action to server"""
        if self.game_state_manager is None:
            return
        
        self.game_state_manager.execute_action(
            self.current_game_id,
            action
        )
    
    def _wait_for_update(self, timeout: float = 5.0):
        """Wait for game state update from server"""
        if self.game_state_manager is None:
            return
        
        self.game_state_manager.wait_for_update(timeout)
    
    def _get_observation(self) -> Dict:
        """Get current observation from game state"""
        if self.game_state_manager is None:
            return self._create_empty_observation()
        
        return self.game_state_manager.get_observation()
    
    def _create_empty_observation(self) -> Dict:
        """Create empty observation"""
        return {
            "turn_number": np.array([0], dtype=np.int32),
            "phase": np.array([0], dtype=np.int32),
            "step": np.array([0], dtype=np.int32),
            "is_my_turn": np.array([0], dtype=np.int32),
            "have_priority": np.array([0], dtype=np.int32),
            "players": np.zeros((4, 15), dtype=np.float32),
            "hand": np.zeros((20, 30), dtype=np.float32),
            "battlefield": np.zeros((50, 35), dtype=np.float32),
            "stack": np.zeros((20, 25), dtype=np.float32),
            "action_mask": np.zeros(1000, dtype=np.int8),
        }
    
    def _calculate_reward(self) -> float:
        """Calculate reward for current state"""
        if self.game_state_manager is None:
            return 0.0
        
        game_state = self.game_state_manager.get_game_state()
        
        if game_state is None:
            return 0.0
        
        my_player = game_state.get_my_player()
        if my_player is None:
            return 0.0
        
        reward = 0.0
        
        # Life differential
        opponents = [p for p in game_state.players if p.player_id != my_player.player_id]
        if opponents:
            my_life = my_player.life
            opp_life = sum(p.life for p in opponents) / len(opponents)
            reward += (my_life - opp_life) * 0.01
        
        # Board state
        my_permanents = len(my_player.battlefield)
        opp_permanents = sum(len(p.battlefield) for p in opponents)
        reward += (my_permanents - opp_permanents) * 0.1
        
        # Card advantage
        my_cards = my_player.hand_count + my_player.library_count
        opp_cards = sum(p.hand_count + p.library_count for p in opponents)
        reward += (my_cards - opp_cards) * 0.01
        
        return reward
    
    def _is_game_over(self) -> bool:
        """Check if game is finished"""
        if self.game_state_manager is None:
            return False
        
        game_state = self.game_state_manager.get_game_state()
        if game_state is None:
            return True
        
        # Check if any player has won
        for player in game_state.players:
            if player.wins >= player.wins_needed:
                return True
            if player.has_left:
                return True
        
        return False
    
    def _get_info(self) -> Dict:
        """Get additional information about current state"""
        info = {
            "episode_step": self.episode_step,
            "episode_reward": self.episode_reward,
        }
        
        if self.game_state_manager:
            game_state = self.game_state_manager.get_game_state()
            
            if game_state:
                my_player = game_state.get_my_player()
                if my_player:
                    info.update({
                        "life": my_player.life,
                        "hand_size": my_player.hand_count,
                        "turn": game_state.turn,
                        "phase": game_state.phase.name if game_state.phase else "UNKNOWN",
                    })
        
        return info
    
    def _cleanup_game(self):
        """Clean up current game"""
        if self.current_game_id and self.connection:
            try:
                self.connection.quit_match(self.current_game_id)
            except:
                pass
        
        self.current_game_id = None
    
    def _render_text(self):
        """Render game state as text"""
        if self.game_state_manager is None:
            print("No game state available")
            return
        
        game_state = self.game_state_manager.get_game_state()
        
        if game_state is None:
            print("No game state available")
            return
        
        print("\n" + "=" * 60)
        print(f"Turn {game_state.turn} - {game_state.phase.name if game_state.phase else 'N/A'}")
        print("=" * 60)
        
        for player in game_state.players:
            marker = ">> " if player.controlled else "   "
            print(f"{marker}{player.name}: Life={player.life}, Hand={player.hand_count}, "
                  f"Library={player.library_count}, Battlefield={len(player.battlefield)}")
        
        print("=" * 60)
    
    def _render_rgb(self) -> np.ndarray:
        """Render game state as RGB array"""
        # Create a simple visualization
        # In a real implementation, this would render the game board
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        return img
