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


def cmd_majesty(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_PRESENCE):
        ch.send("You are not trained in the Presence discipline.\n")
        return

    if game_utils.str_cmp(arg1, "on"):
        if ch.extra.is_set(merc.EXTRA_FAKE_CON):
            ch.send("You already have Majesty on.\n")
            return

        ch.extra.set_bit(merc.EXTRA_FAKE_CON)
        ch.send("Your Majesty is now ON.\n")
        return

    if game_utils.str_cmp(arg1, "off"):
        if not ch.extra.is_set(merc.EXTRA_FAKE_CON):
            ch.send("You already have Majesty off.\n")
            return

        ch.extra.rem_bit(merc.EXTRA_FAKE_CON)
        ch.send("Your Majesty is now OFF.\n")
        return

    if not arg1 or not arg2:
        buf = ["You have the following stats:\n"]
        buf += f"Hitroll: {ch.fake_hit}, Actual: {ch.hitroll}.\n"
        buf += f"Damroll: {ch.fake_dam}, Actual: {ch.damroll}.\n"
        buf += f"Armour: {ch.fake_ac}, Actual: {ch.armor}.\n"
        buf += f"Hp: {ch.fake_hp}, Actual: {ch.hit}.\n"
        buf += f"Mana: {ch.fake_mana}, Actual: {ch.mana}.\n"
        buf += f"Move: {ch.fake_move}, Actual: {ch.move}.\n"
        ch.send("".join(buf))
        return

    value = int(arg2) if arg2.isdigit() else -10000
    if game_utils.str_cmp(arg1, ["hit", "hitroll"]):
        if value not in merc.irange(0, 1000):
            ch.send("Please enter a value between 0 and 1000.\n")
            return

        ch.fake_hit = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg1, ["dam", "damroll"]):
        if value not in merc.irange(0, 1000):
            ch.send("Please enter a value between 0 and 1000.\n")
            return

        ch.fake_dam = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg1, ["ac", "armour", "armor"]):
        if value not in merc.irange(-1000, 100):
            ch.send("Please enter a value between -1000 and 100.\n")
            return

        ch.fake_ac = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg1, ["hp", "hitpoints"]):
        if value not in merc.irange(1, 30000):
            ch.send("Please enter a value between 1 and 30000.\n")
            return

        ch.fake_hp = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg1, "mana"):
        if value not in merc.irange(1, 30000):
            ch.send("Please enter a value between 1 and 30000.\n")
            return

        ch.fake_mana = value
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg1, "move"):
        if value not in merc.irange(1, 30000):
            ch.send("Please enter a value between 1 and 30000.\n")
            return

        ch.fake_move = value
        ch.send("Ok.\n")
        return

    ch.send("You can set: Hit, Dam, Ac, Hp, Mana, Move.\n")


interp.register_command(
    interp.CmdType(
        name="majesty",
        cmd_fun=cmd_majesty,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
