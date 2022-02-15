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

from collections import OrderedDict

import comm
import living
import merc
import settings


class CmdType:
    def __init__(self, name, cmd_fun, position, level, log, show, default_arg=None):
        self.name = name
        self.cmd_fun = cmd_fun
        self.position = position
        self.level = level
        self.log = log
        self.show = show
        self.default_arg = default_arg
        setattr(living.Living, self.cmd_fun.__name__, self.cmd_fun)


# These commands don't need to be here but are, for order. These will always match first with prefixes.
cmd_table = OrderedDict()

cmd_table["north"] = None
cmd_table["east"] = None
cmd_table["south"] = None
cmd_table["west"] = None
cmd_table["up"] = None
cmd_table["down"] = None
cmd_table["at"] = None
cmd_table["buy"] = None
cmd_table["cast"] = None
cmd_table["follow"] = None
cmd_table["goto"] = None
cmd_table["group"] = None
cmd_table["inventory"] = None
cmd_table["kill"] = None
cmd_table["look"] = None
cmd_table["level"] = None
cmd_table["score"] = None
cmd_table["who"] = None


def register_command(entry: CmdType):
    cmd_table[entry.name] = entry

    if settings.DEBUG:
        comm.notify(f"    {entry.name} registered in command table.", merc.CONSOLE_INFO)
