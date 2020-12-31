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
import handler_game
import interp
import merc
import state_checks


def cmd_practice(ch, argument):
    temp, argument = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not argument:
        buf = []
        col = 0
        ch.update_skills()

        for sn, skill in const.skill_table.items():
            if sn not in ch.learned:
                continue

            buf += "{:<18} {:3}%  ".format(skill.name, ch.learned[sn])

            col += 1
            if col % 3 == 0:
                buf += "\n"

        if col % 3 != 0:
            buf += "\n"

        buf += "You have {:,} exp left.\n".format(ch.exp)
        ch.send("".join(buf))
    else:
        if not ch.is_awake():
            ch.send("In your dreams, or what?\n")
            return

        if ch.exp <= 0:
            ch.send("You have no exp left.\n")
            return

        skill = state_checks.prefix_lookup(const.skill_table, argument)
        if not skill or (not ch.is_npc() and ch.level < skill.skill_level):
            ch.send("You can't practice that.\n")
            return

        if ch.learned[skill.name] >= 100:
            ch.send("You are already an adept of {}.\n".format(skill.name))
        elif ch.learned[skill.name] > 0 and (ch.learned[skill.name] // 2) > ch.exp:
            ch.send("You need {} exp to increase {} any more.\n".format(ch.learned[skill.name] // 2, skill.name))
        elif ch.learned[skill.name] == 0 and ch.exp < 500:
            ch.send("You need 500 exp to increase {}.\n".format(skill.name))
        else:
            if ch.learned[skill.name] == 0:
                ch.exp -= 500
                ch.learned[skill.name] += ch.stat(merc.STAT_INT)
            else:
                ch.exp -= ch.learned[skill.name] // 2
                ch.learned[skill.name] += const.int_app[ch.stat(merc.STAT_INT)].learn

            if ch.learned[skill.name] < 100:
                handler_game.act("You practice $T.", ch, None, skill.name, merc.TO_CHAR)
            else:
                ch.learned[skill.name] = 100
                handler_game.act("You are now an adept of $T.", ch, None, skill.name, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="practice",
        cmd_fun=cmd_practice,
        position=merc.POS_SLEEPING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
