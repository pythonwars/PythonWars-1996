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
import nanny


def call_all(ch):
    found = False

    for item in list(instance.items.values()):
        if not item.questowner or not game_utils.str_cmp(ch.name, item.questowner) or item.item_type == merc.ITEM_PAGE:
            continue

        found = True
        in_item = item
        while in_item.in_item:
            in_item = in_item.in_item

        if in_item.in_living and in_item.in_living == ch:
            continue

        if item.in_living and item.in_living != ch:
            handler_game.act("$p suddenly vanishes from your hands!", item.in_living, item, None, merc.TO_CHAR)
            handler_game.act("$p suddenly vanishes from $n's hands!", item.in_living, item, None, merc.TO_ROOM)
            item.in_living.extra.set_bit(merc.EXTRA_CALL_ALL)
            item.get(item)
        elif item.in_room:
            charroom = ch.in_room
            itemroom = item.in_room
            ch.in_room.get(ch)
            itemroom.put(ch)
            handler_game.act("$p vanishes from the ground!", ch, item, None, merc.TO_ROOM)

            if charroom == itemroom:
                handler_game.act("$p vanishes from the ground!", ch, item, None, merc.TO_CHAR)

            ch.in_room.get(ch)
            charroom.put(ch)
            ch.in_room.get(item)
        elif item.in_item:
            item.in_item.get(item)
        else:
            continue

        ch.put(item)
        item.flags.shadowplane = False

        if not ch.head.is_set(merc.LOST_HEAD):
            handler_game.act("$p materializes in your hands.", ch, item, None, merc.TO_CHAR)
            handler_game.act("$p materializes in $n's hands.", ch, item, None, merc.TO_ROOM)

    if not found and not ch.head.is_set(merc.LOST_HEAD):
        ch.send("Nothing happens.\n")

    for d in instance.descriptor_list:
        if d.is_connected(nanny.con_playing) and d.character:
            if d.character.is_npc() or (ch != d.character and not d.character.extra.is_set(merc.EXTRA_CALL_ALL)):
                continue

            d.character.extra.rem_bit(merc.EXTRA_CALL_ALL)
            d.character.save(force=True)


def cmd_call(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not arg:
        ch.send("What object do you wish to call?\n")
        return

    if not ch.head.is_set(merc.LOST_HEAD):
        handler_game.act("Your eyes flicker with yellow energy.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n's eyes flicker with yellow energy.", ch, None, None, merc.TO_ROOM)

    if game_utils.str_cmp(arg, "all"):
        call_all(ch)
        return

    item = ch.get_item_world(arg)
    if not item:
        ch.send("Nothing like that in hell, earth, or heaven.\n")
        return

    if not item.questowner or not game_utils.str_cmp(item.questowner, ch.name) or item.item_type == merc.ITEM_PAGE:
        ch.send("Nothing happens.\n")
        return

    victim = None
    if item.in_living and item.in_living != ch:
        victim = item.in_living
        handler_game.act("$p suddenly vanishes from your hands!", victim, item, None, merc.TO_CHAR)
        handler_game.act("$p suddenly vanishes from $n's hands!", victim, item, None, merc.TO_ROOM)
        victim.get(item)
    elif item.in_room:
        charroom = ch.in_room
        itemroom = item.in_room
        ch.in_room.get(ch)
        itemroom.put(ch)
        handler_game.act("$p vanishes from the ground!", ch, item, None, merc.TO_ROOM)

        if charroom == itemroom:
            handler_game.act("$p vanishes from the ground!", ch, item, None, merc.TO_CHAR)

        ch.in_room.get(ch)
        charroom.put(ch)
        item.in_room.get(item)
    elif item.in_item:
        item.in_item.get(item)
    else:
        if not ch.head.is_set(merc.LOST_HEAD):
            ch.send("Nothing happens.\n")
        return

    ch.put(item)
    item.flags.shadowplane = False
    handler_game.act("$p materializes in your hands.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p materializes in $n's hands.", ch, item, None, merc.TO_ROOM)
    ch.save(force=True)

    if victim:
        victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="call",
        cmd_fun=cmd_call,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
