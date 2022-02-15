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


def cmd_mset(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    arg3 = argument

    if not arg1 or not arg2 or not arg3:
        ch.send("Syntax: mset <victim> <field>  <value>\n"
                "or:     mset <victim> <string> <value>\n\n"
                "Field being one of:\n"
                "  str int wis dex con sex level exp\n"
                "  gold hp mana move primal align\n"
                "  hit dam ac\n\n"
                "String being one of:\n"
                "  name short long description title spec\n")
        return

    victim = ch.get_char_world(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    # Snarf the value (which need not be numeric).
    value = int(arg3) if arg3.isdigit() else -1

    # Set something.
    if game_utils.str_cmp(arg2, "str"):
        if victim.is_npc():
            ch.not_npc()
            return

        if value not in merc.irange(3, 18):
            ch.send("Strength range is 3 to 18.\n")
            return

        if ch.is_judge():
            victim.perm_stat[merc.STAT_STR] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "int"):
        if victim.is_npc():
            ch.not_npc()
            return

        if value not in merc.irange(3, 18):
            ch.send("Intelligence range is 3 to 18.\n")
            return

        if ch.is_judge():
            victim.perm_stat[merc.STAT_INT] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "wis"):
        if victim.is_npc():
            ch.not_npc()
            return

        if value not in merc.irange(3, 18):
            ch.send("Wisdom range is 3 to 18.\n")
            return

        if ch.is_judge():
            victim.perm_stat[merc.STAT_WIS] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "dex"):
        if victim.is_npc():
            ch.not_npc()
            return

        if value not in merc.irange(3, 18):
            ch.send("Dexterity range is 3 to 18.\n")
            return

        if ch.is_judge():
            victim.perm_stat[merc.STAT_DEX] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "con"):
        if victim.is_npc():
            ch.not_npc()
            return

        if value not in merc.irange(3, 18):
            ch.send("Constitution range is 3 to 18.\n")
            return

        if ch.is_judge():
            victim.perm_stat[merc.STAT_CON] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "sex"):
        if value not in merc.irange(0, 2):
            ch.send("Sex range is 0 to 2.\n")
            return

        victim.sex = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "level"):
        if victim.is_npc() and value not in merc.irange(1, 250):
            ch.send("Level range is 1 to 250 for mobs.\n")
            return

        if not ch.is_judge():
            ch.send("Sorry, no can do...\n")
            return

        level_list = [("mortal", 2), ("avatar", 3), ("apprentice", 4), ("mage", 5), ("archmage", 6), ("builder", 7), ("questmaker", 8),
                      ("enforcer", 9), ("judge", 10), ("highjudge", 11)]
        for (aa, bb) in level_list:
            if game_utils.str_cmp(arg3, aa):
                value = bb
                break
        else:
            if not victim.is_npc():
                ch.send("Level should be one of the following:\n"
                        "Mortal, Avatar, Apprentice, Mage, Archmage, Builder, Questmaker, Enforcer,\n"
                        "Judge, or Highjudge.\n")
                return

        if value >= ch.level and not victim.is_npc():
            ch.send("Sorry, no can do...\n")
        else:
            victim.level = value
            ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, ["hitroll", "hit"]):
        smax = 50 if not victim.is_npc() else 250
        if value not in merc.irange(0, smax):
            ch.send(f"Hitroll range is 0 to {smax}.\n")
            return

        if not victim.is_npc() and not ch.is_judge() and ch != victim:
            ch.send("Sorry, no can do...\n")
            return

        victim.hitroll = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, ["damroll", "dam"]):
        smax = 50 if victim.is_npc() else 250
        if value not in merc.irange(0, smax):
            ch.send(f"Damroll range is 0 to {smax}.\n")
            return

        if not victim.is_npc() and not ch.is_judge() and ch != victim:
            ch.send("Sorry, no can do...\n")
            return

        victim.damroll = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, ["armor", "ac"]):
        if not victim.is_npc() and value not in merc.irange(-200, 200):
            ch.send("Armor class range is -200 to 200.\n")
            return

        if not victim.is_npc() and not ch.is_judge() and ch != victim:
            ch.send("Sorry, no can do...\n")
            return

        victim.armor = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "exp"):
        if victim.is_npc():
            ch.not_npc()
            return

        if value < 0:
            ch.send("Exp must be at least 0.\n")
            return

        if value > 500000:
            ch.send("No more than 500000 possible.\n")
            return

        if ch.is_judge() or ch == victim:
            victim.exp = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "gold"):
        if value > 100000 and not ch.is_judge():
            ch.send("Don't be so damn greedy!\n")
        else:
            victim.gold = value
            ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "hp"):
        if value not in merc.irange(1, 30000):
            ch.send("Hp range is 1 to 30,000 hit points.\n")
            return

        if ch.is_judge() or ch == victim or victim.is_npc():
            victim.max_hit = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "mana"):
        if value not in merc.irange(0, 30000):
            ch.send("Mana range is 0 to 30,000 mana points.\n")
            return

        if ch.is_judge() or ch == victim or victim.is_npc():
            victim.max_mana = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "move"):
        if value not in merc.irange(0, 30000):
            ch.send("Move range is 0 to 30,000 move points.\n")
            return

        if ch.is_judge() or ch == victim or victim.is_npc():
            victim.max_move = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "primal"):
        if value not in merc.irange(0, 100):
            ch.send("Primal range is 0 to 100.\n")
            return

        if ch.is_judge() or ch == victim:
            victim.practice = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "align"):
        if value not in merc.irange(-1000, 1000):
            ch.send("Alignment range is -1000 to 1000.\n")
            return

        victim.alignment = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "name"):
        if not victim.is_npc():
            ch.not_pc()
            return

        victim.name = arg3
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "short"):
        victim.short_descr = arg3
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "long"):
        victim.long_descr = arg3
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "title"):
        if victim.is_npc():
            ch.not_npc()
            return

        victim.title = arg3
        ch.send("Ok.\n")
        return

    """
    if game_utils.str_cmp(arg2, "spec"):
        if not victim.is_npc():
            ch.not_pc()
            return

        spec = state_checks.prefix_lookup(tables.spec_table)
        victim.spe
        if ( ( victim->spec_fun = spec_lookup( arg3 ) ) == 0 )
            ch.send("No such spec fun.\n")
            return

        ch.send("Ok.\n")
        return
    """

    # Generate usage message.
    ch.cmd_mset("")


interp.register_command(
    interp.CmdType(
        name="mset",
        cmd_fun=cmd_mset,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
