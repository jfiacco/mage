"""
Tests for data models
"""

import pytest
from uuid import uuid4
import numpy as np
from mage_gym.models import (
    CounterView,
    ManaPoolView,
    AbilityView,
    CardView,
    PermanentView,
    PlayerView,
    GameView,
    GameAction,
    ConnectionConfig,
    MatchOptions,
    DeckCardLists,
)
from mage_gym.enums import Zone, TurnPhase, PhaseStep


class TestCounterView:
    """Test CounterView dataclass"""
    
    def test_creation(self):
        """Test creating a counter"""
        counter = CounterView(name="+1/+1", count=3)
        assert counter.name == "+1/+1"
        assert counter.count == 3


class TestManaPoolView:
    """Test ManaPoolView dataclass"""
    
    def test_empty_pool(self):
        """Test empty mana pool"""
        pool = ManaPoolView()
        assert pool.white == 0
        assert pool.blue == 0
        assert pool.black == 0
        assert pool.red == 0
        assert pool.green == 0
    
    def test_with_mana(self):
        """Test mana pool with mana"""
        pool = ManaPoolView(white=2, blue=3, red=1)
        assert pool.white == 2
        assert pool.blue == 3
        assert pool.red == 1


class TestCardView:
    """Test CardView dataclass"""
    
    def test_basic_card(self):
        """Test creating a basic card"""
        card = CardView(
            id=uuid4(),
            name="Lightning Bolt",
            expansion_set_code="LEA",
            card_number="162"
        )
        assert card.name == "Lightning Bolt"
        assert card.expansion_set_code == "LEA"
    
    def test_card_with_types(self):
        """Test card with types"""
        card = CardView(
            id=uuid4(),
            name="Grizzly Bears",
            expansion_set_code="LEA",
            card_types=["Creature"],
            sub_types=["Bear"]
        )
        assert "Creature" in card.card_types
        assert "Bear" in card.sub_types
    
    def test_card_state(self):
        """Test card state flags"""
        card = CardView(
            id=uuid4(),
            name="Island",
            expansion_set_code="LEA",
            tapped=True,
            face_down=False
        )
        assert card.tapped is True
        assert card.face_down is False


class TestPermanentView:
    """Test PermanentView dataclass"""
    
    def test_permanent_creation(self):
        """Test creating a permanent"""
        perm = PermanentView(
            id=uuid4(),
            name="Grizzly Bears",
            expansion_set_code="LEA",
            attacking=True,
            summoning_sickness=False
        )
        assert perm.name == "Grizzly Bears"
        assert perm.attacking is True
        assert perm.summoning_sickness is False
    
    def test_permanent_combat_state(self):
        """Test permanent combat state"""
        perm = PermanentView(
            id=uuid4(),
            name="Llanowar Elves",
            expansion_set_code="LEA",
            attacking=False,
            blocked=False,
            blocking=True
        )
        assert perm.blocking is True
        assert perm.attacking is False


class TestPlayerView:
    """Test PlayerView dataclass"""
    
    def test_basic_player(self):
        """Test creating a player"""
        player = PlayerView(
            player_id=uuid4(),
            name="Player1",
            controlled=True,
            is_human=True,
            life=20
        )
        assert player.name == "Player1"
        assert player.life == 20
        assert player.controlled is True
    
    def test_player_zones(self):
        """Test player zones"""
        player = PlayerView(
            player_id=uuid4(),
            name="Player1",
            controlled=True,
            is_human=True,
            life=20,
            library_count=53,
            hand_count=7
        )
        assert player.library_count == 53
        assert player.hand_count == 7
        assert len(player.battlefield) == 0
    
    def test_player_priority_state(self):
        """Test player priority passing state"""
        player = PlayerView(
            player_id=uuid4(),
            name="Player1",
            controlled=True,
            is_human=True,
            life=20,
            passed_turn=True,
            passed_until_next_main=False
        )
        assert player.passed_turn is True
        assert player.passed_until_next_main is False


class TestGameView:
    """Test GameView dataclass"""
    
    def test_empty_game(self):
        """Test creating empty game view"""
        game = GameView()
        assert len(game.players) == 0
        assert game.turn == 0
        assert game.my_player_id is None
    
    def test_game_with_players(self):
        """Test game with players"""
        player1 = PlayerView(
            player_id=uuid4(),
            name="Player1",
            controlled=True,
            is_human=True,
            life=20
        )
        player2 = PlayerView(
            player_id=uuid4(),
            name="Player2",
            controlled=False,
            is_human=False,
            life=20
        )
        
        game = GameView(
            players=[player1, player2],
            my_player_id=player1.player_id,
            turn=5,
            phase=TurnPhase.COMBAT,
            step=PhaseStep.DECLARE_ATTACKERS
        )
        
        assert len(game.players) == 2
        assert game.turn == 5
        assert game.phase == TurnPhase.COMBAT
    
    def test_get_my_player(self):
        """Test getting my player"""
        player_id = uuid4()
        player = PlayerView(
            player_id=player_id,
            name="Player1",
            controlled=True,
            is_human=True,
            life=20
        )
        
        game = GameView(
            players=[player],
            my_player_id=player_id
        )
        
        my_player = game.get_my_player()
        assert my_player is not None
        assert my_player.player_id == player_id
    
    def test_get_my_player_none(self):
        """Test getting my player when not set"""
        game = GameView()
        my_player = game.get_my_player()
        assert my_player is None


class TestDeckCardLists:
    """Test DeckCardLists dataclass"""
    
    def test_empty_deck(self):
        """Test empty deck"""
        deck = DeckCardLists()
        assert len(deck.main_deck) == 0
        assert len(deck.sideboard) == 0
    
    def test_deck_with_cards(self):
        """Test deck with cards"""
        deck = DeckCardLists(
            main_deck=["Lightning Bolt"] * 4 + ["Mountain"] * 20,
            sideboard=["Pyroblast"] * 4
        )
        assert len(deck.main_deck) == 24
        assert len(deck.sideboard) == 4
    
    def test_deck_to_dict(self):
        """Test converting deck to dictionary"""
        deck = DeckCardLists(
            main_deck=["Island"] * 20,
            sideboard=["Counterspell"] * 4
        )
        deck_dict = deck.to_dict()
        assert "main_deck" in deck_dict
        assert "sideboard" in deck_dict
        assert len(deck_dict["main_deck"]) == 20


class TestConnectionConfig:
    """Test ConnectionConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = ConnectionConfig()
        assert config.host == "localhost"
        assert config.port == 17171
        assert config.username == "player"
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = ConnectionConfig(
            host="example.com",
            port=12345,
            username="testuser",
            password="testpass"
        )
        assert config.host == "example.com"
        assert config.port == 12345
        assert config.username == "testuser"


class TestMatchOptions:
    """Test MatchOptions dataclass"""
    
    def test_default_options(self):
        """Test default match options"""
        options = MatchOptions()
        assert options.name == "Test Game"
        assert options.game_type == "Two Player Duel"
        assert options.free_mulligans == 0
    
    def test_custom_options(self):
        """Test custom match options"""
        options = MatchOptions(
            name="Custom Game",
            game_type="Multiplayer",
            free_mulligans=1,
            spectators_allowed=False
        )
        assert options.name == "Custom Game"
        assert options.game_type == "Multiplayer"
        assert options.spectators_allowed is False


class TestGameAction:
    """Test GameAction dataclass"""
    
    def test_simple_action(self):
        """Test simple action"""
        action = GameAction(action_type="PASS_PRIORITY")
        assert action.action_type == "PASS_PRIORITY"
        assert action.target_id is None
    
    def test_action_with_target(self):
        """Test action with target"""
        target = uuid4()
        action = GameAction(
            action_type="SELECT_TARGET",
            target_id=target
        )
        assert action.action_type == "SELECT_TARGET"
        assert action.target_id == target
    
    def test_action_with_value(self):
        """Test action with value"""
        action = GameAction(
            action_type="SELECT_AMOUNT",
            value=5
        )
        assert action.action_type == "SELECT_AMOUNT"
        assert action.value == 5
