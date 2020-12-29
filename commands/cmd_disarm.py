#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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
import fight
import game_utils
import interp
import merc


# noinspection PyUnusedLocal
def cmd_disarm(ch, argument):
    if not ch.is_npc() and ch.level < const.skill_table["disarm"].skill_level:
        ch.send("You don't know how to disarm opponents.\n")
        return

    if not ch.get_eq("right_hand") and not ch.get_eq("left_hand"):
        ch.send("You must wield a weapon to disarm.\n")
        return

    victim = ch.fighting
    if not victim:
        ch.send("You aren't fighting anyone.\n")
        return

    item = victim.get_eq("right_hand")
    if not item:
        item = victim.get_eq("left_hand")
        if not item:
            ch.send("Your opponent is not wielding a weapon.\n")
            return

    ch.wait_state(const.skill_table["disarm"].beats)

    percent = game_utils.number_percent() + victim.level - ch.level
    if not victim.is_npc() and victim.immune.is_set(merc.IMM_DISARM):
        ch.send("You failed.\n")
    elif ch.is_npc() or percent < ch.learned["disarm"] * 2 // 3:
        fight.disarm(ch, victim)
    else:
        ch.send("You failed.\n")


interp.register_command(
    interp.CmdType(
        name="disarm",
        cmd_fun=cmd_disarm,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
