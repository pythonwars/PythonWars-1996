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

import const
import game_utils
import interp
import merc
import state_checks


def cmd_slookup(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Slookup what?\n")
        return

    if game_utils.str_cmp(arg, "all"):
        buf = []
        for sn, skill in const.skill_table.items():
            buf += "Sn: {:15}  Slot: {:4}  Skill/spell: '{}'\n".format(sn, skill.slot, skill.name)
        ch.send("".join(buf))
    else:
        skill = state_checks.prefix_lookup(const.skill_table, arg)
        if not skill:
            ch.send("No such skill or spell.\n")
            return

        ch.send("Sn: {:15}  Slot: {:4}  Skill/spell: '{}'\n".format(skill.name, skill.slot, skill.name))


interp.register_command(
    interp.CmdType(
        name="slookup",
        cmd_fun=cmd_slookup,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
