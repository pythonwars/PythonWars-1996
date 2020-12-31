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


def cmd_bind(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Syntax: bind <player> <object>\n")
        return

    victim = ch.get_char_room(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.is_affected(merc.AFF_POLYMORPH):
        ch.send("You cannot do this while they are polymorphed.\n")
        return

    if victim.is_immortal():
        ch.send("Only on mortals or avatars.\n")
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    item = ch.get_item_carry(arg2)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    if item.questmaker:
        ch.send("You cannot bind someone into a modified item.\n")
        return

    if item.chobj:
        ch.send("That item already has someone bound in it.\n")
        return

    ch.send("Ok.\n")
    handler_game.act("$n transforms into a white vapour and pours into $p.", victim, item, None, merc.TO_ROOM)
    handler_game.act("You transform into a white vapour and pour into $p.", victim, item, None, merc.TO_CHAR)
    victim.obj_vnum = item.vnum
    item.chobj = victim
    victim.chobj = item
    victim.affected_by.set_bit(merc.AFF_POLYMORPH)
    victim.extra.set_bit(merc.EXTRA_OSWITCH)
    victim.morph = item.short_descr


interp.register_command(
    interp.CmdType(
        name="bind",
        cmd_fun=cmd_bind,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
