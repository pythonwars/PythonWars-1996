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

import handler_game
import instance
import interp
import merc
import object_creator


# noinspection PyUnusedLocal
def cmd_weaponform(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if ch.is_affected(merc.AFF_POLYMORPH):
        ch.send("You cannot do this while polymorphed.\n")
        return

    if ch.powers[merc.DPOWER_OBJ_VNUM] < 1:
        ch.send("You don't have the ability to change into a weapon.\n")
        return

    if ch.is_affected(merc.AFF_WEBBED):
        ch.send("Not with all this sticky webbing on.\n")
        return

    item_index = instance.item_templates[ch.powers[merc.DPOWER_OBJ_VNUM]]
    if not item_index:
        ch.send("You don't have the ability to change into a weapon.\n")
        return

    item = object_creator.create_item(item_index, 60)
    ch.in_room.put(item)
    handler_game.act("$n transforms into $p and falls to the ground.", ch, item, None, merc.TO_ROOM)
    handler_game.act("You transform into $p and fall to the ground.", ch, item, None, merc.TO_CHAR)
    ch.obj_vnum = ch.powers[merc.DPOWER_OBJ_VNUM]
    item.chobj = ch
    ch.chobj = item
    ch.affected_by.set_bit(merc.AFF_POLYMORPH)
    ch.extra.set_bit(merc.EXTRA_OSWITCH)
    ch.morph = item.short_descr


interp.register_command(
    interp.CmdType(
        name="weaponform",
        cmd_fun=cmd_weaponform,
        position=merc.POS_STANDING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
