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

import fight
import game_utils
import handler_game
import instance
import interp
import merc


def cmd_transfer(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        ch.send("Transfer whom (and where)?\n")
        return

    if game_utils.str_cmp(arg1, "all"):
        for wch in list(instance.players.values()):
            if wch != ch and wch.in_room and ch.can_see(wch):
                if wch.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
                    continue

                ch.cmd_transfer("{} {}".format(wch.name, arg2))
        return

    # Thanks to Grodyn for the optional location parameter.
    if not arg2:
        location = ch.in_room
    else:
        location = game_utils.find_location(ch, arg2)
        if not location:
            ch.send("No such location.\n")
            return

        if location.is_private():
            ch.send("That room is private right now.\n")
            return

    victim = ch.get_char_world(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if not victim.in_room:
        ch.send("They are in limbo.\n")
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    if victim.fighting:
        fight.stop_fighting(victim, True)

    handler_game.act("$n disappears in a mushroom cloud.", victim, None, None, merc.TO_ROOM)
    victim.in_room.get(victim)
    location.put(victim)
    handler_game.act("$n arrives from a puff of smoke.", victim, None, None, merc.TO_ROOM)

    if ch != victim:
        handler_game.act("$n has transferred you.", ch, None, victim, merc.TO_VICT)

    victim.cmd_look("auto")
    ch.send("Ok.\n")

    mount = victim.mount
    if mount:
        mount.in_room.get(mount)
        location.put(mount)

        if ch != mount:
            handler_game.act("$n has transferred you.", ch, None, mount, merc.TO_VICT)
        mount.cmd_look("auto")


interp.register_command(
    interp.CmdType(
        name="transfer",
        cmd_fun=cmd_transfer,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
