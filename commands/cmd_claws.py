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
def cmd_claws(ch, argument):
    if ch.is_npc():
        return

    if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION):
        if not ch.dempower.is_set(merc.DEM_CLAWS):
            ch.send("You haven't been granted the gift of claws.\n")
            return
    elif ch.is_werewolf() and ch.powers[merc.WPOWER_WOLF] < 1:
        ch.huh()
        return
    elif not ch.is_vampire():
        ch.huh()
        return

    if ch.is_vampire():
        if not ch.vampaff.is_set(merc.VAM_PROTEAN):
            ch.send("You are not trained in the Protean discipline.\n")
            return

        if ch.powers[merc.UNI_RAGE] > 0:
            ch.send("Your beast won't let you retract your claws.\n")
            return

    if ch.vampaff.is_set(merc.VAM_CLAWS):
        if ch.is_werewolf():
            ch.send("Your claws slide back under your nails.\n")
            handler_game.act("$n's claws slide back under $s nails.", ch, None, None, merc.TO_ROOM)
        else:
            ch.send("Your talons slide back into your fingers.\n")
            handler_game.act("$n's talons slide back into $s fingers.", ch, None, None, merc.TO_ROOM)
        ch.vampaff.rem_bit(merc.VAM_CLAWS)
        return

    if ch.is_werewolf():
        ch.send("Sharp claws extend from under your finger nails.\n")
        handler_game.act("Sharp claws extend from under $n's finger nails.", ch, None, None, merc.TO_ROOM)
    else:
        ch.send("Razor sharp talons extend from your fingers.\n")
        handler_game.act("Razor sharp talons extend from $n's fingers.", ch, None, None, merc.TO_ROOM)
    ch.vampaff.set_bit(merc.VAM_CLAWS)


interp.register_command(
    interp.CmdType(
        name="claws",
        cmd_fun=cmd_claws,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
