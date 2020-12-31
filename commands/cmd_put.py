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
import state_checks


def cmd_put(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Put what in what?\n")
        return

    if game_utils.str_cmp(arg2, "all") or game_utils.str_prefix("all.", arg2):
        ch.send("You can't do that.\n")
        return

    container = ch.get_item_here(arg2)
    if not container:
        handler_game.act("I see no $T here.", ch, None, arg2, merc.TO_CHAR)
        return

    if container.item_type != merc.ITEM_CONTAINER:
        ch.send("That's not a container.\n")
        return

    if state_checks.is_set(container.value[1], merc.CONT_CLOSED):
        handler_game.act("The $d is closed.", ch, None, container.name, merc.TO_CHAR)
        return

    if not game_utils.str_cmp(arg1, "all") and not game_utils.str_prefix("all.", arg1):
        # 'put obj container'
        item = ch.get_item_carry(arg1)
        if not item:
            ch.send("You do not have that item.\n")
            return

        if item == container:
            ch.send("You can't fold it into itself.\n")
            return

        if item.flags.artifact:
            ch.send("You cannot put artifacts in a container.\n")
            return

        if not ch.can_drop_item(item):
            ch.send("You can't let go of it.\n")
            return

        if item.get_weight() + container.get_weight() > container.value[0]:
            ch.send("It won't fit.\n")
            return

        for item2_id in container.inventory[:]:
            item2 = instance.items[item2_id]

            if item2.chobj and item != item2:
                handler_game.act("A hand reaches inside $P and drops $p.", item2.chobj, item, container, merc.TO_CHAR)

        ch.get(item)
        container.put(item)
        handler_game.act("$n puts $p in $P.", ch, item, container, merc.TO_ROOM)
        handler_game.act("You put $p in $P.", ch, item, container, merc.TO_CHAR)
    else:
        objroom = instance.rooms[merc.ROOM_VNUM_IN_OBJECT]

        # 'put all container' or 'put all.obj container'
        for item in ch.inventory[:]:
            if (len(arg1) == 3 or game_utils.is_name(arg1[4:], item.name)) and ch.can_see_item(item) and not item.equipped_to and \
                    item != container and not item.flags.artifact and ch.can_drop_item(item) and \
                    item.get_weight() + container.true_weight() <= container.value[0]:
                for item2 in container.inventory[:]:
                    if item2.chobj and item2.chobj.in_room:
                        if objroom != instance.rooms[item2.chobj.in_room.vnum]:
                            item2.chobj.in_room.get(item2.chobj)
                            objroom.put(item2.chobj)
                            item2.chobj.cmd_look("auto")

                        if item != item2:
                            handler_game.act("A hand reaches inside $P and drops $p.", item2.chobj, item, container, merc.TO_CHAR)

                ch.get(item)
                container.put(item)
                handler_game.act("$n puts $p in $P.", ch, item, container, merc.TO_ROOM)
                handler_game.act("You put $p in $P.", ch, item, container, merc.TO_CHAR)

    ch.save(force=True)


interp.register_command(
    interp.CmdType(
        name="put",
        cmd_fun=cmd_put,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
