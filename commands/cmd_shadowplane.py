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


def cmd_shadowplane(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_werewolf() or ch.powers[merc.WPOWER_OWL] < 3:
        if not ch.is_vampire():
            ch.huh()
            return

        if not ch.vampaff.is_set(merc.VAM_OBTENEBRATION):
            ch.send("You are not trained in the Obtenebration discipline.\n")
            return

    if ch.is_vampire():
        if ch.blood < 75:
            ch.send("You have insufficient blood.\n")
            return

        ch.blood -= game_utils.number_range(65, 75)

    if not arg:
        ch.affected_by.tog_bit(merc.AFF_SHADOWPLANE)
        if ch.is_affected(merc.AFF_SHADOWPLANE):
            ch.send("You fade into the plane of shadows.\n")
            handler_game.act("The shadows flicker and swallow up $n.", ch, None, None, merc.TO_ROOM)
            ch.cmd_look("auto")
            return

        ch.send("You fade back into the real world.\n")
        handler_game.act("The shadows flicker and $n fades into existance.", ch, None, None, merc.TO_ROOM)
        ch.cmd_look("auto")
        return

    item = ch.get_item_here(arg)
    if not item:
        ch.send("What do you wish to toss into the shadow plane?\n")
        return

    if ch.is_affected(merc.AFF_SHADOWPLANE):
        ch.send("You toss it to the ground and it vanishes.\n")
    else:
        ch.send("You toss it into a shadow and it vanishes.\n")


interp.register_command(
    interp.CmdType(
        name="shadowplane",
        cmd_fun=cmd_shadowplane,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
