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

import const
import game_utils
import handler_ch
import handler_game
import instance
import interp
import merc
import state_checks


def cmd_look(ch, argument):
    wizard = ch.wizard
    if not ch.desc and not wizard:
        return

    if ch.position < merc.POS_SLEEPING:
        ch.send("You can't see anything but stars!\n")
        return

    if ch.position == merc.POS_SLEEPING:
        ch.send("You can't see anything, you're sleeping!\n")
        return

    if ch.check_blind():
        return

    if not ch.is_npc() and ch.in_room.room_flags.is_set(merc.ROOM_TOTAL_DARKNESS) and not ch.itemaff.is_set(merc.ITEMA_VISION) and \
            not ch.is_affected(merc.AFF_SHADOWSIGHT) and not ch.is_immortal():
        ch.send("It is pitch black ...\n")
        return

    if not ch.is_npc() and not ch.act.is_set(merc.PLR_HOLYLIGHT) and not ch.itemaff.is_set(merc.ITEMA_VISION) and \
            not ch.vampaff.is_set(merc.VAM_NIGHTSIGHT) and not ch.is_affected(merc.AFF_SHADOWPLANE) and \
            not (ch.in_room and ch.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT and not ch.is_npc() and ch.chobj and ch.chobj.in_obj) and \
            ch.in_room.is_dark():
        ch.send("It is pitch black ...\n")
        handler_ch.show_char_to_char(ch.in_room.people, ch)
        return

    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or game_utils.str_cmp(arg1, "auto"):
        # 'look' or 'look auto'
        if ch.in_room and ch.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT and not ch.is_npc() and ch.chobj and ch.chobj.in_obj:
            handler_game.act("$p", ch, ch.chobj.in_obj, None, merc.TO_CHAR)
        elif ch.is_affected(merc.AFF_SHADOWPLANE):
            ch.send("The shadow plane\n")
        else:
            ch.send(ch.in_room.name + "\n")

        if not ch.is_npc() and ch.act.is_set(merc.PLR_AUTOEXIT):
            ch.cmd_exits("auto")

        if ch.in_room and ch.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT and not ch.is_npc() and ch.chobj and ch.chobj.in_obj:
            handler_game.act("You are inside $p.", ch, ch.chobj.in_obj, None, merc.TO_CHAR)
            handler_ch.show_list_to_char(ch.chobj.in_obj.items, ch, False, False)
        elif (not arg1 or game_utils.str_cmp(arg1, "auto")) and ch.is_affected(merc.AFF_SHADOWPLANE):
            ch.send("You are standing in complete darkness.\n")
        elif (not ch.is_npc() and not ch.act.is_set(merc.PLR_BRIEF)) and (not arg1 or game_utils.str_cmp(arg1, "auto")):
            ch.send(ch.in_room.description + "\n")

            if ch.in_room.blood > 0:
                if ch.in_room.blood == 1000:
                    buf = "#RYou notice that the room is completely drenched in blood.#n\n"
                elif ch.in_room.blood > 750:
                    buf = "#RYou notice that there is a very large amount of blood around the room.#n\n"
                elif ch.in_room.blood > 500:
                    buf = "#RYou notice that there is a large quantity of blood around the room.#n\n"
                elif ch.in_room.blood > 250:
                    buf = "#RYou notice a fair amount of blood on the floor.#n\n"
                elif ch.in_room.blood > 100:
                    buf = "#RYou notice several blood stains on the floor.#n\n"
                elif ch.in_room.blood > 50:
                    buf = "#RYou notice a few blood stains on the floor.#n\n"
                elif ch.in_room.blood > 25:
                    buf = "#RYou notice a couple of blood stains on the floor.#n\n"
                elif ch.in_room.blood > 0:
                    buf = "#RYou notice a few drops of blood on the floor.#n\n"
                else:
                    buf = "#RYou notice nothing special in the room.#n\n"
                ch.send(buf)

        handler_ch.show_list_to_char(ch.in_room.items, ch, False, False)
        handler_ch.show_char_to_char(ch.in_room.people, ch)
        return

    if game_utils.str_cmp(arg1, ["i", "in"]):
        # 'look in'
        if not arg2:
            ch.send("Look in what?\n")
            return

        item = ch.get_item_here(arg2)
        if not item:
            ch.send("You do not see that here.\n")
            return

        if item.item_type == merc.ITEM_PORTAL:
            proomindex = instance.rooms[item.value[0]]
            location = ch.in_room
            if not proomindex:
                ch.send("It doesn't seem to lead anywhere.\n")
                return

            if item.value[2] == 1 or item.value[2] == 3:
                ch.send("It seems to be closed.\n")
                return

            ch.in_room.get(ch)
            proomindex.put(ch)

            for portal_id in ch.in_room.items:
                portal = instance.items[portal_id]

                if item.value[0] == portal.value[3] and item.value[3] == portal.value[0]:
                    if ch.is_affected(merc.AFF_SHADOWPLANE) and not portal.flags.shadowplane:
                        ch.affected_by.rem_bit(merc.AFF_SHADOWPLANE)
                        ch.cmd_look("auto")
                        ch.affected_by.set_bit(merc.AFF_SHADOWPLANE)
                        break
                    elif not ch.is_affected(merc.AFF_SHADOWPLANE) and portal.flags.shadowplane:
                        ch.affected_by.set_bit(merc.AFF_SHADOWPLANE)
                        ch.cmd_look("auto")
                        ch.affected_by.rem_bit(merc.AFF_SHADOWPLANE)
                        break
                    else:
                        ch.cmd_look("auto")
                        break

            ch.in_room.get(ch)
            location.put(ch)
        elif item.item_type == merc.ITEM_DRINK_CON:
            if item.value[1] <= 0:
                ch.send("It is empty.\n")
                return

            if item.value[1] < item.value[0] // 5:
                ch.send(f"There is a little {const.liq_table[item.value[2]].color} liquid left in it.\n")
            elif item.value[1] < item.value[0] // 4:
                ch.send(f"It contains a small about of {const.liq_table[item.value[2]].color} liquid.\n")
            elif item.value[1] < item.value[0] // 3:
                ch.send(f"It's about a third full of {const.liq_table[item.value[2]].color} liquid.\n")
            elif item.value[1] < item.value[0] // 2:
                ch.send(f"It's about half full of {const.liq_table[item.value[2]].color} liquid.\n")
            elif item.value[1] < item.value[0]:
                ch.send(f"It is almost full of {const.liq_table[item.value[2]].color} liquid.\n")
            elif item.value[1] == item.value[0]:
                ch.send(f"It's completely full of {const.liq_table[item.value[2]].color} liquid.\n")
            else:
                ch.send(f"Somehow it is MORE than full of {const.liq_table[item.value[2]].color} liquid.\n")
        elif item.item_type in [merc.ITEM_CONTAINER, merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC]:
            if state_checks.is_set(item.value[1], merc.CONT_CLOSED):
                ch.send("It is closed.\n")
                return

            handler_game.act("$p contains:", ch, item, None, merc.TO_CHAR)
            handler_ch.show_list_to_char(item.inventory, ch, True, True)
        else:
            ch.send("That is not a container.\n")
        return

    victim = ch.get_char_room(arg1)
    if victim:
        handler_ch.show_char_to_char_1(victim, ch)
        return

    for vch in list(instance.characters.values()):
        if not vch.in_room:
            continue

        if vch.in_room == ch.in_room:
            if not vch.is_npc() and game_utils.str_cmp(arg1, vch.morph):
                handler_ch.show_char_to_char_1(vch, ch)
                return
            continue

    if not ch.is_npc() and ch.chobj and ch.chobj.in_obj:
        item = ch.get_item_in_item(arg1)
        if item:
            ch.send(item.description + "\n")
            return

    item_list = list(ch.items)
    item_list.extend(ch.in_room.items)
    for item_id in item_list:
        item = instance.items[item_id]

        if not ch.is_npc() and ch.chobj and item.chobj and item.chobj == ch:
            continue

        if ch.can_see_item(item):
            pdesc = game_utils.get_extra_descr(arg1, item.extra_descr)
            if pdesc:
                ch.send(pdesc)
                return

        if game_utils.is_name(arg1, item.name):
            ch.send(item.description + "\n")
            return

    pdesc = game_utils.get_extra_descr(arg1, ch.in_room.extra_descr)
    if pdesc:
        ch.send(pdesc)
        return

    dir_list = [(["n", "north"], merc.DIR_NORTH), (["e", "east"], merc.DIR_EAST), (["s", "south"], merc.DIR_SOUTH), (["w", "west"], merc.DIR_WEST),
                (["u", "up"], merc.DIR_UP), (["d", "down"], merc.DIR_DOWN)]
    for (aa, bb) in dir_list:
        if game_utils.str_cmp(arg1, aa):
            door = bb
            break
    else:
        ch.send("You do not see that here.\n")
        return

    # 'look direction'
    pexit = ch.in_room.exit[door]
    if not pexit:
        ch.send("Nothing special there.\n")
        return

    if pexit.keyword and pexit.keyword[0] != " ":
        if pexit.exit_info.is_set(merc.EX_CLOSED):
            handler_game.act("The $d is closed.", ch, None, pexit.keyword, merc.TO_CHAR)
        elif pexit.exit_info.is_set(merc.EX_ISDOOR):
            handler_game.act("The $d is open.", ch, None, pexit.keyword, merc.TO_CHAR)

            pexit = ch.in_room.exit[door]
            if not pexit:
                return

            proomindex = instance.rooms[pexit.to_room]
            if not proomindex:
                return

            location = ch.in_room
            ch.in_room.get(ch)
            proomindex.put(ch)
            ch.cmd_look("auto")
            ch.in_room.get(ch)
            location.put(ch)
        else:
            pexit = ch.in_room.exit[door]
            if not pexit:
                return

            proomindex = instance.rooms[pexit.to_room]
            if not proomindex:
                return

            location = ch.in_room
            ch.in_room.get(ch)
            proomindex.put(ch)
            ch.cmd_look("auto")
            ch.in_room.get(ch)
            location.put(ch)
    else:
        pexit = ch.in_room.exit[door]
        if not pexit:
            return

        proomindex = instance.rooms[pexit.to_room]
        if not proomindex:
            return

        location = ch.in_room
        ch.in_room.get(ch)
        proomindex.put(ch)
        ch.cmd_look("auto")
        ch.in_room.get(ch)
        location.put(ch)


interp.register_command(
    interp.CmdType(
        name="look",
        cmd_fun=cmd_look,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
