"""
Tests for connection module
"""

import pytest
from uuid import UUID
from mage_gym.connection import XMageConnection
from mage_gym.models import MatchOptions, DeckCardLists
from mage_gym.enums import PlayerType, PlayerAction


class TestXMageConnection:
    """Test XMageConnection class"""
    
    def test_initialization(self):
        """Test connection initialization"""
        conn = XMageConnection()
        assert conn._session_id is None
        assert conn._connected is False
    
    def test_connect_success(self):
        """Test successful connection"""
        conn = XMageConnection()
        result = conn.connect("localhost", 17171, "testuser", "testpass")
        
        assert result is True
        assert conn.is_connected() is True
        assert conn.get_session_id() is not None
    
    def test_connect_stores_config(self):
        """Test connection stores configuration"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        assert conn._config is not None
        assert conn._config.host == "localhost"
        assert conn._config.port == 17171
        assert conn._config.username == "testuser"
    
    def test_disconnect(self):
        """Test disconnection"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        conn.disconnect()
        assert conn.is_connected() is False
    
    def test_disconnect_keep_session(self):
        """Test disconnection keeping session"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        session_id = conn.get_session_id()
        
        conn.disconnect(keep_session=True)
        assert conn.is_connected() is False
        assert conn.get_session_id() == session_id
    
    def test_get_main_room_id(self):
        """Test getting main room ID"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        room_id = conn.get_main_room_id()
        assert isinstance(room_id, UUID)
    
    def test_get_main_room_id_not_connected(self):
        """Test getting main room ID when not connected"""
        conn = XMageConnection()
        
        with pytest.raises(ConnectionError):
            conn.get_main_room_id()
    
    def test_create_table(self):
        """Test creating a table"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        room_id = conn.get_main_room_id()
        match_options = MatchOptions(name="Test Game")
        
        table_view = conn.create_table(room_id, match_options)
        assert table_view is not None
        assert hasattr(table_view, 'table_id')
        assert hasattr(table_view, 'game_id')
    
    def test_join_table(self):
        """Test joining a table"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        room_id = conn.get_main_room_id()
        match_options = MatchOptions()
        table_view = conn.create_table(room_id, match_options)
        
        deck = DeckCardLists(main_deck=["Mountain"] * 60)
        result = conn.join_table(
            room_id,
            table_view.table_id,
            "testuser",
            PlayerType.HUMAN,
            5,
            deck,
            ""
        )
        
        assert result is True
    
    def test_send_player_action(self):
        """Test sending player action"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        room_id = conn.get_main_room_id()
        match_options = MatchOptions()
        table_view = conn.create_table(room_id, match_options)
        
        result = conn.send_player_action(
            PlayerAction.PASS_PRIORITY_UNTIL_MY_NEXT_TURN,
            table_view.game_id
        )
        
        assert result is True
    
    def test_send_player_uuid(self):
        """Test sending UUID"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        from uuid import uuid4
        game_id = uuid4()
        data = uuid4()
        
        result = conn.send_player_uuid(game_id, data)
        assert result is True
    
    def test_send_player_boolean(self):
        """Test sending boolean"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        from uuid import uuid4
        game_id = uuid4()
        
        result = conn.send_player_boolean(game_id, True)
        assert result is True
    
    def test_send_player_integer(self):
        """Test sending integer"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        from uuid import uuid4
        game_id = uuid4()
        
        result = conn.send_player_integer(game_id, 5)
        assert result is True
    
    def test_send_player_string(self):
        """Test sending string"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        from uuid import uuid4
        game_id = uuid4()
        
        result = conn.send_player_string(game_id, "test")
        assert result is True
    
    def test_quit_match(self):
        """Test quitting match"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        from uuid import uuid4
        game_id = uuid4()
        
        result = conn.quit_match(game_id)
        assert result is True
    
    def test_concede_game(self):
        """Test conceding game"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        from uuid import uuid4
        game_id = uuid4()
        
        result = conn.concede_game(game_id)
        assert result is True
    
    def test_wait_for_callback_timeout(self):
        """Test waiting for callback with timeout"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        # Should return None on timeout
        callback = conn.wait_for_callback(timeout=0.1)
        assert callback is None
    
    def test_ping(self):
        """Test ping"""
        conn = XMageConnection()
        conn.connect("localhost", 17171, "testuser", "testpass")
        
        # Should not raise exception
        conn.ping()
    
    def test_operations_require_connection(self):
        """Test that operations require connection"""
        conn = XMageConnection()
        
        from uuid import uuid4
        game_id = uuid4()
        
        # All these should raise ConnectionError
        with pytest.raises(ConnectionError):
            conn.ping()
        
        with pytest.raises(ConnectionError):
            conn.send_player_action(PlayerAction.CONCEDE, game_id)
        
        with pytest.raises(ConnectionError):
            conn.quit_match(game_id)
