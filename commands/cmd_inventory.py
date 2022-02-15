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
import handler_ch
import handler_game
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_inventory(ch, argument):
    if not ch.is_npc() and ch.head.is_set(merc.LOST_HEAD):
        ch.send("You are not a container.\n")
        return
    elif not ch.is_npc() and ch.extra.is_set(merc.EXTRA_OSWITCH):
        item = ch.chobj
        if not item:
            ch.send("You are not a container.\n")
            return

        if item.item_type == merc.ITEM_PORTAL:
            proomindex = instance.rooms(item.value[0])
            location = ch.in_room
            if not proomindex:
                ch.send("You don't seem to lead anywhere.\n")
                return

            ch.in_room.get(ch)
            proomindex.put(ch)

            for portal in ch.in_room.items:
                if (item.value[0] == portal.value[3]) and (item.value[3] == portal.value[0]):
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
                ch.send("You are empty.\n")
                return

            if item.value[1] < item.value[0] // 5:
                buf = f"There is a little {const.liq_table[item.value[2]].color} liquid left in you.\n"
            elif item.value[1] < item.value[0] // 4:
                buf = f"You contain a small about of {const.liq_table[item.value[2]].color} liquid.\n"
            elif item.value[1] < item.value[0] // 3:
                buf = f"You're about a third full of {const.liq_table[item.value[2]].color} liquid.\n"
            elif item.value[1] < item.value[0] // 2:
                buf = f"You're about half full of {const.liq_table[item.value[2]].color} liquid.\n"
            elif item.value[1] < item.value[0]:
                buf = f"You are almost full of {const.liq_table[item.value[2]].color} liquid.\n"
            elif item.value[1] == item.value[0]:
                buf = f"You're completely full of {const.liq_table[item.value[2]].color} liquid.\n"
            else:
                buf = f"Somehow you are MORE than full of {const.liq_table[item.value[2]].color} liquid.\n"
            ch.send(buf)
        elif item.item_type in [merc.ITEM_CONTAINER, merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC]:
            handler_game.act("$p contain:", ch, item, None, merc.TO_CHAR)
            handler_ch.show_list_to_char(ch.inventory, ch, True, True)
        else:
            ch.send("You are not a container.\n")
        return

    ch.send("You are carrying:\n")
    handler_ch.show_list_to_char(ch.inventory, ch, True, True)


interp.register_command(
    interp.CmdType(
        name="inventory",
        cmd_fun=cmd_inventory,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
