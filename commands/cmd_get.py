#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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
import handler_item
import instance
import interp
import merc
import state_checks


def cmd_get(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot pick things up while ethereal.\n")
        return

    # Get type.
    if not arg1:
        ch.send("Get what?\n")
        return

    if not arg2:
        if not game_utils.str_cmp(arg1, "all") and not game_utils.str_prefix("all.", arg1):
            # 'get obj'
            item = ch.get_item_list(arg1, ch.in_room.items)
            if not item:
                handler_game.act("I see no $T here.", ch, None, arg1, merc.TO_CHAR)
                return

            handler_item.get_item(ch, item, None)
        else:
            # 'get all' or 'get all.obj'
            found = False
            for item_id in ch.in_room.items:
                item = instance.items[item_id]

                if (len(arg1) == 3 or game_utils.is_name(arg1[4:], item.name)) and ch.can_see_item(item):
                    found = True
                    handler_item.get_item(ch, item, None)

            if not found:
                if len(arg1) == 3:
                    ch.send("I see nothing here.\n")
                else:
                    handler_game.act("I see no $T here.", ch, None, arg1[4:], merc.TO_CHAR)
    else:
        # 'get ... container'
        if game_utils.str_cmp(arg2, "all") or game_utils.str_prefix("all.", arg2):
            ch.send("You can't do that.\n")
            return

        container = ch.get_item_here(arg2)
        if not container:
            handler_game.act("I see no $T here.", ch, None, arg2, merc.TO_CHAR)
            return

        itype = container.item_type
        if itype == merc.ITEM_CORPSE_PC:
            if ch.is_npc():
                ch.send("You can't do that.\n")
                return
        elif itype not in [merc.ITEM_CONTAINER, merc.ITEM_CORPSE_NPC]:
            ch.send("That's not a container.\n")
            return

        if state_checks.is_set(container.value[1], merc.CONT_CLOSED):
            handler_game.act("The $d is closed.", ch, None, container.name, merc.TO_CHAR)
            return

        if not game_utils.str_cmp(arg1, "all") and not game_utils.str_prefix("all.", arg1):
            # 'get obj container'
            item = ch.get_item_list(arg1, container.inventory)
            if not item:
                handler_game.act("I see nothing like that in the $T.", ch, None, arg2, merc.TO_CHAR)
                return

            handler_item.get_item(ch, item, container)
        else:
            # 'get all container' or 'get all.obj container'
            found = False
            for item_id in container.inventory[:]:
                item = instance.items[item_id]

                if (len(arg1) == 3 or game_utils.is_name(arg1[4:], item.name)) and ch.can_see_item(item):
                    found = True
                    handler_item.get_item(ch, item, container)

            if not found:
                if len(arg1) == 3:
                    handler_game.act("I see nothing in the $T.", ch, None, arg2, merc.TO_CHAR)
                else:
                    handler_game.act("I see nothing like that in the $T.", ch, None, arg2, merc.TO_CHAR)
    ch.save(force=True)


interp.register_command(
    interp.CmdType(
        name="get",
        cmd_fun=cmd_get,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="take",
        cmd_fun=cmd_get,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
