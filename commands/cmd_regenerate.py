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

import fight
import game_utils
import handler_game
import interp
import merc


# noinspection PyUnusedLocal
def cmd_regenerate(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if ch.powers[merc.UNI_RAGE] > 0:
        ch.send("You cannot control your regenerative powers while the beast is so strong.\n")
        return

    if ch.position == merc.POS_FIGHTING:
        ch.send("You cannot regenerate while fighting.\n")
        return

    if ch.hit >= ch.max_hit and ch.mana >= ch.max_mana and ch.move >= ch.max_move:
        ch.send("But you are already completely regenerated!\n")
        return

    if ch.blood < 5:
        ch.send("You have insufficient blood.\n")
        return

    ch.blood -= game_utils.number_range(2, 5)
    if ch.hit >= ch.max_hit and ch.mana >= ch.max_mana and ch.move >= ch.max_move:
        ch.send("Your body has completely regenerated.\n")
        handler_game.act("$n's body completely regenerates itself.", ch, None, None, merc.TO_ROOM)
    else:
        ch.send("Your body slowly regenerates itself.\n")

    if ch.hit < 1:
        ch.hit += 1
        fight.update_pos(ch)
        ch.wait_state(merc.PULSE_VIOLENCE * 2)
    else:
        rmin = 5
        rmax = 10
        rmin += 10 - ch.powers[merc.UNI_GEN]
        rmax += 20 - (ch.powers[merc.UNI_GEN] * 2)
        ch.hit = min(ch.hit + game_utils.number_range(rmin, rmax), ch.max_hit)
        ch.mana = min(ch.mana + game_utils.number_range(rmin, rmax), ch.max_mana)
        ch.move = min(ch.move + game_utils.number_range(rmin, rmax), ch.max_move)
        fight.update_pos(ch)


interp.register_command(
    interp.CmdType(
        name="regenerate",
        cmd_fun=cmd_regenerate,
        position=merc.POS_SLEEPING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
