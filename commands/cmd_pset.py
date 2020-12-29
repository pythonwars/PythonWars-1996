#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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


def cmd_pset(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    argument, arg3 = game_utils.read_word(argument)

    if not arg1 or not arg2 or not arg3:
        ch.send("Syntax: pset <victim> <area> <field> <value>\n\n"
                "Area being one of:\n"
                "  quest quest+ quest- weapon immune beast\n"
                "  blue red yellow green purple\n"
                "  mongoose crane crab viper bull mantis\n"
                "  dragon tiger monkey swallow \n\n"
                "Field being one of:\n"
                "Weapon:  slice stab slash whip claw blast\n"
                "Weapon:  pound crush grep bite pierce suck\n"
                "Immune:  slash stab smash animal misc charm\n"
                "Immune:  heat cold acid summon voodoo\n"
                "Immune:  hurl backstab shielded kick disarm\n"
                "Immune:  steal sleep drain sunlight\n"
                "         all\n")
        return

    victim = ch.get_char_world(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.level < merc.NO_GODLESS:
        ch.send("You failed.\n")
        return

    # Snarf the value (which need not be numeric).
    value = int(arg3) if arg3.isdigit() else -1

    # Set something.
    if game_utils.str_cmp(arg2, "beast"):
        if value not in merc.irange(0, 100):
            ch.send("Beast range is 0 to 100.\n")
            return

        if ch.is_judge():
            victim.beast = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "quest"):
        if value not in merc.irange(1, 15000):
            ch.send("Quest range is 1 to 15000.\n")
            return

        if ch.is_judge():
            victim.quest = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "quest+"):
        if value not in merc.irange(1, 15000):
            ch.send("Quest range is 1 to 15000.\n")
            return

        if ch.is_judge():
            victim.quest += value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "quest-"):
        if value not in merc.irange(1, 15000):
            ch.send("Quest range is 1 to 15000.\n")
            return

        if ch.is_judge():
            victim.quest -= value

            if victim.quest < 0:
                victim.quest = 0

            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "viper"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Viper range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_VIPER] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "crane"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Crane range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_CRANE] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "crab"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Crab range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_CRAB] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "mongoose"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Mongoose range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_MONGOOSE] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "bull"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Bull range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_BULL] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "mantis"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Mantis range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_MANTIS] = value
            victim.stance[merc.STANCE_CRANE] = 200
            victim.stance[merc.STANCE_VIPER] = 200
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "dragon"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Dragon range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_DRAGON] = value
            victim.stance[merc.STANCE_CRAB] = 200
            victim.stance[merc.STANCE_BULL] = 200
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "tiger"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Tiger range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_TIGER] = value
            victim.stance[merc.STANCE_BULL] = 200
            victim.stance[merc.STANCE_VIPER] = 200
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "monkey"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Monkey range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_MONKEY] = value
            victim.stance[merc.STANCE_MONGOOSE] = 200
            victim.stance[merc.STANCE_CRANE] = 200
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "swallow"):
        if value not in merc.irange(0, 200):
            ch.send("Stance Swallow range is 0 to 200.\n")
            return

        if ch.is_judge():
            victim.stance[merc.STANCE_SWALLOW] = value
            victim.stance[merc.STANCE_CRAB] = 200
            victim.stance[merc.STANCE_MONGOOSE] = 200
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "purple"):
        smax = 240 if victim.is_mage() else 200
        if value not in merc.irange(4, smax):
            ch.send("Spell range is 4 to {}.\n".format(smax))
            return

        if ch.is_judge():
            victim.spl[merc.PURPLE_MAGIC] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "red"):
        smax = 240 if victim.is_mage() else 200
        if value not in merc.irange(4, smax):
            ch.send("Spell range is 4 to {}.\n".format(smax))
            return

        if ch.is_judge():
            victim.spl[merc.RED_MAGIC] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "blue"):
        smax = 240 if victim.is_mage() else 200
        if value not in merc.irange(4, smax):
            ch.send("Spell range is 4 to {}.\n".format(smax))
            return

        if ch.is_judge():
            victim.spl[merc.BLUE_MAGIC] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "blue"):
        smax = 240 if victim.is_mage() else 200
        if value not in merc.irange(4, smax):
            ch.send("Spell range is 4 to {}.\n".format(smax))
            return

        if ch.is_judge():
            victim.spl[merc.BLUE_MAGIC] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "yellow"):
        smax = 240 if victim.is_mage() else 200
        if value not in merc.irange(4, smax):
            ch.send("Spell range is 4 to {}.\n".format(smax))
            return

        if ch.is_judge():
            victim.spl[merc.YELLOW_MAGIC] = value
            ch.send("Ok.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "immune"):
        if not arg3:
            ch.send("pset <victim> immune <type>\n")
            return

        if ch.is_judge():
            if game_utils.str_cmp(arg3, "all"):
                victim.immune.set_bit(merc.IMM_DRAIN)
                victim.immune.set_bit(merc.IMM_VOODOO)
                victim.immune.set_bit(merc.IMM_SLASH)
                victim.immune.set_bit(merc.IMM_STAB)
                victim.immune.set_bit(merc.IMM_SMASH)
                victim.immune.set_bit(merc.IMM_ANIMAL)
                victim.immune.set_bit(merc.IMM_MISC)
                victim.immune.set_bit(merc.IMM_CHARM)
                victim.immune.set_bit(merc.IMM_HEAT)
                victim.immune.set_bit(merc.IMM_COLD)
                victim.immune.set_bit(merc.IMM_LIGHTNING)
                victim.immune.set_bit(merc.IMM_ACID)
                victim.immune.set_bit(merc.IMM_HURL)
                victim.immune.set_bit(merc.IMM_BACKSTAB)
                victim.immune.set_bit(merc.IMM_KICK)
                victim.immune.set_bit(merc.IMM_DISARM)
                victim.immune.set_bit(merc.IMM_STEAL)
                victim.immune.set_bit(merc.IMM_SLEEP)
                ch.send("All immunities added.\n")
            else:
                imm_list = [("voodoo", merc.IMM_VOODOO), ("slash", merc.IMM_SLASH), ("stab", merc.IMM_STAB), ("smash", merc.IMM_SMASH),
                            ("animal", merc.IMM_ANIMAL), ("misc", merc.IMM_MISC), ("charm", merc.IMM_CHARM), ("heat", merc.IMM_HEAT),
                            ("cold", merc.IMM_COLD), ("lightning", merc.IMM_LIGHTNING), ("acid", merc.IMM_ACID), ("shield", merc.IMM_SHIELDED),
                            ("hurl", merc.IMM_HURL), ("backstab", merc.IMM_BACKSTAB), ("kick", merc.IMM_KICK), ("disarm", merc.IMM_DISARM),
                            ("steal", merc.IMM_STEAL), ("sleep", merc.IMM_SLEEP), ("sunlight", merc.IMM_SUNLIGHT)]

                for (aa, bb) in imm_list:
                    if game_utils.str_cmp(arg3, aa):
                        victim.immune.tog_bit(bb)
                        if victim.immune.is_set(bb):
                            ch.send("Immunity added.\n")
                        else:
                            ch.send("Immunity removed.\n")
                        return
                else:
                    ch.send("No such immunity exists.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    if game_utils.str_cmp(arg2, "weapon"):
        argument, arg4 = game_utils.read_word(argument)

        # Snarf the value (which need not be numeric).
        value = int(arg4) if arg4.isdigit() else -1

        if value not in merc.irange(0, 200):
            ch.send("Weapon skill range is 0 to 200.\n")
            return

        if ch.is_judge():
            if game_utils.str_cmp(arg3, "all"):
                for i in merc.irange(merc.MAX_WPN):
                    victim.wpn[i] = value
                ch.send("Ok.\n")
            else:
                wpn_list = [("unarmed", merc.WPN_UNARMED), ("slice", merc.WPN_SLICE), ("stab", merc.WPN_STAB), ("slash", merc.WPN_SLASH),
                            ("whip", merc.WPN_WHIP), ("claw", merc.WPN_CLAW), ("blast", merc.WPN_BLAST), ("pound", merc.WPN_POUND),
                            ("crush", merc.WPN_CRUSH), ("grep", merc.WPN_GREP), ("bite", merc.WPN_BITE), ("pierce", merc.WPN_PIERCE),
                            ("suck", merc.WPN_SUCK)]
                for (aa, bb) in wpn_list:
                    if game_utils.str_cmp(arg3, aa):
                        victim.wpn[bb] = value
                        ch.send("Ok.\n")
                        return
                else:
                    ch.send("No such weapon skill exists.\n")
        else:
            ch.send("Sorry, no can do...\n")
        return

    # Generate usage message.
    ch.cmd_pset("")


interp.register_command(
    interp.CmdType(
        name="pset",
        cmd_fun=cmd_pset,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
