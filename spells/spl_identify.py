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
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_identify(sn, level, ch, victim, target):
    item = victim
    handler_game.act("You examine $p carefully.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n examines $p carefully.", ch, item, None, merc.TO_ROOM)

    extra = item.item_attribute_names
    if extra and item.item_restriction_names:
        extra += ", "
    extra += item.item_restriction_names
    buf = [f"Object '{item.name}' is type {item.item_type}, extra flags {extra}.\nWeight is {item.weight}, value is {item.cost}.\n"]

    if item.points > 0 and item.item_type not in [merc.ITEM_QUEST, merc.ITEM_PAGE]:
        buf += f"Quest point value is {item.points}.\n"

    if item.questmaker and item.questowner:
        buf += f"This object was created by {item.questmaker}, and is owned by {item.questowner}.\n"
    elif item.questmaker:
        buf += f"This object was created by {item.questmaker}.\n"
    elif item.questowner:
        buf += f"This object is owned by {item.questowner}.\n"

    if item.flags.enchanted:
        buf += "This item has been enchanted.\n"

    if item.flags.spellproof:
        buf += "This item is resistant to offensive spells.\n"

    if item.flags.demonic:
        buf += "This item is crafted from demonsteel.\n"
    elif item.flags.silver:
        buf += "This item is crafted from gleaming silver.\n"

    itype = item.item_type
    if itype in [merc.ITEM_PILL, merc.ITEM_SCROLL, merc.ITEM_POTION]:
        buf += f"Level {item.value[0]} spells of:"

        for i in item.value:
            if 0 <= i < merc.MAX_SKILL:
                buf += f" '{const.skill_table[i].name}'"
        buf += ".\n"
    elif itype == merc.ITEM_QUEST:
        buf += f"Quest point value is {item.value[0]}.\n"
    elif itype == merc.ITEM_QUESTCARD:
        buf += f"Quest completion reward is {item.level} quest points.\n"
    elif itype in [merc.ITEM_WAND, merc.ITEM_STAFF]:
        buf += f"Has {item.value[1]}({item.value[2]}) charges of level {item.value[0]}"

        if 0 <= item.value[3] <= merc.MAX_SKILL:
            buf += f" '{const.skill_table[item.value[3]].name}'"
        buf += ".\n"
    elif itype == merc.ITEM_WEAPON:
        buf += f"Damage is {item.value[1]} to {item.value[2]} (average {(item.value[1] + item.value[2]) // 2}).\n"

        if item.value[0] >= 1000:
            itemtype = item.value[0] - ((item.value[0] // 1000) * 1000)
        else:
            itemtype = item.value[0]

        if itemtype > 0:
            level_list = [(10, " minor"), (20, " lesser"), (30, "n average"), (40, " greater"), (50, " major"), (51, " supreme")]
            for (aa, bb) in level_list:
                if item.level < aa:
                    buf += f"{item.short_descr[0].upper() + item.short_descr[1:]} is a{bb} spell weapon.\n"
                    break
            else:
                buf += f"{item.short_descr[0].upper() + item.short_descr[1:]} is an ultimate spell weapon.\n"

            if itemtype == 1:
                buf += "This weapon is dripping with corrosive acid.\n"
            elif itemtype == 4:
                buf += "This weapon radiates an aura of darkness.\n"
            elif itemtype == 30:
                buf += "This ancient relic is the bane of all evil.\n"
            elif itemtype == 34:
                buf += "This vampiric weapon drinks the souls of its victims.\n"
            elif itemtype == 37:
                buf += "This weapon has been tempered in hellfire.\n"
            elif itemtype == 48:
                buf += "This weapon crackles with sparks of lightning.\n"
            elif itemtype == 53:
                buf += "This weapon is dripping with a dark poison.\n"
            else:
                buf += f"This weapon has been imbued with the power of {const.skill_table[itemtype].name}.\n"

        itemtype = item.value[0] // 1000 if item.value[0] >= 1000 else 0
        if itemtype > 0:
            if itemtype == 4:
                buf += "This weapon radiates an aura of darkness.\n"
            elif itemtype in [27, 2]:
                buf += "This weapon allows the wielder to see invisible things.\n"
            elif itemtype in [39, 3]:
                buf += "This weapon grants the power of flight.\n"
            elif itemtype in [45, 1]:
                buf += "This weapon allows the wielder to see in the dark.\n"
            elif itemtype in [46, 5]:
                buf += "This weapon renders the wielder invisible to the human eye.\n"
            elif itemtype in [52, 6]:
                buf += "This weapon allows the wielder to walk through solid doors.\n"
            elif itemtype in [54, 7]:
                buf += "This holy weapon protects the wielder from evil.\n"
            elif itemtype in [57, 8]:
                buf += "This ancient weapon protects the wielder in combat.\n"
            elif itemtype == 9:
                buf += "This crafty weapon allows the wielder to walk in complete silence.\n"
            elif itemtype == 10:
                buf += "This powerful weapon surrounds its wielder with a shield of lightning.\n"
            elif itemtype == 11:
                buf += "This powerful weapon surrounds its wielder with a shield of fire.\n"
            elif itemtype == 12:
                buf += "This powerful weapon surrounds its wielder with a shield of ice.\n"
            elif itemtype == 13:
                buf += "This powerful weapon surrounds its wielder with a shield of acid.\n"
            elif itemtype == 14:
                buf += "This weapon protects its wielder from clan DarkBlade guardians.\n"
            elif itemtype == 15:
                buf += "This ancient weapon surrounds its wielder with a shield of chaos.\n"
            elif itemtype == 16:
                buf += "This ancient weapon regenerates the wounds of its wielder.\n"
            elif itemtype == 17:
                buf += "This ancient weapon allows its wielder to move at supernatural speed.\n"
            elif itemtype == 18:
                buf += "This razor sharp weapon can slice through armour without difficulty.\n"
            elif itemtype == 19:
                buf += "This ancient weapon protects its wearer from player attacks.\n"
            elif itemtype == 20:
                buf += "This ancient weapon surrounds its wielder with a shield of darkness.\n"
            elif itemtype == 21:
                buf += "This ancient weapon grants superior protection to its wielder.\n"
            elif itemtype == 22:
                buf += "This ancient weapon grants its wielder supernatural vision.\n"
            elif itemtype == 23:
                buf += "This ancient weapon makes its wielder fleet-footed.\n"
            elif itemtype == 24:
                buf += "This ancient weapon conceals its wielder from sight.\n"
            elif itemtype == 25:
                buf += "This ancient weapon invokes the power of the beast.\n"
            else:
                buf += "This item is bugged...please report it.\n"
    elif itype == merc.ITEM_ARMOR:
        buf += f"Armor class is {item.value[0]}.\n"

        if item.value[3] > 0:
            if item.value[3] == 4:
                buf += "This object radiates an aura of darkness.\n"
            elif item.value[3] in [27, 2]:
                buf += "This item allows the wearer to see invisible things.\n"
            elif item.value[3] in [39, 3]:
                buf += "This object grants the power of flight.\n"
            elif item.value[3] in [45, 1]:
                buf += "This item allows the wearer to see in the dark.\n"
            elif item.value[3] in [46, 5]:
                buf += "This object renders the wearer invisible to the human eye.\n"
            elif item.value[3] in [52, 6]:
                buf += "This object allows the wearer to walk through solid doors.\n"
            elif item.value[3] in [54, 7]:
                buf += "This holy relic protects the wearer from evil.\n"
            elif item.value[3] in [57, 8]:
                buf += "This ancient relic protects the wearer in combat.\n"
            elif item.value[3] == 9:
                buf += "This crafty item allows the wearer to walk in complete silence.\n"
            elif item.value[3] == 10:
                buf += "This powerful item surrounds its wearer with a shield of lightning.\n"
            elif item.value[3] == 11:
                buf += "This powerful item surrounds its wearer with a shield of fire.\n"
            elif item.value[3] == 12:
                buf += "This powerful item surrounds its wearer with a shield of ice.\n"
            elif item.value[3] == 13:
                buf += "This powerful item surrounds its wearer with a shield of acid.\n"
            elif item.value[3] == 14:
                buf += "This object protects its wearer from clan DarkBlade guardians.\n"
            elif item.value[3] == 15:
                buf += "This ancient item surrounds its wearer with a shield of chaos.\n"
            elif item.value[3] == 16:
                buf += "This ancient item regenerates the wounds of its wearer.\n"
            elif item.value[3] == 17:
                buf += "This ancient item allows its wearer to move at supernatural speed.\n"
            elif item.value[3] == 18:
                buf += "This powerful item allows its wearer to shear through armour without difficulty.\n"
            elif item.value[3] == 19:
                buf += "This powerful item protects its wearer from player attacks.\n"
            elif item.value[3] == 20:
                buf += "This ancient item surrounds its wearer with a shield of darkness.\n"
            elif item.value[3] == 21:
                buf += "This ancient item grants superior protection to its wearer.\n"
            elif item.value[3] == 22:
                buf += "This ancient item grants its wearer supernatural vision.\n"
            elif item.value[3] == 23:
                buf += "This ancient item makes its wearer fleet-footed.\n"
            elif item.value[3] == 24:
                buf += "This ancient item conceals its wearer from sight.\n"
            elif item.value[3] == 25:
                buf += "This ancient item invokes the power of the beast.\n"
            else:
                buf += "This item is bugged...please report it.\n"

    for aff in item.affected:
        if aff.location != merc.APPLY_NONE and aff.modifier != 0:
            buf += f"Affects {merc.affect_loc_name(aff.location)} by {aff.modifier}.\n"
    ch.send("".join(buf))


const.register_spell(
    const.skill_type(
        name="identify",
        skill_level=3,
        spell_fun=spl_identify,
        target=merc.TAR_OBJ_INV,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(53),
        min_mana=12,
        beats=24,
        noun_damage="",
        msg_off="!Identify!"
    )
)
