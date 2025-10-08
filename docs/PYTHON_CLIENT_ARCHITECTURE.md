# Python Gymnasium Client Architecture for XMage Server

## Table of Contents

1. [Overview](#overview)
2. [Architecture Components](#architecture-components)
3. [Connection and Authentication](#connection-and-authentication)
4. [Communication Protocol](#communication-protocol)
5. [Message Structures](#message-structures)
6. [Game State Representation](#game-state-representation)
7. [Action Space](#action-space)
8. [Observation Space](#observation-space)
9. [Gymnasium Environment Interface](#gymnasium-environment-interface)
10. [Implementation Examples](#implementation-examples)
11. [API Reference](#api-reference)

---

## Overview

This document describes the architecture for a Python client designed as a Gymnasium environment to interface with the XMage (Magic Another Game Engine) server. The XMage server is a Java-based server that uses the JBoss Remoting framework (bisocket transport) for network communication.

### Key Characteristics

- **Protocol**: JBoss Remoting with bisocket transport over TCP
- **Serialization**: Java object serialization
- **Server-side Language**: Java
- **Client-side Language**: Python (requires bridging)
- **Session Management**: Session-based with UUID identifiers
- **Communication Pattern**: Request-response with server-initiated callbacks

---

## Architecture Components

### High-Level Architecture

```
┌─────────────────────────────────────┐
│   Gymnasium Environment Wrapper     │
│  (Standard gym.Env interface)       │
└────────────┬────────────────────────┘
             │
             │ step(), reset(), render()
             │
┌────────────▼────────────────────────┐
│   XMage Game State Manager          │
│  - State synchronization            │
│  - Action translation               │
│  - Observation extraction           │
└────────────┬────────────────────────┘
             │
             │ Game state updates
             │
┌────────────▼────────────────────────┐
│   Network Client Layer              │
│  - Session management               │
│  - Message handling                 │
│  - Callback processing              │
└────────────┬────────────────────────┘
             │
             │ TCP/bisocket
             │
┌────────────▼────────────────────────┐
│   Protocol Bridge                   │
│  - Java serialization bridge        │
│  - Message serialization            │
│  - Object conversion                │
└────────────┬────────────────────────┘
             │
             │ JBoss Remoting Protocol
             │
┌────────────▼────────────────────────┐
│      XMage Server (Java)            │
│  - Game engine                      │
│  - Rules enforcement                │
│  - MageServer interface             │
└─────────────────────────────────────┘
```

### Component Responsibilities

#### 1. **Gymnasium Environment Wrapper**
- Implements `gym.Env` interface
- Defines action and observation spaces
- Manages episode lifecycle (reset, step, done)
- Calculates rewards based on game state

#### 2. **XMage Game State Manager**
- Maintains current game state representation
- Translates high-level actions to XMage protocol
- Extracts observations from game state
- Handles turn-based game flow

#### 3. **Network Client Layer**
- Manages TCP connection to XMage server
- Handles session lifecycle (connect, authenticate, disconnect)
- Processes asynchronous server callbacks
- Implements timeout and reconnection logic

#### 4. **Protocol Bridge**
- Bridges Java serialization to Python
- Can use approaches like:
  - Py4J (Java gateway)
  - JPype (JVM embedding)
  - Custom protocol implementation
  - REST/WebSocket wrapper around Java client

---

## Connection and Authentication

### Connection Workflow

```
Client                          Server
  │                              │
  │─────── Connect ──────────────►│
  │         (host, port)          │
  │                              │
  │◄──── Session Created ────────│
  │    (sessionId: UUID)          │
  │                              │
  │─────── Register/Connect ─────►│
  │    (username, password)       │
  │                              │
  │◄──── Auth Success ───────────│
  │    (user data, server info)   │
  │                              │
  │─────── Get Main Room ────────►│
  │                              │
  │◄──── Room ID ────────────────│
  │                              │
```

### Connection Interface

The client must implement the `Connect` interface:

```python
class XMageConnection:
    """Manages connection to XMage server"""
    
    def connect(self, host: str, port: int, 
                username: str, password: str) -> bool:
        """
        Establish connection to XMage server
        
        Args:
            host: Server hostname or IP
            port: Server port (typically 17171)
            username: User account name
            password: User password
            
        Returns:
            True if connection successful
            
        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
        """
        pass
    
    def disconnect(self, ask_reconnect: bool = False,
                   keep_session: bool = False) -> None:
        """
        Disconnect from server
        
        Args:
            ask_reconnect: Whether to prompt for reconnection
            keep_session: Keep session active for reconnection
        """
        pass
    
    def get_session_id(self) -> str:
        """Get current session UUID"""
        pass
    
    def is_connected(self) -> bool:
        """Check if connected to server"""
        pass
    
    def ping(self) -> None:
        """Send keepalive ping to server"""
        pass
```

### Connection Parameters

```python
@dataclass
class ConnectionConfig:
    """XMage server connection configuration"""
    
    # Server connection
    host: str = "localhost"
    port: int = 17171
    
    # Authentication
    username: str
    password: str
    email: Optional[str] = None
    
    # Transport configuration
    transport: str = "bisocket"  # JBoss Remoting transport
    serialization: str = "java"  # Java object serialization
    
    # Proxy settings (if needed)
    proxy_type: Optional[str] = None  # "SOCKS", "HTTP", or None
    proxy_host: Optional[str] = None
    proxy_port: Optional[int] = None
    
    # Timeout settings
    socket_timeout: int = 30  # seconds
    lease_period: int = 5000  # milliseconds (heartbeat)
    
    # Client metadata
    client_version: str = "1.4.50"  # XMage client version
    user_id_str: Optional[str] = None
```

### Connection URI Format

The XMage server uses JBoss Remoting URIs:

```
bisocket://host:port/?serializationtype=java&onewayThreadPool=mage.remote.CustomThreadPool
```

Example: `bisocket://localhost:17171/?serializationtype=java&onewayThreadPool=mage.remote.CustomThreadPool`

---

## Communication Protocol

### Message Flow

XMage uses two types of communication:

1. **Client-to-Server Requests** (Synchronous)
   - Client invokes methods on `MageServer` interface
   - Server processes and returns response
   - Examples: createTable, joinGame, sendPlayerAction

2. **Server-to-Client Callbacks** (Asynchronous)
   - Server pushes updates via `ClientCallback` objects
   - Client implements `MageClient` callback interface
   - Examples: game state updates, dialog requests, messages

### Protocol Layers

```
┌─────────────────────────────────────┐
│  Application Layer                  │
│  (MageServer/MageClient interfaces) │
├─────────────────────────────────────┤
│  Callback Layer                     │
│  (ClientCallback, ClientCallbackMethod)│
├─────────────────────────────────────┤
│  Serialization Layer                │
│  (Java object serialization)        │
├─────────────────────────────────────┤
│  Transport Layer                    │
│  (JBoss Remoting - bisocket)        │
├─────────────────────────────────────┤
│  Network Layer (TCP)                │
└─────────────────────────────────────┘
```

### Server Interface (MageServer)

The server exposes methods through the `MageServer` interface:

```java
// Key methods from MageServer interface

// Room and table management
UUID serverGetMainRoomId() throws MageException;
TableView roomCreateTable(String sessionId, UUID roomId, 
                         MatchOptions matchOptions) throws MageException;

// Game joining
boolean tableJoinTable(String sessionId, UUID roomId, UUID tableId,
                      String playerName, String playerType, int skill,
                      DeckCardLists deckList, String password) throws MageException;

// Game actions
void sendPlayerAction(PlayerAction playerAction, UUID gameId, 
                     Object data) throws MageException;
void sendPlayerUUID(UUID gameId, String sessionId, UUID data) throws MageException;
void sendPlayerBoolean(UUID gameId, String sessionId, Boolean data) throws MageException;
void sendPlayerInteger(UUID gameId, String sessionId, Integer data) throws MageException;
void sendPlayerString(UUID gameId, String sessionId, String data) throws MageException;
void sendPlayerManaType(UUID gameId, String sessionId, UUID playerId, 
                       ManaType data) throws MageException;

// Game control
void quitMatch(UUID gameId, String sessionId) throws MageException;
void concedeGame(UUID gameId, String sessionId) throws MageException;
```

### Client Callback Interface (MageClient)

The client must implement callback handlers:

```java
// From MageClient interface
void connected(String message);
void disconnected(boolean askToReconnect, boolean keepMySessionActive);
void showMessage(String message);
void showError(String message);
```

---

## Message Structures

### Client Callback Message

All server-to-client updates use the `ClientCallback` structure:

```python
@dataclass
class ClientCallback:
    """Server callback message"""
    
    # Callback identification
    message_id: int  # Sequence number for ordering
    method: ClientCallbackMethod  # What type of callback
    object_id: UUID  # Related object (game, table, etc.)
    
    # Payload data (varies by method)
    data: Any  # Can be GameView, TableView, String, etc.
    
    # Compression flag
    compressed: bool = False  # Whether data is zipped
```

### Client Callback Methods

```python
class ClientCallbackMethod(Enum):
    """Types of server callbacks"""
    
    # Messages
    CHATMESSAGE = "chatMessage"
    SHOW_USERMESSAGE = "showUserMessage"
    SERVER_MESSAGE = "serverMessage"
    
    # Table events
    JOINED_TABLE = "joinedTable"
    
    # Game lifecycle
    START_GAME = "startGame"
    GAME_INIT = "gameInit"
    GAME_UPDATE = "gameUpdate"
    GAME_OVER = "gameOver"
    
    # Game interactions (require response)
    GAME_TARGET = "gameTarget"  # Select target
    GAME_CHOOSE_ABILITY = "gameChooseAbility"  # Choose ability
    GAME_CHOOSE_CHOICE = "gameChooseChoice"  # Make a choice
    GAME_ASK = "gameAsk"  # Yes/No question
    GAME_SELECT = "gameSelect"  # Select cards/permanents
    GAME_PLAY_MANA = "gamePlayMana"  # Pay mana cost
    GAME_PLAY_XMANA = "gamePlayXMana"  # Pay X mana
    GAME_GET_AMOUNT = "gameSelectAmount"  # Select number
    GAME_GET_MULTI_AMOUNT = "gameSelectMultiAmount"  # Select multiple numbers
    GAME_CHOOSE_PILE = "gameChoosePile"  # Choose pile of cards
    
    # Informational updates
    GAME_UPDATE_AND_INFORM = "gameInform"  # Update with message
    GAME_INFORM_PERSONAL = "gameInformPersonal"  # Personal message
    GAME_ERROR = "gameError"  # Error occurred
    
    # Draft
    START_DRAFT = "startDraft"
    DRAFT_INIT = "draftInit"
    DRAFT_PICK = "draftPick"
    DRAFT_UPDATE = "draftUpdate"
    
    # Tournament
    START_TOURNAMENT = "startTournament"
    TOURNAMENT_UPDATE = "tournamentUpdate"
    
    # Watch mode
    WATCHGAME = "watchGame"
```

### Game Client Message

When server requests input, it sends a `GameClientMessage`:

```python
@dataclass
class GameClientMessage:
    """Message requesting player input"""
    
    game_view: GameView  # Current game state
    options: Dict[str, Any]  # Available options
    message: str  # Prompt text
    
    # For selection prompts
    cards_view1: Optional[CardsView] = None  # First set of cards
    cards_view2: Optional[CardsView] = None  # Second set of cards
    targets: Optional[Set[UUID]] = None  # Valid targets
    
    # For amount prompts
    min: Optional[int] = None  # Minimum value
    max: Optional[int] = None  # Maximum value
    
    # For choice prompts
    choice: Optional[Choice] = None  # Available choices
    
    # For multi-amount prompts
    messages: Optional[List[MultiAmountMessage]] = None
    
    flag: bool = False  # Special flag
```

---

## Game State Representation

### GameView Structure

The complete game state is represented by `GameView`:

```python
@dataclass
class GameView:
    """Complete game state snapshot"""
    
    # Player information
    players: List[PlayerView]  # All players
    my_player_id: Optional[UUID]  # Current player (None for watchers)
    
    # Hand and playable objects
    my_hand: CardsView  # Current player's hand
    my_helper_emblems: CardsView  # Helper emblems
    can_play_objects: Optional[PlayableObjectsList]  # Playable cards/abilities
    
    # Opponent information
    opponent_hands: Dict[str, SimpleCardsView]  # Opponent hand sizes
    watched_hands: Dict[str, SimpleCardsView]  # Revealed hands
    
    # Game zones
    stack: CardsView  # Stack (spells/abilities)
    exiles: List[ExileView]  # Exile zones
    revealed: List[RevealedView]  # Revealed cards
    looked_at: List[LookedAtView]  # Looked at (like Scry)
    companion: List[RevealedView]  # Companion zone
    
    # Combat
    combat: List[CombatGroupView]  # Combat groups
    
    # Turn information
    phase: TurnPhase  # Current phase
    step: PhaseStep  # Current step
    turn: int  # Turn number
    active_player_id: UUID  # Active player
    active_player_name: str  # Active player name
    priority_player_name: str  # Player with priority
    
    # Game settings
    priority_time: int  # Priority timer setting
    buffer_time: int  # Buffer time setting
    rollback_turns_allowed: bool  # Can rollback turns
    
    # Special state
    special: bool  # Has special actions available
    
    # Debug info (optional)
    total_errors_count: int = 0
    total_effects_count: int = 0
    game_cycle: int = 0
```

### PlayerView Structure

Each player's state:

```python
@dataclass
class PlayerView:
    """Individual player state"""
    
    # Identity
    player_id: UUID
    name: str
    controlled: bool  # Is this the client's player?
    is_human: bool  # Human or AI
    
    # Life and counters
    life: int
    counters: List[CounterView]  # Poison, energy, etc.
    
    # Match status
    wins: int
    wins_needed: int
    
    # Zones
    library_count: int  # Library size
    hand_count: int  # Hand size
    graveyard: CardsView
    exile: CardsView
    sideboard: CardsView
    battlefield: Dict[UUID, PermanentView]  # Permanents
    
    # Mana
    mana_pool: ManaPoolView
    
    # Turn status
    is_active: bool  # Active player
    has_priority: bool  # Has priority
    timer_active: bool  # Timer running
    
    # Priority passing state
    passed_turn: bool  # Passed until end of turn (F4)
    passed_until_end_of_turn: bool  # F5
    passed_until_next_main: bool  # F6
    passed_until_stack_resolved: bool  # F8
    passed_all_turns: bool  # F9
    passed_until_end_step_before_my_turn: bool  # F11
    
    # Special designations
    monarch: bool  # Has the Monarch
    initiative: bool  # Has the Initiative
    designation_names: List[str]  # Other designations
    
    # Timing
    priority_time_left_secs: int
    buffer_time_left: int
    
    # State
    has_left: bool  # Player left game
    top_card: Optional[CardView]  # Revealed top card
    
    # Command zone
    command_list: List[CommandObjectView]  # Commanders, emblems, etc.
    attachments: List[UUID]  # Attached objects
    
    # Rollback
    states_saved_size: int  # Number of saved states
```

### CardView Structure

Individual card representation:

```python
@dataclass
class CardView:
    """Card representation"""
    
    # Identity
    id: UUID
    name: str
    expansion_set_code: str  # Set code (e.g., "M21")
    card_number: str
    
    # Types
    super_types: List[str]
    card_types: List[str]
    sub_types: List[str]
    
    # Characteristics
    color: Color
    mana_cost: List[str]  # Mana symbols
    converted_mana_cost: int
    
    # Rules
    rules: List[str]  # Rules text
    power: str  # Creature power
    toughness: str  # Creature toughness
    loyalty: str  # Planeswalker loyalty
    
    # State
    tapped: bool
    flipped: bool
    transformed: bool
    face_down: bool
    
    # Counters and damage
    counters: List[CounterView]
    damage: int
    
    # Targeting
    targets: List[UUID]  # Current targets
    
    # Abilities
    abilities: List[AbilityView]
    
    # Status
    controlled: bool  # Controlled by viewing player
    paid: bool  # Costs paid (for stack)
    
    # Zone
    zone: Zone
```

### PermanentView Structure

Permanent on battlefield:

```python
@dataclass
class PermanentView(CardView):
    """Permanent on battlefield (extends CardView)"""
    
    # Permanent-specific state
    attached_to: Optional[UUID]  # What this is attached to
    original_id: UUID  # Original card ID
    
    # Combat
    attacking: bool
    blocked: bool
    blocking: bool
    
    # Abilities
    summoning_sickness: bool
    can_attack: bool
    can_block: bool
    
    # Special states
    phased_in: bool
    monstrous: bool
    renowned: bool
```

---

## Action Space

### Player Actions

The client can send the following types of actions:

```python
class PlayerAction(Enum):
    """Player actions that can be sent to server"""
    
    # Priority control
    PASS_PRIORITY_UNTIL_MY_NEXT_TURN = "pass_until_my_turn"
    PASS_PRIORITY_UNTIL_TURN_END_STEP = "pass_until_end_step"
    PASS_PRIORITY_UNTIL_NEXT_MAIN_PHASE = "pass_until_main"
    PASS_PRIORITY_UNTIL_NEXT_TURN = "pass_until_next_turn"
    PASS_PRIORITY_UNTIL_STACK_RESOLVED = "pass_until_stack_resolved"
    PASS_PRIORITY_UNTIL_END_STEP_BEFORE_MY_NEXT_TURN = "pass_until_end_before_my_turn"
    PASS_PRIORITY_CANCEL_ALL_ACTIONS = "cancel_pass_actions"
    
    # Mana and abilities
    MANA_AUTO_PAYMENT_ON = "auto_mana_on"
    MANA_AUTO_PAYMENT_OFF = "auto_mana_off"
    USE_FIRST_MANA_ABILITY_ON = "use_first_mana_on"
    USE_FIRST_MANA_ABILITY_OFF = "use_first_mana_off"
    
    # Game control
    CONCEDE = "concede"
    UNDO = "undo"
    ROLLBACK_TURNS = "rollback"
    HOLD_PRIORITY = "hold_priority"
    UNHOLD_PRIORITY = "unhold_priority"
    
    # Triggers
    TRIGGER_AUTO_ORDER_ABILITY_FIRST = "trigger_ability_first"
    TRIGGER_AUTO_ORDER_NAME_FIRST = "trigger_name_first"
    TRIGGER_AUTO_ORDER_ABILITY_LAST = "trigger_ability_last"
    TRIGGER_AUTO_ORDER_NAME_LAST = "trigger_name_last"
    TRIGGER_AUTO_ORDER_RESET_ALL = "trigger_reset"
```

### Action API

```python
class XMageGameActions:
    """Interface for sending game actions"""
    
    def send_player_action(self, action: PlayerAction, 
                          game_id: UUID, data: Any = None) -> bool:
        """
        Send a player action
        
        Args:
            action: Type of action
            game_id: Game UUID
            data: Additional data for action
            
        Returns:
            True if action accepted
        """
        pass
    
    def send_player_uuid(self, game_id: UUID, uuid: UUID) -> bool:
        """Send UUID response (e.g., selected card/permanent)"""
        pass
    
    def send_player_boolean(self, game_id: UUID, value: bool) -> bool:
        """Send boolean response (e.g., yes/no)"""
        pass
    
    def send_player_integer(self, game_id: UUID, value: int) -> bool:
        """Send integer response (e.g., amount)"""
        pass
    
    def send_player_string(self, game_id: UUID, value: str) -> bool:
        """Send string response (e.g., choice)"""
        pass
    
    def send_player_mana_type(self, game_id: UUID, 
                             player_id: UUID, mana: ManaType) -> bool:
        """Send mana selection"""
        pass
```

### Structured Actions

For RL agents, actions should be structured:

```python
@dataclass
class GameAction:
    """Structured game action"""
    
    action_type: ActionType
    target_id: Optional[UUID] = None
    value: Optional[Union[int, str, bool]] = None
    mana_selection: Optional[List[ManaType]] = None

class ActionType(Enum):
    """Types of actions in the game"""
    
    # Play actions
    PLAY_LAND = "play_land"
    CAST_SPELL = "cast_spell"
    ACTIVATE_ABILITY = "activate_ability"
    
    # Combat
    DECLARE_ATTACKER = "declare_attacker"
    DECLARE_BLOCKER = "declare_blocker"
    
    # Selection
    SELECT_TARGET = "select_target"
    SELECT_CHOICE = "select_choice"
    SELECT_AMOUNT = "select_amount"
    
    # Mana
    TAP_FOR_MANA = "tap_for_mana"
    PAY_MANA = "pay_mana"
    
    # Priority
    PASS_PRIORITY = "pass_priority"
    RESPOND = "respond"
    
    # Special
    CONCEDE = "concede"
    UNDO = "undo"
```

---

## Observation Space

### Observation Structure for RL

For reinforcement learning, the observation should be a structured representation:

```python
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
    # Player features: [life, library_size, hand_size, graveyard_size,
    #                   battlefield_permanents, mana_available, is_active, ...]
    
    # Hand (variable size, padded)
    hand: np.ndarray  # Shape: (max_hand_size, card_features)
    # Card features: [cmc, colors, types, power, toughness, ...]
    
    # Battlefield (variable size, padded)
    battlefield: np.ndarray  # Shape: (max_battlefield, permanent_features)
    # Permanent features: [controller, cmc, colors, types, power, toughness,
    #                      tapped, summoning_sickness, ...]
    
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
```

### Observation Space Definition

```python
import gymnasium as gym
from gymnasium import spaces

def create_observation_space(config: Dict) -> spaces.Dict:
    """Create Gymnasium observation space"""
    
    return spaces.Dict({
        # Scalar values
        "turn_number": spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
        "phase": spaces.Discrete(7),  # 7 phases
        "step": spaces.Discrete(10),  # ~10 steps
        "is_my_turn": spaces.Discrete(2),
        "have_priority": spaces.Discrete(2),
        
        # Player information
        "players": spaces.Box(
            low=-100, high=10000, 
            shape=(config["max_players"], config["player_features"]), 
            dtype=np.float32
        ),
        
        # Hand
        "hand": spaces.Box(
            low=0, high=100,
            shape=(config["max_hand_size"], config["card_features"]),
            dtype=np.float32
        ),
        
        # Battlefield
        "battlefield": spaces.Box(
            low=0, high=100,
            shape=(config["max_battlefield"], config["permanent_features"]),
            dtype=np.float32
        ),
        
        # Stack
        "stack": spaces.Box(
            low=0, high=100,
            shape=(config["max_stack"], config["stack_features"]),
            dtype=np.float32
        ),
        
        # Action mask
        "action_mask": spaces.MultiBinary(config["num_actions"]),
    })
```

---

## Gymnasium Environment Interface

### Main Environment Class

```python
import gymnasium as gym
from typing import Tuple, Dict, Any, Optional
import numpy as np

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
        deck_list: Optional[Dict] = None,
        opponent_type: str = "ai",  # "ai" or "human"
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
            opponent_type: Type of opponent
            render_mode: Rendering mode
            max_turns: Maximum turns before episode ends
        """
        super().__init__()
        
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.password = password
        self.deck_list = deck_list
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
    
    def _create_action_space(self) -> gym.Space:
        """Create action space definition"""
        # Discrete action space: action_type + parameters
        # This is simplified; actual implementation would be more complex
        return spaces.Dict({
            "action_type": spaces.Discrete(20),  # 20 action types
            "target_id": spaces.Discrete(1000),  # Target object index
            "value": spaces.Box(low=0, high=100, shape=(1,), dtype=np.int32),
        })
    
    def _create_observation_space(self) -> gym.Space:
        """Create observation space definition"""
        return create_observation_space({
            "max_players": 4,
            "max_hand_size": 20,
            "max_battlefield": 50,
            "max_stack": 20,
            "player_features": 15,
            "card_features": 30,
            "permanent_features": 35,
            "stack_features": 25,
            "num_actions": 1000,
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
        truncated = self.episode_step >= self.max_turns
        
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
    
    def close(self):
        """Close the environment and disconnect"""
        if self.connection is not None:
            if self.current_game_id is not None:
                self._cleanup_game()
            self.connection.disconnect()
            self.connection = None
    
    def _connect(self):
        """Establish connection to XMage server"""
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
    
    def _create_game(self) -> UUID:
        """Create a new game on the server"""
        # Get main room
        room_id = self.connection.get_main_room_id()
        
        # Create table with match options
        match_options = self._create_match_options()
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
        
        return table_view.game_id
    
    def _send_action(self, action: Dict):
        """Send action to server"""
        self.game_state_manager.execute_action(
            self.current_game_id, 
            action
        )
    
    def _wait_for_update(self, timeout: float = 30.0):
        """Wait for game state update from server"""
        self.game_state_manager.wait_for_update(timeout)
    
    def _get_observation(self) -> Dict:
        """Get current observation from game state"""
        return self.game_state_manager.get_observation()
    
    def _calculate_reward(self) -> float:
        """Calculate reward for current state"""
        # Example reward shaping
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
        game_state = self.game_state_manager.get_game_state()
        
        info = {
            "episode_step": self.episode_step,
            "episode_reward": self.episode_reward,
        }
        
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
```

---

## Implementation Examples

### Example 1: Basic Connection

```python
"""Basic connection to XMage server"""

from xmage_gym import XMageConnection

# Create connection
conn = XMageConnection()

# Connect to server
success = conn.connect(
    host="localhost",
    port=17171,
    username="test_user",
    password="test_pass"
)

if success:
    print(f"Connected! Session ID: {conn.get_session_id()}")
    
    # Get main room
    room_id = conn.get_main_room_id()
    print(f"Main room ID: {room_id}")
    
    # Disconnect
    conn.disconnect()
else:
    print("Connection failed")
```

### Example 2: Creating and Joining a Game

```python
"""Create and join a game"""

from xmage_gym import XMageConnection, MatchOptions, PlayerType
from xmage_gym.deck import load_deck

# Connect
conn = XMageConnection()
conn.connect("localhost", 17171, "player1", "pass")

# Load deck
deck = load_deck("path/to/deck.txt")

# Create match options
match_options = MatchOptions(
    name="Test Game",
    game_type="Two Player Duel",
    free_mulligans=1,
    password="",
)

# Create table
room_id = conn.get_main_room_id()
table_view = conn.create_table(room_id, match_options)
print(f"Created table: {table_view.table_id}")

# Join table
conn.join_table(
    room_id=room_id,
    table_id=table_view.table_id,
    player_name="player1",
    player_type=PlayerType.HUMAN,
    skill=5,
    deck_list=deck,
    password=""
)

# Start match
conn.start_match(room_id, table_view.table_id)
print("Game started!")
```

### Example 3: Using Gymnasium Interface

```python
"""Train an RL agent using the Gymnasium interface"""

import gymnasium as gym
from xmage_gym import XMageEnv

# Create environment
env = XMageEnv(
    server_host="localhost",
    server_port=17171,
    username="rl_agent",
    password="password",
    opponent_type="ai",
    max_turns=50,
)

# Training loop
num_episodes = 100

for episode in range(num_episodes):
    observation, info = env.reset()
    episode_reward = 0
    done = False
    
    while not done:
        # Select action (random for this example)
        action = env.action_space.sample()
        
        # Execute action
        observation, reward, terminated, truncated, info = env.step(action)
        episode_reward += reward
        done = terminated or truncated
        
        # Render
        if episode % 10 == 0:
            env.render()
    
    print(f"Episode {episode}: Reward = {episode_reward:.2f}")

env.close()
```

### Example 4: Handling Callbacks

```python
"""Handle server callbacks"""

from xmage_gym import XMageConnection, ClientCallback, ClientCallbackMethod
import queue
import threading

class CallbackHandler:
    """Process server callbacks"""
    
    def __init__(self, connection):
        self.connection = connection
        self.callback_queue = queue.Queue()
        self.running = False
        self.thread = None
    
    def start(self):
        """Start callback processing thread"""
        self.running = True
        self.thread = threading.Thread(target=self._process_callbacks)
        self.thread.start()
    
    def stop(self):
        """Stop callback processing"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _process_callbacks(self):
        """Process callbacks from server"""
        while self.running:
            try:
                # Wait for callback
                callback = self.connection.wait_for_callback(timeout=1.0)
                if callback is None:
                    continue
                
                # Handle based on method
                if callback.method == ClientCallbackMethod.GAME_UPDATE:
                    self._handle_game_update(callback)
                elif callback.method == ClientCallbackMethod.GAME_TARGET:
                    self._handle_target_request(callback)
                elif callback.method == ClientCallbackMethod.GAME_ASK:
                    self._handle_yes_no_question(callback)
                # ... handle other callback types
                
            except Exception as e:
                print(f"Error processing callback: {e}")
    
    def _handle_game_update(self, callback: ClientCallback):
        """Handle game state update"""
        game_view = callback.data  # GameView object
        print(f"Game update: Turn {game_view.turn}, Phase {game_view.phase}")
    
    def _handle_target_request(self, callback: ClientCallback):
        """Handle target selection request"""
        message = callback.data  # GameClientMessage
        print(f"Select target: {message.message}")
        # ... select target and respond
    
    def _handle_yes_no_question(self, callback: ClientCallback):
        """Handle yes/no question"""
        message = callback.data  # GameClientMessage
        print(f"Question: {message.message}")
        # ... respond with boolean
```

---

## API Reference

### Core Classes

#### XMageConnection

```python
class XMageConnection:
    """Main connection to XMage server"""
    
    def connect(self, host: str, port: int, username: str, 
                password: str) -> bool:
        """Connect to server and authenticate"""
        
    def disconnect(self, ask_reconnect: bool = False, 
                   keep_session: bool = False) -> None:
        """Disconnect from server"""
        
    def is_connected(self) -> bool:
        """Check connection status"""
        
    def get_session_id(self) -> str:
        """Get session UUID"""
        
    def ping(self) -> None:
        """Send keepalive ping"""
        
    def get_main_room_id(self) -> UUID:
        """Get main room UUID"""
        
    def create_table(self, room_id: UUID, 
                    match_options: MatchOptions) -> TableView:
        """Create new table/game"""
        
    def join_table(self, room_id: UUID, table_id: UUID, 
                  player_name: str, player_type: PlayerType,
                  skill: int, deck_list: DeckCardLists, 
                  password: str) -> bool:
        """Join a table"""
        
    def start_match(self, room_id: UUID, table_id: UUID) -> bool:
        """Start the match"""
        
    def send_player_action(self, action: PlayerAction, 
                          game_id: UUID, data: Any) -> bool:
        """Send player action"""
        
    def send_player_uuid(self, game_id: UUID, uuid: UUID) -> bool:
        """Send UUID response"""
        
    def send_player_boolean(self, game_id: UUID, value: bool) -> bool:
        """Send boolean response"""
        
    def send_player_integer(self, game_id: UUID, value: int) -> bool:
        """Send integer response"""
        
    def send_player_string(self, game_id: UUID, value: str) -> bool:
        """Send string response"""
        
    def quit_match(self, game_id: UUID) -> bool:
        """Quit match"""
```

#### XMageGameStateManager

```python
class XMageGameStateManager:
    """Manages game state synchronization"""
    
    def __init__(self, connection: XMageConnection):
        """Initialize with connection"""
        
    def get_game_state(self) -> Optional[GameView]:
        """Get current game state"""
        
    def get_observation(self) -> Dict:
        """Get RL observation from game state"""
        
    def execute_action(self, game_id: UUID, action: Dict) -> bool:
        """Execute structured action"""
        
    def wait_for_update(self, timeout: float = 30.0) -> bool:
        """Wait for game state update"""
        
    def get_legal_actions(self) -> List[Dict]:
        """Get list of legal actions"""
```

### Data Classes

#### MatchOptions

```python
@dataclass
class MatchOptions:
    """Options for creating a match"""
    
    name: str  # Match name
    game_type: str  # "Two Player Duel", "Multiplayer", etc.
    free_mulligans: int = 0  # Free mulligans allowed
    password: str = ""  # Password protection
    deck_type: str = "Constructed"  # "Constructed", "Limited"
    limited_options: Optional[Dict] = None  # For limited formats
    banned_users: List[str] = field(default_factory=list)
    spectators_allowed: bool = True
    rated_match: bool = False
    range: int = 0  # Multiplayer range
    skill_level: str = "Casual"
```

#### DeckCardLists

```python
@dataclass
class DeckCardLists:
    """Deck card lists"""
    
    main_deck: List[str]  # Main deck card names
    sideboard: List[str] = field(default_factory=list)  # Sideboard
    
    def from_file(cls, path: str) -> 'DeckCardLists':
        """Load from deck file"""
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
```

### Enumerations

#### PlayerType

```python
class PlayerType(Enum):
    HUMAN = "Human"
    COMPUTER_DRAFT = "Computer - draft"
    COMPUTER_DUEL = "Computer - duel"
    COMPUTER_MAD = "Computer - mad"
```

#### TurnPhase

```python
class TurnPhase(Enum):
    BEGINNING = "Beginning"
    PRECOMBAT_MAIN = "Precombat Main"
    COMBAT = "Combat"
    POSTCOMBAT_MAIN = "Postcombat Main"
    END = "End"
```

#### PhaseStep

```python
class PhaseStep(Enum):
    UNTAP = "Untap"
    UPKEEP = "Upkeep"
    DRAW = "Draw"
    PRECOMBAT_MAIN = "Precombat Main"
    BEGIN_COMBAT = "Begin Combat"
    DECLARE_ATTACKERS = "Declare Attackers"
    DECLARE_BLOCKERS = "Declare Blockers"
    COMBAT_DAMAGE = "Combat Damage"
    END_COMBAT = "End Combat"
    POSTCOMBAT_MAIN = "Postcombat Main"
    END_TURN = "End Turn"
    CLEANUP = "Cleanup"
```

#### ManaType

```python
class ManaType(Enum):
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"
    GENERIC = "X"
```

---

## Implementation Notes

### Protocol Bridge Options

Since XMage uses Java serialization and JBoss Remoting, you need a bridge:

#### Option 1: Py4J
- Pros: Native Java interop, can use existing Java client
- Cons: Requires JVM, performance overhead

```python
from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
session = gateway.entry_point.createSession()
```

#### Option 2: REST/WebSocket Wrapper
- Create a Java wrapper that exposes REST/WebSocket API
- Python client communicates via HTTP/WS
- Pros: Language independent, clean separation
- Cons: Requires additional server component

#### Option 3: Custom Protocol Implementation
- Implement JBoss Remoting protocol in Python
- Implement Java serialization in Python
- Pros: No JVM required, full control
- Cons: Complex, maintenance burden

**Recommendation**: Use Py4J with existing Java client for fastest development.

### State Synchronization

The server sends updates asynchronously via callbacks. The client must:

1. Maintain callback queue
2. Process callbacks in order (by message_id)
3. Handle decompress if data is zipped
4. Update local game state
5. Notify waiting threads/coroutines

### Thread Safety

Multiple threads are involved:
- Main thread (RL agent)
- Callback receiver thread
- Action sender thread

Use proper synchronization (locks, queues).

### Error Handling

Handle these error cases:
- Connection lost
- Session expired
- Invalid action
- Timeout waiting for response
- Malformed game state

### Performance Considerations

- Decompress callback data lazily
- Cache frequently accessed game state
- Use efficient data structures for observations
- Consider action batching for high-frequency agents

---

## Conclusion

This architecture provides a comprehensive framework for building a Python Gymnasium environment that interfaces with the XMage server. The key components are:

1. **Protocol Bridge**: Connecting Python to Java/JBoss Remoting
2. **State Management**: Synchronizing game state from server callbacks
3. **Action Translation**: Converting RL actions to XMage commands
4. **Observation Extraction**: Creating RL-friendly observations from game state
5. **Gymnasium Wrapper**: Standard RL interface

The modular design allows for flexibility in implementation choices while maintaining a clean separation of concerns.
