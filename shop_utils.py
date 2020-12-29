#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
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
import instance
import merc


def get_cost(keeper, item, fbuy):
    pshop = instance.npc_templates[keeper.vnum].pshop
    if not item or not pshop:
        return 0

    if fbuy:
        cost = item.cost * pshop.profit_buy // 100
    else:
        cost = 0
        for itype in pshop.buy_type:
            if item.item_type == itype:
                cost = item.cost * pshop.profit_sell // 100
                break

        for item2_id in keeper.inventory[:]:
            item2 = instance.items[item2_id]
            if item == item2:
                cost = 0
                break

    if item.item_type in [merc.ITEM_STAFF, merc.ITEM_WAND]:
        cost = cost * item.value[2] // item.value[1]
    return cost


# Shopping commands.
def find_keeper(ch):
    pshop = None
    keeper = None
    for gch_id in ch.in_room.people[:]:
        gch = instance.characters[gch_id]

        if gch.is_npc():
            keeper_template = instance.npc_templates[gch.vnum]
            if keeper_template.pshop:
                pshop = keeper_template.pshop
                keeper = gch
                break

    if not pshop or not keeper:
        ch.send("You can't do that here.\n")
        return None

    # Shop hours.
    if handler_game.time_info.hour < pshop.open_hour:
        keeper.cmd_say("Sorry, come back later.")
        return None

    if handler_game.time_info.hour > pshop.close_hour:
        keeper.cmd_say("Sorry, come back tomorrow.")
        return None

    # Invisible or hidden people.
    if not keeper.can_see(ch):
        keeper.cmd_say("I don't trade with folks I can't see.")
        return None
    return keeper
