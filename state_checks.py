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


def is_set(flag, bit):
    return flag & bit


def set_bit(var, bit):
    return var | bit


def remove_bit(var, bit):
    return var & ~bit


# utility functions
def name_lookup(pdict, arg, key='name'):
    for i, n in pdict.items():
        if getattr(n, key) == arg:
            return i


def prefix_lookup(pdict, arg):
    if not arg:
        return None
    results = [v for k, v in pdict.items() if k.startswith(arg)]
    if results:
        return results[0]
    return None


def value_lookup(pdict, arg):
    if not arg:
        return None
    for k, v in pdict.items():
        if v == arg:
            return k


def urange(a, b, c):
    return a if b < a else c if b > c else b


def get_carry_weight(ch):
    return ch.carry_weight


# find an effect in an affect list
def affect_find(paf, sn):
    found = [paf_find for paf_find in paf if paf_find.type == sn][:1]
    return found[0] if found else None
