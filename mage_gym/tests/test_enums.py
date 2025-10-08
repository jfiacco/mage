"""
Tests for enumerations
"""

import pytest
from mage_gym.enums import (
    PlayerAction,
    ActionType,
    PlayerType,
    TurnPhase,
    PhaseStep,
    ManaType,
    ClientCallbackMethod,
    Zone,
)


class TestPlayerAction:
    """Test PlayerAction enum"""
    
    def test_pass_priority_actions(self):
        """Test priority passing actions"""
        assert PlayerAction.PASS_PRIORITY_UNTIL_MY_NEXT_TURN
        assert PlayerAction.PASS_PRIORITY_UNTIL_TURN_END_STEP
        assert PlayerAction.PASS_PRIORITY_UNTIL_NEXT_MAIN_PHASE
    
    def test_mana_actions(self):
        """Test mana-related actions"""
        assert PlayerAction.MANA_AUTO_PAYMENT_ON
        assert PlayerAction.MANA_AUTO_PAYMENT_OFF
    
    def test_game_control_actions(self):
        """Test game control actions"""
        assert PlayerAction.CONCEDE
        assert PlayerAction.UNDO
        assert PlayerAction.HOLD_PRIORITY


class TestActionType:
    """Test ActionType enum"""
    
    def test_play_actions(self):
        """Test play actions"""
        assert ActionType.PLAY_LAND
        assert ActionType.CAST_SPELL
        assert ActionType.ACTIVATE_ABILITY
    
    def test_combat_actions(self):
        """Test combat actions"""
        assert ActionType.DECLARE_ATTACKER
        assert ActionType.DECLARE_BLOCKER
    
    def test_selection_actions(self):
        """Test selection actions"""
        assert ActionType.SELECT_TARGET
        assert ActionType.SELECT_CHOICE
        assert ActionType.SELECT_AMOUNT


class TestPlayerType:
    """Test PlayerType enum"""
    
    def test_human_type(self):
        """Test human player type"""
        assert PlayerType.HUMAN.value == "Human"
    
    def test_computer_types(self):
        """Test computer player types"""
        assert PlayerType.COMPUTER_DRAFT
        assert PlayerType.COMPUTER_DUEL
        assert PlayerType.COMPUTER_MAD


class TestTurnPhase:
    """Test TurnPhase enum"""
    
    def test_all_phases(self):
        """Test all turn phases exist"""
        phases = [
            TurnPhase.BEGINNING,
            TurnPhase.PRECOMBAT_MAIN,
            TurnPhase.COMBAT,
            TurnPhase.POSTCOMBAT_MAIN,
            TurnPhase.END,
        ]
        assert len(phases) == 5
    
    def test_phase_values(self):
        """Test phase string values"""
        assert TurnPhase.BEGINNING.value == "BEGINNING"
        assert TurnPhase.COMBAT.value == "COMBAT"


class TestPhaseStep:
    """Test PhaseStep enum"""
    
    def test_beginning_steps(self):
        """Test beginning phase steps"""
        assert PhaseStep.UNTAP
        assert PhaseStep.UPKEEP
        assert PhaseStep.DRAW
    
    def test_combat_steps(self):
        """Test combat phase steps"""
        assert PhaseStep.BEGIN_COMBAT
        assert PhaseStep.DECLARE_ATTACKERS
        assert PhaseStep.DECLARE_BLOCKERS
        assert PhaseStep.COMBAT_DAMAGE
        assert PhaseStep.END_COMBAT
    
    def test_ending_steps(self):
        """Test ending phase steps"""
        assert PhaseStep.END_TURN
        assert PhaseStep.CLEANUP


class TestManaType:
    """Test ManaType enum"""
    
    def test_colored_mana(self):
        """Test colored mana types"""
        assert ManaType.WHITE.value == "W"
        assert ManaType.BLUE.value == "U"
        assert ManaType.BLACK.value == "B"
        assert ManaType.RED.value == "R"
        assert ManaType.GREEN.value == "G"
    
    def test_colorless_mana(self):
        """Test colorless mana"""
        assert ManaType.COLORLESS.value == "C"
        assert ManaType.GENERIC.value == "X"


class TestClientCallbackMethod:
    """Test ClientCallbackMethod enum"""
    
    def test_message_callbacks(self):
        """Test message callback types"""
        assert ClientCallbackMethod.CHATMESSAGE
        assert ClientCallbackMethod.SHOW_USERMESSAGE
        assert ClientCallbackMethod.SERVER_MESSAGE
    
    def test_game_lifecycle_callbacks(self):
        """Test game lifecycle callbacks"""
        assert ClientCallbackMethod.START_GAME
        assert ClientCallbackMethod.GAME_INIT
        assert ClientCallbackMethod.GAME_UPDATE
        assert ClientCallbackMethod.GAME_OVER
    
    def test_interaction_callbacks(self):
        """Test interaction callbacks"""
        assert ClientCallbackMethod.GAME_TARGET
        assert ClientCallbackMethod.GAME_ASK
        assert ClientCallbackMethod.GAME_SELECT


class TestZone:
    """Test Zone enum"""
    
    def test_all_zones(self):
        """Test all zones exist"""
        zones = [
            Zone.HAND,
            Zone.GRAVEYARD,
            Zone.BATTLEFIELD,
            Zone.LIBRARY,
            Zone.STACK,
            Zone.EXILE,
            Zone.COMMAND,
            Zone.OUTSIDE,
        ]
        assert len(zones) == 8
    
    def test_zone_values(self):
        """Test zone string values"""
        assert Zone.BATTLEFIELD.value == "BATTLEFIELD"
        assert Zone.GRAVEYARD.value == "GRAVEYARD"
