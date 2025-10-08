"""
Data models for XMage game state representation

This module defines the data structures that represent the game state,
matching the Java view classes from the XMage server.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from uuid import UUID
import numpy as np

from mage_gym.enums import TurnPhase, PhaseStep, Zone, ManaType, ClientCallbackMethod


@dataclass
class CounterView:
    """Counter on a card or player"""
    name: str
    count: int


@dataclass
class ManaPoolView:
    """Mana pool representation"""
    white: int = 0
    blue: int = 0
    black: int = 0
    red: int = 0
    green: int = 0
    colorless: int = 0
    generic: int = 0


@dataclass
class AbilityView:
    """Ability representation"""
    id: UUID
    name: str
    rules: str
    expansion_set_code: str = ""


@dataclass
class CardView:
    """Card representation"""
    
    # Identity
    id: UUID
    name: str
    expansion_set_code: str
    card_number: str = ""
    
    # Types
    super_types: List[str] = field(default_factory=list)
    card_types: List[str] = field(default_factory=list)
    sub_types: List[str] = field(default_factory=list)
    
    # Characteristics
    color: str = ""
    mana_cost: List[str] = field(default_factory=list)
    converted_mana_cost: int = 0
    
    # Rules
    rules: List[str] = field(default_factory=list)
    power: str = ""
    toughness: str = ""
    loyalty: str = ""
    
    # State
    tapped: bool = False
    flipped: bool = False
    transformed: bool = False
    face_down: bool = False
    
    # Counters and damage
    counters: List[CounterView] = field(default_factory=list)
    damage: int = 0
    
    # Targeting
    targets: List[UUID] = field(default_factory=list)
    
    # Abilities
    abilities: List[AbilityView] = field(default_factory=list)
    
    # Status
    controlled: bool = False
    paid: bool = False
    
    # Zone
    zone: Optional[Zone] = None


@dataclass
class PermanentView(CardView):
    """Permanent on battlefield (extends CardView)"""
    
    # Permanent-specific state
    attached_to: Optional[UUID] = None
    original_id: Optional[UUID] = None
    
    # Combat
    attacking: bool = False
    blocked: bool = False
    blocking: bool = False
    
    # Abilities
    summoning_sickness: bool = False
    can_attack: bool = False
    can_block: bool = False
    
    # Special states
    phased_in: bool = True
    monstrous: bool = False
    renowned: bool = False


@dataclass
class CommandObjectView:
    """Command zone object (commander, emblem, etc.)"""
    id: UUID
    name: str
    expansion_set_code: str = ""


@dataclass
class CombatGroupView:
    """Combat group representation"""
    attacker_id: UUID
    blocker_ids: List[UUID] = field(default_factory=list)
    defender_id: Optional[UUID] = None


@dataclass
class ExileView:
    """Exile zone representation"""
    id: UUID
    name: str
    cards: Dict[UUID, CardView] = field(default_factory=dict)


@dataclass
class RevealedView:
    """Revealed cards view"""
    name: str
    cards: Dict[UUID, CardView] = field(default_factory=dict)


@dataclass
class LookedAtView:
    """Looked at cards (like Scry)"""
    name: str
    cards: Dict[UUID, CardView] = field(default_factory=dict)


@dataclass
class PlayerView:
    """Individual player state"""
    
    # Identity
    player_id: UUID
    name: str
    controlled: bool
    is_human: bool
    
    # Life and counters
    life: int
    counters: List[CounterView] = field(default_factory=list)
    
    # Match status
    wins: int = 0
    wins_needed: int = 2
    
    # Zones
    library_count: int = 0
    hand_count: int = 0
    graveyard: Dict[UUID, CardView] = field(default_factory=dict)
    exile: Dict[UUID, CardView] = field(default_factory=dict)
    sideboard: Dict[UUID, CardView] = field(default_factory=dict)
    battlefield: Dict[UUID, PermanentView] = field(default_factory=dict)
    
    # Mana
    mana_pool: ManaPoolView = field(default_factory=ManaPoolView)
    
    # Turn status
    is_active: bool = False
    has_priority: bool = False
    timer_active: bool = False
    
    # Priority passing state
    passed_turn: bool = False  # F4
    passed_until_end_of_turn: bool = False  # F5
    passed_until_next_main: bool = False  # F6
    passed_until_stack_resolved: bool = False  # F8
    passed_all_turns: bool = False  # F9
    passed_until_end_step_before_my_turn: bool = False  # F11
    
    # Special designations
    monarch: bool = False
    initiative: bool = False
    designation_names: List[str] = field(default_factory=list)
    
    # Timing
    priority_time_left_secs: int = 0
    buffer_time_left: int = 0
    
    # State
    has_left: bool = False
    top_card: Optional[CardView] = None
    
    # Command zone
    command_list: List[CommandObjectView] = field(default_factory=list)
    attachments: List[UUID] = field(default_factory=list)
    
    # Rollback
    states_saved_size: int = 0


@dataclass
class GameView:
    """Complete game state snapshot"""
    
    # Player information
    players: List[PlayerView] = field(default_factory=list)
    my_player_id: Optional[UUID] = None
    
    # Hand and playable objects
    my_hand: Dict[UUID, CardView] = field(default_factory=dict)
    my_helper_emblems: Dict[UUID, CardView] = field(default_factory=dict)
    can_play_objects: Optional[Any] = None  # PlayableObjectsList
    
    # Opponent information
    opponent_hands: Dict[str, int] = field(default_factory=dict)  # name -> hand size
    watched_hands: Dict[str, Dict[UUID, CardView]] = field(default_factory=dict)
    
    # Game zones
    stack: Dict[UUID, CardView] = field(default_factory=dict)
    exiles: List[ExileView] = field(default_factory=list)
    revealed: List[RevealedView] = field(default_factory=list)
    looked_at: List[LookedAtView] = field(default_factory=list)
    companion: List[RevealedView] = field(default_factory=list)
    
    # Combat
    combat: List[CombatGroupView] = field(default_factory=list)
    
    # Turn information
    phase: Optional[TurnPhase] = None
    step: Optional[PhaseStep] = None
    turn: int = 0
    active_player_id: Optional[UUID] = None
    active_player_name: str = ""
    priority_player_name: str = ""
    
    # Game settings
    priority_time: int = 0
    buffer_time: int = 0
    rollback_turns_allowed: bool = False
    
    # Special state
    special: bool = False
    
    # Debug info
    total_errors_count: int = 0
    total_effects_count: int = 0
    game_cycle: int = 0
    
    def get_my_player(self) -> Optional[PlayerView]:
        """Get the player view for the current player"""
        if self.my_player_id is None:
            return None
        for player in self.players:
            if player.player_id == self.my_player_id:
                return player
        return None


@dataclass
class GameClientMessage:
    """Message requesting player input"""
    
    game_view: GameView
    options: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    
    # For selection prompts
    cards_view1: Optional[Dict[UUID, CardView]] = None
    cards_view2: Optional[Dict[UUID, CardView]] = None
    targets: Optional[Set[UUID]] = None
    
    # For amount prompts
    min: Optional[int] = None
    max: Optional[int] = None
    
    # For choice prompts
    choice: Optional[Any] = None
    
    # For multi-amount prompts
    messages: Optional[List[str]] = None
    
    flag: bool = False


@dataclass
class ClientCallback:
    """Server callback message"""
    
    # Callback identification
    message_id: int
    method: ClientCallbackMethod
    object_id: UUID
    
    # Payload data (varies by method)
    data: Any
    
    # Compression flag
    compressed: bool = False


@dataclass
class GameAction:
    """Structured game action"""
    
    action_type: str  # ActionType as string
    target_id: Optional[UUID] = None
    value: Optional[Any] = None
    mana_selection: Optional[List[ManaType]] = None


@dataclass
class GameObservation:
    """RL-friendly game observation"""
    
    # Turn information
    turn_number: int
    phase: int  # Encoded phase
    step: int  # Encoded step
    is_my_turn: bool
    have_priority: bool
    
    # Player states (fixed size array)
    players: np.ndarray  # Shape: (max_players, player_features)
    
    # Hand (variable size, padded)
    hand: np.ndarray  # Shape: (max_hand_size, card_features)
    
    # Battlefield (variable size, padded)
    battlefield: np.ndarray  # Shape: (max_battlefield, permanent_features)
    
    # Stack
    stack: np.ndarray  # Shape: (max_stack, stack_object_features)
    
    # Legal actions mask
    legal_actions: np.ndarray  # Binary mask of legal actions
    
    # Game phase encoding
    phase_encoding: np.ndarray  # One-hot encoding of phase/step
    
    # Additional context
    opponent_hand_sizes: np.ndarray
    mana_pool: np.ndarray  # Available mana by color
    life_totals: np.ndarray


@dataclass
class ConnectionConfig:
    """XMage server connection configuration"""
    
    # Server connection
    host: str = "localhost"
    port: int = 17171
    
    # Authentication
    username: str = "player"
    password: str = "password"
    email: Optional[str] = None
    
    # Transport configuration
    transport: str = "bisocket"
    serialization: str = "java"
    
    # Proxy settings
    proxy_type: Optional[str] = None
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    
    # Timeout settings
    socket_timeout: int = 30
    lease_period: int = 5000
    
    # Client metadata
    client_version: str = "1.4.50"
    user_id_str: Optional[str] = None


@dataclass
class MatchOptions:
    """Options for creating a match"""
    
    name: str = "Test Game"
    game_type: str = "Two Player Duel"
    free_mulligans: int = 0
    password: str = ""
    deck_type: str = "Constructed"
    limited_options: Optional[Dict] = None
    banned_users: List[str] = field(default_factory=list)
    spectators_allowed: bool = True
    rated_match: bool = False
    range: int = 0
    skill_level: str = "Casual"


@dataclass
class DeckCardLists:
    """Deck card lists"""
    
    main_deck: List[str] = field(default_factory=list)
    sideboard: List[str] = field(default_factory=list)
    
    @classmethod
    def from_file(cls, path: str) -> 'DeckCardLists':
        """Load deck from file"""
        main_deck = []
        sideboard = []
        in_sideboard = False
        
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.lower() == 'sideboard':
                    in_sideboard = True
                    continue
                
                # Parse line format: "4 Card Name" or "Card Name"
                parts = line.split(' ', 1)
                if len(parts) == 2 and parts[0].isdigit():
                    count = int(parts[0])
                    card_name = parts[1]
                else:
                    count = 1
                    card_name = line
                
                for _ in range(count):
                    if in_sideboard:
                        sideboard.append(card_name)
                    else:
                        main_deck.append(card_name)
        
        return cls(main_deck=main_deck, sideboard=sideboard)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "main_deck": self.main_deck,
            "sideboard": self.sideboard
        }
