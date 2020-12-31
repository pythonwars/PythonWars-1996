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


# noinspection PyUnusedLocal
def cmd_serpent(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_SERPENTIS):
        ch.send("You are not trained in the Serpentis discipline.\n")
        return

    if ch.is_affected(merc.AFF_POLYMORPH):
        if not ch.polyaff.is_set(merc.POLY_SERPENT):
            ch.send("You cannot polymorph from this form.\n")
            return

        handler_game.act("You transform back into human.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n transform into human form.", ch, None, None, merc.TO_ROOM)
        ch.polyaff.rem_bit(merc.POLY_SERPENT)
        ch.affected_by.rem_bit(merc.AFF_POLYMORPH)
        ch.clear_stats()
        ch.morph = ""
        return

    if ch.blood < 50:
        ch.send("You have insufficient blood.\n")
        return

    ch.blood -= game_utils.number_range(40, 50)
    ch.clear_stats()

    if ch.stance[0] != -1:
        ch.cmd_stance("")

    if ch.mounted == merc.IS_RIDING:
        ch.cmd_dismount("")

    ch.mod_str = 10
    handler_game.act("You transform into a huge serpent.", ch, None, None, merc.TO_CHAR)
    handler_game.act("$n transforms into a huge serpent.", ch, None, None, merc.TO_ROOM)
    ch.polyaff.set_bit(merc.POLY_SERPENT)
    ch.affected_by.set_bit(merc.AFF_POLYMORPH)
    ch.morph = "{} the huge serpent".format(ch.name)


interp.register_command(
    interp.CmdType(
        name="serpent",
        cmd_fun=cmd_serpent,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
