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
import state_checks


def cmd_turn(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Syntax: Turn <book> <forward/back>\n")
        return

    item = ch.get_item_here(arg1)
    if not item:
        ch.send("You don't have that book.\n")
        return

    if item.item_type != merc.ITEM_BOOK:
        ch.send("That's not a book.\n")
        return

    if state_checks.is_set(item.value[1], merc.CONT_CLOSED):
        ch.send("First you should open it.\n")
        return

    value = int(arg2) if arg2.isdigit() else 0

    if game_utils.str_cmp(arg2, ["f", "forward"]):
        if item.value[2] >= item.value[3]:
            ch.send("But you are already at the end of the book.\n")
            return

        item.value[2] += 1
        handler_game.act("You flip forward a page in $p.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$n flips forward a page in $p.", ch, item, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg2, ["b", "backward"]):
        if item.value[2] <= 0:
            ch.send("But you are already at the beginning of the book.\n")
            return

        item.value[2] -= 1
        handler_game.act("You flip backward a page in $p.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$n flips backward a page in $p.", ch, item, None, merc.TO_ROOM)
    elif arg2.isdigit() and value in merc.irange(0, item.value[3]):
        if value == item.value[2]:
            handler_game.act("$p is already open at that page.", ch, item, None, merc.TO_CHAR)
            return

        if value < item.value[2]:
            handler_game.act("You flip backwards through $p.", ch, item, None, merc.TO_CHAR)
            handler_game.act("$n flips backwards through $p.", ch, item, None, merc.TO_ROOM)
        else:
            handler_game.act("You flip forwards through $p.", ch, item, None, merc.TO_CHAR)
            handler_game.act("$n flips forwards through $p.", ch, item, None, merc.TO_ROOM)
        item.value[2] = value
    else:
        ch.send("Do you wish to turn forward or backward a page?\n")


interp.register_command(
    interp.CmdType(
        name="turn",
        cmd_fun=cmd_turn,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
