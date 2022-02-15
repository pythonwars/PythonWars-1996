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

import comm
import game_utils
import handler_game
import interp
import merc


def count_imms(ch):
    count = 0
    imm_list = [merc.IMM_SLASH, merc.IMM_STAB, merc.IMM_SMASH, merc.IMM_ANIMAL, merc.IMM_MISC, merc.IMM_CHARM, merc.IMM_HEAT, merc.IMM_COLD,
                merc.IMM_LIGHTNING, merc.IMM_ACID, merc.IMM_SLEEP, merc.IMM_DRAIN, merc.IMM_VOODOO, merc.IMM_HURL, merc.IMM_BACKSTAB,
                merc.IMM_KICK, merc.IMM_DISARM, merc.IMM_STEAL]
    for imm in imm_list:
        if ch.immune.is_set(imm):
            count += 1
    return (count * 10000) + 10000


def cmd_train(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_npc():
        return

    last = True
    is_ok = False

    if not arg1:
        ch.send(f"You have {ch.exp:,} experience points.\n")
        arg1 = "foo"

    isok_list = ["str", "int", "wis", "dex", "con", "hp", "mana", "move", "primal"]
    for stat in isok_list:
        if game_utils.str_cmp(arg1, stat):
            is_ok = True
    else:
        if game_utils.str_cmp(arg1, "silver") and ch.is_werewolf():
            is_ok = True

    if arg2 and is_ok:
        if not arg2.isdigit():
            ch.send("Please enter a numeric value.\n")
            return

        amount = int(arg2)
        if amount not in merc.irange(1, 50):
            ch.send("Please enter a value between 1 and 50.\n")
            return

        if amount > 1:
            ch.cmd_train(f"{arg1} {amount - 1}")
            last = False

    cost = 200
    immcost = count_imms(ch)
    primal = (1 + ch.practice) * 500
    silver = (1 + ch.powers[merc.WPOWER_SILVER]) * 2500
    max_stat = 25 if ch.is_highlander() else 18

    if game_utils.str_cmp(arg1, "str"):
        pability = merc.STAT_STR
        poutput = "strength"
    elif game_utils.str_cmp(arg1, "int"):
        pability = merc.STAT_INT
        poutput = "intelligence"
    elif game_utils.str_cmp(arg1, "wis"):
        pability = merc.STAT_WIS
        poutput = "wisdom"
    elif game_utils.str_cmp(arg1, "dex"):
        pability = merc.STAT_DEX
        poutput = "dexterity"
    elif game_utils.str_cmp(arg1, "con"):
        pability = merc.STAT_CON
        poutput = "constitution"
    elif game_utils.str_cmp(arg1, "avatar") and ch.level == 2:
        cost = 1000
        pability = ch.level
        poutput = "level"
    elif game_utils.str_cmp(arg1, "hp") and ch.max_hit < 30000:
        cost = ch.max_hit - ch.perm_stat[merc.STAT_CON]
        pability = ch.max_hit
        poutput = "hp"
    elif game_utils.str_cmp(arg1, "mana") and ch.max_mana < 30000:
        cost = ch.max_mana - ch.perm_stat[merc.STAT_WIS]
        pability = ch.max_mana
        poutput = "mana"
    elif game_utils.str_cmp(arg1, "move") and ch.max_move < 30000:
        cost = ch.max_move - ch.perm_stat[merc.STAT_CON]
        pability = ch.max_move
        poutput = "move"
    elif game_utils.str_cmp(arg1, "primal") and ch.practice < 100:
        cost = primal
        pability = ch.practice
        poutput = "primal"
    elif game_utils.str_cmp(arg1, "silver") and ch.is_werewolf() and ch.powers[merc.WPOWER_SILVER] < 100:
        cost = silver
        pability = ch.powers[merc.WPOWER_SILVER]
        poutput = "tolerance to silver"
    else:
        imm_list = [("slash", merc.IMM_SLASH, "resistant to slashing and slicing weapons"), ("stab", merc.IMM_STAB, "resistant to stabbing and piercing weapons"),
                    ("smash", merc.IMM_SMASH, "resistant to blasting, pounding and crushing weapons"), ("beast", merc.IMM_ANIMAL, "resistant to claw and bite attacks"),
                    ("grab", merc.IMM_MISC, "resistant to grepping, sucking and whipping weapons"), ("charm", merc.IMM_CHARM, "immune to charm spells"),
                    ("heat", merc.IMM_HEAT, "immune to heat and fire spells"), ("cold", merc.IMM_COLD, "immune to cold spells"),
                    ("lightning", merc.IMM_LIGHTNING, "immune to lightning and electrical spells"), ("acid", merc.IMM_ACID, "immune to acid spells"),
                    ("sleep", merc.IMM_SLEEP, "immune to the sleep spell"), ("drain", merc.IMM_DRAIN, "immune to the energy drain spell"),
                    ("voodoo", merc.IMM_VOODOO, "immune to voodoo magic"), ("hurl", merc.IMM_HURL, "immune to being hurled"),
                    ("backstab", merc.IMM_BACKSTAB, "immune to being backstabbed"), ("kick", merc.IMM_KICK, "immune to being kicked"),
                    ("disarm", merc.IMM_DISARM, "immune to being disarmed"), ("steal", merc.IMM_STEAL, "immune to being stolen from")]
        for (aa, bb, cc) in imm_list:
            if game_utils.str_cmp(arg1, aa) and not ch.immune.is_set(bb):
                if ch.exp < immcost:
                    ch.send("You don't have enough exp.\n")
                    return

                ch.exp -= immcost
                ch.immune.set_bit(bb)
                ch.send(f"You are now {cc}.\n")
                return
        else:
            buf = ["You can train the following:\n"]
            buf += "Stats:"

            if ch.perm_stat[merc.STAT_STR] < max_stat:
                buf += " Str"

            if ch.perm_stat[merc.STAT_INT] < max_stat:
                buf += " Int"

            if ch.perm_stat[merc.STAT_WIS] < max_stat:
                buf += " Wis"

            if ch.perm_stat[merc.STAT_DEX] < max_stat:
                buf += " Dex"

            if ch.perm_stat[merc.STAT_CON] < max_stat:
                buf += " Con"

            if ch.perm_stat[merc.STAT_STR] >= max_stat and ch.perm_stat[merc.STAT_INT] >= max_stat and ch.perm_stat[merc.STAT_WIS] >= max_stat and \
                    ch.perm_stat[merc.STAT_DEX] >= max_stat and ch.perm_stat[merc.STAT_CON] >= max_stat:
                buf += " None left to train"
            buf += ".\n"

            if ch.level == 2:
                buf += "Become an avatar - 1000 exp.\n"

            if ch.max_hit < 30000:
                buf += f"Hp               - {ch.max_hit - ch.perm_stat[merc.STAT_CON]} exp per point.\n"

            if ch.max_mana < 30000:
                buf += f"Mana             - {ch.max_mana - ch.perm_stat[merc.STAT_WIS]} exp per point.\n"

            if ch.max_move < 30000:
                buf += f"Move             - {ch.max_move - ch.perm_stat[merc.STAT_CON]} exp per point.\n"

            if ch.practice < 100:
                buf += f"Primal           - {primal} exp per point of primal energy.\n"

            if ch.powers[merc.WPOWER_SILVER] < 100 and ch.is_werewolf():
                buf += f"Silver tolerance - {silver} exp per point of tolerance.\n"

            buf += f"Natural resistances and immunities - {immcost} exp each.\n"

            # Weapon resistance affects
            buf += "Weapon resistances:"
            found = False
            imm_list = [(merc.IMM_SLASH, " Slash"), (merc.IMM_STAB, " Stab"), (merc.IMM_SMASH, " Smash"), (merc.IMM_ANIMAL, " Beast"),
                        (merc.IMM_MISC, " Grab")]
            for (aa, bb) in imm_list:
                if not ch.immune.is_set(aa):
                    found = True
                    buf += bb
            else:
                if not found:
                    buf += " None left to learn.\n"
                else:
                    buf += ".\n"

            # Spell immunity affects
            buf += "Magical immunities:"
            found = False
            imm_list = [(merc.IMM_CHARM, " Charm"), (merc.IMM_HEAT, " Heat"), (merc.IMM_COLD, " Cold"), (merc.IMM_LIGHTNING, " Lightning"),
                        (merc.IMM_ACID, " Acid"), (merc.IMM_SLEEP, " Sleep"), (merc.IMM_DRAIN, " Drain"), (merc.IMM_VOODOO, " Voodoo")]
            for (aa, bb) in imm_list:
                if not ch.immune.is_set(aa):
                    found = True
                    buf += bb
            else:
                if not found:
                    buf += " None left to learn.\n"
                else:
                    buf += ".\n"

            # Skill immunity affects
            buf += "Skill immunities:"
            imm_list = [(merc.IMM_HURL, " Hurl"), (merc.IMM_BACKSTAB, " Backstab"), (merc.IMM_KICK, " Kick"), (merc.IMM_DISARM, " Disarm"),
                        (merc.IMM_STEAL, " Steal")]
            found = False
            for (aa, bb) in imm_list:
                if not ch.immune.is_set(aa):
                    found = True
                    buf += bb
            else:
                if not found:
                    buf += " None left to learn.\n"
                else:
                    buf += ".\n"

            ch.send("".join(buf))
            return

    if pability >= max_stat and game_utils.str_cmp(arg1, ["str", "int", "wis", "dex", "con"]):
        if last:
            handler_game.act("Your $T is already at maximum.", ch, None, poutput, merc.TO_CHAR)
        return

    if pability >= 30000 and game_utils.str_cmp(arg1, ["hp", "mana", "move"]):
        if last:
            handler_game.act("Your $T is already at maximum.", ch, None, poutput, merc.TO_CHAR)
        return

    if pability >= 100 and game_utils.str_cmp(arg1, ["primal", "silver"]):
        if last:
            handler_game.act("Your $T is already at maximum.", ch, None, poutput, merc.TO_CHAR)
        return

    if cost < 1:
        cost = 1

    if cost > ch.exp:
        if last:
            ch.send("You don't have enough exp.\n")
        return

    ch.exp -= cost

    if game_utils.str_cmp(arg1, "avatar"):
        ch.level = merc.LEVEL_AVATAR
    elif game_utils.str_cmp(arg1, "hp"):
        ch.max_hit += 1
    elif game_utils.str_cmp(arg1, "mana"):
        ch.max_mana += 1
    elif game_utils.str_cmp(arg1, "move"):
        ch.max_move += 1
    elif game_utils.str_cmp(arg1, "silver"):
        ch.powers[merc.WPOWER_SILVER] += 1
    elif game_utils.str_cmp(arg1, "primal"):
        ch.practice += 1
    else:
        ch.perm_stat[pability] += 1

    if game_utils.str_cmp(arg1, "avatar"):
        handler_game.act("You become an avatar!", ch, None, None, merc.TO_CHAR)
        comm.info(f"{ch.name} has become an avatar!")

        if ch.level < ch.trust:
            ch.level = ch.trust

        if not ch.is_npc() and ch.vampaff.is_set(merc.VAM_MORTAL):
            ch.mortalvamp("")
    elif last:
        handler_game.act("Your $T increases!", ch, None, poutput, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="train",
        cmd_fun=cmd_train,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
