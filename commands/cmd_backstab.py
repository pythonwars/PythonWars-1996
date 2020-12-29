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
import handler_game
import interp
import merc


def cmd_backstab(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Backstab whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim == ch:
        ch.not_self()
        return

    if fight.is_safe(ch, victim):
        return

    item = ch.get_eq("right_hand")
    if not item or item.value[3] != 11:
        item = ch.get_eq("left_hand")
        if not item or item.value[3] != 11:
            ch.send("You need to wield a piercing weapon.\n")
            return

    if victim.fighting:
        ch.send("You can't backstab a fighting person.\n")
        return

    if victim.hit < victim.max_hit:
        handler_game.act("$N is hurt and suspicious ... you can't sneak up.", ch, None, victim, merc.TO_CHAR)
        return

    fight.check_killer(ch, victim)
    ch.wait_state(const.skill_table["backstab"].beats)

    if not victim.is_npc() and victim.immune.is_set(merc.IMM_BACKSTAB):
        fight.damage(ch, victim, 0, "backstab")
    elif not victim.is_npc() or ch.is_npc() or game_utils.number_percent() < ch.learned["backstab"]:
        fight.multi_hit(ch, victim, "backstab")
    else:
        fight.damage(ch, victim, 0, "backstab")


interp.register_command(
    interp.CmdType(
        name="backstab",
        cmd_fun=cmd_backstab,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="bs",
        cmd_fun=cmd_backstab,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
