#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
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

import random

import const
import fight
import game_utils
import handler_ch
import handler_game
import handler_magic
import instance
import merc
import object_creator


# Core procedure for dragons.
def dragon(ch, spell_name):
    if ch.position != merc.POS_FIGHTING:
        return False

    victim = None
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]
        if vch.fighting == ch and game_utils.number_bits(2) == 0:
            victim = vch
            break

    if not victim or spell_name not in const.skill_table:
        return False

    const.skill_table[spell_name].spell_fun(spell_name, ch.level, ch, victim, merc.TARGET_CHAR)
    return True


# Special procedures for mobiles.
def spec_breath_any(ch):
    if ch.position != merc.POS_FIGHTING:
        return False

    chance = game_utils.number_bits(3)
    if chance == 0:
        return spec_breath_fire(ch)
    elif chance in [1, 2]:
        return spec_breath_lightning(ch)
    elif chance == 3:
        return spec_breath_gas(ch)
    elif chance == 4:
        return spec_breath_acid(ch)
    elif chance in [5, 6, 7]:
        return spec_breath_frost(ch)
    return False


def spec_breath_acid(ch):
    return dragon(ch, "acid breath")


def spec_breath_fire(ch):
    return dragon(ch, "fire breath")


def spec_breath_frost(ch):
    return dragon(ch, "frost breath")


def spec_breath_gas(ch):
    if ch.position != merc.POS_FIGHTING:
        return False

    sn = "gas breath"
    if sn not in const.skill_table:
        return False
    const.skill_table[sn].spell_fun(sn, ch.level, ch, None, merc.TARGET_CHAR)
    return True


def spec_breath_lightning(ch):
    return dragon(ch, "lightning breath")


def spec_cast_adept(ch):
    if not ch.is_awake():
        return False

    victim = None
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]
        if vch != ch and ch.can_see(vch) and game_utils.number_bits(1) == 0:
            victim = vch
            break

    if not victim:
        return False

    num = game_utils.number_bits(3)
    if num == 0:
        handler_game.act("$n utters the word 'tehctah'.", ch, None, None, merc.TO_ROOM)
        const.skill_table["armor"].spell_fun('armor', ch.level, ch, victim, merc.TARGET_CHAR)
        return True
    elif num == 1:
        handler_game.act("$n utters the word 'nhak'.", ch, None, None, merc.TO_ROOM)
        const.skill_table["bless"].spell_fun('bless', ch.level, ch, victim, merc.TARGET_CHAR)
        return True
    elif num == 2:
        handler_game.act("$n utters the words 'yeruf'.", ch, None, None, merc.TO_ROOM)
        const.skill_table["cure blindness"].spell_fun('cure blindness', ch.level, ch, victim, merc.TARGET_CHAR)
        return True
    elif num == 3:
        handler_game.act("$n utters the words 'garf'.", ch, None, None, merc.TO_ROOM)
        const.skill_table["cure light"].spell_fun('cure light', ch.level, ch, victim, merc.TARGET_CHAR)
        return True
    elif num == 4:
        handler_game.act("$n utters the words 'rozar'.", ch, None, None, merc.TO_ROOM)
        const.skill_table["cure poison"].spell_fun('cure poison', ch.level, ch, victim, merc.TARGET_CHAR)
        return True
    elif num == 5:
        handler_game.act("$n utters the word 'nadroj'.", ch, None, None, merc.TO_ROOM)
        const.skill_table["refresh"].spell_fun('refresh', ch.level, ch, victim, merc.TARGET_CHAR)
        return True
    return False


def spec_cast_cleric(ch):
    if ch.position != merc.POS_FIGHTING:
        return False

    victim = None
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]
        if vch.fighting == ch and game_utils.number_bits(2) == 0:
            victim = vch
            break

    if not victim:
        return False

    while True:
        num = random.randint(0, 16)
        if num == 0:
            min_level = 0
            spell = "blindness"
        elif num == 1:
            min_level = 3
            spell = "cause serious"
        elif num == 2:
            min_level = 7
            spell = "earthquake"
        elif num == 3:
            min_level = 9
            spell = "cause critical"
        elif num == 4:
            min_level = 10
            spell = "dispel evil"
        elif num == 5:
            min_level = 12
            spell = "curse"
        elif num == 6:
            min_level = 12
            spell = "change sex"
        elif num == 7:
            min_level = 13
            spell = "flamestrike"
        elif num in [8, 9, 10]:
            min_level = 15
            spell = "harm"
        else:
            min_level = 16
            spell = "dispel magic"

        if ch.level >= min_level:
            break

    if spell not in const.skill_table:
        return False

    const.skill_table[spell].spell_fun(spell, ch.level, ch, victim, merc.TARGET_CHAR)
    return True


def spec_cast_judge(ch):
    if ch.position != merc.POS_FIGHTING:
        return False

    victim = None
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]
        if vch.fighting == ch and game_utils.number_bits(2) == 0:
            victim = vch
            break

    if not victim:
        return False

    spell = "high explosive"
    if spell not in const.skill_table:
        return False

    const.skill_table[spell].spell_fun(spell, ch.level, ch, victim, merc.TARGET_CHAR)
    return True


def spec_cast_mage(ch):
    if ch.position != merc.POS_FIGHTING:
        return False

    victim = None
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]
        if vch.fighting == ch and game_utils.number_bits(2) == 0:
            victim = vch
            break

    if not victim:
        return False

    while True:
        num = game_utils.number_bits(4)
        if num == 0:
            min_level = 0
            spell = "blindness"
        elif num == 1:
            min_level = 3
            spell = "chill touch"
        elif num == 2:
            min_level = 7
            spell = "weaken"
        elif num == 3:
            min_level = 8
            spell = "teleport"
        elif num == 4:
            min_level = 11
            spell = "colour spray"
        elif num == 5:
            min_level = 12
            spell = "change sex"
        elif num == 6:
            min_level = 13
            spell = "energy drain"
        elif num in [7, 8, 9]:
            min_level = 15
            spell = "fireball"
        else:
            min_level = 20
            spell = "acid blast"

        if ch.level >= min_level:
            break

    if spell not in const.skill_table:
        return False

    const.skill_table[spell].spell_fun(spell, ch.level, ch, victim, merc.TARGET_CHAR)
    return True


def spec_cast_undead(ch):
    if ch.position != merc.POS_FIGHTING:
        return False

    victim = None
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]
        if vch.fighting == ch and game_utils.number_bits(2) == 0:
            victim = vch
            break

    if not victim:
        return False

    while True:
        num = game_utils.number_bits(4)
        if num == 0:
            min_level = 0
            spell = "curse"
        elif num == 1:
            min_level = 3
            spell = "weaken"
        elif num == 2:
            min_level = 6
            spell = "chill touch"
        elif num == 3:
            min_level = 9
            spell = "blindness"
        elif num == 4:
            min_level = 12
            spell = "poison"
        elif num == 5:
            min_level = 15
            spell = "energy drain"
        elif num == 6:
            min_level = 18
            spell = "harm"
        elif num == 7:
            min_level = 21
            spell = "teleport"
        else:
            min_level = 24
            spell = "gate"

        if ch.level >= min_level:
            break

    if spell not in const.skill_table:
        return False

    const.skill_table[spell].spell_fun(spell, ch.level, ch, victim, merc.TARGET_CHAR)
    return True


def spec_fido(ch):
    if not ch.is_awake():
        return False

    for corpse_id in ch.in_room.items:
        corpse = instance.items[corpse_id]

        if corpse.item_type != merc.ITEM_CORPSE_NPC:
            continue

        handler_game.act("$n savagely devours a corpse.", ch, None, None, merc.TO_ROOM)
        for item_id in corpse.inventory[:]:
            item = instance.items[item_id]
            corpse.get(item)
            ch.in_room.put(item)

        corpse.extract()
        return True
    return False


def spec_guard(ch):
    if not ch.is_awake() or ch.fighting:
        return False

    max_evil = 300
    ech = None

    victim = None
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]

        if not vch.is_npc() and vch.race > 24 and game_utils.number_percent() > 95:
            victim = vch
            break

        if vch.fighting and vch.fighting != ch and vch.alignment < max_evil:
            max_evil = vch.alignment
            ech = vch

    if victim:
        chance = game_utils.number_range(1, 5)
        if chance == 1:
            ch.cmd_say(f"It is an honour to meet you, {victim.name}!")
        elif chance == 2:
            handler_game.act("You bow deeply before $N.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n bows deeply before you.", ch, None, victim, merc.TO_VICT)
            handler_game.act("$n bows deeply before $N.", ch, None, victim, merc.TO_NOTVICT)
        elif chance == 3:
            handler_game.act("You shake $N's hand.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n shakes your hand.", ch, None, victim, merc.TO_VICT)
            handler_game.act("$n shakes $N's hand.", ch, None, victim, merc.TO_NOTVICT)
            ch.cmd_say(f"It's a pleasure to see you again, {victim.name}!")
        elif chance == 4:
            handler_game.act("You pat $N on the back.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n pats you on the back.", ch, None, victim, merc.TO_VICT)
            handler_game.act("$n pats $N on the back.", ch, None, victim, merc.TO_NOTVICT)
            ch.cmd_say(f"Greetings {victim.name}!  If you need anything, just say!")
        else:
            handler_game.act("You beam a smile at $N.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n beams a smile at you.", ch, None, victim, merc.TO_VICT)
            handler_game.act("$n beams a smile at $N.", ch, None, victim, merc.TO_NOTVICT)
        return True

    if ech:
        if not ech.is_npc() and ech.race >= 25:
            ch.cmd_say(f"How DARE you attack {ech.name}? You shall DIE!")
            ch.cmd_rescue(ech.name)
            return True

        handler_game.act("$n screams 'PROTECT THE INNOCENT!!  BANZAI!!", ch, None, None, merc.TO_ROOM)
        fight.multi_hit(ch, ech, merc.TYPE_UNDEFINED)
        return True
    return False


def spec_janitor(ch):
    if not ch.is_awake():
        return False

    for trash_id in ch.in_room.items:
        trash = instance.items[trash_id]

        if not trash.flags.take:
            continue

        if trash.item_type in [merc.ITEM_DRINK_CON, merc.ITEM_TRASH] or trash.cost < 10:
            handler_game.act("$n picks up some trash.", ch, None, None, merc.TO_ROOM)
            ch.in_room.get(trash)
            ch.put(trash)
            return True
    return False


pos = 0
move = False
path = ""


def spec_mayor(ch):
    open_path = "W3a3003b33000c111d0d111Oe333333Oe22c222112212111a1S."
    close_path = "W3a3003b33000c111d0d111CE333333CE22c222112212111a1S."

    global pos, move, path

    if not move:
        if handler_game.time_info.hour == 6:
            path = open_path
            move = True
            pos = 0

        if handler_game.time_info.hour == 20:
            path = close_path
            move = True
            pos = 0

    if ch.fighting:
        return spec_cast_cleric(ch)

    if not move or ch.position < merc.POS_SLEEPING:
        return False

    if path[pos] in ["0", "1", "2", "3"]:
        handler_ch.move_char(ch, int(path[pos]))
    elif path[pos] == 'W':
        ch.position = merc.POS_STANDING
        handler_game.act("$n awakens and groans loudly.", ch, None, None, merc.TO_ROOM)
    elif path[pos] == 'S':
        ch.position = merc.POS_SLEEPING
        handler_game.act("$n lies down and falls asleep.", ch, None, None, merc.TO_ROOM)
    elif path[pos] == 'a':
        ch.cmd_say("Hello Honey!")
    elif path[pos] == 'b':
        ch.cmd_say("What a view!  I must do something about that dump!")
    elif path[pos] == 'c':
        ch.cmd_say("Vandals!  Youngsters have no respect for anything!")
    elif path[pos] == 'd':
        ch.cmd_say("Good day, citizens!")
    elif path[pos] == 'e':
        ch.cmd_say("I hereby declare the city of Midgaard open!")
    elif path[pos] == 'E':
        ch.cmd_say("I hereby declare the city of Midgaard closed!")
    elif path[pos] == 'O':
        # ch.cmd_unlock("gate")
        ch.cmd_open("gate")
    elif path[pos] == 'C':
        ch.cmd_close("gate")
        # ch.cmd_lock("gate")
    elif path[pos] == '.':
        move = False
    pos += 1
    return False


def spec_poison(ch):
    victim = ch.fighting
    if ch.position != merc.POS_FIGHTING or not victim or game_utils.number_percent() > 2 * ch.level:
        return False

    handler_game.act("You bite $N!", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n bites $N!", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n bites you!", ch, None, victim, merc.TO_VICT)
    const.skill_table['poison'].spell_fun('poison', ch.level, ch, victim, merc.TARGET_CHAR)
    return True


def spec_thief(ch):
    if ch.position != merc.POS_STANDING:
        return False

    for victim_id in ch.in_room.people[:]:
        victim = instance.characters[victim_id]
        if victim.is_npc() or (not victim.is_npc() and victim.immune.is_set(merc.IMM_STEAL)) or victim.is_immortal() or \
                game_utils.number_bits(2) != 0 or not ch.can_see(victim):
            continue

        if victim.is_awake() and game_utils.number_range(0, ch.level) == 0:
            handler_game.act("You discover $n's hands in your wallet!", ch, None, victim, merc.TO_VICT)
            handler_game.act("$N discovers $n's hands in $S wallet!", ch, None, victim, merc.TO_NOTVICT)
            return True
        else:
            gold = victim.gold * game_utils.number_range(1, 20) // 100
            ch.gold += gold
            victim.gold -= gold
            return True
    return False


def spec_eater(ch):
    # The spec_eater is a hungry bugger who eats players.  If they get
    # eaten, they get transported to the room with the same vnum as the
    # mob Example:  A spec_eater dragon with the vnum 31305 would send
    # anybody eaten to room 31305.
    # KaVir.
    victim = ch.fighting
    if ch.position != merc.POS_FIGHTING or game_utils.number_percent() > 50 or not victim:
        return False

    handler_game.act("$n stares at $N hungrily and licks $s lips!", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n stares at you hungrily and licks $s lips!", ch, None, victim, merc.TO_VICT)

    if game_utils.number_percent() > 25:
        return False

    room_index = instance.rooms[ch.vnum]
    handler_game.act("$n opens $s mouth wide and lunges at you!", ch, None, victim, merc.TO_VICT)
    handler_game.act("$n swallows you whole!", ch, None, victim, merc.TO_VICT)
    handler_game.act("$n opens $s mouth wide and lunges at $N!", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n swallows $N whole!", ch, None, victim, merc.TO_NOTVICT)
    victim.in_room.get(victim)
    room_index.put(victim)
    ch.cmd_emote("burps loudly.")
    victim.cmd_look("auto")
    return True


# Spec_rogue, coded by Malice.
# To add to the life of mobs... they pickup and wear equipment
def spec_rogue(ch):
    if not ch.is_awake():
        return False

    for item_id in ch.in_room.items:
        item = instance.items[item_id]

        if not item.flags.take or item.item_type == merc.ITEM_CORPSE_NPC:
            continue

        if item.item_type not in [merc.ITEM_DRINK_CON, merc.ITEM_TRASH] and not ((item.flags.anti_evil and ch.is_evil()) or
                                                                                 (item.flags.anti_good and ch.is_good()) or
                                                                                 (item.flags.anti_neutral and ch.is_neutral())):
            handler_game.act("$n picks up $p and examines it carefully.", ch, item, None, merc.TO_ROOM)
            ch.in_room.get(item)
            ch.put(item)

            # Now compare it to what we already have
            obj = None
            for item2_id in ch.inventory[:]:
                item2 = instance.items[item2_id]

                if not item2.equipped_to and ch.can_see_item(item2) and item.item_type == item2.item_type and \
                        (item.flags.take and item2.equipped_to in item.equips_to):
                    obj = item2
                    break

            if not obj:
                itype = item.item_type
                if itype == merc.ITEM_FOOD:
                    ch.cmd_say("This looks like a tasty morsel!")
                    ch.cmd_eat(item.name)
                elif itype == merc.ITEM_WAND:
                    ch.cmd_say("Wow, a magic wand!")
                    ch.equip(item, replace=False)
                elif itype == merc.ITEM_STAFF:
                    ch.cmd_say("Kewl, a magic staff!")
                    ch.equip(item, replace=False)
                elif itype == merc.ITEM_WEAPON:
                    ch.cmd_say("Hey, this looks like a nifty weapon!")
                    ch.equip(item, replace=False)
                elif itype == merc.ITEM_ARMOR:
                    ch.cmd_say("Oooh...a nice piece of armor!")
                    ch.equip(item, replace=False)
                elif itype == merc.ITEM_POTION:
                    ch.cmd_say("Great!  I was feeling a little thirsty!")
                    handler_game.act("You quaff $p.", ch, item, None, merc.TO_CHAR)
                    handler_game.act("$n quaffs $p.", ch, item, None, merc.TO_ROOM)
                    handler_magic.obj_cast_spell(item.value[1], item.level, ch, ch, None)
                    handler_magic.obj_cast_spell(item.value[2], item.level, ch, ch, None)
                    handler_magic.obj_cast_spell(item.value[3], item.level, ch, ch, None)
                    ch.get(item)
                    item.extract()
                elif itype == merc.ITEM_SCROLL:
                    ch.cmd_say("Hmmm I wonder what this says?")
                    handler_game.act("You recite $p.", ch, item, None, merc.TO_CHAR)
                    handler_game.act("$n recites $p.", ch, item, None, merc.TO_ROOM)
                    handler_magic.obj_cast_spell(item.value[1], item.level, ch, None, item)
                    handler_magic.obj_cast_spell(item.value[2], item.level, ch, None, item)
                    handler_magic.obj_cast_spell(item.value[3], item.level, ch, None, item)
                    item.etract()
                else:
                    ch.cmd_say("Hey, what a find!")
                return True

            if item.level > obj.level:
                ch.cmd_say("Now THIS looks like an improvement!")
                ch.equip(item, replace=True)
            else:
                ch.cmd_say("I don't want this piece of junk!")
                handler_game.act("You don't like the look of $p.", ch, item, None, merc.TO_CHAR)
                ch.cmd_drop(item.name)
                ch.cmd_sacrifice(item.name)
            return True
    return False


def spec_clan_guardian(ch):
    if ch.fighting or not ch.in_room:
        return False

    for victim in list(instance.characters.values()):
        if victim.is_npc() or victim.is_immortal() or not victim.in_room or victim.chobj or victim.in_room.area != ch.in_room.area or \
                victim.in_room == ch.in_room or (victim.is_vampire() and victim.special.is_set(merc.SPC_INCONNU)) or \
                (victim.clan and game_utils.str_cmp(victim.clan, "DarkLight")):
            continue

        item = victim.get_item_carry("dlwr5")
        if item and item.vnum == 6641:
            return False

        if ch.in_room != victim.in_room:
            handler_game.act("$n disappears in a haze of red!", victim, None, None, merc.TO_ROOM)
            handler_game.act("You disappear into a haze of red!", victim, None, None, merc.TO_CHAR)
            victim.in_room.get(victim)
            ch.in_room.put(victim)
            handler_game.act("$n appears in a haze of red!", victim, None, None, merc.TO_ROOM)
            handler_game.act("You appear into a haze of red!", victim, None, None, merc.TO_CHAR)

        handler_game.act("$n shouts at you \"You shall DIE!\"", ch, None, victim, merc.TO_VICT)
        handler_game.act("You let out a battlecry as you defend the clan headquaters!", ch, None, victim, merc.TO_CHAR)

        if victim.position <= merc.POS_MORTAL and victim.is_hero() and ch.position == merc.POS_STANDING:
            victim.in_room.get(victim)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(victim)
            continue

        ch.cmd_shout(f"{victim.name} Is In DarkLight Headquarters! Attack!")
        fight.multi_hit(ch, victim, "backstab")
        return True
    return False


def spec_clan_torcalta(ch):
    if ch.fighting or not ch.in_room:
        return False

    for victim in list(instance.characters.values()):
        if victim.is_npc() or victim.is_immortal() or not victim.in_room or victim.chobj or victim.in_room.area != ch.in_room.area or \
                victim.in_room == ch.in_room or (victim.is_vampire() and victim.special.is_set(merc.SPC_INCONNU)) or \
                (victim.clan and game_utils.str_cmp(victim.clan, "Torc Alta")):
            continue

        if ch.in_room != victim.in_room:
            handler_game.act("$n disappears in a swirl of smoke!", ch, None, None, merc.TO_ROOM)
            handler_game.act("You disappear in a swirl of smoke!", ch, None, None, merc.TO_CHAR)
            ch.in_room.get(ch)
            victim.in_room.put(ch)
            handler_game.act("$n appears in a swirl of smoke!", ch, None, None, merc.TO_ROOM)
            handler_game.act("You appear in a swirl of smoke!", ch, None, None, merc.TO_CHAR)

        handler_game.act("$n shouts at you \"You shall DIE!\"", ch, None, victim, merc.TO_VICT)
        handler_game.act("You let out a battlecry as you defend the clan headquarters!", ch, None, victim, merc.TO_CHAR)
        const.skill_table["curse"].spell_function("curse", 100, ch, victim)

        if victim.position <= merc.POS_MORTAL and victim.is_hero() and ch.position == merc.POS_STANDING:
            victim.in_room.get(victim)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(victim)
            continue

        ch.cmd_shout(f"{victim.name} Is in the Torc Alta Headquarters! Attack!")
        fight.multi_hit(ch, victim, "punch")
        return True
    return False


def spec_clan_spiritknights(ch):
    if ch.fighting or not ch.in_room:
        return False

    for victim in list(instance.characters.values()):
        if victim.is_npc() or victim.is_immortal() or not victim.in_room or victim.chobj or victim.in_room.area != ch.in_room.area or \
                victim.in_room == ch.in_room or (victim.is_vampire() and victim.special.is_set(merc.SPC_INCONNU)) or \
                (victim.clan and game_utils.str_cmp(victim.clan, "Spirit Knights")):
            continue

        if ch.in_room != victim.in_room:
            handler_game.act("$n disappears in a swirl of smoke!", ch, None, None, merc.TO_ROOM)
            handler_game.act("You disappear in a swirl of smoke!", ch, None, None, merc.TO_CHAR)
            ch.in_room.get(ch)
            victim.in_room.put(ch)
            handler_game.act("$n appears in a swirl of smoke!", ch, None, None, merc.TO_ROOM)
            handler_game.act("You appear in a swirl of smoke!", ch, None, None, merc.TO_CHAR)

        handler_game.act("$n shouts at you \"You shall DIE!\"", ch, None, victim, merc.TO_VICT)
        handler_game.act("You let out a battlecry as you defend the clan headquarters!", ch, None, victim, merc.TO_CHAR)
        const.skill_table["curse"].spell_function("curse", 100, ch, victim)

        if victim.position <= merc.POS_MORTAL and victim.is_hero() and ch.position == merc.POS_STANDING:
            victim.in_room.get(victim)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(victim)
            continue

        ch.cmd_shout(f"{victim.name} Is in the Spirit Knights Headquarters! Attack!")
        fight.multi_hit(ch, victim, "punch")
        return True
    return False


def spec_clan_werewolf(ch):
    if ch.fighting:
        if game_utils.number_range(1, 2) == 1:
            return spec_breath_frost(ch)
        else:
            return spec_eater(ch)

    if not ch.in_room:
        return False

    for victim in list(instance.characters.values()):
        if victim.is_npc() or victim.is_immortal() or not victim.in_room or victim.chobj or victim.in_room.area != ch.in_room.area or \
                victim.is_werewolf():
            continue

        # Stop Fenris jumping into his own stomach :)
        if ch.in_room != victim.in_room and victim.in_room.vnum != 29732:
            handler_game.act("$n burrows into the ground!", ch, None, None, merc.TO_ROOM)
            handler_game.act("You burrow into the ground!", ch, None, None, merc.TO_CHAR)
            ch.in_room.get(ch)
            victim.in_room.put(ch)
            handler_game.act("$n bursts from the ground!", ch, None, None, merc.TO_ROOM)
            handler_game.act("You burst from the ground!", ch, None, None, merc.TO_CHAR)

        if victim.position <= merc.POS_MORTAL and victim.is_hero() and ch.position == merc.POS_STANDING:
            victim.in_room.get(victim)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(victim)
            continue

        fight.one_hit(ch, victim, (merc.TYPE_HIT + 10), 0)
        return True
    return False


def spec_kavir_guardian(ch):
    if not ch.in_room:
        return False

    for victim in list(instance.characters.values()):
        if victim.is_npc() or victim.is_immortal() or not victim.in_room or victim.chobj or victim.in_room.area != ch.in_room.area or \
                victim.in_room == ch.in_room or (victim.is_vampire() and victim.special.is_set(merc.SPC_INCONNU)) or \
                (victim.clan and game_utils.str_cmp(victim.clan, "DarkBlade") or victim.itemaff.is_set(merc.ITEMA_DBPASS)):
            continue

        if ch.in_room != victim.in_room:
            victim.in_room.get(ch)
            ch.in_room.put(victim)

        if victim.position <= merc.POS_MORTAL and victim.is_hero() and ch.position == merc.POS_STANDING:
            victim.in_room.get(victim)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(victim)
            continue

        fight.multi_hit(ch, victim, merc.TYPE_UNDEFINED)
        return True
    return False


def spec_zombie_lord(ch):
    consider = 4
    north_ok = True
    east_ok = True
    south_ok = True
    west_ok = True
    up_ok = True
    down_ok = True
    countup = 6

    if ch.position <= merc.POS_SITTING:
        ch.cmd_stand("")
        return True

    victim = ch.fighting
    if victim:
        if ch.is_affected(merc.AFF_FAERIE_FIRE):
            handler_game.act("$n's eyes glow bright red for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["dispel magic"].spell_fun("dispel magic", ch.level, ch, ch)
        elif ch.is_affected(merc.AFF_POISON):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["cure poison"].spell_fun("cure poison", ch.level, ch, ch)
        elif ch.is_affected(merc.AFF_BLIND):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["cure blindness"].spell_fun("cure blindness", ch.level, ch, ch)
        elif ch.is_affected(merc.AFF_CURSE):
            handler_game.act("$n's eyes glow bright purple for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["remove curse"].spell_fun("remove curse", ch.level, ch, ch)
        elif not ch.is_affected(merc.AFF_SANCTUARY):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["sanctuary"].spell_fun("sanctuary", ch.level, ch, ch)
        elif not ch.is_affected("frenzy") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["frenzy"].spell_fun("frenzy", ch.level, ch, ch)
        elif not ch.is_affected("darkblessing") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["darkblessing"].spell_fun("darkblessing", ch.level, ch, ch)
        elif not ch.is_affected("bless") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["bless"].spell_fun("bless", ch.level, ch, ch)
        elif not ch.is_affected("stone skin") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["stone skin"].spell_fun("stone skin", ch.level, ch, ch)
        elif not ch.is_affected("armor") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["armor"].spell_fun("armor", ch.level, ch, ch)
        elif not ch.is_affected("shield") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["shield"].spell_fun("shield", ch.level, ch, ch)
        elif not victim.is_affected(merc.AFF_FAERIE_FIRE) and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright red for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["faerie fire"].spell_fun("faerie fire", ch.level, ch, victim)
        elif not victim.is_affected(merc.AFF_BLIND) and game_utils.number_percent() < 15:
            handler_game.act("$n's eyes glow bright red for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["blindness"].spell_fun("blindness", ch.level, ch, victim)
        elif not victim.is_affected(merc.AFF_CURSE) and game_utils.number_percent() < 15:
            handler_game.act("$n's eyes glow bright red for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["curse"].spell_fun("curse", ch.level, ch, victim)
        elif not ch.bleeding.empty():
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["clot"].spell_fun("clot", ch.level, ch, ch)
        elif ch.hit < ch.max_hit * 0.5 and game_utils.number_percent() < 75:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["heal"].spell_fun("heal", ch.level, ch, ch)
        elif ch.hit < ch.max_hit * 0.25 and game_utils.number_percent() < 50:
            ch.cmd_flee("")
            ch.spectype = merc.ZOMBIE_REST
        elif ch.hit < ch.max_hit * 0.1 and game_utils.number_percent() < 25:
            handler_game.act("$n's eyes glow bright green for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["teleport"].spell_fun("teleport", ch.level, ch, ch)
            ch.spectype = merc.ZOMBIE_REST
        else:
            chance = game_utils.number_range(1, 10)
            if chance == 1:
                ch.cmd_disarm("")
            elif chance in [2, 3, 4, 5]:
                handler_game.act("$n's eyes glow bright red for a moment.", ch, None, None, merc.TO_ROOM)
                const.skill_table["dispel magic"].spell_fun("dispel magic", ch.level, ch, victim)
            elif chance in [6, 7, 8]:
                handler_game.act("$n's eyes glow bright red for a moment.", ch, None, None, merc.TO_ROOM)
                const.skill_table["harm"].spell_fun("harm", ch.level, ch, victim)
            else:
                ch.cmd_kick("")

        victim = ch.fighting
        if not victim:
            return True

        chance = game_utils.number_percent()
        if chance == 1:
            ch.cmd_say("Foolish mortal, you think you can kill what is already dead?")
        elif chance == 2:
            ch.cmd_say(f"I shall feast on your soul for this, {victim.short_descr if victim.is_npc() else victim.name}")
        elif chance == 3:
            ch.cmd_shout(f"{victim.short_descr if victim.is_npc() else victim.name} shall pay for his arrogance!")
        elif chance == 4:
            ch.cmd_say("This fight shall be your last!")
        return True

    if ch.spectype not in [merc.ZOMBIE_TRACKING, merc.ZOMBIE_REST]:
        item = ch.get_item_here("corpse")
        if item:
            mob_index = instance.npc_templates[item.value[2]]
            if not mob_index:
                return spec_rogue(ch)

            victim = object_creator.create_mobile(mob_index)
            ch.in_room.put(victim)
            victim.name = f"zombie {victim.name}"
            victim.long_descr = f"The zombie of {victim.short_descr} stands here.\n"
            victim.short_descr = f"the zombie of {victim.short_descr}"
            handler_game.act("$n makes a few gestures over $p.", ch, item, None, merc.TO_ROOM)
            handler_game.act("$n clambers to $s feet.", victim, None, None, merc.TO_ROOM)
            victim.powertype = "zombie"

            for item2_id in item.inventory[:]:
                item2 = instance.items[item2_id]
                item.get(item2)
                victim.put(item2)
            item.extract()
            victim.cmd_wear("all")
            victim.cmd_say("I shall spread the corruption!  The time of the Apocalypse is at hand!")

        door = game_utils.number_range(0, 5)
        for door in range(merc.MAX_DIR):
            pexit = ch.in_room.exit[door]
            to_room = instance.rooms[pexit.to_room] if pexit else None
            if not pexit or not to_room:
                if door == merc.DIR_NORTH:
                    north_ok = False
                    countup -= 1
                elif door == merc.DIR_SOUTH:
                    south_ok = False
                    countup -= 1
                elif door == merc.DIR_EAST:
                    east_ok = False
                    countup -= 1
                elif door == merc.DIR_WEST:
                    west_ok = False
                    countup -= 1
                elif door == merc.DIR_UP:
                    up_ok = False
                    countup -= 1
                elif door == merc.DIR_DOWN:
                    down_ok = False
                    countup -= 1

        if countup < 1:
            ch.cmd_say("Damn, I hate it when this happens!")
            ch.cmd_recall("")
            return True

        while True:
            option = game_utils.number_range(0, 5)
            pexit = ch.in_room.exit[option]
            to_room = instance.rooms[pexit.to_room] if pexit else None
            if not pexit or not to_room:
                continue

            if countup > 1 and option == ch.specpower:
                continue

            option_list = [(merc.DIR_NORTH, "north"), (merc.DIR_EAST, "east"), (merc.DIR_SOUTH, "south"), (merc.DIR_WEST, "west"),
                           (merc.DIR_UP, "up"), (merc.DIR_DOWN, "down")]
            if pexit.exit_info.is_set(merc.EX_CLOSED):
                for (aa, bb) in option_list:
                    if option == aa:
                        ch.cmd_open(bb)

            for (aa, bb) in option_list:
                if option == aa:
                    ch.specpower = merc.rev_dir[aa]
                    break
            else:
                break

            handler_ch.move_char(ch, option)
            break

        for victim_id in ch.in_room.people[:]:
            victim = instance.characters[victim_id]

            if victim == ch or (not victim.is_npc() and victim.is_hero() and victim.hit < 0) or victim.is_immortal() or fight.is_safe(ch, victim) or \
                    not victim.is_npc() or not ch.can_see(victim):
                continue

            if victim.is_npc() and (game_utils.str_cmp(victim.powertype, "zombie") or victim.vnum == 30011):
                continue

            if victim.in_room == ch.in_room:
                handler_game.act("$n examines $N closely, looking for $S weaknesses.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n examines you closely, looking for your weaknesses.", ch, None, victim, merc.TO_VICT)

                if victim.hit > ch.hit * 1.5:
                    consider -= 1
                elif victim.hit * 1.5 < ch.hit:
                    consider += 1

                if victim.armor - 50 > ch.armor:
                    consider -= 1
                elif victim.armor + 50 < ch.armor:
                    consider += 1

                if victim.hitroll + 10 < ch.hitroll:
                    consider += 1
                elif victim.hitroll - 10 > ch.hitroll:
                    consider -= 1

                if victim.damroll + 10 < ch.damroll:
                    consider += 1
                elif victim.damroll - 10 > ch.damroll:
                    consider -= 1

                if consider == 8:
                    ch.cmd_say("This shouldn't take more than a few seconds!")
                elif consider == 7:
                    ch.cmd_say("Ha! You are no match for me!")
                elif consider == 6:
                    ch.cmd_say("I should be able to win this one...")
                elif consider == 5:
                    ch.cmd_say("Hmmm, close match, but I think I have the edge.")
                elif consider == 4:
                    ch.cmd_say("This one will be tricky...")
                elif consider == 3:
                    ch.cmd_say("Hmmm, I'm not sure if I can win this one.")
                elif consider == 2:
                    ch.cmd_say("Heheh better not risk it...")
                elif consider == 1:
                    ch.cmd_say("I'd need a lot of luck...better not.")
                elif consider == 0:
                    ch.cmd_say("I think I'll give this one a miss!!!")

                if victim.is_immortal() or consider < 3:
                    continue

                ch.cmd_kill(victim.name)
                return True

    if ch.spectype == merc.ZOMBIE_NOTHING:
        ch.spectype = game_utils.number_range(1, 3)
        return spec_rogue(ch)
    elif ch.spectype in [merc.ZOMBIE_TRACKING, merc.ZOMBIE_ANIMATE, merc.ZOMBIE_CAST]:
        if ch.is_affected(merc.AFF_FAERIE_FIRE):
            handler_game.act("$n's eyes glow bright red for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["dispel magic"].spell_fun("dispel magic", ch.level, ch, ch)
        elif ch.is_affected(merc.AFF_POISON) and game_utils.number_percent() < 75:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["cure poison"].spell_fun("cure poison", ch.level, ch, ch)
        elif ch.is_affected(merc.AFF_BLIND) and game_utils.number_percent() < 75:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["cure blindness"].spell_fun("cure blindness", ch.level, ch, ch)
        elif ch.is_affected(merc.AFF_CURSE) and game_utils.number_percent() < 75:
            handler_game.act("$n's eyes glow bright purple for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["remove curse"].spell_fun("remove curse", ch.level, ch, ch)
        elif not ch.is_affected(merc.AFF_SANCTUARY) and game_utils.number_percent() < 75:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["sanctuary"].spell_fun("sanctuary", ch.level, ch, ch)
        elif not ch.is_affected("frenzy") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["frenzy"].spell_fun("frenzy", ch.level, ch, ch)
        elif not ch.is_affected("darkblessing") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["darkblessing"].spell_fun("darkblessing", ch.level, ch, ch)
        elif not ch.is_affected("bless") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["bless"].spell_fun("bless", ch.level, ch, ch)
        elif not ch.is_affected("stone skin") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["stone skin"].spell_fun("stone skin", ch.level, ch, ch)
        elif not ch.is_affected("armor") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["armor"].spell_fun("armor", ch.level, ch, ch)
        elif not ch.is_affected("shield") and game_utils.number_percent() < 50:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["shield"].spell_fun("shield", ch.level, ch, ch)
        elif not ch.bleeding.empty():
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["clot"].spell_fun("clot", ch.level, ch, ch)
        elif ch.hit < ch.max_hit:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["heal"].spell_fun("heal", ch.level, ch, ch)
        elif not ch.is_affected("frenzy"):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["frenzy"].spell_fun("frenzy", ch.level, ch, ch)
        elif not ch.is_affected("darkblessing"):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["darkblessing"].spell_fun("darkblessing", ch.level, ch, ch)
        elif not ch.is_affected("bless"):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["bless"].spell_fun("bless", ch.level, ch, ch)
        elif not ch.is_affected("stone skin"):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["stone skin"].spell_fun("stone skin", ch.level, ch, ch)
        elif not ch.is_affected("armor"):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["armor"].spell_fun("armor", ch.level, ch, ch)
        elif not ch.is_affected("shield"):
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["shield"].spell_fun("shield", ch.level, ch, ch)
        else:
            ch.spectype = 0

        if ch.hit < ch.max_hit * 0.25:
            ch.spectype = merc.ZOMBIE_REST
        return True
    elif ch.spectype == merc.ZOMBIE_REST:
        if ch.hit >= ch.max_hit:
            ch.cmd_stand("")
            ch.spectype = 0
            return True

        if ch.is_affected(merc.AFF_CURSE):
            handler_game.act("$n's eyes glow bright purple for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["remove curse"].spell_fun("remove curse", ch.level, ch, ch)
            return True

        if ch.in_room.vnum != merc.ROOM_VNUM_ALTAR:
            ch.cmd_recall("")

        if ch.in_room.vnum == merc.ROOM_VNUM_TEMPLE:
            ch.cmd_north("")

        if ch.position == merc.POS_STANDING:
            ch.cmd_rest("")

        if ch.hit < ch.max_hit:
            handler_game.act("$n's eyes glow bright blue for a moment.", ch, None, None, merc.TO_ROOM)
            const.skill_table["heal"].spell_fun("heal", ch.level, ch, ch)
        return True
    return False


spec_table = {"spec_breath_any": spec_breath_any, "spec_breath_acid": spec_breath_acid, "spec_breath_fire": spec_breath_fire,
              "spec_breath_frost": spec_breath_frost, "spec_breath_gas": spec_breath_gas, "spec_breath_lightning": spec_breath_lightning,
              "spec_cast_adept": spec_cast_adept, "spec_cast_cleric": spec_cast_cleric, "spec_cast_judge": spec_cast_judge,
              "spec_cast_mage": spec_cast_mage, "spec_cast_undead": spec_cast_undead, "spec_fido": spec_fido, "spec_guard": spec_guard,
              "spec_janitor": spec_janitor, "spec_mayor": spec_mayor, "spec_poison": spec_poison, "spec_thief": spec_thief,
              "spec_eater": spec_eater, "spec_rogue": spec_rogue, "spec_clan_guardian": spec_clan_guardian,
              "spec_clan_torcalta": spec_clan_torcalta, "spec_clan_spiritknights": spec_clan_spiritknights,
              "spec_clan_werewolf": spec_clan_werewolf, "spec_kavir_guardian": spec_kavir_guardian, "spec_zombie_lord": spec_zombie_lord}
