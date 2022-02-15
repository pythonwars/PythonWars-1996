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


def cmd_clandisc(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if ch.powers[merc.UNI_CURRENT] == -1:
        ch.powers[merc.UNI_CURRENT] = ch.powers[merc.UNI_AFF]

    clanmax = 10
    clancount = 0
    disc_list = [merc.VAM_PROTEAN, merc.VAM_CELERITY, merc.VAM_FORTITUDE, merc.VAM_POTENCE, merc.VAM_OBFUSCATE, merc.VAM_OBTENEBRATION,
                 merc.VAM_SERPENTIS, merc.VAM_AUSPEX, merc.VAM_DOMINATE, merc.VAM_PRESENCE]
    for disc in disc_list:
        if ch.vampaff.is_set(disc) or ch.vampass.is_set(disc):
            clancount += 1

    cost = 0 if clancount < 3 else (clancount - 2 * 10)
    if cost > 50:
        cost = 50

    if not arg:
        found = False
        buf = ["Current powers:"]
        disc_list = [(merc.VAM_PROTEAN, "Protean"), (merc.VAM_CELERITY, "Celerity"), (merc.VAM_FORTITUDE, "Fortitude"), (merc.VAM_POTENCE, "Potence"),
                     (merc.VAM_OBFUSCATE, "Obfuscate"), (merc.VAM_OBTENEBRATION, "Obtenebration"), (merc.VAM_SERPENTIS, "Serpentis"),
                     (merc.VAM_AUSPEX, "Auspex"), (merc.VAM_DOMINATE, "Dominate"), (merc.VAM_PRESENCE, "Presence")]
        for (aa, bb) in disc_list:
            if ch.vampaff.is_set(aa) and not ch.vamppass.is_set(aa):
                found = True
                buf += f" {bb}"
            elif ch.vampaff.is_set(aa):
                buf += f" {bb.upper()}"
                found = True

        if not found:
            buf += " None"
        buf += ".\n"
        ch.send("".join(buf))

        if clancount < clanmax:
            buf += f"It will cost you {cost} primal to gain another discipline.\n"

        if cost > ch.practice:
            ch.send("".join(buf))
            return

        buf += "Select from:"
        disc_list = [(merc.VAM_PROTEAN, "Protean"), (merc.VAM_CELERITY, "Celerity"), (merc.VAM_FORTITUDE, "Fortitude"), (merc.VAM_POTENCE, "Potence"),
                     (merc.VAM_OBFUSCATE, "Obfuscate"), (merc.VAM_OBTENEBRATION, "Obtenebration"), (merc.VAM_SERPENTIS, "Serpentis"),
                     (merc.VAM_AUSPEX, "Auspex"), (merc.VAM_DOMINATE, "Dominate"), (merc.VAM_PRESENCE, "Presence")]
        for (aa, bb) in disc_list:
            if not ch.vampaff.is_set(aa):
                buf += f" {bb}"
        ch.send("".join(buf))
        return

    if clancount >= clanmax:
        if game_utils.str_cmp(arg, "protean") and (ch.vampaff.is_set(merc.VAM_PROTEAN) or ch.vamppass.is_set(merc.VAM_PROTEAN)):
            ch.send("Powers: Nightsight, Claws, Change.\n")
        elif game_utils.str_cmp(arg, "celerity") and (ch.vampaff.is_set(merc.VAM_CELERITY) or ch.vamppass.is_set(merc.VAM_CELERITY)):
            ch.send("Powers: An extra attack, Reduced move cost for spells.\n")
        elif game_utils.str_cmp(arg, "fortitude") and (ch.vampaff.is_set(merc.VAM_FORTITUDE) or ch.vampass.is_set(merc.VAM_FORTITUDE)):
            ch.send("Powers: 1-100% damage reduction, +50 one time hp bonus.\n")
        elif game_utils.str_cmp(arg, "potence") and (ch.vampaff.is_set(merc.VAM_POTENCE) or ch.vampass.is_set(merc.VAM_POTENCE)):
            ch.send("Powers: 150% normal damage in combat.\n")
        elif game_utils.str_cmp(arg, "obfuscate") and (ch.vampaff.is_set(merc.VAM_OBFUSCATE) or ch.vampass.is_set(merc.VAM_OBFUSCATE)):
            ch.send("Powers: Mask, Mortal, Shield.\n")
        elif game_utils.str_cmp(arg, "obtenebration") and (ch.vampaff.is_set(merc.VAM_OBTENEBRATION) or ch.vampass.is_set(merc.VAM_OBTENEBRATION)):
            ch.send("Powers: Shadowplane, Shadowsight, Nightsight.\n")
        elif game_utils.str_cmp(arg, "serpentis") and (ch.vampaff.is_set(merc.VAM_SERPENTIS) or ch.vampass.is_set(merc.VAM_SERPENTIS)):
            ch.send("Powers: Darkheart, Serpent, Poison, Nightsight.\n")
        elif game_utils.str_cmp(arg, "auspex") and (ch.vampaff.is_set(merc.VAM_AUSPEX) or ch.vampass.is_set(merc.VAM_AUSPEX)):
            ch.send("Powers: Truesight, Scry, Readaura.\n")
        elif game_utils.str_cmp(arg, "dominate") and (ch.vampaff.is_set(merc.VAM_DOMINATE) or ch.vampass.is_set(merc.VAM_DOMINATE)):
            ch.send("Powers: Evileye, Command, Shield, Ghoul.\n")
        elif game_utils.str_cmp(arg, "presence") and (ch.vampaff.is_set(merc.VAM_PRESENCE) or ch.vampass.is_set(merc.VAM_PRESENCE)):
            ch.send("Powers: Majesty.\n")
        else:
            ch.send("You don't know any such Discipline.\n")
        return

    if game_utils.str_cmp(arg, "protean"):
        if ch.vampaff.is_set(merc.VAM_PROTEAN) or ch.vampass.is_set(merc.VAM_PROTEAN) or cost > ch.practice:
            ch.send("Powers: Nightsight, Claws, Change.\n")
            return

        ch.send("You master the discipline of Protean.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_PROTEAN)
        ch.vampaff.set_bit(merc.VAM_PROTEAN)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "celerity"):
        if ch.vampaff.is_set(merc.VAM_CELERITY) or ch.vampass.is_set(merc.VAM_CELERITY) or cost > ch.practice:
            ch.send("Powers: An extra attack, Reduced move cost for spells.\n")
            return

        ch.send("You master the discipline of Celerity.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_CELERITY)
        ch.vampaff.set_bit(merc.VAM_CELERITY)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "fortitude"):
        if ch.vampaff.is_set(merc.VAM_FORTITUDE) or ch.vampass.is_set(merc.VAM_FORTITUDE) or cost > ch.practice:
            ch.send("Powers: 1-100% damage reduction, +50 one time hp bonus.\n")
            return

        ch.send("You master the discipline of Fortitude.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_FORTITUDE)
        ch.vampaff.set_bit(merc.VAM_FORTITUDE)
        ch.practice -= cost
        ch.max_hit += 50
        ch.hit += 50
    elif game_utils.str_cmp(arg, "potence"):
        if ch.vampaff.is_set(merc.VAM_POTENCE) or ch.vampass.is_set(merc.VAM_POTENCE) or cost > ch.practice:
            ch.send("Powers: 150% normal damage in combat.\n")
            return

        ch.send("You master the discipline of Potence.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_POTENCE)
        ch.vampaff.set_bit(merc.VAM_POTENCE)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "obfuscate"):
        if ch.vampaff.is_set(merc.VAM_OBFUSCATE) or ch.vampass.is_set(merc.VAM_OBFUSCATE) or cost > ch.practice:
            ch.send("Powers: Mask, Mortal, Shield.\n")
            return

        ch.send("You master the discipline of Obfuscate.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_OBFUSCATE)
        ch.vampaff.set_bit(merc.VAM_OBFUSCATE)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "obtenebration"):
        if ch.vampaff.is_set(merc.VAM_OBTENEBRATION) or ch.vampass.is_set(merc.VAM_OBTENEBRATION) or cost > ch.practice:
            ch.send("Powers: Shadowplane, Shadowsight, Nightsight.\n")
            return

        ch.send("You master the discipline of Obtenebration.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_OBTENEBRATION)
        ch.vampaff.set_bit(merc.VAM_OBTENEBRATION)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "serpentis"):
        if ch.vampaff.is_set(merc.VAM_SERPENTIS) or ch.vampass.is_set(merc.VAM_SERPENTIS) or cost > ch.practice:
            ch.send("Powers: Darkheart, Serpent, Poison, Nightsight.\n")
            return

        ch.send("You master the discipline of Serpentis.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_SERPENTIS)
        ch.vampaff.set_bit(merc.VAM_SERPENTIS)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "auspex"):
        if ch.vampaff.is_set(merc.VAM_AUSPEX) or ch.vampass.is_set(merc.VAM_AUSPEX) or cost > ch.practice:
            ch.send("Powers: Truesight, Scry, Readaura.\n")
            return

        ch.send("You master the discipline of Auspex.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_AUSPEX)
        ch.vampaff.set_bit(merc.VAM_AUSPEX)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "dominate"):
        if ch.vampaff.is_set(merc.VAM_DOMINATE) or ch.vampass.is_set(merc.VAM_DOMINATE) or cost > ch.practice:
            ch.send("Powers: Evileye, Command, Shield, Ghoul.\n")
            return

        ch.send("You master the discipline of Dominate.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_DOMINATE)
        ch.vampaff.set_bit(merc.VAM_DOMINATE)
        ch.practice -= cost
    elif game_utils.str_cmp(arg, "presence"):
        if ch.vampaff.is_set(merc.VAM_PRESENCE) or ch.vampass.is_set(merc.VAM_PRESENCE) or cost > ch.practice:
            ch.send("Powers: Majesty.\n")
            return

        ch.send("You master the discipline of Presence.\n")

        if clancount < 3:
            ch.vampass.set_bit(merc.VAM_PRESENCE)
        ch.vampaff.set_bit(merc.VAM_PRESENCE)
        ch.practice -= cost
    else:
        ch.send("No such discipline.\n")


interp.register_command(
    interp.CmdType(
        name="clandisc",
        cmd_fun=cmd_clandisc,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
