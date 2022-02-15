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


def cmd_bloodline(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    argument, arg3 = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if arg1:
        arg1 = arg1[0].upper() + arg1[1:]
    if arg2:
        arg2 = arg2[0].upper() + arg2[1:]
    if arg3:
        arg3 = arg3[0].upper() + arg3[1:]

    if not ch.clan and ch.powers[merc.UNI_GEN] != 1:
        ch.cmd_say("In the name of Gaia, I announce my Garou heritage.")
        ch.cmd_say(f"My name is {ch.name}, I am a Ronin of no tribe.")
        return

    ch.cmd_say("In the name of Gaia, I announce my Garou heritage.")

    if ch.powers[merc.UNI_GEN] != 1:
        if ch.powers[merc.UNI_GEN] == 4:
            buf2 = arg3
        elif ch.powers[merc.UNI_GEN] == 3:
            buf2 = arg2
        elif ch.powers[merc.UNI_GEN] == 2:
            buf2 = arg1
        else:
            buf2 = ""

        if ch.powers[merc.UNI_GEN] == 1:
            buf = f"My name is {ch.name}, chosen Champion of Gaia."
        elif ch.powers[merc.UNI_GEN] == 2:
            buf = f"My name is {ch.name}, Chieftain of the {ch.clan} tribe, pup of {buf2}."
        else:
            buf = f"My name is {ch.name}, of the {ch.clan} tribe, pup of {buf2}."
        ch.cmd_say(buf)

    if arg3:
        ch.cmd_say(f"My name is {arg3}, of the {ch.clan} tribe, pup of {arg2}.")

    if arg2:
        if arg1:
            buf = f"My name is {arg2}, Chieftain of the {ch.clan} tribe, pup of {arg1}."
        else:
            buf = f"My name is {arg2}, of the {ch.clan} tribe, pup of {arg1}."
        ch.cmd_say(buf)

    if ch.powers[merc.UNI_GEN] == 1:
        buf = f"My name is {ch.name}, chosen Champion of Gaia."
    else:
        buf = f"My name is {arg1}, chosen Champion of Gaia."
    ch.cmd_say(buf)


def cmd_tradition(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    argument, arg3 = game_utils.read_word(argument)
    argument, arg4 = game_utils.read_word(argument)
    argument, arg5 = game_utils.read_word(argument)
    argument, arg6 = game_utils.read_word(argument)

    if arg1:
        arg1 = arg1[0].upper() + arg1[1:]
    if arg2:
        arg2 = arg2[0].upper() + arg2[1:]
    if arg3:
        arg3 = arg3[0].upper() + arg3[1:]
    if arg4:
        arg4 = arg4[0].upper() + arg4[1:]
    if arg5:
        arg5 = arg5[0].upper() + arg5[1:]
    if arg6:
        arg6 = arg6[0].upper() + arg6[1:]

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.powers[merc.UNI_GEN] in range(1, 8):
        ch.huh()
        return

    if ch.powers[merc.UNI_GEN] == 2:
        buf3 = "Antediluvian"
    elif ch.rank == merc.AGE_NEONATE:
        buf3 = "Neonate"
    elif ch.rank == merc.AGE_ANCILLA:
        buf3 = "Ancilla"
    elif ch.rank == merc.AGE_ELDER:
        buf3 = "Elder"
    elif ch.rank == merc.AGE_METHUSELAH:
        buf3 = "Methuselah"
    else:
        buf3 = "Childe"

    if ch.powers[merc.UNI_GEN] == 6:
        buf2 = "Sixth"
    elif ch.powers[merc.UNI_GEN] == 5:
        buf2 = "Fifth"
    elif ch.powers[merc.UNI_GEN] == 4:
        buf2 = "Fourth"
    elif ch.powers[merc.UNI_GEN] == 3:
        buf2 = "Third"
    elif ch.powers[merc.UNI_GEN] == 2:
        buf2 = "Second"
    else:
        buf2 = "Seventh"

    if ch.powers[merc.UNI_GEN] == 1:
        ch.cmd_say(f"As is the tradition, I recite the lineage of {ch.name}, Sire of all Kindred.")
    else:
        ch.cmd_say(f"As is the tradition, I recite the lineage of {ch.name}, {buf3} of the {buf2} Generation.")

    if ch.powers[merc.UNI_GEN] != 1:
        if ch.powers[merc.UNI_GEN] == 7:
            buf2 = arg6
        elif ch.powers[merc.UNI_GEN] == 6:
            buf2 = arg5
        elif ch.powers[merc.UNI_GEN] == 5:
            buf2 = arg4
        elif ch.powers[merc.UNI_GEN] == 4:
            buf2 = arg3
        elif ch.powers[merc.UNI_GEN] == 3:
            buf2 = arg2
        elif ch.powers[merc.UNI_GEN] == 2:
            buf2 = arg1

        if ch.special.is_set(merc.SPC_ANARCH) or not ch.clan:
            buf = f"My name is {ch.name}.  I am of no clan.  My sire is {buf2}."
        elif ch.powers[merc.UNI_GEN] == 2:
            buf = f"My name is {ch.name}.  I founded {ch.clan}.  My sire is {buf2}."
        else:
            buf = f"My name is {ch.name}.  I am of {ch.clan}.  My sire is {buf2}."
        ch.cmd_say(buf)

    if arg6:
        ch.cmd_say(f"My name is {arg6}.  My sire is {arg5}.")

    if arg5:
        ch.cmd_say(f"My name is {arg5}.  My sire is {arg4}.")

    if arg4:
        ch.cmd_say(f"My name is {arg4}.  My sire is {arg3}.")

    if arg3:
        ch.cmd_say(f"My name is {arg3}.  My sire is {arg2}.")

    if arg2:
        ch.cmd_say(f"My name is {arg2}.  My sire is {arg1}.")

    if ch.powers[merc.UNI_GEN] == 1:
        buf = f"My name is {ch.name}.  All Kindred are my childer."
    else:
        buf = f"My name is {arg1}.  All Kindred are my childer."
    ch.cmd_say(buf)

    if ch.powers[merc.UNI_GEN] == 7:
        buf = f"My name is {ch.name}, childe of {arg6}, childe of {arg5}, childe of {arg4}, childe of {arg3}, childe of {arg2}, childe of {arg1}.  Recognize my lineage."

    if ch.powers[merc.UNI_GEN] == 6:
        buf = f"My name is {ch.name}, childe of {arg5}, childe of {arg4}, childe of {arg3}, childe of {arg2}, childe of {arg1}.  Recognize my lineage."

    if ch.powers[merc.UNI_GEN] == 5:
        buf = f"My name is {ch.name}, childe of {arg4}, childe of {arg3}, childe of {arg2}, childe of {arg1}.  Recognize my lineage."

    if ch.powers[merc.UNI_GEN] == 4:
        buf = f"My name is {ch.name}, childe of {arg3}, childe of {arg2}, childe of {arg1}.  Recognize my lineage."

    if ch.powers[merc.UNI_GEN] == 3:
        buf = f"My name is {ch.name}, childe of {arg2}, childe of {arg1}.  Recognize my lineage."

    if ch.powers[merc.UNI_GEN] == 2:
        buf = f"My name is {ch.name}, childe of {arg1}.  Recognize my lineage."

    if ch.powers[merc.UNI_GEN] == 1:
        buf = f"My name is {ch.name}.  Recognize my lineage."
    ch.cmd_say(buf)


# noinspection PyUnusedLocal
def cmd_introduce(ch, argument):
    if ch.is_npc():
        return

    if ch.is_vampire() and ch.powers[merc.UNI_GEN] in range(1, 8):
        ch.cmd_tradition(ch.lord)
    elif ch.is_werewolf() and ch.is_hero() and ch.powers[merc.UNI_GEN] in range(1, 5):
        ch.cmd_bloodline(ch.lord)
    else:
        ch.huh()


interp.register_command(
    interp.CmdType(
        name="introduce",
        cmd_fun=cmd_introduce,
        position=merc.POS_STANDING, level=1,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
