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
import handler_room
import instance
import interp
import merc
import state_checks


def cmd_unlock(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Unlock what?\n")
        return

    item = ch.get_item_here(arg)
    if item:
        # 'unlock object'
        if item.item_type != merc.ITEM_CONTAINER:
            ch.send("That's not a container.\n")
            return

        if not state_checks.is_set(item.value[1], merc.CONT_CLOSED):
            ch.send("It's not closed.\n")
            return

        if item.value[2] < 0:
            ch.send("It can't be unlocked.\n")
            return

        if not ch.valid_key(item.value[2]):
            ch.send("You lack the key.\n")
            return

        if not state_checks.is_set(item.value[1], merc.CONT_LOCKED):
            ch.send("It's already unlocked.\n")
            return

        state_checks.remove_bit(item.value[1], merc.CONT_LOCKED)
        ch.send("*Click*\n")
        handler_game.act("$n unlocks $p.", ch, item, None, merc.TO_ROOM)
        return

    door = handler_room.find_door(ch, arg)
    if door >= 0:
        # 'unlock door'
        pexit = ch.in_room.exit[door]
        if not pexit.exit_info.is_set(merc.EX_CLOSED):
            ch.send("It's not closed.\n")
            return

        if pexit.key < 0:
            ch.send("It can't be unlocked.\n")
            return

        if not ch.valid_key(pexit.key):
            ch.send("You lack the key.\n")
            return

        if not pexit.exit_info.is_set(merc.EX_LOCKED):
            ch.send("It's already unlocked.\n")
            return

        pexit.exit_info.rem_bit(merc.EX_LOCKED)
        ch.send("*Click*\n")
        handler_game.act("$n unlocks the $d.", ch, None, pexit.keyword, merc.TO_ROOM)

        # unlock the other side
        to_room = instance.rooms[pexit.to_room]
        if to_room and to_room.exit[merc.rev_dir[door]] != 0 and to_room.exit[merc.rev_dir[door]].to_room == ch.in_room:
            to_room.exit[merc.rev_dir[door]].exit_info.rem_bit(merc.EX_LOCKED)


interp.register_command(
    interp.CmdType(
        name="unlock",
        cmd_fun=cmd_unlock,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
