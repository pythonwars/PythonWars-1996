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

import game_utils
import handler_game
import interp
import merc


def cmd_otransfer(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        ch.send("Otransfer which object?\n")
        return

    if not arg2:
        victim = ch
    else:
        victim = ch.get_char_world(arg2)
        if not victim:
            ch.not_here(arg2)
            return

    item = ch.get_item_world(arg1)
    if not item:
        ch.send("Nothing like that in hell, earth, or heaven.\n")
        return

    if not ch.is_judge() and (not item.questmaker or not game_utils.str_cmp(ch.name, item.questmaker)):
        ch.send("You don't have permission to otransfer that item.\n")
        return

    if item.in_living:
        if not item.in_living.is_npc() and item.in_living.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
            ch.send("You failed.\n")
            handler_game.act("$p flickers briefly with energy.", item.in_living, item, None, merc.TO_CHAR)
            return

        handler_game.act("$p vanishes from your hands in an explosion of energy.", item.in_living, item, None, merc.TO_CHAR)
        handler_game.act("$p vanishes from $n's hands in an explosion of energy.", item.in_living, item, None, merc.TO_ROOM)
        item.in_living.get(item)
    elif item.in_item:
        item.in_item.get(item)
    elif item.in_room:
        chroom = ch.in_room
        objroom = item.in_room
        ch.in_room.get(ch)
        objroom.put(ch)
        handler_game.act("$p vanishes from the ground in an explosion of energy.", ch, item, None, merc.TO_ROOM)

        if chroom == objroom:
            handler_game.act("$p vanishes from the ground in an explosion of energy.", ch, item, None, merc.TO_CHAR)

        ch.in_room.get(ch)
        chroom.put(ch)
        item.in_room.get(item)
    else:
        ch.send("You were unable to get it.\n")
        return

    victim.put(item)
    handler_game.act("$p appears in your hands in an explosion of energy.", victim, item, None, merc.TO_CHAR)
    handler_game.act("$p appears in $n's hands in an explosion of energy.", victim, item, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="otransfer",
        cmd_fun=cmd_otransfer,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
