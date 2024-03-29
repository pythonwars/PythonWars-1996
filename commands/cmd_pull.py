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
import handler_magic
import instance
import interp
import merc
import object_creator
import state_checks


def cmd_pull(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        ch.send("Which item do you wish to pull?\n")
        return

    item = ch.get_item_wear(arg1)
    if not item:
        item = ch.get_item_here(arg1)
        if not item:
            ch.send("You can't find that item.\n")
            return

        # You should only be able to use nontake items on floor
        if item.flags.take:
            ch.send("But you are not wearing it!\n")
            return

    if not item.spectype.is_set(merc.SITEM_PULL):
        ch.send("This item cannot be pulled.\n")
        return

    if item.spectype.is_set(merc.SITEM_TARGET) and not arg2:
        ch.send("Who do you wish to use it on?\n")
        return

    if item.spectype.is_set(merc.SITEM_TARGET):
        victim = ch.get_char_room(arg2)
        if not victim:
            ch.not_here(arg2)
            return
    else:
        victim = ch

    if item.chpoweruse:
        handler_game.kavitem(item.chpoweruse, ch, item, None, merc.TO_CHAR)

    if item.victpoweruse:
        handler_game.kavitem(item.victpoweruse, ch, item, None, merc.TO_ROOM)

    if item.spectype.is_set(merc.SITEM_SPELL):
        castlevel = state_checks.urange(1, item.level, 60)
        handler_magic.obj_cast_spell(item.specpower, castlevel, ch, victim, None)
        ch.wait_state(merc.PULSE_VIOLENCE // 2)

        if item.spectype.is_set(merc.SITEM_DELAY1):
            ch.wait_state(merc.PULSE_VIOLENCE // 2)

        if item.spectype.is_set(merc.SITEM_DELAY2):
            ch.wait_state(merc.PULSE_VIOLENCE)
        return

    if item.spectype.is_set(merc.SITEM_TRANSPORTER):
        if item.chpoweron:
            handler_game.kavitem(item.chpoweron, ch, item, None, merc.TO_CHAR)

        if item.victpoweron:
            handler_game.kavitem(item.victpoweron, ch, item, None, merc.TO_ROOM)

        proomindex = instance.rooms[item.specpower]
        item.specpower = ch.in_room.vnum
        if not proomindex:
            return

        ch.in_room.get(ch)
        proomindex.put(ch)
        ch.cmd_look("auto")

        if item.chpoweroff:
            handler_game.kavitem(item.chpoweroff, ch, item, None, merc.TO_CHAR)

        if item.victpoweroff:
            handler_game.kavitem(item.victpoweroff, ch, item, None, merc.TO_ROOM)

        if not item.flags.artifact and ch.in_room.room_flags.is_set(merc.ROOM_NO_TELEPORT) and item.flags.take:
            ch.send("A powerful force hurls you from the room.\n")
            handler_game.act("$n is hurled from the room by a powerful force.", ch, None, None, merc.TO_ROOM)
            ch.position = merc.POS_STUNNED
            ch.in_room.get(ch)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_TEMPLE][0]
            instance.rooms[room_id].put(ch)
            handler_game.act("$n appears in the room, and falls to the ground stunned.", ch, None, None, merc.TO_ROOM)

        mount = ch.mount
        if mount:
            mount.in_room.get(mount)
            ch.in_room.put(mount)
            mount.cmd_look("auto")
    elif item.spectype.is_set(merc.SITEM_TELEPORTER):
        if item.chpoweron:
            handler_game.kavitem(item.chpoweron, ch, item, None, merc.TO_CHAR)

        if item.victpoweron:
            handler_game.kavitem(item.victpoweron, ch, item, None, merc.TO_ROOM)

        proomindex = instance.rooms[item.specpower]
        if not proomindex:
            return

        ch.in_room.get(ch)
        proomindex.put(ch)
        ch.cmd_look("auto")

        if item.chpoweroff:
            handler_game.kavitem(item.chpoweroff, ch, item, None, merc.TO_CHAR)

        if item.victpoweroff:
            handler_game.kavitem(item.victpoweroff, ch, item, None, merc.TO_ROOM)

        if not item.flags.artifact and ch.in_room.room_flags.is_set(merc.ROOM_NO_TELEPORT) and item.flags.take:
            ch.send("A powerful force hurls you from the room.\n")
            handler_game.act("$n is hurled from the room by a powerful force.", ch, None, None, merc.TO_ROOM)
            ch.position = merc.POS_STUNNED
            ch.in_room.get(ch)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_TEMPLE][0]
            instance.rooms[room_id].put(ch)
            handler_game.act("$n appears in the room, and falls to the ground stunned.", ch, None, None, merc.TO_ROOM)

        mount = ch.mount
        if mount:
            mount.in_room.get(mount)
            ch.in_room.put(mount)
            mount.cmd_look("auto")
    elif item.spectype.is_set(merc.SITEM_OBJECT):
        if item.specpower not in instance.item_templates:
            return

        item2 = object_creator.create_item(instance.item_templates[item.specpower], ch.level)
        if item2.flags.take:
            ch.put(item2)
        else:
            ch.in_room.put(item2)
    elif item.spectype.is_set(merc.SITEM_MOBILE):
        if item.specpower not in instance.npc_templates:
            return

        npc = object_creator.create_mobile(instance.npc_templates[item.specpower])
        ch.in_room.put(npc)
    elif item.spectype.is_set(merc.SITEM_ACTION):
        ch.interpret(item.victpoweron)

        if item.victpoweroff:
            for vch_id in ch.in_room.people[:]:
                vch = instance.characters[vch_id]

                if ch == vch:
                    continue

                vch.interpret(item.victpoweroff)
                continue


interp.register_command(
    interp.CmdType(
        name="pull",
        cmd_fun=cmd_pull,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
