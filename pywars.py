#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
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

import logging
import os
import sys
import time

from comm import game_loop, init_descriptor, close_socket, notify
from hotfix import init_monitoring
import merc
from miniboa import TelnetServer
from settings import PORT


def boot_log(self, message, *args, **kws):
    if self.level <= 21:
        self._log(21, message, args, **kws)


sys.path.append(os.getcwd())
logging.addLevelName(21, "BOOT")
logging.Logger.boot = boot_log
logging.basicConfig(format="%(asctime)s %(levelname)-8s %(module)16s| %(message)s", level=21)
logger = logging.getLogger()

startup_time = time.time()
server = None


def pywars():
    global server

    sys.path.append(os.getcwd())

    server = TelnetServer(port=PORT)
    server.on_connect = init_descriptor
    server.on_disconnect = close_socket

    init_monitoring()
    game_loop(server)
    notify("Termination of game", merc.CONSOLE_CRITICAL)


if __name__ == "__main__":
    pywars()
