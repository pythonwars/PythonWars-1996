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

import collections

import comm
import game_utils
import handler_room
import instance
import interp
import merc
import shop_utils


def cmd_list(ch, argument):
    argument, arg = game_utils.read_word(argument)

    buf = []
    if ch.in_room.room_flags.is_set(merc.ROOM_PET_SHOP):
        proomindexnext = None
        if ch.in_room.vnum + 1 in instance.room_templates:
            proomindexnext = handler_room.get_room_by_vnum(ch.in_room.vnum + 1)
        if not proomindexnext:
            comm.notify("cmd_list: bad pet shop at vnum {}".format(ch.in_room.vnum), merc.CONSOLE_ERROR)
            ch.send("You can't do that here.\n")
            return

        found = False
        for pet_id in proomindexnext.people[:]:
            pet = instance.characters[pet_id]

            if pet.act.is_set(merc.ACT_PET):
                if not found:
                    found = True
                    buf = "Pets for sale:\n"

                buf += "[{:2}] {:8} - {}\n".format(pet.level, 10 * pet.level * pet.level, pet.short_descr)

        if not found:
            buf += "Sorry, we're out of pets right now.\n"
        ch.send("".join(buf))
        return

    keeper = shop_utils.find_keeper(ch)
    if not keeper:
        return

    items = collections.OrderedDict()
    for item_id in keeper.inventory[:]:
        item = instance.items[item_id]
        cost = shop_utils.get_cost(keeper, item, True)

        if not item.equipped_to and ch.can_see_item(item) and cost > 0 and (not arg or not game_utils.str_prefix(arg, item.name)):
            if item.inventory:
                items[(item.vnum, item.short_descr)] = (item.vnum, -1)
            else:
                k = (item.vnum, item.short_descr)
                if k not in items:
                    items[k] = (item, 1)
                else:
                    items[k][1] += 1

    if not items:
        if not arg:
            buf += "You can't buy anything here.\n"
        else:
            buf += "You can't buy that here.\n"

    buf += "[Lv Price] Item\n"

    for k, p in items.items():
        item, count = p
        cost = shop_utils.get_cost(keeper, item, True)
        buf += "[{:2} {:5}] {}\n".format(item.level, cost, item.short_descr.capitalize())
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="list",
        cmd_fun=cmd_list,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
