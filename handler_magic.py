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

import comm
import const
import fight
import game_utils
import handler_game
import merc
import state_checks


# Magic functions
def say_spell(ch, spell):
    """
    syl_dict = {"ar": "abra", "au": "kada", "bless": "fido", "blind": "nose", "bur": "mosa", "cu": "judi", "de": "oculo", "en": "unso",
                "light": "dies", "lo": "hi", "mor": "zak", "move": "sido", "ness": "lacri", "ning": "illa", "per": "duda",  "ra": "gru",
                "re": "candus", "son": "sabru", "tect": "infra", "tri": "cula", "ven": "nofo",
                "a": "a", "b": "b", "c": "q", "d": "e", "e": "z", "f": "y", "g": "o", "h": "p", "i": "u", "j": "y", "k": "t", "l": "r",
                "m": "w", "n": "i", "o": "a", "p": "s", "q": "d", "r": "f", "s": "g", "t": "h", "u": "j", "v": "z", "w": "x", "x": "n",
                "y": "l", "z": "k"}
    spell_name = game_utils.mass_replace(spell.name, syl_dict)

    buf1 = "$n utters the words, '{}'.".format(spell_name)
    buf2 = "$n utters the words, '{}'.".format(spell.name)
    """

    color_list = [(merc.PURPLE_MAGIC, "#M", "purple"), (merc.RED_MAGIC, "#R", "red"), (merc.BLUE_MAGIC, "#B", "blue"),
                  (merc.GREEN_MAGIC, "#G", "green"), (merc.YELLOW_MAGIC, "#Y", "yellow")]
    for (aa, bb, cc) in color_list:
        if spell.target == aa:
            handler_game.act(bb + "Your eyes glow bright $T for a moment.#n", ch, None, cc, merc.TO_CHAR)
            handler_game.act(bb + "$n's eyes glow bright $T for a moment.#n", ch, None, cc, merc.TO_ROOM)
            break


def saves_spell(level, victim):
    if not victim.is_npc():
        tsave = sum([victim.spl[0], victim.spl[1], victim.spl[2], victim.spl[3], victim.spl[4]]) * 0.05
        save = 50 + (tsave - level - victim.saving_throw) * 5
    else:
        save = 50 + (victim.level - level - victim.saving_throw) * 5
    save = state_checks.urange(15, save, 85)
    return game_utils.number_percent() < save


target_name = ''


# for finding mana costs -- temporary version
def mana_cost(ch, min_mana, level):
    if ch.level + 2 == level:
        return 1000
    return max(min_mana, (100 // (2 + ch.level - level)))


def find_spell(ch, name):
    # finds a spell the character can cast if possible
    from const import skill_table
    found = None
    if ch.is_npc():
        return state_checks.prefix_lookup(skill_table, name)
    for key, sn in skill_table.items():
        if key.startswith(name.lower()):
            if not found:
                found = sn
            if ch.level >= sn.skill_level and key in ch.learned:
                return sn
    return found


# Cast spells at targets using a magical object.
def obj_cast_spell(sn, level, ch, victim, obj):
    global target_name

    target = merc.TARGET_NONE
    if not sn:
        return

    if sn not in const.skill_table or not const.skill_table[sn].spell_fun:
        comm.notify("obj_cast_spell: bad sn {}".format(sn), merc.CONSOLE_ERROR)
        return

    sn = const.skill_table[sn]
    if sn.target == merc.TAR_IGNORE:
        vo = None
    elif sn.target == merc.TAR_CHAR_OFFENSIVE:
        if not victim:
            victim = ch.fighting

        if not victim:
            ch.send("You can't do that.\n")
            return

        vo = victim
        target = merc.TARGET_CHAR
    elif sn.target == merc.TAR_CHAR_DEFENSIVE:
        if not victim:
            victim = ch

        vo = victim
        target = merc.TARGET_CHAR
    elif sn.target == merc.TAR_CHAR_SELF:
        vo = ch
        target = merc.TARGET_CHAR
    elif sn.target == merc.TAR_OBJ_INV:
        if not obj:
            ch.send("You can't do that.\n")
            return
        vo = obj
        target = merc.TARGET_ITEM
    else:
        comm.notify("obj_cast_spell: bad target for sn {}".format(sn.name), merc.CONSOLE_ERROR)
        return

    target_name = ""
    sn.spell_fun(sn, level, ch, vo, target)

    if sn.target == merc.TAR_CHAR_OFFENSIVE and victim != ch and instance.characters[victim.master] != ch:
        for vch_id in ch.in_room.people[:]:
            vch = instance.characters[vch_id]

            if victim == vch and not victim.fighting:
                fight.multi_hit(victim, ch, merc.TYPE_UNDEFINED)
                break
