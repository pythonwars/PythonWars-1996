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

import handler_item
import handler_npc
import handler_room
import instance
import interp
import merc
import sys_utils
import world_classes

previous_snapshot = None


# noinspection PyUnusedLocal
def cmd_driver(ch, argument):
    global previous_snapshot

    current_snapshot = sys_utils.ResourceSnapshot()

    buf = [current_snapshot.log_data(previous=previous_snapshot, do_indent=False)]
    previous_snapshot = current_snapshot
    buf += "\n\n"
    buf += "{:12} {:8} {:8} {:8}  {:8} {:8} {:8}\n".format("", "Areas", "Rooms", "Shops", "Items", "NPCs", "Players")
    buf += "{:12} {:8} {:8} {:8}  {:8} {:8} {:8}\n".format("" * 12, "-" * 8, "-" * 8, "-" * 8, "-" * 8, "-" * 8, "-" * 8)
    buf += "{:12} {:8} {:8} {:8}  {:8} {:8} {:8}\n".format("Templates:", world_classes.Area.template_count,
                                                           handler_room.Room.template_count, len(instance.shop_templates),
                                                           handler_item.Items.template_count, handler_npc.Npc.template_count, "")
    buf += "{:12} {:8} {:8} {:8}  {:8} {:8} {:8}\n".format("Instances:", world_classes.Area.instance_count,
                                                           handler_room.Room.instance_count, len(instance.shops),
                                                           handler_item.Items.instance_count, handler_npc.Npc.instance_count,
                                                           len(instance.descriptor_list))

    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="driver",
        cmd_fun=cmd_driver,
        position=merc.POS_DEAD, level=12,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
