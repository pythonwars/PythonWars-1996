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

import handler_game
import interp
import merc


# noinspection PyUnusedLocal
def cmd_flex(ch, argument):
    handler_game.act("You flex your bulging muscles.", ch, None, None, merc.TO_CHAR)
    handler_game.act("$n flexes $s bulging muscles.", ch, None, None, merc.TO_ROOM)

    if ch.is_npc():
        return

    if (ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION)) and not ch.dempower.is_set(merc.DEM_MIGHT):
        return
    elif not ch.is_werewolf() or ch.powers[merc.WPOWER_BEAR] < 1:
        return

    if ch.extra.is_set(merc.EXTRA_TIED_UP):
        handler_game.act("The ropes restraining you snap.", ch, None, None, merc.TO_CHAR)
        handler_game.act("The ropes restraining $n snap.", ch, None, None, merc.TO_ROOM)
        ch.extra.rem_bit(merc.EXTRA_TIED_UP)

    if ch.is_affected("web") or ch.is_affected(merc.AFF_WEBBED):
        handler_game.act("The webbing entrapping $n breaks away.", ch, None, None, merc.TO_ROOM)
        ch.send("The webbing entrapping you breaks away.\n")
        ch.affect_strip("web")
        ch.affected_by.rem_bit(merc.AFF_WEBBED)

    ch.wait_state(merc.PULSE_VIOLENCE)


interp.register_command(
    interp.CmdType(
        name="flex",
        cmd_fun=cmd_flex,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
