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

import game_utils
import handler_game
import interp
import merc


def cmd_wings(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if not ch.dempower.is_set(merc.DEM_WINGS):
        ch.send("You haven't been granted the gift of wings.\n")
        return

    if arg:
        if not ch.demaff.is_set(merc.DEM_WINGS):
            ch.send("First you better get your wings out!\n")
            return

        if game_utils.str_cmp(arg, ["unfold", "u"]):
            if ch.demaff.is_set(merc.DEM_UNFOLDED):
                ch.send("But your wings are already unfolded!\n")
                return

            ch.send("Your wings unfold from behind your back.\n")
            handler_game.act("$n's wings unfold from behind $s back.", ch, None, None, merc.TO_ROOM)
            ch.demaff.set_bit(merc.DEM_UNFOLDED)
            return

        if game_utils.str_cmp(arg, ["fold", "f"]):
            if not ch.demaff.is_set(merc.DEM_UNFOLDED):
                ch.send("But your wings are already folded!\n")
                return

            ch.send("Your wings fold up behind your back.\n")
            handler_game.act("$n's wings fold up behind $s back.", ch, None, None, merc.TO_ROOM)
            ch.demaff.rem_bit(merc.DEM_UNFOLDED)
            return

        ch.send("Do you want to FOLD or UNFOLD your wings?\n")
        return

    if ch.demaff.is_set(merc.DEM_WINGS):
        if ch.demaff.is_set(merc.DEM_UNFOLDED):
            ch.send("Your wings fold up behind your back.\n")
            handler_game.act("$n's wings fold up behind $s back.", ch, None, None, merc.TO_ROOM)
            ch.demaff.rem_bit(merc.DEM_UNFOLDED)

        ch.send("Your wings slide into your back.\n")
        handler_game.act("$n's wings slide into $s back.", ch, None, None, merc.TO_ROOM)
        ch.demaff.rem_bit(merc.DEM_WINGS)
        return

    ch.send("Your wings extend from your back.\n")
    handler_game.act("A pair of wings extend from $n's back.", ch, None, None, merc.TO_ROOM)
    ch.demaff.set_bit(merc.DEM_WINGS)


interp.register_command(
    interp.CmdType(
        name="wings",
        cmd_fun=cmd_wings,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
