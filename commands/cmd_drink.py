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

import comm
import const
import game_utils
import handler_game
import instance
import interp
import merc


def cmd_drink(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        item = None
        for obj_id in ch.in_room.items:
            obj = instance.items[obj_id]
            if obj.item_type == merc.ITEM_FOUNTAIN:
                item = obj
                break

        if not item:
            ch.send("Drink what?\n")
            return
    else:
        item = ch.get_item_here(arg)
        if not item:
            ch.send("You can't find it.\n")
            return

    if item.item_type == merc.ITEM_POTION:
        ch.cmd_quaff(item.name)
        return
    elif item.item_type == merc.ITEM_FOUNTAIN:
        liquid = item.value[2]
        if liquid < 0:
            comm.notify("cmd_drink: bad liquid number {}".format(liquid), merc.CONSOLE_WARNING)
            liquid = item.value[2] = 0

        if ch.is_affected(merc.AFF_SHADOWPLANE) and item.in_room and not item.flags.shadowplane:
            ch.send("You are too insubstantual.\n")
            return
        elif not ch.is_affected(merc.AFF_SHADOWPLANE) and item.in_room and item.flags.shadowplane:
            ch.send("It is too insubstantual.\n")
            return

        if ch.is_affected(merc.AFF_ETHEREAL):
            ch.send("You can only drink from things you are carrying while ethereal.\n")
            return

        if liquid != 13 and ch.is_vampire():
            ch.send("You can only drink blood.\n")
            return

        handler_game.act("$n drinks $T from $p.", ch, item, const.liq_table[liquid].name, merc.TO_ROOM)
        handler_game.act("You drink $T from $p.", ch, item, const.liq_table[liquid].name, merc.TO_CHAR)
        amount = game_utils.number_range(3, 10)
        amount = min(amount, item.value[1])

        if item.value[3] != 0 and (not ch.is_npc() and not ch.is_vampire()):
            # The shit was poisoned!

            handler_game.act("$n chokes and gags.", ch, None, None, merc.TO_ROOM)
            ch.send("You choke and gag.\n")
            aff = handler_game.AffectData(type="poison", duration=amount * 3, location=merc.APPLY_NONE, bitvector=merc.AFF_POISON)
            ch.affect_join(aff)
    elif item.item_type == merc.ITEM_DRINK_CON:
        if item.value[1] <= 0:
            ch.send("It is already empty.\n")
            return

        liquid = item.value[2]
        if liquid < 0:
            comm.notify("cmd_drink: bad liquid number {}".format(liquid), merc.CONSOLE_WARNING)
            liquid = item.value[2] = 0

        if liquid != 13 and ch.is_vampire():
            ch.send("You can only drink blood.\n")
            return

        handler_game.act("$n drinks $T from $p.", ch, item, const.liq_table[liquid].name, merc.TO_ROOM)
        handler_game.act("You drink $T from $p.", ch, item, const.liq_table[liquid].name, merc.TO_CHAR)
        amount = game_utils.number_range(3, 10)
        amount = min(amount, item.value[1])

        if item.value[3] != 0 and (not ch.is_npc() and not ch.is_vampire()):
            # The shit was poisoned!
            handler_game.act("$n chokes and gags.", ch, None, None, merc.TO_ROOM)
            ch.send("You choke and gag.\n")
            aff = handler_game.AffectData(type="poison", duration=amount * 3, location=merc.APPLY_NONE, bitvector=merc.AFF_POISON)
            ch.affect_join(aff)

        item.value[1] -= amount
        if item.value[1] <= 0:
            item.value[1] = 0
    else:
        ch.send("You can't drink from that.\n")


interp.register_command(
    interp.CmdType(
        name="drink",
        cmd_fun=cmd_drink,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
