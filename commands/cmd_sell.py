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


def cmd_sell(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Sell what?\n")
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

    handler_game.act("$n sells $p.", ch, item, None, merc.TO_ROOM)
    handler_game.act("You sell $p for {:,} gold piece{}.".format(cost, "" if cost == 1 else "s"), ch, item, None, merc.TO_CHAR)
    ch.gold += cost
    keeper.gold -= cost
    if keeper.gold < 0:
        keeper.gold = 0

    if item.item_type == merc.ITEM_TRASH:
        item.extract()
    else:
        ch.get(item)
        keeper.put(item)


interp.register_command(
    interp.CmdType(
        name="sell",
        cmd_fun=cmd_sell,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
