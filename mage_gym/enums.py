"""
Enumerations for XMage game constants

This module defines all the enumeration types used in the XMage game,
matching the Java enums from the XMage server.
"""

from enum import Enum


class PlayerAction(Enum):
    """Player actions that can be sent to server"""
    
    # Priority control
    PASS_PRIORITY_UNTIL_MY_NEXT_TURN = "PASS_PRIORITY_UNTIL_MY_NEXT_TURN"
    PASS_PRIORITY_UNTIL_TURN_END_STEP = "PASS_PRIORITY_UNTIL_TURN_END_STEP"
    PASS_PRIORITY_UNTIL_NEXT_MAIN_PHASE = "PASS_PRIORITY_UNTIL_NEXT_MAIN_PHASE"
    PASS_PRIORITY_UNTIL_NEXT_TURN = "PASS_PRIORITY_UNTIL_NEXT_TURN"
    PASS_PRIORITY_UNTIL_STACK_RESOLVED = "PASS_PRIORITY_UNTIL_STACK_RESOLVED"
    PASS_PRIORITY_UNTIL_END_STEP_BEFORE_MY_NEXT_TURN = "PASS_PRIORITY_UNTIL_END_STEP_BEFORE_MY_NEXT_TURN"
    PASS_PRIORITY_CANCEL_ALL_ACTIONS = "PASS_PRIORITY_CANCEL_ALL_ACTIONS"
    
    # Mana and abilities
    MANA_AUTO_PAYMENT_ON = "MANA_AUTO_PAYMENT_ON"
    MANA_AUTO_PAYMENT_OFF = "MANA_AUTO_PAYMENT_OFF"
    USE_FIRST_MANA_ABILITY_ON = "USE_FIRST_MANA_ABILITY_ON"
    USE_FIRST_MANA_ABILITY_OFF = "USE_FIRST_MANA_ABILITY_OFF"
    
    # Game control
    CONCEDE = "CONCEDE"
    UNDO = "UNDO"
    ROLLBACK_TURNS = "ROLLBACK_TURNS"
    HOLD_PRIORITY = "HOLD_PRIORITY"
    UNHOLD_PRIORITY = "UNHOLD_PRIORITY"
    
    # Triggers
    TRIGGER_AUTO_ORDER_ABILITY_FIRST = "TRIGGER_AUTO_ORDER_ABILITY_FIRST"
    TRIGGER_AUTO_ORDER_NAME_FIRST = "TRIGGER_AUTO_ORDER_NAME_FIRST"
    TRIGGER_AUTO_ORDER_ABILITY_LAST = "TRIGGER_AUTO_ORDER_ABILITY_LAST"
    TRIGGER_AUTO_ORDER_NAME_LAST = "TRIGGER_AUTO_ORDER_NAME_LAST"
    TRIGGER_AUTO_ORDER_RESET_ALL = "TRIGGER_AUTO_ORDER_RESET_ALL"


class ActionType(Enum):
    """Types of actions in the game"""
    
    # Play actions
    PLAY_LAND = "PLAY_LAND"
    CAST_SPELL = "CAST_SPELL"
    ACTIVATE_ABILITY = "ACTIVATE_ABILITY"
    
    # Combat
    DECLARE_ATTACKER = "DECLARE_ATTACKER"
    DECLARE_BLOCKER = "DECLARE_BLOCKER"
    
    # Selection
    SELECT_TARGET = "SELECT_TARGET"
    SELECT_CHOICE = "SELECT_CHOICE"
    SELECT_AMOUNT = "SELECT_AMOUNT"
    
    # Mana
    TAP_FOR_MANA = "TAP_FOR_MANA"
    PAY_MANA = "PAY_MANA"
    
    # Priority
    PASS_PRIORITY = "PASS_PRIORITY"
    RESPOND = "RESPOND"
    
    # Special
    CONCEDE = "CONCEDE"
    UNDO = "UNDO"


class PlayerType(Enum):
    """Player types"""
    HUMAN = "Human"
    COMPUTER_DRAFT = "Computer - draft"
    COMPUTER_DUEL = "Computer - duel"
    COMPUTER_MAD = "Computer - mad"


class TurnPhase(Enum):
    """Turn phases"""
    BEGINNING = "BEGINNING"
    PRECOMBAT_MAIN = "PRECOMBAT_MAIN"
    COMBAT = "COMBAT"
    POSTCOMBAT_MAIN = "POSTCOMBAT_MAIN"
    END = "END"


class PhaseStep(Enum):
    """Phase steps"""
    UNTAP = "UNTAP"
    UPKEEP = "UPKEEP"
    DRAW = "DRAW"
    PRECOMBAT_MAIN = "PRECOMBAT_MAIN"
    BEGIN_COMBAT = "BEGIN_COMBAT"
    DECLARE_ATTACKERS = "DECLARE_ATTACKERS"
    DECLARE_BLOCKERS = "DECLARE_BLOCKERS"
    COMBAT_DAMAGE = "COMBAT_DAMAGE"
    END_COMBAT = "END_COMBAT"
    POSTCOMBAT_MAIN = "POSTCOMBAT_MAIN"
    END_TURN = "END_TURN"
    CLEANUP = "CLEANUP"


class ManaType(Enum):
    """Mana types"""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"
    GENERIC = "X"


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
    GAME_TARGET = "gameTarget"
    GAME_CHOOSE_ABILITY = "gameChooseAbility"
    GAME_CHOOSE_CHOICE = "gameChooseChoice"
    GAME_ASK = "gameAsk"
    GAME_SELECT = "gameSelect"
    GAME_PLAY_MANA = "gamePlayMana"
    GAME_PLAY_XMANA = "gamePlayXMana"
    GAME_GET_AMOUNT = "gameSelectAmount"
    GAME_GET_MULTI_AMOUNT = "gameSelectMultiAmount"
    GAME_CHOOSE_PILE = "gameChoosePile"
    
    # Informational updates
    GAME_UPDATE_AND_INFORM = "gameInform"
    GAME_INFORM_PERSONAL = "gameInformPersonal"
    GAME_ERROR = "gameError"
    
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


class Zone(Enum):
    """Card zones"""
    HAND = "HAND"
    GRAVEYARD = "GRAVEYARD"
    BATTLEFIELD = "BATTLEFIELD"
    LIBRARY = "LIBRARY"
    STACK = "STACK"
    EXILE = "EXILE"
    COMMAND = "COMMAND"
    OUTSIDE = "OUTSIDE"
