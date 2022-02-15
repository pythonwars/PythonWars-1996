#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
#
#  ROM 2.4 is copyright 1993-1998 Russ Taylor.  ROM has been brought to
#  you by the ROM consortium:  Russ Taylor (rtaylor@hypercube.org),
#  Gabrielle Taylor (gtaylor@hypercube.org), and Brian Moore (zump@rom.org).
#
#  Ported to Python by Davion of MudBytes.net using Miniboa
#  (https://code.google.com/p/miniboa/).
#
#  In order to use any part of this Merc Diku Mud, you must comply with
#  both the original Diku license in 'license.doc' as well the Merc
#  license in 'license.txt'.  In particular, you may not remove either of
#  these copyright notices.
#
#  Much time and thought has gone into this software, and you are
#  benefiting.  We hope that you share your changes too.  What goes
#  around, comes around.

import collections
import time

import comm
import state_checks

# Merc Setup
# Letter->Bit conversion
BV01 = 1
BV02 = 1 << 1
BV03 = 1 << 2
BV04 = 1 << 3
BV05 = 1 << 4
BV06 = 1 << 5
BV07 = 1 << 6
BV08 = 1 << 7
BV09 = 1 << 8
BV10 = 1 << 9
BV11 = 1 << 10
BV12 = 1 << 11
BV13 = 1 << 12
BV14 = 1 << 13
BV15 = 1 << 14
BV16 = 1 << 15
BV17 = 1 << 16
BV18 = 1 << 17
BV19 = 1 << 18
BV20 = 1 << 19
BV21 = 1 << 20
BV22 = 1 << 21
BV23 = 1 << 22
BV24 = 1 << 23
BV25 = 1 << 24
BV26 = 1 << 25
BV27 = 1 << 26
BV28 = 1 << 27
BV29 = 1 << 28
BV30 = 1 << 29
BV31 = 1 << 30
BV32 = 1 << 31
BV33 = 1 << 32
BV34 = 1 << 33
BV35 = 1 << 34
BV36 = 1 << 35
BV37 = 1 << 36
BV38 = 1 << 37
BV39 = 1 << 38
BV40 = 1 << 39
BV41 = 1 << 40
BV42 = 1 << 41
BV43 = 1 << 42
BV44 = 1 << 43
BV45 = 1 << 44
BV46 = 1 << 45
BV47 = 1 << 46
BV48 = 1 << 47
BV49 = 1 << 48
BV50 = 1 << 49
BV51 = 1 << 50
BV52 = 1 << 51

# Boot Time, Current Time
boot_time = int(time.time())
copy_time = int(time.time())
current_time = int(time.time())

# Game parameters
SCREEN_WIDTH = 79
ANSI_STRING1 = "drgybpcwDRGYBPCWnxLiufvsIUFVS"
ANSI_STRING2 = "^#"
MAX_TRADE = 5
MAX_STATS = 5
MAX_SKILL = 150
SKILL_THAC0_32 = 18
SKILL_THAC0_00 = 6

# Character levels
MAX_LEVEL = 12

NO_GODLESS = (MAX_LEVEL - 2)
LEVEL_IMPLEMENTOR = (MAX_LEVEL - 0)
LEVEL_HIGHJUDGE = (MAX_LEVEL - 1)
LEVEL_JUDGE = (MAX_LEVEL - 2)
LEVEL_ENFORCER = (MAX_LEVEL - 3)
LEVEL_QUESTMAKER = (MAX_LEVEL - 4)
LEVEL_BUILDER = (MAX_LEVEL - 5)
LEVEL_IMMORTAL = (MAX_LEVEL - 5)
LEVEL_ARCHMAGE = (MAX_LEVEL - 6)
LEVEL_MAGE = (MAX_LEVEL - 7)
LEVEL_APPRENTICE = (MAX_LEVEL - 8)
LEVEL_HERO = (MAX_LEVEL - 9)
LEVEL_AVATAR = (MAX_LEVEL - 9)
LEVEL_MORTAL = (MAX_LEVEL - 10)

# TODO: RemoveDebug - switch to false
GDCF = True
GDF = True

# Global Constants
PULSE_PER_SECOND = 4
MILLISECONDS_PER_PULSE = float(1000.0 / PULSE_PER_SECOND)

PULSE_VIOLENCE = 3 * PULSE_PER_SECOND
PULSE_MOBILE = 4 * PULSE_PER_SECOND
PULSE_TICK = 30 * PULSE_PER_SECOND
PULSE_AREA = 60 * PULSE_PER_SECOND
PULSE_WW = 4 * PULSE_PER_SECOND


"""
Console log types.
NONE      - Largely shouldn't be used, placeholding 0 value and for random times not wanting a log message.
DEBUG     - Detailed information, typically of interest only when diagnosing problems.
INFO      - Confirmation that things are working as expected.
WARNING   - An indication that something unexpected happened, or indicative of some problem in the near
            future (e.g. ‘disk space low’). The software is still working as expected.
ERROR     - Due to a more serious problem, the software has not been able to perform some function.
CRITICAL  - A serious error, indicating that the program itself may be unable to continue running.
BOOT      - Boot up message.
EXCEPTION - An exception occured.
"""
CONSOLE_NONE = 0
CONSOLE_DEBUG = 1
CONSOLE_INFO = 2
CONSOLE_WARNING = 3
CONSOLE_ERROR = 4
CONSOLE_CRITICAL = 5
CONSOLE_BOOT = 6
CONSOLE_EXCEPTION = 7

# Time - Quarter of Day
SUN_DARK = 0
SUN_RISE = 1
SUN_LIGHT = 2
SUN_SET = 3

# Weather Defines
SKY_CLOUDLESS = 0
SKY_CLOUDY = 1
SKY_RAINING = 2
SKY_LIGHTNING = 3

# Dice Numbers
DICE_NUMBER = 0
DICE_TYPE = 1
DICE_BONUS = 2

# Target types
TAR_IGNORE = 0
TAR_CHAR_OFFENSIVE = 1
TAR_CHAR_DEFENSIVE = 2
TAR_CHAR_SELF = 3
TAR_OBJ_INV = 4

PURPLE_MAGIC = 0
RED_MAGIC = 1
BLUE_MAGIC = 2
GREEN_MAGIC = 3
YELLOW_MAGIC = 4
MAX_MAGIC = 5

TARGET_CHAR = 0
TARGET_ITEM = 1
TARGET_ROOM = 2
TARGET_NONE = 3

# To types for act function
TO_ROOM = 0
TO_NOTVICT = 1
TO_VICT = 2
TO_CHAR = 3

# Log types
LOG_NORMAL = 0
LOG_ALWAYS = 1
LOG_NEVER = 2

# Hit or Undefined
TYPE_UNDEFINED = -1
TYPE_HIT = 1000

# Affected by Bits
AFF_BLIND = BV01
AFF_INVISIBLE = BV02
AFF_DETECT_EVIL = BV03
AFF_DETECT_INVIS = BV04
AFF_DETECT_MAGIC = BV05
AFF_DETECT_HIDDEN = BV06
AFF_SHADOWPLANE = BV07
AFF_SANCTUARY = BV08
AFF_FAERIE_FIRE = BV09
AFF_INFRARED = BV10
AFF_CURSE = BV11
AFF_FLAMING = BV12
AFF_POISON = BV13
AFF_PROTECT = BV14
AFF_ETHEREAL = BV15
AFF_SNEAK = BV16
AFF_HIDE = BV17
AFF_SLEEP = BV18
AFF_CHARM = BV19
AFF_FLYING = BV20
AFF_PASS_DOOR = BV21
AFF_POLYMORPH = BV22
AFF_SHADOWSIGHT = BV23
AFF_WEBBED = BV24
AFF_DARKNESS = BV26

# Bits for 'itemaffect'.
ITEMA_SHOCKSHIELD = BV01
ITEMA_FIRESHIELD = BV02
ITEMA_ICESHIELD = BV03
ITEMA_ACIDSHIELD = BV04
ITEMA_DBPASS = BV05
ITEMA_CHAOSSHIELD = BV06
ITEMA_ARTIFACT = BV07
ITEMA_REGENERATE = BV08
ITEMA_SPEED = BV09
ITEMA_VORPAL = BV10
ITEMA_PEACE = BV11
ITEMA_RIGHT_SILVER = BV12
ITEMA_LEFT_SILVER = BV13
ITEMA_REFLECT = BV14
ITEMA_RESISTANCE = BV15
ITEMA_VISION = BV16
ITEMA_STALKER = BV17
ITEMA_VANISH = BV18
ITEMA_RAGER = BV19
ITEMA_HIGHLANDER = BV20

# Immunities, for players.
IMM_SLASH = BV01  # Resistance to slash, slice
IMM_STAB = BV02  # Resistance to stab, pierce
IMM_SMASH = BV03  # Resistance to blast, pound, crush
IMM_ANIMAL = BV04  # Resistance to bite, claw
IMM_MISC = BV05  # Resistance to grep, suck, whip
IMM_CHARM = BV06  # Immune to charm spell
IMM_HEAT = BV07  # Immune to fire/heat spells
IMM_COLD = BV08  # Immune to frost/cold spells
IMM_LIGHTNING = BV09  # Immune to lightning spells
IMM_ACID = BV10  # Immune to acid spells
IMM_SUMMON = BV11  # Immune to being summoned
IMM_VOODOO = BV12  # Immune to voodoo magic
IMM_VAMPIRE = BV13  # Allow yourself to become a vampire
IMM_STAKE = BV14  # Immune to being staked (vamps only)
IMM_SUNLIGHT = BV15  # Immune to sunlight (vamps only)
IMM_SHIELDED = BV16  # For Obfuscate. Block scry, etc
IMM_HURL = BV17  # Cannot be hurled
IMM_BACKSTAB = BV18  # Cannot be backstabbed
IMM_KICK = BV19  # Cannot be kicked
IMM_DISARM = BV20  # Cannot be disarmed
IMM_STEAL = BV21  # Cannot have stuff stolen
IMM_SLEEP = BV22  # Immune to sleep spell
IMM_DRAIN = BV23  # Immune to energy drain
IMM_DEMON = BV24  # Allow yourself to become a demon
IMM_TRANSPORT = BV25  # Objects can't be transported to you

# Rune, Glyph and Sigil bits.
RUNE_FIRE = BV01
RUNE_AIR = BV02
RUNE_EARTH = BV03
RUNE_WATER = BV04
RUNE_DARK = BV05
RUNE_LIGHT = BV06
RUNE_LIFE = BV07
RUNE_DEATH = BV08
RUNE_MIND = BV09
RUNE_SPIRIT = BV10
RUNE_MASTER = BV11
GLYPH_CREATION = BV01
GLYPH_DESTRUCTION = BV02
GLYPH_SUMMONING = BV03
GLYPH_TRANSFORMATION = BV04
GLYPH_TRANSPORTATION = BV05
GLYPH_ENHANCEMENT = BV06
GLYPH_REDUCTION = BV07
GLYPH_CONTROL = BV08
GLYPH_PROTECTION = BV09
GLYPH_INFORMATION = BV10
SIGIL_SELF = BV01
SIGIL_TARGETING = BV02
SIGIL_AREA = BV03
SIGIL_OBJECT = BV04

# Bits for 'polymorph'.
POLY_BAT = BV01
POLY_WOLF = BV02
POLY_MIST = BV03
POLY_SERPENT = BV04
POLY_RAVEN = BV05
POLY_FISH = BV06
POLY_FROG = BV07

# Bits for 'vampire'.
VAM_FANGS = BV01
VAM_CLAWS = BV02
VAM_NIGHTSIGHT = BV03
VAM_FLYING = BV04  # For flying creatures
VAM_SONIC = BV05  # For creatures with full detect
VAM_CHANGED = BV06  # Changed using a vampire power
VAM_PROTEAN = BV07  # Claws, nightsight, and change
VAM_CELERITY = BV08  # 66%/33% chance 1/2 extra attacks
VAM_FORTITUDE = BV09  # 5 hp less per hit taken
VAM_POTENCE = BV10  # Deal out 1.5 times normal damage
VAM_OBFUSCATE = BV11  # Disguise and invis
VAM_AUSPEX = BV12  # Truesight, etc
VAM_OBTENEBRATION = BV13  # Shadowplane/sight and shadowbody
VAM_SERPENTIS = BV14  # Eyes/serpent, heart/darkness, etc
VAM_DISGUISED = BV15  # For the Obfuscate disguise ability
VAM_MORTAL = BV16  # For Obfuscate mortal ability
VAM_DOMINATE = BV17  # Evileye, command
VAM_EVILEYE = BV18  # Evileye, command
VAM_PRESENCE = BV19  # Presence discipline

# Score.
SCORE_TOTAL_XP = 0
SCORE_HIGH_XP = 1
SCORE_TOTAL_LEVEL = 2
SCORE_HIGH_LEVEL = 3
SCORE_QUEST = 4
SCORE_NUM_QUEST = 5
MAX_SCORE = 6

# Mounts
IS_ON_FOOT = 0
IS_MOUNT = BV01
IS_RIDING = BV02
IS_CARRIED = BV03
IS_CARRYING = BV04

# Zombie Lord.
ZOMBIE_NOTHING = 0
ZOMBIE_TRACKING = 1
ZOMBIE_ANIMATE = 2
ZOMBIE_CAST = 3
ZOMBIE_REST = 4

# Damcap values.
DAM_CAP = 0
DAM_CHANGE = 1

# AGE Bits.
AGE_CHILDE = 0
AGE_NEONATE = 1
AGE_ANCILLA = 2
AGE_ELDER = 3
AGE_METHUSELAH = 4

# Special Bits
SPC_CHAMPION = BV01
SPC_DEMON_LORD = BV02
SPC_WOLFMAN = BV03
SPC_PRINCE = BV04
SPC_SIRE = BV05
SPC_ANARCH = BV06
SPC_INCONNU = BV07

# Bits For Highlanders
HPOWER_WPNSKILL = 0

# Bits For Mages
MPOWER_RUNE0 = 0
MPOWER_RUNE1 = 1
MPOWER_RUNE2 = 2
MPOWER_RUNE3 = 3
MPOWER_RUNE4 = 4

# Body Parts
# Head
LOST_EYE_L = BV01
LOST_EYE_R = BV02
LOST_EAR_L = BV03
LOST_EAR_R = BV04
LOST_NOSE = BV05
BROKEN_NOSE = BV06
BROKEN_JAW = BV07
BROKEN_SKULL = BV08
LOST_HEAD = BV09
LOST_TOOTH_1 = BV10
LOST_TOOTH_2 = BV11
LOST_TOOTH_4 = BV12
LOST_TOOTH_8 = BV13
LOST_TOOTH_16 = BV14
LOST_TONGUE = BV15

# For Body
BROKEN_RIBS_1 = BV01
BROKEN_RIBS_2 = BV02
BROKEN_RIBS_4 = BV03
BROKEN_RIBS_8 = BV04
BROKEN_RIBS_16 = BV05
BROKEN_SPINE = BV06
BROKEN_NECK = BV07
CUT_THROAT = BV08
CUT_STOMACH = BV09
CUT_CHEST = BV10

# For Arms
BROKEN_ARM = BV01
LOST_ARM = BV02
LOST_HAND = BV03
LOST_FINGER_I = BV04  # Index finger
LOST_FINGER_M = BV05  # Middle finger
LOST_FINGER_R = BV06  # Ring finger
LOST_FINGER_L = BV07  # Little finger
LOST_THUMB = BV08
BROKEN_FINGER_I = BV09  # Index finger
BROKEN_FINGER_M = BV10  # Middle finger
BROKEN_FINGER_R = BV11  # Ring finger
BROKEN_FINGER_L = BV12  # Little finger
BROKEN_THUMB = BV13

# For Legs
BROKEN_LEG = BV01
LOST_LEG = BV02
LOST_FOOT = BV03
LOST_TOE_A = BV04
LOST_TOE_B = BV05
LOST_TOE_C = BV06
LOST_TOE_D = BV07  # Smallest toe
LOST_TOE_BIG = BV08
BROKEN_TOE_A = BV09
BROKEN_TOE_B = BV10
BROKEN_TOE_C = BV11
BROKEN_TOE_D = BV12  # Smallest toe
BROKEN_TOE_BIG = BV13

# For Bleeding
BLEEDING_HEAD = BV01
BLEEDING_THROAT = BV02
BLEEDING_ARM_L = BV03
BLEEDING_ARM_R = BV04
BLEEDING_HAND_L = BV05
BLEEDING_HAND_R = BV06
BLEEDING_LEG_L = BV07
BLEEDING_LEG_R = BV08
BLEEDING_FOOT_L = BV09
BLEEDING_FOOT_R = BV10

# Item quest flags.
QUEST_STR = BV01
QUEST_DEX = BV02
QUEST_INT = BV03
QUEST_WIS = BV04
QUEST_CON = BV05
QUEST_HITROLL = BV06
QUEST_DAMROLL = BV07
QUEST_HIT = BV08
QUEST_MANA = BV09
QUEST_MOVE = BV10
QUEST_AC = BV11
QUEST_NAME = BV12
QUEST_SHORT = BV13
QUEST_LONG = BV14
QUEST_FREENAME = BV15
QUEST_ENCHANTED = BV16
QUEST_SPELLPROOF = BV17
QUEST_IMPROVED = BV19
QUEST_MASTER_RUNE = BV20


# Totems for werewolves.
WPOWER_MANTIS = 0
WPOWER_BEAR = 1
WPOWER_LYNX = 2
WPOWER_BOAR = 3
WPOWER_OWL = 4
WPOWER_SPIDER = 5
WPOWER_WOLF = 6
WPOWER_HAWK = 7
WPOWER_SILVER = 8
UNI_GEN = 9
UNI_AFF = 10
UNI_CURRENT = 11
UNI_RAGE = 12
UNI_FORM0 = 13
UNI_FORM1 = 14
DEMON_CURRENT = 15
DEMON_TOTAL = 16
DEMON_POWER = 17
DPOWER_FLAGS = 18
DPOWER_CURRENT = 19
DPOWER_OBJ_VNUM = 20
MAX_POWERS = 40

# Demons
DEM_FANGS = BV01
DEM_CLAWS = BV02
DEM_HORNS = BV03
DEM_HOOVES = BV04
DEM_EYES = BV05
DEM_WINGS = BV06
DEM_MIGHT = BV07
DEM_TOUGH = BV08
DEM_SPEED = BV09
DEM_TRAVEL = BV10
DEM_SCRY = BV11
DEM_SHADOWSIGHT = BV12
DEM_MOVE = BV13
DEM_LEAP = BV14
DEM_MAGIC = BV15
DEM_LIFESPAN = BV16
DEM_UNFOLDED = BV17

# Weapon types.
WPN_UNARMED = 0
WPN_SLICE = 1
WPN_STAB = 2
WPN_SLASH = 3
WPN_WHIP = 4
WPN_CLAW = 5
WPN_BLAST = 6
WPN_POUND = 7
WPN_CRUSH = 8
WPN_GREP = 9
WPN_BITE = 10
WPN_PIERCE = 11
WPN_SUCK = 12
MAX_WPN = 13

'''
Character Defines
'''


''' Equipment Slot Strings - for use with displaying EQ to characters '''

eq_slot_strings = collections.OrderedDict([("light", "[Light         ] "),
                                           ("left_finger", "[On Finger     ] "),
                                           ("right_finger", "[On Finger     ] "),
                                           ("neck_one", "[Around Neck   ] "),
                                           ("neck_two", "[Around Neck   ] "),
                                           ("body", "[On Body       ] "),
                                           ("head", "[On Head       ] "),
                                           ("legs", "[On Legs       ] "),
                                           ("feet", "[On Feet       ] "),
                                           ("hands", "[On Hands      ] "),
                                           ("arms", "[On Arms       ] "),
                                           ("off_hand", "[Off Hand      ] "),
                                           ("about_body", "[Around Body   ] "),
                                           ("waist", "[Around Waist  ] "),
                                           ("left_wrist", "[Around Wrist  ] "),
                                           ("right_wrist", "[Around Wrist  ] "),
                                           ("right_hand", "[Right Hand    ] "),
                                           ("left_hand", "[Left Hand     ] "),
                                           ("face", "[On Face       ] "),
                                           ("left_scabbard", "[Left Scabbard ] "),
                                           ("right_scabbard", "[Right Scabbard] ")])

# Sexes
SEX_NEUTRAL = 0
SEX_MALE = 1
SEX_FEMALE = 2

# Stats
STAT_STR = 0
STAT_INT = 1
STAT_WIS = 2
STAT_DEX = 3
STAT_CON = 4

# Positions
POS_DEAD = 0
POS_MORTAL = 1
POS_INCAP = 2
POS_STUNNED = 3
POS_SLEEPING = 4
POS_MEDITATING = 5
POS_SITTING = 6
POS_RESTING = 7
POS_FIGHTING = 8
POS_STANDING = 9

# ACT bits for players.
PLR_IS_NPC = BV01     # Don't EVER set.
PLR_AUTOEXIT = BV02
PLR_AUTOLOOT = BV03
PLR_AUTOSAC = BV04
PLR_BLANK = BV05
PLR_BRIEF = BV06
PLR_COMBINE = BV07
PLR_PROMPT = BV08
PLR_TELNET_GA = BV09
PLR_HOLYLIGHT = BV10
PLR_WIZINVIS = BV11
PLR_ANSI = BV12
PLR_INCOG = BV13
PLR_GODLESS = BV14

# Player sentances.
SENT_SILENCE = BV01
SENT_NO_EMOTE = BV02
SENT_NO_TELL = BV03
SENT_LOG = BV04
SENT_DENY = BV05
SENT_FREEZE = BV06

# ACT Bits for NPCs
ACT_IS_NPC = BV01  # Auto set for mobs
ACT_SENTINEL = BV02
ACT_SCAVENGER = BV03
ACT_AGGRESSIVE = BV06
ACT_STAY_AREA = BV07
ACT_WIMPY = BV08
ACT_PET = BV09
ACT_TRAIN = BV10
ACT_PRACTICE = BV11
ACT_MOUNT = BV12
ACT_NOPARTS = BV13
ACT_NOEXP = BV14

# Extra bits.
EXTRA_TRUSTED = BV01
EXTRA_NEWPASS = BV02
EXTRA_OSWITCH = BV03
EXTRA_SWITCH = BV04
EXTRA_FAKE_CON = BV05
EXTRA_TIED_UP = BV06
EXTRA_GAGGED = BV07
EXTRA_BLINDFOLDED = BV08
EXTRA_PROMPT = BV09
EXTRA_MARRIED = BV10
EXTRA_CALL_ALL = BV11
EXTRA_ANTI_GODLESS = BV12
EXTRA_NOTE_TRUST = BV13

# Special types.
SITEM_ACTIVATE = BV01
SITEM_TWIST = BV02
SITEM_PRESS = BV03
SITEM_PULL = BV04
SITEM_TARGET = BV05
SITEM_SPELL = BV06
SITEM_TRANSPORTER = BV07
SITEM_TELEPORTER = BV08
SITEM_DELAY1 = BV09
SITEM_DELAY2 = BV10
SITEM_OBJECT = BV11
SITEM_MOBILE = BV12
SITEM_ACTION = BV13
SITEM_MORPH = BV14
SITEM_SILVER = BV15
SITEM_WOLFWEAPON = BV16
SITEM_DROWWEAPON = BV17
SITEM_CHAMPWEAPON = BV18
SITEM_DEMONIC = BV19
SITEM_HIGHLANDER = BV20

# Advanced spells. (SITEM_* continued)
ADV_DAMAGE = BV21
ADV_AFFECT = BV22
ADV_ACTION = BV23
ADV_AREA_AFFECT = BV24
ADV_VICTIM_TARGET = BV25
ADV_OBJECT_TARGET = BV26
ADV_GLOBAL_TARGET = BV27
ADV_NEXT_PAGE = BV28
ADV_PARAMETER = BV29
ADV_SPELL_FIRST = BV30
ADV_NOT_CASTER = BV31
ADV_NO_PLAYERS = BV32
ADV_SECOND_VICTIM = BV33
ADV_SECOND_OBJECT = BV34
ADV_REVERSED = BV35
ADV_STARTED = BV36
ADV_FINISHED = BV37
ADV_FAILED = BV38
ADV_MESSAGE_1 = BV39
ADV_MESSAGE_2 = BV40
ADV_MESSAGE_3 = BV41

# Advanced spell actions.
ACTION_NONE = 0
ACTION_MOVE = 1
ACTION_MOB = 2
ACTION_OBJECT = 3

# Tool types.
TOOL_PEN = BV01
TOOL_PLIERS = BV02
TOOL_SCALPEL = BV03

# Advanced spell affects.
ADV_STR = BV01
ADV_DEX = BV02
ADV_INT = BV03
ADV_WIS = BV04
ADV_CON = BV05
ADV_SEX = BV06
ADV_MANA = BV07
ADV_HIT = BV08
ADV_MOVE = BV09
ADV_AC = BV10
ADV_HITROLL = BV11
ADV_DAMROLL = BV12
ADV_SAVING_SPELL = BV13

# For Spec powers on players
EYE_SPELL = BV01  # Spell when they look at you
EYE_SELFACTION = BV02  # You do action when they look
EYE_ACTION = BV03  # Others do action when they look

# Room text flags (KaVir).
RT_LIGHTS = BV01  # Toggles lights on/off
RT_SAY = BV02  # Use this if no others powers
RT_ENTER = BV03
RT_CAST = BV04
RT_THROWOUT = BV05  # Erm...can't remember ;)
RT_OBJECT = BV06  # Creates an object
RT_MOBILE = BV07  # Creates a mobile
RT_LIGHT = BV08  # Lights on ONLY
RT_DARK = BV09  # Lights off ONLY
RT_OPEN_LIFT = BV10  # Open lift
RT_CLOSE_LIFT = BV11  # Close lift
RT_MOVE_LIFT = BV12  # Move lift
RT_SPELL = BV13  # Cast a spell
RT_PORTAL = BV14  # Creates a one-way portal */
RT_TELEPORT = BV15  # Teleport player to room */
RT_ACTION = BV16
RT_BLANK_1 = BV17
RT_BLANK_2 = BV18
RT_RETURN = BV21  # Perform once
RT_PERSONAL = BV22  # Only shows message to char
RT_TIMER = BV23  # Sets object timer to 1 tick

# Stances for combat
STANCE_NONE = -1
STANCE_NORMAL = 0
STANCE_VIPER = 1
STANCE_CRANE = 2
STANCE_CRAB = 3
STANCE_MONGOOSE = 4
STANCE_BULL = 5
STANCE_MANTIS = 6
STANCE_DRAGON = 7
STANCE_TIGER = 8
STANCE_MONKEY = 9
STANCE_SWALLOW = 10
MAX_STANCE = 15

# Channel bits.
CHANNEL_CHAT = BV01
CHANNEL_IMMTALK = BV02
CHANNEL_MUSIC = BV03
CHANNEL_QUESTION = BV04
CHANNEL_SHOUT = BV05
CHANNEL_YELL = BV06
CHANNEL_VAMPTALK = BV07
CHANNEL_HOWL = BV08
CHANNEL_PRAY = BV09
CHANNEL_INFO = BV10
CHANNEL_MAGETALK = BV11
CHANNEL_TELL = BV12

'''
Room Defines
'''


# Room Sector Types
SECT_INSIDE = 0
SECT_CITY = 1
SECT_FIELD = 2
SECT_FOREST = 3
SECT_HILLS = 4
SECT_MOUNTAIN = 5
SECT_WATER_SWIM = 6
SECT_WATER_NOSWIM = 7
SECT_UNUSED = 8
SECT_AIR = 9
SECT_DESERT = 10
SECT_MAX = 11

# Directions
DIR_NORTH = 0
DIR_EAST = 1
DIR_SOUTH = 2
DIR_WEST = 3
DIR_UP = 4
DIR_DOWN = 5
MAX_DIR = 6

# Movement
dir_name = ["north", "east", "south", "west", "up", "down"]
rev_dir = [2, 3, 0, 1, 5, 4]
movement_loss = [1, 2, 2, 3, 4, 6, 4, 1, 6, 10, 6]

# Room Flags
ROOM_DARK = BV01
ROOM_NO_MOB = BV03
ROOM_INDOORS = BV04
ROOM_PRIVATE = BV10
ROOM_SAFE = BV11
ROOM_SOLITARY = BV12
ROOM_PET_SHOP = BV13
ROOM_NO_RECALL = BV14
ROOM_NO_TELEPORT = BV15
ROOM_TOTAL_DARKNESS = BV16
ROOM_BLADE_BARRIER = BV17

# Exit Flags
EX_ISDOOR = BV01
EX_CLOSED = BV02
EX_LOCKED = BV03
EX_PICKPROOF = BV06

'''
Item Defines
'''


# Apply Types
APPLY_NONE = 0
APPLY_STR = 1
APPLY_DEX = 2
APPLY_INT = 3
APPLY_WIS = 4
APPLY_CON = 5
APPLY_SEX = 6
APPLY_CLASS = 7
APPLY_LEVEL = 8
APPLY_AGE = 9
APPLY_HEIGHT = 10
APPLY_WEIGHT = 11
APPLY_MANA = 12
APPLY_HIT = 13
APPLY_MOVE = 14
APPLY_GOLD = 15
APPLY_EXP = 16
APPLY_AC = 17
APPLY_HITROLL = 18
APPLY_DAMROLL = 19
APPLY_SAVING_PARA = 20
APPLY_SAVING_ROD = 21
APPLY_SAVING_PETRI = 22
APPLY_SAVING_BREATH = 23
APPLY_SAVING_SPELL = 24
APPLY_POLY = 25

# Item types
ITEM_LIGHT = "light"
ITEM_SCROLL = "scroll"
ITEM_WAND = "wand"
ITEM_STAFF = "staff"
ITEM_WEAPON = "weapon"
ITEM_TREASURE = "treasure"
ITEM_ARMOR = "armor"
ITEM_POTION = "potion"
ITEM_FURNITURE = "furniture"
ITEM_TRASH = "trash"
ITEM_CONTAINER = "container"
ITEM_DRINK_CON = "drink"
ITEM_KEY = "key"
ITEM_FOOD = "food"
ITEM_MONEY = "money"
ITEM_BOAT = "boat"
ITEM_CORPSE_NPC = "npc_corpse"
ITEM_CORPSE_PC = "pc_corpse"
ITEM_FOUNTAIN = "fountain"
ITEM_PILL = "pill"
ITEM_PORTAL = "portal"
ITEM_EGG = "egg"
ITEM_VOODOO = "voodoo"
ITEM_STAKE = "stake"
ITEM_MISSILE = "missile"
ITEM_AMMO = "ammo"
ITEM_QUEST = "quest"
ITEM_QUESTCARD = "questcard"
ITEM_QUESTMACHINE = "questmachine"
ITEM_SYMBOL = "symbol"
ITEM_BOOK = "book"
ITEM_PAGE = "page"
ITEM_TOOL = "tool"

# NPC constants
MOB_VNUM_CITYGUARD = 3060
MOB_VNUM_VAMPIRE = 3404
MOB_VNUM_HOUND = 30000
MOB_VNUM_GUARDIAN = 30001
MOB_VNUM_MOUNT = 30006
MOB_VNUM_FROG = 30007
MOB_VNUM_RAVEN = 30008
MOB_VNUM_CAT = 30009
MOB_VNUM_DOG = 30010
MOB_VNUM_EYE = 30012

# Item constants
OBJ_VNUM_MONEY_ONE = 2
OBJ_VNUM_MONEY_SOME = 3
OBJ_VNUM_CORPSE_NPC = 10
OBJ_VNUM_CORPSE_PC = 11
OBJ_VNUM_SEVERED_HEAD = 12
OBJ_VNUM_TORN_HEART = 13
OBJ_VNUM_SLICED_ARM = 14
OBJ_VNUM_SLICED_LEG = 15
OBJ_VNUM_FINAL_TURD = 16
OBJ_VNUM_MUSHROOM = 20
OBJ_VNUM_LIGHT_BALL = 21
OBJ_VNUM_SPRING = 22
OBJ_VNUM_BLOOD_SPRING = 23
OBJ_VNUM_SOULBLADE = 30000
OBJ_VNUM_PORTAL = 30001
OBJ_VNUM_EGG = 30002
OBJ_VNUM_EMPTY_EGG = 30003
OBJ_VNUM_SPILLED_ENTRAILS = 30004
OBJ_VNUM_QUIVERING_BRAIN = 30005
OBJ_VNUM_SQUIDGY_EYEBALL = 30006
OBJ_VNUM_SPILT_BLOOD = 30007
OBJ_VNUM_VOODOO_DOLL = 30010
OBJ_VNUM_RIPPED_FACE = 30012
OBJ_VNUM_TORN_WINDPIPE = 30013
OBJ_VNUM_CRACKED_HEAD = 30014
OBJ_VNUM_SLICED_EAR = 30025
OBJ_VNUM_SLICED_NOSE = 30026
OBJ_VNUM_KNOCKED_TOOTH = 30027
OBJ_VNUM_TORN_TONGUE = 30028
OBJ_VNUM_SEVERED_HAND = 30029
OBJ_VNUM_SEVERED_FOOT = 30030
OBJ_VNUM_SEVERED_THUMB = 30031
OBJ_VNUM_SEVERED_INDEX = 30032
OBJ_VNUM_SEVERED_MIDDLE = 30033
OBJ_VNUM_SEVERED_RING = 30034
OBJ_VNUM_SEVERED_LITTLE = 30035
OBJ_VNUM_SEVERED_TOE = 30036
OBJ_VNUM_PROTOPLASM = 30037
OBJ_VNUM_QUESTCARD = 30039
OBJ_VNUM_QUESTMACHINE = 30040

# Room constants
ROOM_VNUM_LIMBO = 2
ROOM_VNUM_CHAT = 1200
ROOM_VNUM_TEMPLE = 3001
ROOM_VNUM_ALTAR = 3054
ROOM_VNUM_SCHOOL = 3700
ROOM_VNUM_HELL = 30000
ROOM_VNUM_CRYPT = 30001
ROOM_VNUM_DISCONNECTION = 30002
ROOM_VNUM_IN_OBJECT = 30008

# Container Values (EG, Bags, etc)
CONT_CLOSEABLE = 1
CONT_PICKPROOF = 2
CONT_CLOSED = 4
CONT_LOCKED = 8


'''
Conversion Maps
'''


# Item Bits
rom_wear_flag_map = {"A": "Take",
                     "B": "Finger",
                     "C": "Neck",
                     "D": "Body",
                     "E": "Head",
                     "F": "Legs",
                     "G": "Feet",
                     "H": "Hands",
                     "I": "Arms",
                     "J": "Shield",
                     "K": "About",
                     "L": "Waist",
                     "M": "Wrist",
                     "N": "Right Hand",
                     "O": "Left Hand",
                     "P": "Face"}


rom_wear_loc_map = {-1: None,
                    0: "Light",
                    1: "Left Finger",
                    2: "Right Finger",
                    3: "Neck",
                    4: "Neck",
                    5: "Body",
                    6: "Head",
                    7: "Legs",
                    8: "Feet",
                    9: "Hands",
                    10: "Arms",
                    11: "Off Hand",
                    12: "About",
                    13: "Waist",
                    14: "Left Wrist",
                    15: "Right Wrist",
                    16: "Right Hand",
                    17: "Left Hand",
                    18: "Face",
                    19: "Left Scabbard",
                    20: "Right Scabbard"}


# Equpiment wear locations.
# Used in #RESETS.
wear_num_to_str = collections.OrderedDict([(-1, "none"),
                                           (0, "light"),
                                           (1, "left_finger"),
                                           (2, "right_finger"),
                                           (3, "neck_one"),
                                           (4, "neck_two"),
                                           (5, "body"),
                                           (6, "head"),
                                           (7, "legs"),
                                           (8, "feet"),
                                           (9, "hands"),
                                           (10, "arms"),
                                           (11, "shield"),
                                           (12, "about"),
                                           (13, "waist"),
                                           (14, "left_wrist"),
                                           (15, "right_wrist"),
                                           (16, "right_hand"),
                                           (17, "left_hand"),
                                           (18, "face"),
                                           (19, "right_scabbard"),
                                           (20, "left_scabbard")])


'''
Legacy Bits n Bobs
'''


# legacy WEAR locations
WEAR_NONE = -1
WEAR_LIGHT = 0
WEAR_FINGER_L = 1
WEAR_FINGER_R = 2
WEAR_NECK_1 = 3
WEAR_NECK_2 = 4
WEAR_BODY = 5
WEAR_HEAD = 6
WEAR_LEGS = 7
WEAR_FEET = 8
WEAR_HANDS = 9
WEAR_ARMS = 10
WEAR_SHIELD = 11
WEAR_ABOUT = 12
WEAR_WAIST = 13
WEAR_WRIST_L = 14
WEAR_WRIST_R = 15
WEAR_WIELD = 16
WEAR_HOLD = 17
WEAR_FACE = 18
WEAR_SCABBARD_L = 19
WEAR_SCABBARD_R = 20
MAX_WEAR = 21

# Extra flags - Legacy
ITEM_GLOW = BV01
ITEM_HUM = BV02
ITEM_THROWN = BV03
ITEM_KEEP = BV04
ITEM_VANISH = BV05
ITEM_INVIS = BV06
ITEM_MAGIC = BV07
ITEM_NODROP = BV08
ITEM_BLESS = BV09
ITEM_ANTI_GOOD = BV10
ITEM_ANTI_EVIL = BV11
ITEM_ANTI_NEUTRAL = BV12
ITEM_NOREMOVE = BV13
ITEM_INVENTORY = BV14
ITEM_LOYAL = BV15
ITEM_SHADOWPLANE = BV16

# Wear flags - Legacy
ITEM_TAKE = BV01
ITEM_WEAR_FINGER = BV02
ITEM_WEAR_NECK = BV03
ITEM_WEAR_BODY = BV04
ITEM_WEAR_HEAD = BV05
ITEM_WEAR_LEGS = BV06
ITEM_WEAR_FEET = BV07
ITEM_WEAR_HANDS = BV08
ITEM_WEAR_ARMS = BV09
ITEM_WEAR_SHIELD = BV10
ITEM_WEAR_ABOUT = BV11
ITEM_WEAR_WAIST = BV12
ITEM_WEAR_WRIST = BV13
ITEM_WIELD = BV14
ITEM_HOLD = BV15
ITEM_WEAR_FACE = BV16


# Return ascii name of an affect location.
def affect_loc_name(location):
    affect_loc = {APPLY_NONE: "none",
                  APPLY_STR: "strength",
                  APPLY_DEX: "dexterity",
                  APPLY_INT: "intelligence",
                  APPLY_WIS: "wisdom",
                  APPLY_CON: "constitution",
                  APPLY_SEX: "sex",
                  APPLY_CLASS: "class",
                  APPLY_LEVEL: "level",
                  APPLY_AGE: "age",
                  APPLY_HEIGHT: "height",
                  APPLY_WEIGHT: "weight",
                  APPLY_MANA: "mana",
                  APPLY_HIT: "hp",
                  APPLY_MOVE: "moves",
                  APPLY_GOLD: "gold",
                  APPLY_EXP: "experience",
                  APPLY_AC: "armor class",
                  APPLY_HITROLL: "hit roll",
                  APPLY_DAMROLL: "damage roll",
                  APPLY_SAVING_PARA: "save vs paralyze",
                  APPLY_SAVING_ROD: "save vs rod",
                  APPLY_SAVING_PETRI: "save vs petrification",
                  APPLY_SAVING_BREATH: "save vs breath",
                  APPLY_SAVING_SPELL: "save vs spell",
                  APPLY_POLY: "polymorph"}

    location = affect_loc.get(location, None)
    if not location:
        comm.notify(f"affect_location_name: unknown location {location}", CONSOLE_INFO)
        return "(unknown)"
    return location


# Return ascii name of an affect bit vector.
def affect_bit_name(vector):
    buf = ""
    if vector & AFF_BLIND:
        buf += " blind"
    if vector & AFF_INVISIBLE:
        buf += " invisible"
    if vector & AFF_DETECT_EVIL:
        buf += " detect_evil"
    if vector & AFF_DETECT_INVIS:
        buf += " detect_invis"
    if vector & AFF_DETECT_MAGIC:
        buf += " detect_magic"
    if vector & AFF_DETECT_HIDDEN:
        buf += " detect_hidden"
    if vector & AFF_SANCTUARY:
        buf += " sanctuary"
    if vector & AFF_FAERIE_FIRE:
        buf += " faerie_fire"
    if vector & AFF_INFRARED:
        buf += " infrared"
    if vector & AFF_CURSE:
        buf += " curse"
    if vector & AFF_POISON:
        buf += " poison"
    if vector & AFF_SLEEP:
        buf += " sleep"
    if vector & AFF_SNEAK:
        buf += " sneak"
    if vector & AFF_HIDE:
        buf += " hide"
    if vector & AFF_CHARM:
        buf += " charm"
    if vector & AFF_FLYING:
        buf += " flying"
    if vector & AFF_PASS_DOOR:
        buf += " pass_door"
    if not buf:
        return "none"
    return buf.lstrip()


# return ascii name of an act vector
def act_bit_name(act_flags):
    buf = ""

    if state_checks.is_set(act_flags, ACT_IS_NPC):
        buf += " npc"
        if act_flags & ACT_SENTINEL:
            buf += " sentinel"
        if act_flags & ACT_SCAVENGER:
            buf += " scavenger"
        if act_flags & ACT_AGGRESSIVE:
            buf += " aggressive"
        if act_flags & ACT_STAY_AREA:
            buf += " stay_area"
        if act_flags & ACT_WIMPY:
            buf += " wimpy"
        if act_flags & ACT_PET:
            buf += " pet"
        if act_flags & ACT_TRAIN:
            buf += " train"
        if act_flags & ACT_PRACTICE:
            buf += " practice"
    else:
        buf += " player"
        if act_flags & PLR_AUTOEXIT:
            buf += " autoexit"
        if act_flags & PLR_AUTOLOOT:
            buf += " autoloot"
        if act_flags & PLR_AUTOSAC:
            buf += " autosac"
        if act_flags & PLR_HOLYLIGHT:
            buf += " holy_light"
    return "none" if not buf else buf


# inclusive range function. Here in merc.py since the file is included more often than game_utils.py (less typing also)
def irange(start=0, stop=1, step=1):
    return range(start, (stop + 1) if step >= 0 else (stop - 1), step)
