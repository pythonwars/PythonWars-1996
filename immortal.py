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

import merc


class Immortal:
    def __init__(self):
        super().__init__()
        self._trust = 0
        self.invis_level = 0
        self.incog_level = 0

    def is_immortal(self):
        return self.trust >= merc.LEVEL_IMMORTAL

    def is_hero(self):
        return self.trust >= merc.LEVEL_HERO

    def is_avatar(self):
        return self.trust >= merc.LEVEL_AVATAR

    def is_judge(self):
        return self.trust >= merc.LEVEL_JUDGE

    def is_implementor(self):
        return self.trust >= merc.LEVEL_IMPLEMENTOR

    # Retrieve a character's trusted level for permission checking.
    @property
    def trust(self):
        ch = self
        # noinspection PyUnresolvedReferences
        if self.desc and self.desc.original:
            # noinspection PyUnresolvedReferences
            ch = self.desc.original

        if ch._trust != 0:
            return ch._trust

        if ch.is_npc() and ch.level >= merc.LEVEL_HERO:
            return merc.LEVEL_HERO - 1

        return ch.level

    @trust.setter
    def trust(self, value):
        self._trust = int(value)
