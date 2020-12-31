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

import handler_game
import interp
import merc


# noinspection PyUnusedLocal
def cmd_fangs(ch, argument):
    if ch.is_npc():
        return

    if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION):
        if not ch.dempower.is_set(merc.DEM_FANGS):
            ch.send("You haven't been granted the gift of fangs.\n")
            return
    elif ch.is_werewolf():
        if ch.powers[merc.WPOWER_WOLF] < 2:
            ch.huh()
            return
    elif not ch.is_vampire():
        ch.huh()
        return

    if ch.is_vampire() and ch.powers[merc.UNI_RAGE] > 0:
        ch.send("Your beast won't let you retract your fangs.\n")
        return

    ch.vampaff.tog_bit(merc.VAM_FANGS)
    if ch.vampaff.is_set(merc.VAM_FANGS):
        ch.send("Your fangs extend out of your gums.\n")
        handler_game.act("A pair of razor sharp fangs extend from $n's mouth.", ch, None, None, merc.TO_ROOM)
    else:
        ch.send("Your fangs slide back into your gums.\n")
        handler_game.act("$n's fangs slide back into $s gums.", ch, None, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="fangs",
        cmd_fun=cmd_fangs,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
