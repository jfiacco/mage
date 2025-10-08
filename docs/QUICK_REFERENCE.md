# Python XMage Client Quick Reference

Quick reference guide for the XMage Python Gymnasium client. See [PYTHON_CLIENT_ARCHITECTURE.md](PYTHON_CLIENT_ARCHITECTURE.md) for full details.

## Connection Quick Start

```python
from xmage_gym import XMageConnection

# Connect to server
conn = XMageConnection()
conn.connect("localhost", 17171, "username", "password")

# Get main room
room_id = conn.get_main_room_id()
```

## Create a Game

```python
# Create table
match_options = MatchOptions(name="My Game", game_type="Two Player Duel")
table = conn.create_table(room_id, match_options)

# Join with deck
conn.join_table(room_id, table.table_id, "player", 
                PlayerType.HUMAN, 5, deck_list, "")

# Start match
conn.start_match(room_id, table.table_id)
```

## Gymnasium Interface

```python
import gymnasium as gym
from xmage_gym import XMageEnv

# Create environment
env = XMageEnv(
    server_host="localhost",
    username="player",
    opponent_type="ai"
)

# Standard gym loop
obs, info = env.reset()
done = False

while not done:
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

env.close()
```

## Key Data Structures

### GameView
```python
game_view.players          # List[PlayerView]
game_view.my_hand          # CardsView
game_view.stack            # CardsView
game_view.phase            # TurnPhase
game_view.turn             # int
game_view.active_player_id # UUID
```

### PlayerView
```python
player.life                # int
player.hand_count          # int
player.battlefield         # Dict[UUID, PermanentView]
player.graveyard           # CardsView
player.has_priority        # bool
player.is_active           # bool
```

### CardView
```python
card.name                  # str
card.mana_cost             # List[str]
card.card_types            # List[str]
card.power                 # str
card.toughness             # str
card.tapped                # bool
```

## Common Actions

### Send Actions
```python
# Pass priority
conn.send_player_action(PlayerAction.PASS_PRIORITY_CANCEL_ALL_ACTIONS, game_id)

# Select target
conn.send_player_uuid(game_id, target_uuid)

# Answer yes/no
conn.send_player_boolean(game_id, True)

# Select amount
conn.send_player_integer(game_id, 5)
```

## Client Callback Types

| Callback Method | Purpose | Response Required |
|----------------|---------|-------------------|
| `GAME_UPDATE` | Game state changed | No |
| `GAME_TARGET` | Select target | Yes (UUID) |
| `GAME_ASK` | Yes/No question | Yes (boolean) |
| `GAME_SELECT` | Select cards | Yes (UUIDs) |
| `GAME_PLAY_MANA` | Pay mana | Yes (mana types) |
| `GAME_GET_AMOUNT` | Select number | Yes (integer) |
| `GAME_CHOOSE_CHOICE` | Make choice | Yes (string) |
| `GAME_OVER` | Game ended | No |

## Turn Phases

1. **BEGINNING**
   - Untap
   - Upkeep
   - Draw

2. **PRECOMBAT_MAIN**
   - Main phase before combat

3. **COMBAT**
   - Begin Combat
   - Declare Attackers
   - Declare Blockers
   - Combat Damage
   - End Combat

4. **POSTCOMBAT_MAIN**
   - Main phase after combat

5. **END**
   - End Turn
   - Cleanup

## Connection URI Format

```
bisocket://host:port/?serializationtype=java&onewayThreadPool=mage.remote.CustomThreadPool
```

Example: `bisocket://localhost:17171/?serializationtype=java&onewayThreadPool=mage.remote.CustomThreadPool`

## Protocol Bridge Options

### Option 1: Py4J (Recommended)
```python
from py4j.java_gateway import JavaGateway
gateway = JavaGateway()
session = gateway.entry_point.createSession()
```

**Pros**: Native Java interop, use existing client  
**Cons**: Requires JVM

### Option 2: REST/WebSocket Wrapper
Create Java wrapper exposing HTTP/WebSocket API

**Pros**: Language independent  
**Cons**: Additional server component

### Option 3: Custom Implementation
Implement JBoss Remoting + Java serialization in Python

**Pros**: No JVM, full control  
**Cons**: Complex, maintenance burden

## Error Handling

```python
try:
    conn.connect(host, port, username, password)
except ConnectionError as e:
    print(f"Connection failed: {e}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
```

## Observation Space (RL)

```python
observation = {
    "turn_number": int,
    "phase": int,  # Encoded
    "is_my_turn": bool,
    "have_priority": bool,
    "players": np.ndarray,  # (max_players, features)
    "hand": np.ndarray,  # (max_hand, features)
    "battlefield": np.ndarray,  # (max_battlefield, features)
    "action_mask": np.ndarray,  # Valid actions
}
```

## Action Space (RL)

```python
action = {
    "action_type": int,  # Discrete(20)
    "target_id": int,  # Discrete(1000)
    "value": int,  # Box(0, 100)
}
```

## Server Methods Reference

| Method | Parameters | Returns |
|--------|-----------|---------|
| `serverGetMainRoomId()` | - | UUID |
| `roomCreateTable()` | sessionId, roomId, options | TableView |
| `tableJoinTable()` | sessionId, roomId, tableId, ... | boolean |
| `sendPlayerAction()` | action, gameId, data | void |
| `sendPlayerUUID()` | gameId, sessionId, uuid | void |
| `sendPlayerBoolean()` | gameId, sessionId, bool | void |
| `sendPlayerInteger()` | gameId, sessionId, int | void |
| `quitMatch()` | gameId, sessionId | void |

## Useful Constants

```python
# Default server port
DEFAULT_PORT = 17171

# Lease period (heartbeat)
LEASE_PERIOD = 5000  # milliseconds

# Player types
PlayerType.HUMAN
PlayerType.COMPUTER_DUEL
PlayerType.COMPUTER_DRAFT

# Mana types
ManaType.WHITE = "W"
ManaType.BLUE = "U"
ManaType.BLACK = "B"
ManaType.RED = "R"
ManaType.GREEN = "G"
ManaType.COLORLESS = "C"
```

## Resources

- [Full Architecture Documentation](PYTHON_CLIENT_ARCHITECTURE.md)
- [XMage Wiki](https://github.com/magefree/mage/wiki)
- [XMage GitHub](https://github.com/magefree/mage)
