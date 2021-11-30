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


def cmd_leap(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if not ch.dempower.is_set(merc.DEM_LEAP):
        ch.send("You haven't been granted the gift of leaping.\n")
        return

    item = ch.chobj
    if not item:
        ch.huh()
        return

    if not item.chobj or item.chobj != ch:
        ch.huh()
        return

    if item.in_room and not arg:
        ch.send("Where do you want to leap?\n")
        return

    if item.in_room:
        victim = ch.get_char_room(arg)
        if victim:
            handler_game.act("$p leaps into your hands.", victim, item, None, merc.TO_CHAR)
            handler_game.act("$p leaps into $n's hands.", victim, item, None, merc.TO_ROOM)
            item.in_room.get(item)
            victim.put(item)
        else:
            container = ch.get_item_room(arg)
            if container:
                if container.item_type not in [merc.ITEM_CONTAINER, merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC]:
                    ch.send("You cannot leap into that sort of object.\n")
                    return

                handler_game.act("$p leap into $P.", ch, item, container, merc.TO_CHAR)
                handler_game.act("$p leaps into $P.", ch, item, container, merc.TO_ROOM)
                item.in_room.get(item)
                container.put(item)
            else:
                ch.send("Nothing here by that name.\n")
        return

    if item.in_living:
        handler_game.act("$p leaps from your hands.", item.in_living, item, None, merc.TO_CHAR)
        handler_game.act("$p leaps from $n's hands.", item.in_living, item, None, merc.TO_ROOM)
        item.in_living.get(item)
        ch.in_room.put(item)
        return
    else:
        container = item.in_item
        if container and container.in_room:
            container.get(item)
            container.in_room.put(item)
            ch.in_room.get(ch)
            container.in_room.put(ch)
            handler_game.act("$p leap from $P.", ch, item, container, merc.TO_CHAR)
            handler_game.act("$p leaps from $P.", ch, item, container, merc.TO_ROOM)
            return

        if item.in_room:
            ch.send("You seem unable to leap anywhere.\n")
        else:
            ch.send("You seem to be stuck!\n")


interp.register_command(
    interp.CmdType(
        name="leap",
        cmd_fun=cmd_leap,
        position=merc.POS_RESTING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
