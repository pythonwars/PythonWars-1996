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

import const
import interp
import merc


def obj_score(ch, item):
    buf = ["You are {}.\n".format(item.short_descr)]

    extra = item.item_attribute_names + " " + item.item_restriction_names
    buf += "Type {}, Extra flags {}.\n".format(item.item_type, extra)
    buf += "You weigh {} pounds and are worth {} gold coins.\n".format(item.weight, item.cost)

    if item.questmaker and item.questowner:
        buf += "You were created by {}, and are owned by {}.\n".format(item.questmaker, item.questowner)
    elif item.questmaker:
        buf += "You were created by {}.\n".format(item.questmaker)
    elif item.questowner:
        buf += "You are owned by {}.\n".format(item.questowner)

    itype = item.item_type
    if itype in [merc.ITEM_PILL, merc.ITEM_SCROLL, merc.ITEM_POTION]:
        buf += "Level {} spells of:".format(item.value[0])

        for i in item.value:
            if 0 <= i < merc.MAX_SKILL:
                buf += " '" + const.skill_table[i].name + "'"
        buf += ".\n"
    elif itype == merc.ITEM_QUEST:
        buf += "Your quest point value is {}.\n".format(item.value[0])
    elif itype in [merc.ITEM_WAND, merc.ITEM_STAFF]:
        buf += "You have {}({}) charges of level {}".format(item.value[1], item.value[2], item.value[0])

        if 0 <= item.value[3] <= merc.MAX_SKILL:
            buf += " '" + const.skill_table[item.value[3]].name + "'"
        buf += ".\n"
    elif itype == merc.ITEM_WEAPON:
        buf += "You inflict {} to {} damage in combat (average {}).\n".format(item.value[1], item.value[2], (item.value[1] + item.value[2]) // 2)

        if item.value[0] >= 1000:
            itemtype = item.value[0] - ((item.value[0] // 1000) * 1000)
        else:
            itemtype = item.value[0]

        if itemtype > 0:
            level_list = [(10, " minor"), (20, " lesser"), (30, "n average"), (40, " greater"), (50, " major"), (51, " supreme")]
            for (aa, bb) in level_list:
                if item.level < aa:
                    buf += "You are a{} spell weapon.\n".format(bb)
                    break
            else:
                buf += "You are an ultimate spell weapon.\n"

            if itemtype == 1:
                buf += "You are dripping with corrosive acid.\n"
            elif itemtype == 4:
                buf += "You radiates an aura of darkness.\n"
            elif itemtype == 30:
                buf += "You are the bane of all evil.\n"
            elif itemtype == 34:
                buf += "You drink the souls of your victims.\n"
            elif itemtype == 37:
                buf += "You have been tempered in hellfire.\n"
            elif itemtype == 48:
                buf += "You crackle with sparks of lightning.\n"
            elif itemtype == 53:
                buf += "You are dripping with a dark poison.\n"
            else:
                buf += "You have been imbued with the power of {}.\n".format(const.skill_table[itemtype].name)

        itemtype = item.value[0] // 1000 if item.value[0] >= 1000 else 0
        if itemtype > 0:
            if itemtype == 4:
                buf += "You radiate an aura of darkness.\n"
            elif itemtype in [27, 2]:
                buf += "You a allow your wielder to see invisible things.\n"
            elif itemtype in [39, 3]:
                buf += "You grant your wielder the power of flight.\n"
            elif itemtype in [45, 1]:
                buf += "You allow your wielder to see in the dark.\n"
            elif itemtype in [46, 5]:
                buf += "You render your wielder invisible to the human eye.\n"
            elif itemtype in [52, 6]:
                buf += "You allow your wielder to walk through solid doors.\n"
            elif itemtype in [54, 7]:
                buf += "You protect your wielder from evil.\n"
            elif itemtype in [57, 8]:
                buf += "You protect your wielder in combat.\n"
            elif itemtype == 9:
                buf += "You allow your wielder to walk in complete silence.\n"
            elif itemtype == 10:
                buf += "You surround your wielder with a shield of lightning.\n"
            elif itemtype == 11:
                buf += "You surround your wielder with a shield of fire.\n"
            elif itemtype == 12:
                buf += "You surround your wielder with a shield of ice.\n"
            elif itemtype == 13:
                buf += "You surround your wielder with a shield of acid.\n"
            elif itemtype == 14:
                buf += "You protect your wielder from clan DarkBlade guardians.\n"
            elif itemtype == 15:
                buf += "You surround your wielder with a shield of chaos.\n"
            elif itemtype == 16:
                buf += "You regenerate the wounds of your wielder.\n"
            elif itemtype == 17:
                buf += "You enable your wielder to move at supernatural speed.\n"
            elif itemtype == 18:
                buf += "You can slice through armour without difficulty.\n"
            elif itemtype == 19:
                buf += "You protect your wielder from player attacks.\n"
            elif itemtype == 20:
                buf += "You surround your wielder with a shield of darkness.\n"
            elif itemtype == 21:
                buf += "You grant your wielder superior protection.\n"
            elif itemtype == 22:
                buf += "You grant your wielder supernatural vision.\n"
            elif itemtype == 23:
                buf += "You make your wielder fleet-footed.\n"
            elif itemtype == 24:
                buf += "You conceal your wielder from sight.\n"
            elif itemtype == 25:
                buf += "You invoke the power of your wielders beast.\n"
            else:
                buf += "You are bugged...please report it.\n"
    elif itype == merc.ITEM_ARMOR:
        buf += "Your armor class is {}.\n".format(item.value[0])

        if item.value[3] > 0:
            if item.value[3] == 4:
                buf += "You radiate an aura of darkness.\n"
            elif item.value[3] in [27, 2]:
                buf += "You allow your wearer to see invisible things.\n"
            elif item.value[3] in [39, 3]:
                buf += "You grant your wearer the power of flight.\n"
            elif item.value[3] in [45, 1]:
                buf += "You allow your wearer to see in the dark.\n"
            elif item.value[3] in [46, 5]:
                buf += "You allow your wearer invisible to the human eye.\n"
            elif item.value[3] in [52, 6]:
                buf += "You allow your wearer to walk through solid doors.\n"
            elif item.value[3] in [54, 7]:
                buf += "You protect your wearer from evil.\n"
            elif item.value[3] in [57, 8]:
                buf += "You protect your wearer in combat.\n"
            elif item.value[3] == 9:
                buf += "You allow your wearer to walk in complete silence.\n"
            elif item.value[3] == 10:
                buf += "You surround your wearer with a shield of lightning.\n"
            elif item.value[3] == 11:
                buf += "You surround your wearer with a shield of fire.\n"
            elif item.value[3] == 12:
                buf += "You surround your wearer with a shield of ice.\n"
            elif item.value[3] == 13:
                buf += "You surround your wearer with a shield of acid.\n"
            elif item.value[3] == 14:
                buf += "You protect your wearer from clan DarkBlade guardians.\n"
            elif item.value[3] == 15:
                buf += "You surround your wearer with a shield of chaos.\n"
            elif item.value[3] == 16:
                buf += "You regnerate the wounds of your wearer.\n"
            elif item.value[3] == 17:
                buf += "You enable your wearer to move at supernatural speed.\n"
            elif item.value[3] == 18:
                buf += "You can slice through armour without difficulty.\n"
            elif item.value[3] == 19:
                buf += "You protect your wearer from player attacks.\n"
            elif item.value[3] == 20:
                buf += "You surround your wearer with a shield of darkness.\n"
            elif item.value[3] == 21:
                buf += "You grant your wearer superior protection.\n"
            elif item.value[3] == 22:
                buf += "You grant your wearer supernatural vision.\n"
            elif item.value[3] == 23:
                buf += "You make your wearer fleet-footed.\n"
            elif item.value[3] == 24:
                buf += "You conceal your wearer from sight.\n"
            elif item.value[3] == 25:
                buf += "You invoke the power of your wearers beast.\n"
            else:
                buf += "You are bugged...please report it.\n"

    for aff in item.affected:
        if aff.location != merc.APPLY_NONE and aff.modifier != 0:
            buf += "You affect {} by {}.\n".format(merc.affect_loc_name(aff.location), aff.modifier)
    ch.send("".join(buf))


# noinspection PyUnusedLocal
def cmd_score(ch, argument):
    if not ch.is_npc() and (ch.extra.is_set(merc.EXTRA_OSWITCH) or ch.head.is_set(merc.LOST_HEAD)):
        obj_score(ch, ch.chobj)
        return

    buf = ["You are {}{}.  You have been playing for {} hours.\n".format(ch.name, "" if ch.is_npc() else ch.title,
                                                                         (ch.get_age() - 17) * 2)]

    if not ch.is_npc():
        buf += ch.other_age(is_self=True)

    if ch.trust != ch.level:
        buf += "You are trusted at level {}.\n".format(ch.trust)

    buf += "You have {}/{} hit, {}/{} mana, {}/{} movement, {} primal energy.\n".format(ch.hit, ch.max_hit, ch.mana, ch.max_mana, ch.move,
                                                                                        ch.max_move, ch.practice)
    buf += "You are carrying {}/{} items with weight {}/{} kg.\n".format(ch.carry_number, ch.can_carry_n(), ch.carry_weight, ch.can_carry_w())
    buf += "Str: {}  Int: {}  Wis: {}  Dex: {}  Con: {}.\n".format(ch.stat(merc.STAT_STR), ch.stat(merc.STAT_INT), ch.stat(merc.STAT_WIS),
                                                                   ch.stat(merc.STAT_DEX), ch.stat(merc.STAT_CON))
    buf += "You have scored {} exp, and have {} gold coins.\n".format(ch.exp, ch.gold)

    if not ch.is_npc() and (ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION)):
        buf += "You have {} out of {} points of demonic power stored.\n".format(ch.powers[merc.DEMON_CURRENT], ch.powers[merc.DEMON_TOTAL])

    buf += "Autoexit: {}.  Autoloot: {}.  Autosac: {}.\n".format("yes" if (not ch.is_npc() and ch.act.is_set(merc.PLR_AUTOEXIT)) else "no",
                                                                 "yes" if (not ch.is_npc() and ch.act.is_set(merc.PLR_AUTOLOOT)) else "no",
                                                                 "yes" if (not ch.is_npc() and ch.act.is_set(merc.PLR_AUTOSAC)) else "no")
    buf += "Wimpy set to {} hit points.\n".format(ch.wimpy)

    pos_list = [(merc.POS_DEAD, "DEAD!!"), (merc.POS_MORTAL, "mortally wounded."), (merc.POS_INCAP, "incapacitated."),
                (merc.POS_STUNNED, "stunned."), (merc.POS_SLEEPING, "sleeping."), (merc.POS_RESTING, "resting."),
                (merc.POS_MEDITATING, "meditating."), (merc.POS_SITTING, "sitting."), (merc.POS_STANDING, "standing."),
                (merc.POS_FIGHTING, "fighting.")]
    for (aa, bb) in pos_list:
        if ch.position == aa:
            buf += "You are {}\n".format(bb)
            break

    buf += "AC: {}.  You are ".format(ch.armor)
    ac_list = [(101, "naked!\n"), (80, "barely clothed.\n"), (60, "wearing clothes.\n"), (40, "slightly armored.\n"),
               (20, "somewhat armored.\n"), (0, "armored.\n"), (-50, "well armored.\n"), (-100, "strongly armored.\n"),
               (-250, "heavily armored.\n"), (-500, "superbly armored.\n"), (-749, "divinely armored.\n")]
    for (aa, bb) in ac_list:
        if ch.armor >= aa:
            buf += bb
            break
    else:
        buf += "ultimately armored!\n"

    buf += "Hitroll: {}.  Damroll: {}.  ".format(ch.hitroll, ch.damroll)

    if not ch.is_npc() and ch.is_vampire():
        buf += "Blood: %d.\n".format(ch.blood)
        buf += "Beast: {}.  ".format(ch.beast)

        beast_list = [(0, "You have attained Golconda!\n"), (5, "You have almost reached Golconda!\n"), (10, "You are nearing Golconda!\n"),
                      (15, "You have great control over your beast.\n"), (20, "Your beast has little influence over your actions.\n"),
                      (30, "You are in control of your beast.\n"), (40, "You are able to hold back the beast.\n"),
                      (60, "You are constantly struggling for control of your beast.\n"), (75, "Your beast has great control over your actions.\n"),
                      (90, "The power of the beast overwhelms you.\n"), (99, "You have almost lost your battle with the beast!\n")]
        for (aa, bb) in beast_list:
            if ch.beast <= aa:
                buf += bb
                break
        else:
            buf += "The beast has taken over!\n"
    else:
        buf += "\n"

    buf += "Alignment: {}.  You are ".format(ch.alignment)
    align_list = [(900, "angelic.\n"), (700, "saintly.\n"), (350, "good.\n"), (100, "kind.\n"), (-100, "neutral.\n"), (-350, "mean.\n"),
                  (-700, "evil.\n"), (-900, "demonic.\n")]
    for (aa, bb) in align_list:
        if ch.alignment > aa:
            buf += bb
            break
    else:
        buf += "satanic.\n"

    if not ch.is_npc():
        buf += "Status: {}.  You are ".format(ch.race)

        if ch.level == 1:
            buf += "a Mortal.\n"
        elif ch.level == 2:
            buf += "a Mortal.\n"
        elif ch.level == 7:
            buf += "a Builder.\n"
        elif ch.level == 8:
            buf += "a Quest Maker.\n"
        elif ch.level == 9:
            buf += "an Enforcer.\n"
        elif ch.level == 10:
            buf += "a Judge.\n"
        elif ch.level == 11:
            buf += "a High Judge.\n"
        elif ch.level == 12:
            buf += "an Implementor.\n"
        elif ch.race <= 0:
            buf += "an Avatar.\n"
        elif ch.race <= 4:
            buf += "an Immortal.\n"
        elif ch.race <= 9:
            buf += "a Godling.\n"
        elif ch.race <= 14:
            buf += "a Demigod.\n"
        elif ch.race <= 19:
            buf += "a Lesser God.\n"
        elif ch.race <= 24:
            buf += "a Greater God.\n"
        else:
            buf += "a Supreme God.\n"

        if ch.pkill == 0:
            ss1 = "no players"
        elif ch.pkill == 1:
            ss1 = "{} player".format(ch.pkill)
        else:
            ss1 = "{} players".format(ch.pkill)
        if ch.pdeath == 0:
            ss2 = "no players"
        elif ch.pdeath == 1:
            ss2 = "{} player".format(ch.pdeath)
        else:
            ss2 = "{} players".format(ch.pdeath)
        buf += "You have killed {} and have been killed by {}.\n".format(ss1, ss2)

        if ch.mkill == 0:
            ss1 = "no mobs"
        elif ch.mkill == 1:
            ss1 = "{} mob".format(ch.mkill)
        else:
            ss1 = "{} mobs".format(ch.mkill)
        if ch.mdeath == 0:
            ss2 = "no mobs"
        elif ch.mdeath == 1:
            ss2 = "{} mob".format(ch.mdeath)
        else:
            ss2 = "{} mobs".format(ch.mdeath)
        buf += "You have killed {} and have been killed by {}.\n".format(ss1, ss2)

        if ch.quest > 0:
            if ch.quest == 1:
                buf += "You have a single quest point.\n"
            else:
                buf += "You have {} quest points.\n".format(ch.quest)

    if ch.is_affected(merc.AFF_HIDE):
        buf += "You are keeping yourself hidden from those around you.\n"

    if not ch.is_npc():
        if ch.is_werewolf() and ch.powers[merc.WPOWER_SILVER] > 0:
            buf += "You have attained {} points of silver tolerance.\n".format(ch.powers[merc.WPOWER_SILVER])

        if ch.is_vampire() and ch.powers[merc.UNI_RAGE] > 0:
            buf += "The beast is in control of your actions:  Affects Hitroll and Damroll by +{}.\n".format(ch.powers[merc.UNI_RAGE])
        elif ch.special.is_set(merc.SPC_WOLFMAN) and ch.powers[merc.UNI_RAGE] > 0:
            buf += "You are raging:  Affects Hitroll and Damroll by +{}.\n".format(ch.powers[merc.UNI_RAGE])
        elif ch.is_demon() and ch.powers[merc.DEMON_POWER] > 0:
            buf += "You are wearing demonic armour:  Affects Hitroll and Damroll by +{}.\n".format(ch.powers[merc.DEMON_POWER] *
                                                                                                   ch.powers[merc.DEMON_POWER])
        elif ch.special.is_set(merc.SPC_CHAMPION) and ch.powers[merc.DEMON_POWER] > 0:
            buf += "You are wearing demonic armour:  Affects Hitroll and Damroll by +{}.\n".format(ch.powers[merc.DEMON_POWER] *
                                                                                                   ch.powers[merc.DEMON_POWER])

    if ch.affected:
        buf += "You are affected by:\n"

        for paf in ch.affected:
            buf += "Spell: '{}'".format(const.skill_table[paf.type].name)
            buf += " modifies {} by {} for {} hours with bits {}.\n".format(merc.affect_loc_name(paf.location), paf.modifier, paf.duration,
                                                                            merc.affect_bit_name(paf.bitvector))
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="score",
        cmd_fun=cmd_score,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
