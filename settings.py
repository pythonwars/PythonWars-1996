#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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

import os

# Game settings
PORT = 4123
LOCAL_NAME = "LAPTOP-OHJ1VMIL"

MAX_STRING_LENGTH = 4096
MAX_INPUT_LENGTH = 1024
MAX_ITERATIONS = 300

# File Extensions
DATA_EXTN = ".json"

# Folders
AREA_DIR = os.path.join("area")
DATA_DIR = os.path.join("data")
DOC_DIR = os.path.join("docs")
LOG_DIR = os.path.join("logs")

DATA_FLAG_DIR = os.path.join(DATA_DIR, "flag_tables")
PLAYER_DIR = os.path.join(DATA_DIR, "players")
SYSTEM_DIR = os.path.join(DATA_DIR, "system")
WORLD_DIR = os.path.join(DATA_DIR, "world")

INSTANCE_DIR = os.path.join(WORLD_DIR, "instances")

# Files
AREA_LIST = "area.lst"
BUG_FILE = os.path.join(SYSTEM_DIR, "bugs.txt")
IDEA_FILE = os.path.join(SYSTEM_DIR, "ideas.txt")
INSTANCE_FILE = os.path.join(SYSTEM_DIR, "instance_tracker.txt")
NOTE_FILE = os.path.join(SYSTEM_DIR, "notes.txt")
SHUTDOWN_FILE = os.path.join(SYSTEM_DIR, "shutdown.txt")
TYPO_FILE = os.path.join(SYSTEM_DIR, "typo.txt")

# Features
WIZLOCK = False
LOGALL = False
DEBUG = False
