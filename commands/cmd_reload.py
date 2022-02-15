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
import hotfix
import interp
import merc


def cmd_reload(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        found = False

        buf = ["Files to be reloaded:\n"]
        for fp, pair in hotfix.modified_files.copy().items():
            found = True
            buf += f"  {fp}\n"

        if not found:
            buf += "  (none)\n"

        found = False
        buf += "\nFiles that can't be reloaded:\n"
        for fp, pair in hotfix.modunrel_files.copy().items():
            found = True
            buf += f"  {fp}\n"

        if not found:
            buf += "  (none)\n"

        found = False
        buf += "\nDeleted files:\n"
        for fp, pair in hotfix.deleted_files.copy().items():
            found = True
            buf += f"  {fp}\n"

        if not found:
            buf += "  (none)\n"

        ch.send("".join(buf))
        return

    if game_utils.str_cmp(arg, "now"):
        if len(hotfix.modified_files) < 1:
            ch.send("There are no files to reload.\n")
            return

        hotfix.reload_files(ch)
        ch.send("Files reloaded.\n")
        return

    ch.send("Usage: reload\n"
            "       reload now\n")


interp.register_command(
    interp.CmdType(
        name="reload",
        cmd_fun=cmd_reload,
        position=merc.POS_DEAD, level=12,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
