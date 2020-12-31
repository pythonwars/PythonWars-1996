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


def show_spell(ch, spell_type):
    if ch.is_npc():
        return

    type_list = [(0, "untrained at"), (25, "an apprentice at"), (50, "a student at"), (75, "a scholar at"), (100, "a magus at"),
                 (125, "an adept at"), (150, "a mage at"), (175, "a warlock at"), (199, "a master wizard at")]
    for (aa, bb) in type_list:
        if ch.spl[spell_type] <= aa:
            bufskill = bb
            break
    else:
        if ch.is_mage() and ch.spl[spell_type] >= 240:
            bufskill = "the complete master of"
        else:
            bufskill = "a grand sorcerer at"

    type_list = [(merc.PURPLE_MAGIC, "purple"), (merc.RED_MAGIC, "red"), (merc.BLUE_MAGIC, "blue"), (merc.GREEN_MAGIC, "green"),
                 (merc.YELLOW_MAGIC, "yellow")]
    for (aa, bb) in type_list:
        if spell_type == aa:
            ch.send("You are {} {} magic.\n".format(bufskill, bb))
            return


def cmd_spell(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        show_spell(ch, merc.PURPLE_MAGIC)
        show_spell(ch, merc.RED_MAGIC)
        show_spell(ch, merc.BLUE_MAGIC)
        show_spell(ch, merc.GREEN_MAGIC)
        show_spell(ch, merc.YELLOW_MAGIC)
    else:
        arg_list = [("purple", merc.PURPLE_MAGIC), ("red", merc.RED_MAGIC), ("blue", merc.BLUE_MAGIC), ("green", merc.GREEN_MAGIC),
                    ("yellow", merc.YELLOW_MAGIC)]
        for (aa, bb) in arg_list:
            if game_utils.str_cmp(arg, aa):
                show_spell(ch, bb)
                break
        else:
            ch.send("You know of no such magic.\n")


interp.register_command(
    interp.CmdType(
        name="spells",
        cmd_fun=cmd_spell,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
