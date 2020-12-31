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

import interp
import merc


# noinspection PyUnusedLocal
def cmd_immune(ch, argument):
    if ch.is_npc():
        return

    buf = ["--------------------------------------------------------------------------------\n"]
    buf += "                                -= Immunities =-\n"
    buf += "--------------------------------------------------------------------------------\n"

    # Display weapon resistances
    buf += "Weapons:"

    imm_list = [(merc.IMM_SLASH, " Slash Slice"), (merc.IMM_STAB, " Stab Pierce"), (merc.IMM_SMASH, " Blast Crush Pound"),
                (merc.IMM_ANIMAL, " Claw Bite"), (merc.IMM_MISC, " Grep Whip Suck")]
    found = False
    for (aa, bb) in imm_list:
        if ch.immune.is_set(aa):
            buf += bb
            found = True

    if not found:
        buf += " None"
    buf += ".\n"

    # Display spell immunities
    buf += "Spells :"

    imm_list = [(merc.IMM_CHARM, " Charm"), (merc.IMM_HEAT, " Heat"), (merc.IMM_COLD, " Cold"), (merc.IMM_LIGHTNING, " Lightning"),
                (merc.IMM_ACID, " Acid"), (merc.IMM_SUMMON, " Summon"), (merc.IMM_VOODOO, " Voodoo"), (merc.IMM_SLEEP, " Sleep"),
                (merc.IMM_DRAIN, " Drain"), (merc.IMM_TRANSPORT, " Transport")]

    found = False
    for (aa, bb) in imm_list:
        if ch.immune.is_set(aa):
            buf += bb
            found = True

    if not found:
        buf += " None"
    buf += ".\n"

    # Display skill immunities
    buf += "Skills :"

    imm_list = [(merc.IMM_HURL, " Hurl"), (merc.IMM_BACKSTAB, " Backstab"), (merc.IMM_KICK, " Kick"), (merc.IMM_DISARM, " Disarm"),
                (merc.IMM_STEAL, " Steal")]

    found = False
    for (aa, bb) in imm_list:
        if ch.immune.is_set(aa):
            buf += bb
            found = True

    if not found:
        buf += " None"
    buf += ".\n"
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="immune",
        cmd_fun=cmd_immune,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
