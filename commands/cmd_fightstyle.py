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


def cmd_fightstyle(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Syntax is: fightstyle <number> <style>.\n"
                "Style can be selected from the following (enter style in text form):\n"
                "[ 1]*Trip      [ 2]*Kick      [ 3] Bash      [ 4] Elbow     [ 5] Knee\n"
                "[ 6] Headbutt  [ 7]*Disarm    [ 8] Bite      [ 9]*Dirt      [10] Grapple\n"
                "[11] Punch     [12]*Gouge     [13] Rip       [14]*Stamp     [15] Backfist\n"
                "[16] Jumpkick  [17] Spinkick  [18] Hurl      [19] Sweep     [20] Charge\n"
                f"Selected options: 1:[{ch.cmbt[0]}] 2:[{ch.cmbt[1]}] 3:[{ch.cmbt[2]}] 4:[{ch.cmbt[3]}] 5:[{ch.cmbt[4]}] 6:[{ch.cmbt[5]}] 7:[{ch.cmbt[6]}] 8:[{ch.cmbt[7]}]\n\n"
                "* This has been coded (others are not yet in).\n")
        return

    value = int(arg1) if arg1.isdigit() else -1
    if value not in merc.irange(1, 8):
        ch.send("Please enter a value between 1 and 8.\n")
        return

    arg_list = [("clear", 0), ("trip", 1), ("kick", 2), ("bash", 3), ("elbow", 4), ("knee", 5), ("headbutt", 6), ("disarm", 7), ("bite", 8),
                ("dirt", 9), ("grapple", 10), ("punch", 11), ("gouge", 12), ("rip", 13), ("stamp", 14), ("backfist", 15), ("jumpkick", 16),
                ("spinkick", 17), ("hurl", 18), ("sweep", 19), ("charge", 20)]
    for (aa, bb) in arg_list:
        if game_utils.str_cmp(arg2, bb):
            selection = bb
            break
    else:
        ch.cmd_fightstyle("")
        return

    ch.cmbt[value - 1] = selection
    ch.send(f"Combat option {value} now set to {arg2} ({ch.cmbt[0]})\n")


interp.register_command(
    interp.CmdType(
        name="fightstyle",
        cmd_fun=cmd_fightstyle,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
