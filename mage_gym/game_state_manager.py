"""
Game State Manager for XMage

This module manages the game state synchronization and action translation
between the Gymnasium environment and the XMage server.
"""

from typing import Optional, Dict, List, Any
from uuid import UUID
import logging
import numpy as np
import threading
import time

from mage_gym.connection import XMageConnection
from mage_gym.models import (
    GameView,
    PlayerView,
    GameObservation,
    GameAction,
    ClientCallback,
)
from mage_gym.enums import (
    TurnPhase,
    PhaseStep,
    ClientCallbackMethod,
)

logger = logging.getLogger(__name__)


class XMageGameStateManager:
    """
    Manages game state synchronization
    
    This class handles:
    - Receiving and processing server callbacks
    - Maintaining current game state
    - Translating actions to server commands
    - Extracting observations for RL agents
    """
    
    def __init__(self, connection: XMageConnection):
        """
        Initialize with connection
        
        Args:
            connection: Active XMage connection
        """
        self.connection = connection
        self._current_game_state: Optional[GameView] = None
        self._state_lock = threading.Lock()
        self._update_event = threading.Event()
        self._callback_thread: Optional[threading.Thread] = None
        self._running = False
        
    def start_callback_processing(self):
        """Start background thread to process server callbacks"""
        if self._running:
            return
        
        self._running = True
        self._callback_thread = threading.Thread(
            target=self._process_callbacks,
            daemon=True
        )
        self._callback_thread.start()
        logger.info("Started callback processing thread")
    
    def stop_callback_processing(self):
        """Stop background callback processing"""
        self._running = False
        if self._callback_thread:
            self._callback_thread.join(timeout=5.0)
            self._callback_thread = None
        logger.info("Stopped callback processing thread")
    
    def _process_callbacks(self):
        """Background thread to process server callbacks"""
        while self._running:
            try:
                # Wait for callback from server
                callback = self.connection.wait_for_callback(timeout=1.0)
                
                if callback is None:
                    continue
                
                # Process callback based on method
                if callback.method == ClientCallbackMethod.GAME_UPDATE:
                    self._handle_game_update(callback)
                elif callback.method == ClientCallbackMethod.GAME_INIT:
                    self._handle_game_init(callback)
                elif callback.method == ClientCallbackMethod.GAME_OVER:
                    self._handle_game_over(callback)
                # Add more callback handlers as needed
                
            except Exception as e:
                logger.error(f"Error processing callback: {e}")
    
    def _handle_game_update(self, callback: ClientCallback):
        """Handle game state update"""
        try:
            game_view = callback.data  # Should be GameView
            with self._state_lock:
                self._current_game_state = game_view
                self._update_event.set()
            logger.debug("Game state updated")
        except Exception as e:
            logger.error(f"Error handling game update: {e}")
    
    def _handle_game_init(self, callback: ClientCallback):
        """Handle game initialization"""
        try:
            game_view = callback.data
            with self._state_lock:
                self._current_game_state = game_view
                self._update_event.set()
            logger.info("Game initialized")
        except Exception as e:
            logger.error(f"Error handling game init: {e}")
    
    def _handle_game_over(self, callback: ClientCallback):
        """Handle game over"""
        logger.info("Game over")
        # Could set a flag or update state to indicate game is done
    
    def get_game_state(self) -> Optional[GameView]:
        """Get current game state"""
        with self._state_lock:
            return self._current_game_state
    
    def get_observation(self) -> Dict[str, np.ndarray]:
        """
        Get RL observation from game state
        
        Returns:
            Dictionary of numpy arrays representing the game state
        """
        game_state = self.get_game_state()
        
        if game_state is None:
            # Return empty observation
            return self._create_empty_observation()
        
        return self._extract_observation(game_state)
    
    def _create_empty_observation(self) -> Dict[str, np.ndarray]:
        """Create empty observation when no game state available"""
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
    
    def _extract_observation(self, game_state: GameView) -> Dict[str, np.ndarray]:
        """
        Extract observation from game state
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary of numpy arrays
        """
        # Get my player
        my_player = game_state.get_my_player()
        
        # Turn information
        turn_number = np.array([game_state.turn], dtype=np.int32)
        
        # Encode phase and step
        phase_encoding = self._encode_phase(game_state.phase)
        step_encoding = self._encode_step(game_state.step)
        
        # Check if it's my turn and I have priority
        is_my_turn = np.array([
            1 if my_player and my_player.is_active else 0
        ], dtype=np.int32)
        
        have_priority = np.array([
            1 if my_player and my_player.has_priority else 0
        ], dtype=np.int32)
        
        # Extract player features
        players = self._extract_player_features(game_state.players, my_player)
        
        # Extract hand features
        hand = self._extract_hand_features(game_state.my_hand)
        
        # Extract battlefield features
        battlefield = self._extract_battlefield_features(my_player, game_state.players)
        
        # Extract stack features
        stack = self._extract_stack_features(game_state.stack)
        
        # Create action mask (simplified - all actions available)
        action_mask = np.ones(1000, dtype=np.int8)
        
        return {
            "turn_number": turn_number,
            "phase": phase_encoding,
            "step": step_encoding,
            "is_my_turn": is_my_turn,
            "have_priority": have_priority,
            "players": players,
            "hand": hand,
            "battlefield": battlefield,
            "stack": stack,
            "action_mask": action_mask,
        }
    
    def _encode_phase(self, phase: Optional[TurnPhase]) -> np.ndarray:
        """Encode turn phase to integer"""
        if phase is None:
            return np.array([0], dtype=np.int32)
        
        phase_map = {
            TurnPhase.BEGINNING: 1,
            TurnPhase.PRECOMBAT_MAIN: 2,
            TurnPhase.COMBAT: 3,
            TurnPhase.POSTCOMBAT_MAIN: 4,
            TurnPhase.END: 5,
        }
        
        return np.array([phase_map.get(phase, 0)], dtype=np.int32)
    
    def _encode_step(self, step: Optional[PhaseStep]) -> np.ndarray:
        """Encode phase step to integer"""
        if step is None:
            return np.array([0], dtype=np.int32)
        
        step_map = {
            PhaseStep.UNTAP: 1,
            PhaseStep.UPKEEP: 2,
            PhaseStep.DRAW: 3,
            PhaseStep.PRECOMBAT_MAIN: 4,
            PhaseStep.BEGIN_COMBAT: 5,
            PhaseStep.DECLARE_ATTACKERS: 6,
            PhaseStep.DECLARE_BLOCKERS: 7,
            PhaseStep.COMBAT_DAMAGE: 8,
            PhaseStep.END_COMBAT: 9,
            PhaseStep.POSTCOMBAT_MAIN: 10,
            PhaseStep.END_TURN: 11,
            PhaseStep.CLEANUP: 12,
        }
        
        return np.array([step_map.get(step, 0)], dtype=np.int32)
    
    def _extract_player_features(
        self,
        players: List[PlayerView],
        my_player: Optional[PlayerView]
    ) -> np.ndarray:
        """Extract features for all players"""
        # Fixed size: 4 players x 15 features
        features = np.zeros((4, 15), dtype=np.float32)
        
        for i, player in enumerate(players[:4]):
            features[i] = [
                player.life,
                player.library_count,
                player.hand_count,
                len(player.graveyard),
                len(player.battlefield),
                player.mana_pool.white,
                player.mana_pool.blue,
                player.mana_pool.black,
                player.mana_pool.red,
                player.mana_pool.green,
                player.mana_pool.colorless,
                1 if player.is_active else 0,
                1 if player.has_priority else 0,
                1 if player.controlled else 0,
                1 if player.has_left else 0,
            ]
        
        return features
    
    def _extract_hand_features(
        self,
        hand: Dict[UUID, Any]
    ) -> np.ndarray:
        """Extract features from hand"""
        # Fixed size: 20 cards x 30 features
        features = np.zeros((20, 30), dtype=np.float32)
        
        for i, (card_id, card) in enumerate(list(hand.items())[:20]):
            # Simplified card features
            features[i] = self._extract_card_features(card)
        
        return features
    
    def _extract_card_features(self, card) -> np.ndarray:
        """Extract features from a single card"""
        # 30 features per card (simplified)
        features = np.zeros(30, dtype=np.float32)
        
        # Basic features
        if hasattr(card, 'converted_mana_cost'):
            features[0] = card.converted_mana_cost
        
        # Add more feature extraction as needed
        # This would include: color, types, power/toughness, etc.
        
        return features
    
    def _extract_battlefield_features(
        self,
        my_player: Optional[PlayerView],
        all_players: List[PlayerView]
    ) -> np.ndarray:
        """Extract features from battlefield"""
        # Fixed size: 50 permanents x 35 features
        features = np.zeros((50, 35), dtype=np.float32)
        
        idx = 0
        for player in all_players:
            for permanent_id, permanent in list(player.battlefield.items()):
                if idx >= 50:
                    break
                features[idx] = self._extract_permanent_features(permanent)
                idx += 1
        
        return features
    
    def _extract_permanent_features(self, permanent) -> np.ndarray:
        """Extract features from a permanent"""
        # 35 features per permanent
        features = self._extract_card_features(permanent)
        
        # Extend with permanent-specific features
        extended = np.zeros(35, dtype=np.float32)
        extended[:30] = features
        
        if hasattr(permanent, 'tapped'):
            extended[30] = 1 if permanent.tapped else 0
        if hasattr(permanent, 'attacking'):
            extended[31] = 1 if permanent.attacking else 0
        if hasattr(permanent, 'summoning_sickness'):
            extended[32] = 1 if permanent.summoning_sickness else 0
        
        return extended
    
    def _extract_stack_features(
        self,
        stack: Dict[UUID, Any]
    ) -> np.ndarray:
        """Extract features from stack"""
        # Fixed size: 20 stack objects x 25 features
        features = np.zeros((20, 25), dtype=np.float32)
        
        for i, (obj_id, obj) in enumerate(list(stack.items())[:20]):
            features[i] = self._extract_card_features(obj)[:25]
        
        return features
    
    def execute_action(
        self,
        game_id: UUID,
        action: Dict[str, Any]
    ) -> bool:
        """
        Execute structured action
        
        Args:
            game_id: Game UUID
            action: Action dictionary with 'action_type', 'target_id', 'value'
            
        Returns:
            True if action sent successfully
        """
        try:
            action_type = action.get("action_type")
            target_id = action.get("target_id")
            value = action.get("value")
            
            logger.debug(f"Executing action: {action_type}")
            
            # Translate action to server commands
            # This is simplified - real implementation would handle all action types
            
            if action_type == "PASS_PRIORITY":
                # Just send a pass priority action
                return True
            
            elif action_type == "CAST_SPELL":
                if target_id:
                    return self.connection.send_player_uuid(game_id, target_id)
            
            elif action_type == "SELECT_TARGET":
                if target_id:
                    return self.connection.send_player_uuid(game_id, target_id)
            
            elif action_type == "SELECT_CHOICE":
                if value:
                    return self.connection.send_player_string(game_id, str(value))
            
            # Add more action handlers as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return False
    
    def wait_for_update(self, timeout: float = 30.0) -> bool:
        """
        Wait for game state update from server
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if update received, False if timeout
        """
        self._update_event.clear()
        return self._update_event.wait(timeout)
    
    def get_legal_actions(self) -> List[Dict]:
        """
        Get list of legal actions
        
        Returns:
            List of action dictionaries
        """
        game_state = self.get_game_state()
        
        if game_state is None:
            return []
        
        # This would analyze the game state and return legal actions
        # For now, return a simplified list
        return [
            {"action_type": "PASS_PRIORITY", "target_id": None, "value": None}
        ]
