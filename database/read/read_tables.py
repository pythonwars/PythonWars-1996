#  PythonWars->MOTU-Mud copyright © 2020 by Paul Penner. All rights reserved.
#  No claim of ownership is asserted over the Masters of the Universe brand, it
#  is purely a fan work. No part of this codebase may be used without written
#  permission.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
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

import json
import os

import comm
from database.tracker import tables
import merc
from settings import DEBUG, DATA_FLAG_DIR, DATA_EXTN


def read_tables(listener=None, loc=DATA_FLAG_DIR, extn=DATA_EXTN):
    if listener:
        # This means the game is running. Wipe the current data.
        comm.notify("Clearing all tables.", merc.CONSOLE_INFO)

        for tok in tables:
            comm.notify("    Clearing {}".format(tok.name), merc.CONSOLE_INFO)

            if not tok.filter:
                tok.table.clear()
            else:
                affected = tok.filter(tok.table)

                for k, v in tok.table.copy().items():
                    if k in affected:
                        del(tok.table[k])

        listener.send("Tables cleared. Rebuilding...\n")

    for tok in tables:
        path = "{}{}".format(os.path.join(loc, tok.name), extn)

        if DEBUG:
            comm.notify("        Loading {}({})".format(tok.name, path), merc.CONSOLE_INFO)

        if os.path.isfile(path):
            jso = ""
            with open(path, "r+") as fp:
                for line in fp:
                    jso += line

            data = json.loads(jso)
        else:
            comm.notify("    Failed to find file {}".format(path), merc.CONSOLE_ERROR)

            if listener:
                listener.send("Failed to load {}.\n".format(path))

            continue

        try:
            for k, v in data.items():
                if type(k) == str and k.isdigit():
                    k = int(k)

                if tok.tupletype:
                    tok.table[k] = tok.tupletype._make(v)
                else:
                    tok.table[k] = v
        except AttributeError:  # It's a list
            for v in data:
                tok.table.append(v)
