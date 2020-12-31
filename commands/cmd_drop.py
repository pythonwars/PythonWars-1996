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
import instance
import interp
import merc
import object_creator


def cmd_drop(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Drop what?\n")
        return

    if arg.isdigit():
        # 'drop NNNN coins'
        amount = int(arg)
        argument, arg = game_utils.read_word(argument)

        if amount <= 0 or (not game_utils.str_cmp(arg, ["coins", "coin"])):
            ch.send("Sorry, you can't do that.\n")
            return

        # Otherwise causes complications if there's a pile on each plane
        if ch.is_affected(merc.AFF_SHADOWPLANE):
            ch.send("You cannot drop coins in the shadowplane.\n")
            return

        if ch.gold < amount:
            ch.send("You haven't got that many coins.\n")
            return

        ch.gold -= amount

        for item_id in ch.in_room.items:
            item = instance.items[item_id]

            if item.vnum == merc.OBJ_VNUM_MONEY_ONE:
                amount += 1
                item.extract()
            elif item.vnum == merc.OBJ_VNUM_MONEY_SOME:
                amount += item.value[0]
                item.extract()

        object_creator.create_money(amount).to_room(ch.in_room)
        handler_game.act("$n drops some gold.", ch, None, None, merc.TO_ROOM)
        ch.send("Ok.\n")
        ch.save(force=True)
        return

    if not game_utils.str_cmp(arg, "all") and not game_utils.str_prefix("all.", arg):
        # 'drop obj'
        item = ch.get_item_carry(arg)
        if not item:
            ch.send("You do not have that item.\n")
            return

        if not ch.can_drop_item(item):
            ch.send("You can't let go of it.\n")
            return

        ch.get(item)
        ch.in_room.put(item)

        # Objects should only have a shadowplane flag when on the floor
        if ch.is_affected(merc.AFF_SHADOWPLANE) and not item.flags.shadowplane:
            item.flags.shadowplane = True

        handler_game.act("$n drops $p.", ch, item, None, merc.TO_ROOM)
        handler_game.act("You drop $p.", ch, item, None, merc.TO_CHAR)
    else:
        # 'drop all' or 'drop all.obj'
        found = False
        for item_id in ch.inventory[:]:
            item = instance.items[item_id]

            if (len(arg) == 3 or game_utils.is_name(arg[4:], item.name)) and ch.can_see_item(item) and not item.equipped_to and ch.can_drop_item(item):
                found = True
                ch.get(item)
                ch.in_room.put(item)

                # Objects should only have a shadowplane flag when on the floor
                if ch.is_affected(merc.AFF_SHADOWPLANE) and not item.flags.shadowplane:
                    item.flags.shadowplane = True

                handler_game.act("$n drops $p.", ch, item, None, merc.TO_ROOM)
                handler_game.act("You drop $p.", ch, item, None, merc.TO_CHAR)

        if not found:
            if len(arg) == 3:
                handler_game.act("You are not carrying anything.", ch, None, arg, merc.TO_CHAR)
            else:
                handler_game.act("You are not carrying any $T.", ch, None, arg[4:], merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="drop",
        cmd_fun=cmd_drop,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
