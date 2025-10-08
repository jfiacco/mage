# mage_gym: Python Gymnasium Environment for XMage

A Python Gymnasium-compatible environment for interacting with the XMage (Magic Another Game Engine) server for reinforcement learning applications.

## Overview

`mage_gym` provides a standard RL interface to the XMage server, allowing researchers and developers to train agents to play Magic: The Gathering using modern reinforcement learning algorithms.

## Architecture

The package follows the architecture described in `docs/PYTHON_CLIENT_ARCHITECTURE.md` and consists of:

- **Gymnasium Environment Wrapper** (`env.py`): Standard `gym.Env` interface
- **XMage Game State Manager** (`game_state_manager.py`): State synchronization and action translation
- **Network Client Layer** (`connection.py`): Session and message handling
- **Data Models** (`models.py`): Game state representations matching Java views
- **Enumerations** (`enums.py`): Game constants and action types
- **Utilities** (`utils.py`): Helper functions

## Installation

### Requirements

- Python 3.8+
- NumPy
- Gymnasium
- (Optional) Pytest for running tests

### Install from source

```bash
cd mage_gym
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Basic Usage

```python
import gymnasium as gym
from mage_gym import XMageEnv

# Create environment
env = XMageEnv(
    server_host="localhost",
    server_port=17171,
    username="player1",
    password="password",
    opponent_type="ai",
    max_turns=50,
)

# Training loop
observation, info = env.reset()
done = False

while not done:
    # Select action (random for this example)
    action = env.action_space.sample()
    
    # Execute action
    observation, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    
    # Render (optional)
    env.render()

env.close()
```

### Using a Custom Deck

```python
from mage_gym import XMageEnv
from mage_gym.models import DeckCardLists

# Load deck from file
deck = DeckCardLists.from_file("path/to/deck.txt")

# Or create programmatically
deck = DeckCardLists(
    main_deck=["Mountain"] * 20 + ["Lightning Bolt"] * 4 + ["Shock"] * 4,
    sideboard=["Pyroblast"] * 4
)

env = XMageEnv(
    server_host="localhost",
    server_port=17171,
    username="player1",
    password="password",
    deck_list=deck,
)
```

### Connection Management

```python
from mage_gym import XMageConnection

# Direct connection management
conn = XMageConnection()
success = conn.connect("localhost", 17171, "user", "pass")

if success:
    print(f"Connected! Session: {conn.get_session_id()}")
    
    # Get main room
    room_id = conn.get_main_room_id()
    
    # Disconnect
    conn.disconnect()
```

## Observation Space

The observation is a dictionary containing:

- `turn_number`: Current turn number (1D array)
- `phase`: Current phase encoded as integer (1D array)
- `step`: Current step encoded as integer (1D array)
- `is_my_turn`: Boolean indicating if it's your turn (1D array)
- `have_priority`: Boolean indicating if you have priority (1D array)
- `players`: Player states (4 x 15 array)
  - Features: life, library count, hand count, graveyard size, battlefield size, mana pool, etc.
- `hand`: Hand cards (20 x 30 array)
  - Features: CMC, colors, types, power/toughness, etc.
- `battlefield`: Permanents (50 x 35 array)
  - Features: card features + tapped, attacking, summoning sickness, etc.
- `stack`: Stack objects (20 x 25 array)
- `action_mask`: Binary mask of legal actions (1000-element array)

## Action Space

The action space is a dictionary with:

- `action_type`: Discrete action type (20 types)
- `target_id`: Target object index (0-999)
- `value`: Additional value parameter (1D array, 0-100)

Action types include:
- Play land
- Cast spell
- Activate ability
- Declare attackers/blockers
- Select targets
- Pass priority
- And more...

## Testing

Run the test suite with pytest:

```bash
cd mage_gym
pytest tests/ -v
```

Run specific test modules:

```bash
pytest tests/test_enums.py -v
pytest tests/test_models.py -v
pytest tests/test_connection.py -v
pytest tests/test_utils.py -v
pytest tests/test_env.py -v
```

## Implementation Notes

### Protocol Bridge

This implementation provides a **stub/mock** bridge to the XMage server. A production implementation would require one of:

1. **Py4J**: Bridge to Java client via JVM gateway
2. **JPype**: Embed JVM in Python process
3. **REST/WebSocket Wrapper**: Java wrapper exposing HTTP/WS API
4. **Custom Protocol**: Implement JBoss Remoting in Python

**Recommendation**: Use Py4J with the existing Java client for fastest development.

### State Synchronization

The `XMageGameStateManager` handles asynchronous server callbacks in a background thread, maintaining the current game state and notifying waiting threads when updates arrive.

### Thread Safety

Multiple threads are involved:
- Main thread (RL agent)
- Callback receiver thread
- Action sender thread

Proper synchronization is implemented using locks and events.

## Architecture

See `../docs/PYTHON_CLIENT_ARCHITECTURE.md` for detailed architecture documentation.

## API Reference

### XMageEnv

Main Gymnasium environment class.

**Methods:**
- `reset(seed=None, options=None)`: Reset to initial state
- `step(action)`: Execute action
- `render()`: Render current state
- `close()`: Clean up and disconnect

### XMageConnection

Connection management class.

**Methods:**
- `connect(host, port, username, password)`: Connect to server
- `disconnect()`: Disconnect from server
- `get_session_id()`: Get session UUID
- `create_table(room_id, match_options)`: Create game table
- `join_table(...)`: Join game table
- `send_player_action(action, game_id, data)`: Send action
- `quit_match(game_id)`: Quit match

### XMageGameStateManager

Game state management class.

**Methods:**
- `get_game_state()`: Get current GameView
- `get_observation()`: Get RL observation
- `execute_action(game_id, action)`: Execute action
- `wait_for_update(timeout)`: Wait for state update
- `get_legal_actions()`: Get legal actions

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest tests/ -v`
2. Code follows existing style
3. New features include tests
4. Documentation is updated

## License

See LICENSE file in the repository root.

## Related Documentation

- [Python Client Architecture](../docs/PYTHON_CLIENT_ARCHITECTURE.md)
- [XMage Server Documentation](https://github.com/magefree/mage)

## Acknowledgments

This project interfaces with the XMage server, an open-source Magic: The Gathering game engine.
