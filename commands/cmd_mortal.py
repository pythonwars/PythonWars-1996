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

import const
import handler_game
import interp
import merc
import state_checks


# noinspection PyUnusedLocal
def cmd_mortal(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire() and not ch.vampaff.is_set(merc.VAM_MORTAL):
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_OBFUSCATE):
        ch.send("You are not trained in the Obfuscate discipline.\n")
        return

    if ch.is_vampire():
        if ch.blood < 100:
            ch.send("You must be at full blood to use this power.\n")
            return

        # Have to make sure they have enough blood to change back
        blood = ch.blood
        ch.blood = 666

        # Remove physical vampire attributes when you take mortal form
        if ch.vampaff.is_set(merc.VAM_DISGUISED):
            ch.cmd_mask("self")

        if ch.immune.is_set(merc.IMM_SHIELDED):
            ch.cmd_shield("")

        if ch.is_affected(merc.AFF_SHADOWPLANE):
            ch.cmd_shadowplane("")

        if ch.vampaff.is_set(merc.VAM_FANGS):
            ch.cmd_fangs("")

        if ch.vampaff.is_set(merc.VAM_CLAWS):
            ch.cmd_claws("")

        if ch.vampaff.is_set(merc.VAM_NIGHTSIGHT):
            ch.cmd_nightsight("")

        if ch.is_affected(merc.AFF_SHADOWSIGHT):
            ch.cmd_shadowsight("")

        if ch.act.is_set(merc.PLR_HOLYLIGHT):
            ch.cmd_truesight("")

        if ch.vampaff.is_set(merc.VAM_CHANGED):
            ch.cmd_change("human")

        if ch.polyaff.is_set(merc.POLY_SERPENT):
            ch.cmd_serpent("")

        ch.powers[merc.UNI_RAGE] = 0
        ch.blood = blood
        ch.send("Colour returns to your skin and you warm up a little.\n")
        handler_game.act("Colour returns to $n's skin.", ch, None, None, merc.TO_ROOM)
        ch.ch_class = state_checks.prefix_lookup(const.class_table, "human")
        ch.vampaff.set_bit(merc.VAM_MORTAL)
        return

    ch.send("You skin pales and cools.\n")
    handler_game.act("$n's skin pales slightly.", ch, None, None, merc.TO_ROOM)
    ch.ch_class = state_checks.prefix_lookup(const.class_table, "vampire")
    ch.vampaff.rem_bit(merc.VAM_MORTAL)


interp.register_command(
    interp.CmdType(
        name="mortal",
        cmd_fun=cmd_mortal,
        position=merc.POS_FIGHTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
