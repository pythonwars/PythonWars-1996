#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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

import const
import instance
import merc


class Inventory:
    def __init__(self):
        super().__init__()
        self.inventory = []
        self.carry_weight = 0
        self.carry_number = 0

    @property
    def people(self):
        return tuple(char_id for char_id in self.inventory if char_id in instance.characters)

    @property
    def items(self):
        return tuple(item_id for item_id in self.inventory if item_id in instance.items)

    # Retrieve a character's carry capacity.
    def can_carry_n(self):
        # noinspection PyUnresolvedReferences
        if not self.is_npc() and self.is_immortal():
            return 1000

        # noinspection PyUnresolvedReferences
        if self.is_npc() and self.act.is_set(merc.ACT_PET):
            return 0

        # noinspection PyUnresolvedReferences
        return merc.MAX_WEAR + 2 * self.stat(merc.STAT_DEX) // 3

    # Retrieve a character's carry capacity.
    def can_carry_w(self):
        # noinspection PyUnresolvedReferences
        if not self.is_npc() and self.is_immortal():
            return 10000000

        # noinspection PyUnresolvedReferences
        if self.is_npc() and self.act.is_set(merc.ACT_PET):
            return 0

        # noinspection PyUnresolvedReferences
        return const.str_app[self.stat(merc.STAT_STR)].carry
