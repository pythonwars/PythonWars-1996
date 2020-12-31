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


def cmd_sset(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    argument, arg3 = game_utils.read_word(argument)

    if not arg1 or not arg2 or not arg3:
        ch.send("Syntax: sset <victim> <skill> <value>\n"
                "or:     sset <victim> all     <value>\n"
                "Skill being any skill or spell.\n")
        return

    victim = ch.get_char_world(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    fall = game_utils.str_cmp(arg2, "all")
    sn = state_checks.prefix_lookup(const.skill_table, arg2)
    if not fall and not sn:
        ch.send("No such skill or spell.\n")
        return

    # Snarf the value.
    if not arg3.isdigit():
        ch.send("Value must be numeric.\n")
        return

    value = int(arg3)
    if value not in merc.irange(0, 100):
        ch.send("Value range is 0 to 100.\n")
        return

    if fall:
        for sn in const.skill_table.keys():
            victim.learned[sn] = value
    else:
        victim.learned[sn.name] = value
    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="sset",
        cmd_fun=cmd_sset,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
