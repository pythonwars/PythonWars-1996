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

import interp
import merc


# noinspection PyUnusedLocal
def cmd_upkeep(ch, argument):
    if ch.is_npc():
        return

    if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION):
        buf = ["--------------------------------------------------------------------------------\n"]
        buf += "                              -= Demonic powers =-\n"
        buf += "--------------------------------------------------------------------------------\n"

        if ch.powers[merc.DPOWER_FLAGS] < 1:
            buf += "You have no demonic powers.\n"

        if ch.dempower.is_set(merc.DEM_FANGS):
            if ch.vampaff.is_set(merc.VAM_FANGS):
                buf += "You have a pair of long pointed fangs extending from your gums.\n"
            else:
                buf += "You have a pair of long pointed fangs, but they are not currently extended.\n"

        if ch.dempower.is_set(merc.DEM_CLAWS):
            if ch.vampaff.is_set(merc.VAM_CLAWS):
                buf += "You have a pair of razor sharp claws extending from your fingers.\n"
            else:
                buf += "You have a pair of razor sharp claws, but they are not currently extended.\n"

        if ch.dempower.is_set(merc.DEM_HORNS):
            if ch.demaff.is_set(merc.DEM_HORNS):
                buf += "You have a pair of curved horns extending from your forehead.\n"
            else:
                buf += "You have a pair of curved horns, but they are not currently extended.\n"

        if ch.dempower.is_set(merc.DEM_HOOVES):
            if ch.demaff.is_set(merc.DEM_HOOVES):
                buf += "You have hooves instead of feet.\n"
            else:
                buf += "You are able to transform your feet into hooves at will.\n"

        if ch.dempower.is_set(merc.DEM_EYES):
            if ch.vampaff.is_set(merc.VAM_NIGHTSIGHT):
                buf += "Your eyes are glowing bright red, allowing you to see in the dark.\n"
            else:
                buf += "You are able to see in the dark, although that power is not currently activated.\n"

        if ch.dempower.is_set(merc.DEM_WINGS):
            if not ch.demaff.is_set(merc.DEM_WINGS):
                buf += "You have the ability to extend wings from your back.\n"
            elif ch.demaff.is_set(merc.DEM_UNFOLDED):
                buf += "You have a pair of large leathery wings unfolded behind your back.\n"
            else:
                buf += "You have a pair of large leathery wings folded behind your back.\n"

        if ch.dempower.is_set(merc.DEM_MIGHT):
            buf += "Your muscles ripple with supernatural strength.\n"

        if ch.dempower.is_set(merc.DEM_TOUGH):
            buf += "Your skin reflects blows with supernatural toughness.\n"

        if ch.dempower.is_set(merc.DEM_SPEED):
            buf += "You move with supernatural speed and grace.\n"

        if ch.dempower.is_set(merc.DEM_TRAVEL):
            buf += "You are able to travel to other demons at will.\n"

        if ch.dempower.is_set(merc.DEM_SCRY):
            buf += "You are able to scry over great distances at will.\n"

        if ch.dempower.is_set(merc.DEM_SHADOWSIGHT):
            if ch.is_affected(merc.AFF_SHADOWSIGHT):
                buf += "You are able see things in the shadowplane.\n"
            else:
                buf += "You are able to view the shadowplane, although you are not currently doing so.\n"

        ch.send("".join(buf))
    elif ch.is_vampire():
        buf = ["--------------------------------------------------------------------------------\n"]
        buf += "                              -= Vampire upkeep =-\n"
        buf += "--------------------------------------------------------------------------------\n"
        buf += "Staying alive...upkeep 1.\n"

        if ch.vampaff.is_set(merc.VAM_DISGUISED):
            if ch.beast == 0:
                buf += "You are disguised as {}...no upkeep.\n".format(ch.morph)
            elif ch.beast == 100:
                buf += "You are disguised as {}...upkeep 10-20.\n".format(ch.morph)
            else:
                buf += "You are disguised as {}...upkeep 5-10.\n".format(ch.name)

        if ch.immune.is_set(merc.IMM_SHIELDED):
            if ch.beast == 0:
                buf += "You are shielded...no upkeep.\n"
            elif ch.beast == 100:
                buf += "You are shielded...upkeep 2-6.\n"
            else:
                buf += "You are shielded...upkeep 1-3.\n"

        if ch.is_affected(merc.AFF_SHADOWPLANE):
            buf += "You are in the shadowplane...no upkeep.\n"

        if ch.vampaff.is_set(merc.VAM_FANGS):
            if ch.beast == 0:
                buf += "You have your fangs out...no upkeep.\n"
            elif ch.beast == 100:
                buf += "You have your fangs out...upkeep 2.\n"
            else:
                buf += "You have your fangs out...upkeep 1.\n"

        if ch.vampaff.is_set(merc.VAM_CLAWS):
            if ch.beast == 0:
                buf += "You have your claws out...no upkeep.\n"
            elif ch.beast == 100:
                buf += "You have your claws out...upkeep 2-6.\n"
            else:
                buf += "You have your claws out...upkeep 1-3.\n"

        if ch.vampaff.is_set(merc.VAM_NIGHTSIGHT):
            if ch.beast == 0:
                buf += "You have nightsight...no upkeep.\n"
            elif ch.beast == 100:
                buf += "You have nightsight...upkeep 2.\n"
            else:
                buf += "You have nightsight...upkeep 1.\n"

        if ch.is_affected(merc.AFF_SHADOWPLANE):
            if ch.beast == 0:
                buf += "You have shadowsight...no upkeep.\n"
            elif ch.beast == 100:
                buf += "You are shadowsight...upkeep 2-6.\n"
            else:
                buf += "You are shadowsight...upkeep 1-3.\n"

        if ch.act.is_set(merc.PLR_HOLYLIGHT):
            if ch.beast == 0:
                buf += "You have truesight...no upkeep.\n"
            elif ch.beast == 100:
                buf += "You have truesight...upkeep 2-10.\n"
            else:
                buf += "You have truesight...upkeep 1-5.\n"

        if ch.vampaff.is_set(merc.VAM_CHANGED):
            if ch.polyaff.is_set(merc.POLY_BAT):
                poly = "bat"
            elif ch.polyaff.is_set(merc.POLY_WOLF):
                poly = "wolf"
            else:
                poly = "mist"

            if ch.beast == 0:
                buf += "You have changed into {} form...no upkeep.\n".format(poly)
            elif ch.beast == 100:
                buf += "You have changed into {} form...upkeep 10-20.\n".format(poly)
            else:
                buf += "You have changed into {} form...upkeep 5-10.\n".format(poly)

        if ch.polyaff.is_set(merc.POLY_SERPENT):
            if ch.beast == 0:
                buf += "You are in serpent form...no upkeep.\n"
            elif ch.beast == 100:
                buf += "You are in serpent form...upkeep 6-8.\n"
            else:
                buf += "You are in serpent form...upkeep 1-3.\n"

        ch.send("".join(buf))
    else:
        ch.huh()


interp.register_command(
    interp.CmdType(
        name="upkeep",
        cmd_fun=cmd_upkeep,
        position=merc.POS_DEAD, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
