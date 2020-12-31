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

import comm
import const
import game_utils
import interp
import merc


def cmd_web(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_werewolf() or ch.powers[merc.WPOWER_SPIDER] < 2:
        ch.huh()
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot web an ethereal person.\n")
        return

    sn = "web"
    if sn not in const.skill_table:
        comm.notify("cmd_web: missing sn (web) in skill_table", merc.CONSOLE_WARNING)
        return

    spelltype = const.skill_table[sn].target
    level = ch.spl[spelltype] * 0.25
    const.skill_table[sn].spell_fun(sn, level, ch, victim, merc.TARGET_CHAR)
    ch.wait_state(merc.PULSE_VIOLENCE)


interp.register_command(
    interp.CmdType(
        name="web",
        cmd_fun=cmd_web,
        position=merc.POS_FIGHTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
