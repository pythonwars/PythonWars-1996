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
import interp
import merc


def cmd_oswitch(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not arg:
        ch.send("Switch into what?\n")
        return

    if ch.extra.is_set(merc.EXTRA_OSWITCH) or ch.head.is_set(merc.LOST_HEAD):
        ch.send("You are already oswitched.\n")
        return

    if ch.is_affected(merc.AFF_POLYMORPH):
        ch.send("Not while polymorphed.\n")
        return

    if ch.is_npc() or ch.extra.is_set(merc.EXTRA_SWITCH):
        ch.send("Not while switched.\n")
        return

    item = ch.get_item_world(arg)
    if not item:
        ch.not_here()
        return

    if item.chobj:
        ch.send("Object in use.\n")
        return

    mount = ch.mount
    if mount:
        ch.cmd_dismount("")

    item.chobj = ch
    ch.chobj = item
    ch.affected_by.set_bit(merc.AFF_POLYMORPH)
    ch.extra.set_bit(merc.EXTRA_OSWITCH)
    ch.morph = item.short_descr
    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="oswitch",
        cmd_fun=cmd_oswitch,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
