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
import shop_utils


def cmd_value(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Value what?\n")
        return

    keeper = shop_utils.find_keeper(ch)
    if not keeper:
        return

    item = ch.get_item_carry(arg)
    if not item:
        handler_game.act("$n tells you 'You don't have that item'.", keeper, None, ch, merc.TO_VICT)
        ch.reply = keeper
        return

    if not ch.can_drop_item(item):
        ch.send("You can't let go of it.\n")
        return

    cost = shop_utils.get_cost(keeper, item, False)
    if cost <= 0:
        handler_game.act("$n looks uninterested in $p.", keeper, item, ch, merc.TO_VICT)
        return

    handler_game.act(f"$n tells you 'I'll give you {cost:,} gold coins for $p'.", keeper, item, ch, merc.TO_VICT)
    ch.reply = keeper


interp.register_command(
    interp.CmdType(
        name="value",
        cmd_fun=cmd_value,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
