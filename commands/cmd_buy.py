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
import game_utils
import handler_game
import handler_room
import instance
import interp
import merc
import object_creator
import shop_utils


def cmd_buy(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Buy what?\n")
        return

    if ch.in_room.room_flags.is_set(merc.ROOM_PET_SHOP):
        if ch.is_npc():
            return

        proomindexnext = None
        if ch.in_room.vnum + 1 in instance.room_templates:
            proomindexnext = handler_room.get_room_by_vnum(ch.in_room.vnum + 1)
        if not proomindexnext:
            comm.notify(f"cmd_buy: bad pet shop at vnum {ch.in_room.vnum}", merc.CONSOLE_ERROR)
            ch.send("Sorry, you can't buy that here.\n")
            return

        in_room = ch.in_room
        ch.in_room = proomindexnext
        pet = ch.get_char_room(arg)
        ch.in_room = in_room

        if not pet or not pet.act.is_set(merc.ACT_PET):
            ch.send("Sorry, you can't buy that here.\n")
            return

        if ch.gold < 10 * pet.level * pet.level:
            ch.send("You can't afford it.\n")
            return

        if ch.level < pet.level:
            ch.send("You're not ready for this pet.\n")
            return

        ch.gold -= 10 * pet.level * pet.level
        pet = object_creator.create_mobile(instance.npc_templates[pet.vnum])
        pet.act.set_bit(merc.ACT_PET)
        pet.affected_by.set_bit(merc.AFF_CHARM)

        argument, arg = game_utils.read_word(argument)
        if arg:
            pet.name = f"{pet.name} {arg}"

        pet.description = f"{pet.description}A neck tag says 'I belong to {ch.name}'.\n"
        ch.in_room.put(pet)
        pet.add_follower(ch)
        ch.send("Enjoy your pet.\n")
        handler_game.act("$n bought $N as a pet.", ch, None, pet, merc.TO_ROOM)
    else:
        keeper = shop_utils.find_keeper(ch)
        if not keeper:
            return

        item = keeper.get_item_carry(arg)
        cost = shop_utils.get_cost(keeper, item, True)
        if cost <= 0 or not ch.can_see_item(item):
            handler_game.act("$n tells you 'I don't sell that -- try 'list''.", keeper, None, ch, merc.TO_VICT)
            ch.reply = keeper
            return

        if ch.gold < cost:
            handler_game.act("$n tells you 'You can't afford to buy $p'.", keeper, item, ch, merc.TO_VICT)
            ch.reply = keeper
            return

        if item.level > ch.level and ch.level < 3:
            handler_game.act("$n tells you 'You can't use $p yet'.", keeper, item, ch, merc.TO_VICT)
            ch.reply = keeper
            return

        if ch.carry_number + 1 > ch.can_carry_n():
            ch.send("You can't carry that many items.\n")
            return

        if ch.carry_weight + item.get_weight() > ch.can_carry_w():
            ch.send("You can't carry that much weight.\n")
            return

        handler_game.act("$n buys $p.", ch, item, None, merc.TO_ROOM)
        handler_game.act("You buy $p.", ch, item, None, merc.TO_CHAR)
        ch.gold -= cost
        keeper.gold += cost

        if item.flags.inventory:
            item = object_creator.create_item(instance.item_templates[item.vnum], item.level)
        else:
            item.in_living.get(item)
        ch.put(item)


interp.register_command(
    interp.CmdType(
        name="buy",
        cmd_fun=cmd_buy,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
