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

import game_utils
import handler_game
import interp
import merc


def sheath(ch, right_hand):
    hand = "right" if right_hand else "left"
    scabbard = "right_scabbard" if right_hand else "left_scabbard"
    scabbard = ch.get_eq(scabbard)
    if scabbard:
        handler_game.act("You already have $p in your $T scabbard.", ch, scabbard, hand, merc.TO_CHAR)
        return

    item = "right_hand" if right_hand else "left_hand"
    item = ch.get_eq(item)
    if not item:
        ch.send("You are not holding anything in your {} hand.\n".format(hand))
        return

    if item.item_type != merc.ITEM_WEAPON:
        handler_game.act("$p is not a weapon.", ch, item, None, merc.TO_CHAR)
        return

    handler_game.act("You slide $p into your $T scabbard.", ch, item, hand, merc.TO_CHAR)
    handler_game.act("$n slides $p into $s $T scabbard.", ch, item, hand, merc.TO_ROOM)
    ch.unequip(item.equipped_to, silent=True, forced=True)
    ch.equip(item, replace=False, verbose=False, to_loc="right_scabbard" if right_hand else "left_scabbard")


def cmd_sheath(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Which hand, left or right?\n")
    elif game_utils.str_cmp(arg, ["all", "both"]):
        sheath(ch, right_hand=True)
        sheath(ch, right_hand=False)
    elif game_utils.str_cmp(arg, ["l", "left"]):
        sheath(ch, right_hand=False)
    elif game_utils.str_cmp(arg, ["r", "right"]):
        sheath(ch, right_hand=True)
    else:
        ch.send("Which hand, left or right?\n")


interp.register_command(
    interp.CmdType(
        name="sheath",
        cmd_fun=cmd_sheath,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
