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


def cmd_inpart(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if not arg1 or not arg2:
        ch.send("Syntax: Inpart <person> <power>\n"
                "Fangs (2500), Claws (2500), Horns (2500), Hooves (1500), Nightsight (3000),\n"
                "Wings (1000), Might (7500), Toughness (7500), Speed (7500), Travel (1500),\n"
                "Scry (7500), Shadowsight (7500), Move (500), Leap (500), Magic (1000),\n"
                "Lifespan (100), Pact (0), Prince (0), Longsword (0), Shortsword (0).\n")
        return

    victim = ch.get_char_world(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.level != merc.LEVEL_AVATAR or (victim != ch and not victim.special.is_set(merc.SPC_CHAMPION)):
        ch.send("Only on a champion.\n")
        return

    if victim != ch and not game_utils.str_cmp(victim.lord, ch.name) and not game_utils.str_cmp(victim.lord, ch.lord) and victim.lord:
        ch.send("They are not your champion.\n")
        return

    if game_utils.str_cmp(arg2, "pact"):
        if ch == victim:
            ch.not_self()
            return

        if victim.is_immortal():
            ch.not_imm()
            return

        if victim.special.is_set(merc.SPC_SIRE):
            victim.send("You have lost the power to make pacts!\n")
            ch.send("You remove their power to make pacts.\n")
            victim.special.rem_bit(merc.SPC_SIRE)
        else:
            victim.send("You have been granted the power to make pacts!\n")
            ch.send("You grant them the power to make pacts.\n")
            victim.special.set_bit(merc.SPC_SIRE)
        victim.save(force=True)
        return

    if game_utils.str_cmp(arg2, "prince"):
        if ch == victim:
            ch.not_self()
            return

        if not ch.is_demon():
            ch.send("Only the Demon Lord has the power to make princes.\n")
            return

        if victim.special.is_set(merc.SPC_PRINCE):
            victim.send("You have lost your princehood!\n")
            ch.send("You remove their princehood.\n")
            victim.special.rem_bit(merc.SPC_PRINCE)
        else:
            victim.send("You have been made a prince!\n")
            ch.send("You make them a prince.\n")
            victim.special.set_bit(merc.SPC_PRINCE)
        victim.save(force=True)
        return

    if game_utils.str_cmp(arg2, "longsword"):
        victim.send("You have been granted the power to transform into a demonic longsword!\n")
        ch.send("You grant them the power to transform into a demonic longsword.\n")
        victim.powers[merc.DPOWER_OBJ_VNUM] = 29662
        victim.save(force=True)
        return

    if game_utils.str_cmp(arg2, "shortsword"):
        victim.send("You have been granted the power to transform into a demonic shortsword!\n")
        ch.send("You grant them the power to transform into a demonic shortsword.\n")
        victim.powers[merc.DPOWER_OBJ_VNUM] = 29663
        victim.save(force=True)
        return

    inpart_list = [("fangs", merc.DEM_FANGS, 2500), ("claws", merc.DEM_CLAWS, 2500), ("horns", merc.DEM_HORNS, 2500), ("hooves", merc.DEM_HOOVES, 1500),
                   ("nightsight", merc.DEM_EYES, 3000), ("wings", merc.DEM_WINGS, 1000), ("might", merc.DEM_MIGHT, 7500),
                   ("toughness", merc.DEM_TOUGH, 7500), ("speed", merc.DEM_SPEED, 7500), ("travel", merc.DEM_TRAVEL, 1500),
                   ("scry", merc.DEM_SCRY, 7500), ("shadowsight", merc.DEM_SHADOWSIGHT, 3000), ("move", merc.DEM_MOVE, 500),
                   ("leap", merc.DEM_LEAP, 500), ("magic", merc.DEM_MAGIC, 1000), ("lifespan", merc.DEM_LIFESPAN, 100)]
    for (aa, bb, cc) in inpart_list:
        if game_utils.str_cmp(arg2, aa):
            inpart = bb
            cost = cc
            break
    else:
        ch.inpart("")
        return

    if victim.dempower.is_set(inpart):
        ch.send("They have already got that power.\n")
        return

    if ch.powers[merc.DEMON_TOTAL] < cost or ch.powers[merc.DEMON_CURRENT] < cost:
        ch.send("You have insufficient power to inpart that gift.\n")
        return

    victim.dempower.set_bit(inpart)
    ch.powers[merc.DEMON_TOTAL] -= cost
    ch.powers[merc.DEMON_CURRENT] -= cost

    if victim != ch:
        victim.send("You have been granted a demonic gift from your patron!\n")
        victim.save(force=True)

    ch.send("Ok.\n")
    ch.save(force=True)


interp.register_command(
    interp.CmdType(
        name="inpart",
        cmd_fun=cmd_inpart,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
