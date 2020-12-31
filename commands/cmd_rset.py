#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
#
#  GodWars improvements copyright © 1995, 1996 by Richard Woolcock.
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

import game_utils
import interp
import merc


# TODO - Known broken - needs TLC
def cmd_rset(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    arg3 = argument

    if not arg1 or not arg2 or not arg3:
        ch.send("Syntax: rset <location> <field> value\n\n"
                "Field being one of:\n"
                "  flags sector\n")
        return

    location = game_utils.find_location(ch, arg1)
    if not location:
        ch.send("No such location.\n")
        return

    # Snarf the value.
    value = int(arg3) if arg3.isdigit() else -1

    # Set something.
    if game_utils.str_cmp(arg2, "flags"):
        location.room_flags.bits = value
        return

    if game_utils.str_cmp(arg2, "sector"):
        location.sector_type = value
        return

    # Generate usage message.
    ch.cmd_rset("")


interp.register_command(
    interp.CmdType(
        name="rset",
        cmd_fun=cmd_rset,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
