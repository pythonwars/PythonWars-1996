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
import handler_ch
import instance
import interp
import merc
import nanny


# New 'who' command originally by Alander of Rivers of Mud.
def cmd_who(ch, argument):
    ilevellower = 0
    ilevelupper = merc.MAX_LEVEL
    fclassrestrict = False
    fimmortalonly = False
    nmatch = 0

    # Parse arguments.
    while True:
        argument, arg = game_utils.read_word(argument)
        if not arg:
            break

        if arg.isdigit():
            ch.send("Enter 'Avatar' for level 3's, or 'God' for level 4's and 5's.\n")
            return

        if game_utils.str_cmp(arg, ["imm", "immortal", "ava", "avatar"]):
            fclassrestrict = True
        elif game_utils.str_cmp(arg, ["god", "imp"]):
            fimmortalonly = True
        else:
            ch.send("Enter 'Avatar' for level 3's, or 'God' for level 4's and 5's.\n")
            return

    class_str = ""

    # Now show matching chars.
    for d in instance.descriptor_list:
        # Check for match against restrictions.
        # Don't use trust as that exposes trusted mortals.
        if not d.is_connected(nanny.con_playing) or not ch.can_see(d.character):
            continue

        wch = handler_ch.ch_desc(d)
        if wch.level < ilevellower or wch.level > ilevelupper or \
                (fimmortalonly and wch.level < merc.LEVEL_IMMORTAL) or \
                (fclassrestrict and wch.level != merc.LEVEL_HERO):
            continue

        nmatch += 1

        # Figure out what to print for class.
        if (wch.head.is_set(merc.LOST_HEAD) or wch.extra.is_set(merc.EXTRA_OSWITCH)) and wch.chobj:
            if wch.chobj.vnum == merc.OBJ_VNUM_SEVERED_HEAD:
                title = "A Head       "
            elif wch.chobj.vnum == merc.OBJ_VNUM_QUIVERING_BRAIN:
                title = "A Brain      "
            else:
                title = "An Object    "
        else:
            if wch.level == merc.MAX_LEVEL - 0:
                title = "Implementor  "
            elif wch.level == merc.MAX_LEVEL - 1:
                title = "High Judge   "
            elif wch.level == merc.MAX_LEVEL - 2:
                title = "Judge        "
            elif wch.level == merc.MAX_LEVEL - 3:
                title = "Enforcer     "
            elif wch.level == merc.MAX_LEVEL - 4:
                title = "Quest Maker  "
            elif wch.level == merc.MAX_LEVEL - 5:
                title = "Builder      "
            elif wch.level in [merc.MAX_LEVEL - 6, merc.MAX_LEVEL - 7, merc.MAX_LEVEL - 8,
                               merc.MAX_LEVEL - 9]:
                if wch.race <= 0:
                    title = "Avatar       "
                elif wch.race <= 4:
                    title = "Immortal     "
                elif wch.race <= 9:
                    title = "Godling      "
                elif wch.race <= 14:
                    title = "Demigod      "
                elif wch.race <= 19:
                    title = "Lesser God   "
                elif wch.race <= 24:
                    title = "Greater God  "
                else:
                    title = "Supreme God  "
            elif wch.level in [merc.MAX_LEVEL - 10, merc.MAX_LEVEL - 11, merc.MAX_LEVEL - 12]:
                title = "Mortal       "
            else:
                title = "Bugged       "

        if wch.is_vampire():
            openb = "<"
            closeb = ">"
        elif wch.is_werewolf():
            openb = "("
            closeb = ")"
        elif wch.is_demon():
            openb = "["
            closeb = "]"
        elif wch.is_mage():
            openb = "{"
            closeb = "}"
        else:
            openb = "["
            closeb = "]"

        if game_utils.str_cmp(wch.ch_class.name, "demon"):
            if wch.special.is_set(merc.SPC_DEMON_LORD):
                kav = ". {}Demon Lord{}".format(openb, closeb)
            else:
                if wch.special.is_set(merc.SPC_PRINCE):
                    kav = ". {}Demon Prince{}{}".format(openb, "ss" if wch.sex == merc.SEX_FEMALE else "",
                                                        closeb)
                elif wch.special.is_set(merc.SPC_SIRE):
                    kav = ". {}Demon{}".format(openb, closeb)
                else:
                    kav = ". {}Champion of {}{}".format(openb, wch.lord, closeb)
        elif game_utils.str_cmp(wch.ch_class.name, "vampire"):
            if wch.powers[merc.UNI_GEN] == 1:
                kav = ". {}Master Vampire{}".format(openb, closeb)
            elif wch.powers[merc.UNI_GEN] == 2:
                kav = ". {}Founder of {}{}".format(openb, wch.clan, closeb)
            elif wch.special.is_set(merc.SPC_PRINCE):
                kav = ". {}{} Prince{}{}".format(openb, wch.clan,
                                                 "ss" if wch.sex == merc.SEX_FEMALE else "", closeb)
            else:
                if wch.special.is_set(merc.SPC_INCONNU):
                    clanname = "Inconnu"
                elif wch.special.is_set(merc.SPC_ANARCH):
                    clanname = "Anarch"
                elif not wch.clan:
                    clanname = "Caitiff"
                else:
                    clanname = wch.clan

                if wch.powers[merc.UNI_GEN] == 2:
                    kav = ". {}{} Antediluvian{}".format(openb, clanname, closeb)
                else:
                    rank_list = [(merc.AGE_NEONATE, "Neonate"), (merc.AGE_ANCILLA, "Ancilla"), (merc.AGE_ELDER, "Elder"),
                                 (merc.AGE_METHUSELAH, "Methuselah")]
                    for (aa, bb) in rank_list:
                        if wch.rank == aa:
                            kav = ". {}{} {}{}".format(openb, clanname, bb, closeb)
                            break
                    else:
                        kav = ". {}{} Childe{}".format(openb, clanname, closeb)
        elif game_utils.str_cmp(wch.name, "werewolf"):
            if wch.powers[merc.UNI_GEN] == 1:
                kav = ". {}Master Werewolf{}".format(openb, closeb)
            elif wch.clan:
                if wch.powers[merc.UNI_GEN] == 2:
                    kav = ". {}{} Chief{}".format(openb, wch.clan, closeb)
                elif wch.special.is_set(merc.SPC_PRINCE):
                    kav = ". {}{} Shaman{}".format(openb, wch.clan, closeb)
                else:
                    kav = ". {}{}{}".format(openb, wch.clan, closeb)
            else:
                kav = ". {}Ronin{}".format(openb, closeb)
        elif game_utils.str_cmp(wch.ch_class.name, "mage"):
            mage_list = [(merc.RED_MAGIC, "Red"), (merc.BLUE_MAGIC, "Blue"), (merc.GREEN_MAGIC, "Green"), (merc.YELLOW_MAGIC, "Yellow")]
            for (aa, bb) in mage_list:
                if wch.powers[merc.MPOWER_RUNE0] == aa:
                    mage_col = bb
                    break
            else:
                mage_col = "Purple"

            if wch.level == merc.LEVEL_APPRENTICE:
                kav = ". {}{} Apprentice{}".format(openb, mage_col, closeb)
            elif wch.level == merc.LEVEL_MAGE:
                kav = ". {}{} Mage{}".format(openb, mage_col, closeb)
            else:
                kav = ". {}{} Archmage{}".format(openb, mage_col, closeb)
        elif game_utils.str_cmp(wch.ch_class.name, "highlander"):
            kav = ". {}Highlander{}".format(openb, closeb)
        else:
            kav = "."

        class_str += "{} {}{}{}\n".format(title, wch.name, wch.title, kav)

    buf = ["--------------------------------------------------------------------------------\n"]
    buf += class_str
    buf += "--------------------------------------------------------------------------------\n"

    if nmatch == 1:
        buf += "You are the only visible player connected!\n"
    else:
        buf += "There are a total of {} visible players connected.\n".format(nmatch)

    buf += "--------------------------------------------------------------------------------\n"
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="who",
        cmd_fun=cmd_who,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
