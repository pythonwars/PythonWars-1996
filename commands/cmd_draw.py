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


def draw(ch, right_hand):
    hand = "right" if right_hand else "left"
    item = "right_hand" if right_hand else "left_hand"
    item = ch.get_eq(item)
    if item:
        handler_game.act("You already have $p in your $T hand.", ch, item, hand, merc.TO_CHAR)
        return

    scabbard = "right_scabbard" if right_hand else "left_scabbard"
    scabbard = ch.get_eq(scabbard)
    if not scabbard:
        ch.send(f"Your {hand} scabbard is empty.\n")
        return

    handler_game.act("You draw $p from your left scabbard.", ch, scabbard, None, merc.TO_CHAR)
    handler_game.act("$n draws $p from $s left scabbard.", ch, scabbard, None, merc.TO_ROOM)
    ch.unequip(scabbard.equipped_to, silent=True, forced=True)
    ch.equip(scabbard, replace=False, verbose=False, to_loc="right_hand" if right_hand else "left_hand")


def cmd_draw(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not ch.is_npc() and ch.special.is_set(merc.SPC_WOLFMAN):
        ch.send("Not in this form.\n")
        return

    if not arg:
        ch.send("Which hand, left or right?\n")
    elif game_utils.str_cmp(arg, ["all", "both"]):
        draw(ch, right_hand=True)
        draw(ch, right_hand=False)
    elif game_utils.str_cmp(arg, ["l", "left"]):
        draw(ch, right_hand=False)
    elif game_utils.str_cmp(arg, ["r", "right"]):
        draw(ch, right_hand=True)
    else:
        ch.send("Which hand, left or right?\n")


interp.register_command(
    interp.CmdType(
        name="draw",
        cmd_fun=cmd_draw,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
