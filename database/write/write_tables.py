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
from settings import DATA_EXTN, DATA_FLAG_DIR


def write_tables(listener=None, loc=DATA_FLAG_DIR, extn=DATA_EXTN):
    comm.notify("    Writing Tables", merc.CONSOLE_INFO)

    if listener:
        listener.send("Writing tables...\n")

    os.makedirs(loc, 0o755, True)

    for tok in tables:
        path = "{}{}".format(os.path.join(loc, tok.name), extn)
        comm.notify("        Writing {}({})".format(tok.name, path), merc.CONSOLE_INFO)

        if listener:
            listener.send("\t{}\n".format(tok.name))

        write_table(path, tok)


def write_table(path, tok):
    with open(path, "w") as fp:
        if tok.filter:
            fp.write(json.dumps(tok.filter(tok.table), indent=2, sort_keys=True))
        else:
            fp.write(json.dumps(tok.table, indent=2, sort_keys=True))
