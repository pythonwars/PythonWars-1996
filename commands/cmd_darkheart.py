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

import fight
import game_utils
import handler_game
import interp
import merc
import object_creator


# noinspection PyUnusedLocal
def cmd_darkheart(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_SERPENTIS):
        ch.send("You are not trained in the Serpentis discipline.\n")
        return

    if ch.immune.is_set(merc.IMM_STAKE):
        ch.send("But you've already torn your heart out!\n")
        return

    if ch.blood < 100:
        ch.send("You have insufficient blood.\n")
        return

    ch.blood -= 100
    ch.send("You rip your heart from your body and toss it to the ground.\n")
    handler_game.act("$n rips $s heart out and tosses it to the ground.", ch, None, None, merc.TO_ROOM)
    object_creator.make_part(ch, "heart")
    ch.hit -= game_utils.number_range(10, 20)
    fight.update_pos(ch)

    if ch.position == merc.POS_DEAD and not ch.is_hero():
        ch.send("You have been KILLED!!\n\n")
        fight.raw_kill(ch)
        return

    ch.immune.set_bit(merc.IMM_STAKE)


interp.register_command(
    interp.CmdType(
        name="darkheart",
        cmd_fun=cmd_darkheart,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
