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


def cmd_scry(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION):
        if not ch.dempower.is_set(merc.DEM_SCRY):
            ch.send("You haven't been granted the gift of claws.\n")
            return
    elif not ch.is_vampire() and not ch.itemaff.is_set(merc.ITEMA_VISION):
        ch.huh()
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION) and not ch.vampaff.is_set(merc.VAM_AUSPEX) and \
            not ch.itemaff.is_set(merc.ITEMA_VISION):
        ch.send("You are not trained in the Auspex discipline.\n")
        return

    if not arg:
        ch.send("Scry on whom?\n")
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch.is_vampire() and not ch.itemaff.is_set(merc.ITEMA_VISION):
        if ch.blood < 25:
            ch.send("You have insufficient blood.\n")
            return

        ch.blood -= game_utils.number_range(15, 25)

    if not victim.is_npc() and victim.immune.is_set(merc.IMM_SHIELDED) and not ch.itemaff.is_set(merc.ITEMA_VISION):
        ch.send("You are unable to locate them.\n")
        return

    chroom = ch.in_room
    victimroom = victim.in_room
    ch.in_room.get(ch)
    victimroom.put(ch)

    if ch.is_affected(merc.AFF_SHADOWPLANE) and not victim.is_affected(merc.AFF_SHADOWPLANE):
        ch.affected_by.rem_bit(merc.AFF_SHADOWPLANE)
        ch.cmd_look("auto")
        ch.affected_by.set_bit(merc.AFF_SHADOWPLANE)
    elif not ch.is_affected(merc.AFF_SHADOWPLANE) and victim.is_affected(merc.AFF_SHADOWPLANE):
        ch.affected_by.set_bit(merc.AFF_SHADOWPLANE)
        ch.cmd_look("auto")
        ch.affected_by.rem_bit(merc.AFF_SHADOWPLANE)
    else:
        ch.cmd_look("auto")
    ch.in_room.get(ch)
    chroom.put(ch)


interp.register_command(
    interp.CmdType(
        name="scry",
        cmd_fun=cmd_scry,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
