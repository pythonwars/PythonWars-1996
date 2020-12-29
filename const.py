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

from collections import OrderedDict, namedtuple

import comm
import merc
import settings

spell_lookup_dict = {}


def slot(i):
    return i


skill_type = namedtuple("skilltype", "name, skill_level, spell_fun, target, minimum_position, "
                                     "pgsn, slot, min_mana, beats, noun_damage, msg_off")
skill_table = OrderedDict()


def register_spell(entry: skill_type):
    skill_table[entry.name] = entry
    spell_lookup_dict[entry.name] = [entry.slot]

    if settings.DEBUG:
        comm.notify("    {}:{} registered in skill table".format(entry.slot, entry.name), merc.CONSOLE_BOOT)


class_type = namedtuple("class_type", "name, who_name, skill_adept, thac0_00, thac0_32")
class_table = OrderedDict()

# Attribute bonus structures.
str_app_type = namedtuple("str_app_type", "tohit, todam, carry, wield")
str_app = OrderedDict()

int_app_type = namedtuple("int_app_type", "learn")
int_app = OrderedDict()

wis_app_type = namedtuple("wis_app_type", "practice")
wis_app = OrderedDict()

dex_app_type = namedtuple("dex_app_type", "defensive")
dex_app = OrderedDict()

con_app_type = namedtuple("con_app_type", "hitp, shock")
con_app = OrderedDict()


# attack table  -- not very organized :(
attack_type = namedtuple("attack_type", "name, noun, damage")
attack_table = OrderedDict()

liq_type = namedtuple("liq_type", "name, color, proof, full, thirst")
liq_table = OrderedDict()

social_type = namedtuple("social_type", "name, char_no_arg, others_no_arg, char_found, others_found,"
                                        "vict_found, char_auto, others_auto")
social_table = OrderedDict()
