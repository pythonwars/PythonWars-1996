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
def cmd_rage(ch, argument):
    if ch.is_npc():
        return

    if ch.is_vampire():
        if ch.powers[merc.UNI_RAGE] >= 25:
            ch.send("Your beast is already controlling you.\n")
            return

        if not ch.vampaff.is_set(merc.VAM_NIGHTSIGHT):
            ch.cmd_nightsight("")

        if not ch.vampaff.is_set(merc.VAM_FANGS):
            ch.cmd_fangs("")

        if not ch.vampaff.is_set(merc.VAM_CLAWS):
            ch.cmd_claws("")

        ch.send("You bare yours fangs and growl as your inner beast consumes you.\n")
        handler_game.act("$n bares $s fangs and growls as $s inner beast consumes $m.", ch, None, None, merc.TO_ROOM)
        ch.powers[merc.UNI_RAGE] += game_utils.number_range(10, 20)
        if ch.beast > 0:
            ch.beastlike()

        ch.wait_state(merc.PULSE_VIOLENCE)
        return

    if not ch.is_werewolf() or ch.powers[merc.WPOWER_BEAR] < 2:
        ch.huh()
        return

    if not ch.special.is_set(merc.SPC_WOLFMAN):
        ch.send("You start snarling angrilly.\n")
        handler_game.act("$n starts snarling angrilly.", ch, None, None, merc.TO_ROOM)
        ch.powers[merc.UNI_RAGE] += game_utils.number_range(10, 20)

        if ch.powers[merc.UNI_RAGE] >= 100:
            ch.werewolf()

        ch.wait_state(merc.PULSE_VIOLENCE)
        return

    ch.send("But you are already in a rage!\n")


interp.register_command(
    interp.CmdType(
        name="rage",
        cmd_fun=cmd_rage,
        position=merc.POS_FIGHTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
