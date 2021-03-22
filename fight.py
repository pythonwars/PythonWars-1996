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

import comm
import const
import game_utils
import handler_ch
import handler_game
import instance
import merc
import object_creator
import state_checks
import update


# Control the fights going on.
# Called periodically by update_handler.
def violence_update():
    ch_list = [ch_id for ch_id in instance.characters.keys()]
    for character in ch_list:
        ch = instance.characters.get(character, None)
        if ch:
            victim = ch.fighting
            if not victim or not ch.in_room:
                continue

            if ch.is_awake() and victim.is_awake() and ch.in_room == victim.in_room:
                multi_hit(ch, victim, merc.TYPE_UNDEFINED)
            else:
                stop_fighting(ch, False)

            victim = ch.fighting
            if not victim:
                continue

            # Fun for the whole family!
            for rch_id in ch.in_room.people[:]:
                rch = instance.characters[rch_id]
                if rch.is_awake() and not rch.fighting:
                    # Mounts auto-assist their riders and vice versa.
                    mount = rch.mount
                    if mount:
                        if mount == ch:
                            multi_hit(rch, victim, merc.TYPE_UNDEFINED)
                        continue

                    # PCs auto-assist others in their group.
                    if not ch.is_npc() or ch.is_affected(merc.AFF_CHARM):
                        if (not rch.is_npc() or rch.is_affected(merc.AFF_CHARM)) and ch.is_same_group(rch):
                            multi_hit(rch, victim, merc.TYPE_UNDEFINED)
                        continue

                    # NPCs assist NPC's of same type or 12.5% chance regardless.
                    if rch.is_npc() and not rch.is_affected(merc.AFF_CHARM):
                        if rch.vnum == ch.vnum or game_utils.number_bits(3) == 0:
                            target = None
                            number = 0
                            for vch_id in ch.in_room.people[:]:
                                vch = instance.characters[vch_id]

                                if rch.can_see(vch) and vch.is_same_group(victim) and game_utils.number_range(0, number) == 0:
                                    target = vch
                                    number += 1

                            if target:
                                multi_hit(rch, target, merc.TYPE_UNDEFINED)


# Do one group of attacks.
def multi_hit(ch, victim, dt):
    if ch.position < merc.POS_SLEEPING:
        return

    if dt == "headbutt":
        one_hit(ch, victim, dt, 1)
        return

    if not ch.is_npc() and ch.itemaff.is_set(merc.ITEMA_PEACE):
        ch.send("You are unable to attack them.\n")
        return

    if not victim.is_npc() and victim.itemaff.is_set(merc.ITEMA_PEACE):
        ch.send("You can't seem to attack them.\n")
        return

    wieldorig = 0
    wield1 = ch.get_eq("right_hand")
    wield2 = ch.get_eq("left_hand")

    if wield1 and wield1.item_type == merc.ITEM_WEAPON:
        wieldorig = 1

    if wield2 and wield2.item_type == merc.ITEM_WEAPON:
        wieldorig += 2

    wieldtype = wieldorig
    if wieldorig == 3:
        wieldtype = 2 if game_utils.number_range(1, 2) == 2 else 1

    wield = wield2 if wieldtype == 2 else wield1

    if not ch.is_npc() and ch.stance[0] > 0 and game_utils.number_percent() == 1:
        stance = ch.stance[0]
        if ch.stance[stance] >= 200:
            special_move(ch, victim)
            return

    one_hit(ch, victim, dt, wieldtype)

    if not victim or victim.position != merc.POS_FIGHTING:
        return

    # Only want one spell per round from spell weapons...otherwise it's
    # too powerful, and would unbalance player killing (as this is a PK mud).
    if dt == merc.TYPE_UNDEFINED:
        dt = merc.TYPE_HIT
        if wield and wield.item_type == merc.ITEM_WEAPON:
            dt += wield.value[3]
            """
            if wield.value[0] >= 1:
                # Look, just don't ask...   KaVir
                if wield.value[0] >= 1000:
                    sn = wield.value[0] - ((wield.value[0] // 1000) * 1000)
                else:
                    sn = wield.value[0]
                if sn != 0 and victim.position == merc.POS_FIGHTING:
                    const.skill_table[sn].spell_fun(sn, wield.level, ch, victim)
            """
    if not victim or victim.position != merc.POS_FIGHTING:
        return

    if ch.fighting != victim or dt in ["backstab", "headbutt"]:
        return

    if not victim.is_npc() and not victim.special.is_set(merc.SPC_WOLFMAN) and game_utils.number_percent() <= victim.learned["fastdraw"]:
        wpntype1 = 0
        wpntype2 = 0

        scabbard = victim.get_eq("right_scabbard")
        if scabbard:
            wpntype1 = scabbard.value[3] if scabbard.value[3] in merc.irange(0, 12) else 0
            item = victim.get_eq("right_hand")
            if item:
                victim.get(item)
                victim.in_room.put(item)
                handler_game.act("You hurl $p aside.", victim, item, None, merc.TO_CHAR)
                handler_game.act("$n hurls $p aside.", victim, item, None, merc.TO_ROOM)
            victim.cmd_draw("right")

        scabbard = victim.get_eq("left_scabbard")
        if scabbard:
            wpntype2 = scabbard.value[3] if scabbard.value[3] in merc.irange(0, 12) else 0
            item = victim.get_eq("left_hand")
            if item:
                victim.get(item)
                victim.in_room.put(item)
                handler_game.act("You hurl $p aside.", victim, item, None, merc.TO_CHAR)
                handler_game.act("$n hurls $p aside.", victim, item, None, merc.TO_ROOM)
            victim.cmd_draw("left")

        if wpntype1 > 0:
            one_hit(victim, ch, merc.TYPE_UNDEFINED, 1)

        if not victim or victim.position != merc.POS_FIGHTING:
            return

        if wpntype2 > 0:
            one_hit(victim, ch, merc.TYPE_UNDEFINED, 2)

        if not victim or victim.position != merc.POS_FIGHTING:
            return

    maxcount = number_attacks(ch)
    if not ch.is_npc():
        if wield and wield.item_type == merc.ITEM_WEAPON:
            tempnum = wield.value[3]
            chance = ch.wpn[tempnum] * 0.5
        else:
            chance = ch.wpn[0] * 0.5
        if game_utils.number_percent() <= chance:
            maxcount += 1

    if wieldorig == 3:
        maxcount += 1

    for _ in merc.irange(maxcount):
        wieldtype = wieldorig
        if wieldorig == 3:
            wieldtype = 2 if game_utils.number_range(1, 2) == 2 else 1

        one_hit(ch, victim, -1, wieldtype)

        if not victim or victim.position != merc.POS_FIGHTING or ch.fighting != victim:
            return

    if not ch.is_npc() and ch.vampaff.is_set(merc.VAM_FANGS):
        one_hit(ch, victim, merc.TYPE_HIT + 10, 0)

    if not victim or victim.position != merc.POS_FIGHTING:
        return

    if not ch.is_npc() and ch.is_demon() and ch.demaff.is_set(merc.DEM_HORNS) and game_utils.number_range(1, 3) == 1:
        multi_hit(ch, victim, "headbutt")

    if not victim or victim.position != merc.POS_FIGHTING:
        return

    if not ch.is_npc() and ch.is_vampire() and ch.vampaff.is_set(merc.VAM_SERPENTIS):
        const.skill_table["poison"].spell_fun("poison", ch.level * game_utils.number_range(5, 10), ch, victim)
    elif not ch.is_npc() and ch.werewolf() and ch.powers[merc.WPOWER_SPIDER] > 0:
        const.skill_table["poison"].spell_fun("poison", ch.level * game_utils.number_range(5, 10), ch, victim)

    if victim.itemaff.empty():
        return

    level = victim.level if (victim.is_npc() or victim.spl[1] < 4) else (victim.spl[1] * 0.25)
    level = int(level)

    if victim.itemaff.is_set(merc.ITEMA_SHOCKSHIELD) and ch.position == merc.POS_FIGHTING:
        sn = "lightning bolt"
        if sn in const.skill_table:
            const.skill_table[sn].spell_fun(sn, level, victim, ch, merc.TARGET_CHAR)

    if victim.itemaff.is_set(merc.ITEMA_FIRESHIELD) and ch.position == merc.POS_FIGHTING:
        sn = "fireball"
        if sn in const.skill_table:
            const.skill_table[sn].spell_fun(sn, level, victim, ch, merc.TARGET_CHAR)

    if victim.itemaff.is_set(merc.ITEMA_ICESHIELD) and ch.position == merc.POS_FIGHTING:
        sn = "chill touch"
        if sn in const.skill_table:
            const.skill_table[sn].spell_fun(sn, level, victim, ch, merc.TARGET_CHAR)

    if victim.itemaff.is_set(merc.ITEMA_ACIDSHIELD) and ch.position == merc.POS_FIGHTING:
        sn = "acid blast"
        if sn in const.skill_table:
            const.skill_table[sn].spell_fun(sn, level, victim, ch, merc.TARGET_CHAR)

    if victim.itemaff.is_set(merc.ITEMA_CHAOSSHIELD) and ch.position == merc.POS_FIGHTING:
        sn = "chaos blast"
        if sn in const.skill_table:
            const.skill_table[sn].spell_fun(sn, level, victim, ch, merc.TARGET_CHAR)


def number_attacks(ch):
    count = 1

    if ch.is_npc():
        if ch.level >= 50:
            count += 1

        if ch.level >= 100:
            count += 1
        return count

    if ch.stance[0] == merc.STANCE_VIPER and game_utils.number_percent() > ch.stance[merc.STANCE_VIPER] * 0.5:
        count += 1
    elif ch.stance[0] == merc.STANCE_MANTIS and game_utils.number_percent() > ch.stance[merc.STANCE_MANTIS] * 0.5:
        count += 1
    elif ch.stance[0] == merc.STANCE_TIGER and game_utils.number_percent() > ch.stance[merc.STANCE_TIGER] * 0.5:
        count += 1

    if not ch.is_npc():
        if ch.is_vampire() and ch.vampaff.is_set(merc.VAM_CELERITY):
            count += 1
        elif ch.is_werewolf() and ch.powers[merc.WPOWER_LYNX] > 2:
            count += 1
        elif ch.is_demon() and ch.dempower.is_set(merc.DEM_SPEED):
            count += 1

    if ch.itemaff.is_set(merc.ITEMA_SPEED):
        count += 1
    return count


# Hit one guy once.
def one_hit(ch, victim, dt, handtype):
    # just in case
    if victim.instance_id == ch.instance_id or not ch or not victim:
        return

    # Can't beat a dead char!
    # Guard against weird room-leavings.
    if victim.position == merc.POS_DEAD or ch.in_room != victim.in_room:
        return

    if not ch.is_npc() and ch.itemaff.is_set(merc.ITEMA_PEACE):
        ch.send("You are unable to attack them.\n")
        return

    if not victim.is_npc() and victim.itemaff.is_set(merc.ITEMA_PEACE):
        ch.send("You can't seem to attack them.\n")
        return

    # Figure out the type of damage message.
    if handtype == 2:
        wield = ch.get_eq("left_hand")
        right_hand = False
    else:
        wield = ch.get_eq("right_hand")
        right_hand = True

    if dt == merc.TYPE_UNDEFINED:
        dt = merc.TYPE_HIT
        if wield and wield.item_type == merc.ITEM_WEAPON:
            dt += wield.value[3]

    level = (ch.wpn[dt - 1000] // 5) if ch.wpn[dt - 1000] > 5 else 1
    level = state_checks.urange(1, level, 40)

    # Calculate to-hit-armor-class-0 versus armor.
    if ch.is_npc():
        thac0_00 = 20
        thac0_32 = 0
    else:
        thac0_00 = merc.SKILL_THAC0_00
        thac0_32 = merc.SKILL_THAC0_32

    thac0 = game_utils.interpolate(level, thac0_00, thac0_32) - ch.hitroll
    victim_ac = max(-75, victim.armor // 10)

    if not ch.can_see(victim):
        victim_ac -= 4

    # The moment of excitement!
    diceroll = game_utils.number_bits(5)
    if diceroll == 0 or (diceroll != 19 and diceroll < thac0 - victim_ac):
        # Miss.
        damage(ch, victim, 0, dt)

        if not is_safe(ch, victim):
            ch.improve_wpn(dt, right_hand)
            ch.improve_stance()
        return

    # Hit.
    # Calc damage.
    if ch.is_npc():
        dam = random.randint(ch.level // 2, ch.level * 3 // 2)
        if not wield:
            dam += dam // 2
    else:
        if ch.vampaff.is_set(merc.VAM_CLAWS) and not wield:
            dam = game_utils.number_range(10, 20)
        elif wield and wield.item_type == merc.ITEM_WEAPON:
            dam = game_utils.number_range(wield.value[1], wield.value[2])
        else:
            dam = game_utils.number_range(1, 4)

    # Bonuses.
    dam += ch.damroll

    if not victim.is_awake():
        dam *= 2

    if dt == "backstab":
        dam *= game_utils.number_range(2, 4)

    if not ch.is_npc() and ch.is_vampire() and ch.vampaff.is_set(merc.VAM_POTENCE):
        dam *= 1.5
    elif not ch.is_npc() and ch.is_demon() and ch.dempower.is_set(merc.DEM_MIGHT):
        dam *= 1.5

    if not victim.is_npc() and victim.is_werewolf():
        if victim.special.is_set(merc.SPC_WOLFMAN):
            dam *= 0.5

        if victim.powers[merc.WPOWER_BOAR] > 2:
            dam *= 0.5

        if wield and wield.flags.silver:
            dam *= 2
        else:
            gloves = ch.get_eq("hands")
            if gloves and gloves.flags.silver:
                dam *= 2

    if not ch.is_npc():
        # Vampires should be tougher at night and weaker during the day.
        if ch.is_vampire():
            if handler_game.weather_info.sunlight == merc.SUN_LIGHT and dam > 1:
                dam //= 1.5
            elif handler_game.weather_info.sunlight == merc.SUN_DARK:
                dam *= 1.5

        if dt >= merc.TYPE_HIT:
            dam = dam + (dam * ((ch.wpn[dt - 1000] + 1) // 100))

        stance = ch.stance[0]
        if ch.stance[0] == merc.STANCE_NORMAL:
            dam *= 1.25
        else:
            dam = dambonus(ch, victim, dam, stance)

    dam = int(dam)
    if dam <= 0:
        dam = 1

    damage(ch, victim, dam, dt)

    if not is_safe(ch, victim):
        ch.improve_wpn(dt, right_hand)
        ch.improve_stance()


def can_counter(ch):
    return not ch.is_npc() and ch.stance[0] == merc.STANCE_MONKEY


def can_bypass(ch, victim):
    if ch.is_npc() or victim.is_npc():
        return False

    return ch.stance[0] in [merc.STANCE_VIPER, merc.STANCE_MANTIS, merc.STANCE_TIGER]


def update_damcap(ch, victim):
    max_dam = 1000

    if not ch.is_npc():
        if (ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION)) and ch.in_room:
            if ch.in_room.vnum == merc.ROOM_VNUM_HELL:
                max_dam = 10000
            max_dam += ch.powers[merc.DEMON_POWER] * 20
        elif ch.is_vampire():
            if ch.powers[merc.UNI_GEN] < 3:
                max_dam = 1500
            elif ch.powers[merc.UNI_GEN] < 4:
                max_dam = 1400
            elif ch.powers[merc.UNI_GEN] < 5:
                max_dam = 1300
            else:
                max_dam = 1200

            max_dam += ch.powers[merc.UNI_RAGE] * 10

            if ch.vampaff.is_set(merc.VAM_POTENCE):
                max_dam += 100

            if ch.rank == merc.AGE_METHUSELAH:
                max_dam += 300
            elif ch.rank == merc.AGE_ELDER:
                max_dam += 200
            elif ch.rank == merc.AGE_ANCILLA:
                max_dam += 100
        elif ch.special.is_set(merc.SPC_WOLFMAN):
            if ch.powers[merc.UNI_GEN] < 2:
                max_dam = 2000
            elif ch.powers[merc.UNI_GEN] < 3:
                max_dam = 1900
            elif ch.powers[merc.UNI_GEN] < 4:
                max_dam = 1800
            else:
                max_dam = 1700
            max_dam += ch.powers[merc.UNI_RAGE]
        elif ch.is_demon():
            max_dam += 500
        elif ch.special.is_set(merc.SPC_CHAMPION):
            max_dam += 250
        elif ch.is_highlander() and ch.itemaff.is_set(merc.ITEMA_HIGHLANDER):
            wpn = ch.powers[merc.HPOWER_WPNSKILL]
            if wpn in [1, 3]:
                max_dam += ch.wpn[wpn]

        if ch.itemaff.is_set(merc.ITEMA_ARTIFACT):
            max_dam += 500

        if victim.itemaff.is_set(merc.ITEMA_ARTIFACT):
            max_dam -= 500

        if victim.is_npc() or victim.stance[0] != merc.STANCE_MONKEY:
            if ch.stance[0] == merc.STANCE_BULL:
                max_dam += 250
            elif ch.stance[0] == merc.STANCE_DRAGON:
                max_dam += 250
            elif ch.stance[0] == merc.STANCE_TIGER:
                max_dam += 250
    else:
        max_dam += ch.level * 2

    if not victim.is_npc():
        if victim.is_werewolf():
            silver_tol = victim.powers[merc.WPOWER_SILVER] * 2.5

            if ch.itemaff.is_set(merc.ITEMA_RIGHT_SILVER):
                max_dam += 250 - silver_tol

            if ch.itemaff.is_set(merc.ITEMA_LEFT_SILVER):
                max_dam += 250 - silver_tol

        if ch.is_npc() or ch.stance[0] != merc.STANCE_MONKEY:
            if victim.stance[0] == merc.STANCE_CRAB:
                max_dam -= 250
            elif victim.stance[0] == merc.STANCE_DRAGON:
                max_dam -= 250
            elif victim.stance[0] == merc.STANCE_SWALLOW:
                max_dam -= 250

        if (victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION)) and victim.in_room and victim.in_room.vnum == merc.ROOM_VNUM_HELL:
            max_dam *= 0.2

    max_dam = max(1000, max_dam)
    ch.damcap[merc.DAM_CAP] = max_dam
    ch.damcap[merc.DAM_CHANGE] = 0


# Inflict damage from a hit.
def damage(ch, victim, dam, dt):
    max_dam = ch.damcap[merc.DAM_CAP]

    if victim.position == merc.POS_DEAD:
        return False

    # Stop up any residual loopholes.
    if ch.damcap[merc.DAM_CHANGE] == 1:
        update_damcap(ch, victim)

    dam = min(int(dam), max_dam)

    if victim != ch:
        # Certain attacks are forbidden.
        # Most other attacks are returned.
        if is_safe(ch, victim):
            return

        check_killer(ch, victim)

        if victim.position > merc.POS_STUNNED:
            if not victim.fighting:
                set_fighting(victim, ch)

        if victim.position > merc.POS_STUNNED:
            if not ch.fighting:
                set_fighting(ch, victim)

            # If victim is charmed, ch might attack victim's master.
            if ch.is_npc() and victim.is_npc() and victim.is_affected(merc.AFF_CHARM) and victim.master and \
                    instance.characters[victim.master].in_room == ch.in_room and game_utils.number_bits(3) == 0:
                stop_fighting(ch, False)
                multi_hit(ch, instance.characters[victim.master], merc.TYPE_UNDEFINED)
                return

        # More charm stuff.
        if victim.master and instance.characters[victim.master] == ch:
            handler_ch.stop_follower(victim)

        # Damage modifiers.
        if ch.is_affected(merc.AFF_HIDE):
            if not victim.can_see(ch):
                dam *= 1.5
                ch.send("You use your concealment to get a surprise attack!\n")

            ch.affected_by.rem_bit(merc.AFF_HIDE)
            handler_game.act("$n leaps from $s concealment.", ch, None, None, merc.TO_ROOM)

        if victim.is_affected(merc.AFF_SANCTUARY) and dam > 1:
            dam *= 0.5

        if victim.is_affected(merc.AFF_PROTECT) and ch.is_evil() and dam > 1:
            dam -= dam * 0.25

        dam = max(0, int(dam))

        # Check for disarm, trip, parry, and dodge.
        if type(dt) == int and dt >= merc.TYPE_HIT:
            if ch.is_npc() and game_utils.number_percent() < ch.level * 0.5:
                disarm(ch, victim)

            if ch.is_npc() and game_utils.number_percent() < ch.level * 0.5:
                trip(ch, victim)

            if check_parry(ch, victim, dt):
                return

            if not victim.is_npc() and victim.stance[0] == merc.STANCE_CRANE and victim.stance[merc.STANCE_CRANE] > 100 and not can_counter(ch) and \
                    not can_bypass(ch, victim) and check_parry(ch, victim, dt):
                return
            elif not victim.is_npc() and victim.stance[0] == merc.STANCE_MANTIS and victim.stance[merc.STANCE_MANTIS] > 100 and \
                    not can_counter(ch) and not can_bypass(ch, victim) and check_parry(ch, victim, dt):
                return

            if check_dodge(ch, victim, dt):
                return

            if not victim.is_npc() and victim.stance[0] == merc.STANCE_MONGOOSE and victim.stance[merc.STANCE_MONGOOSE] > 100 and \
                    not can_counter(ch) and not can_bypass(ch, victim) and check_dodge(ch, victim, dt):
                return
            elif not victim.is_npc() and victim.stance[0] == merc.STANCE_SWALLOW and victim.stance[merc.STANCE_SWALLOW] > 100 and \
                    not can_counter(ch) and not can_bypass(ch, victim) and check_dodge(ch, victim, dt):
                return

        dam_message(ch, victim, dam, dt)

    hurt_person(ch, victim, dam)


def adv_damage(ch, victim, dam):
    if victim.position == merc.POS_DEAD:
        return

    dam = min(int(dam), 1000)

    if victim != ch:
        if is_safe(ch, victim):
            return

        check_killer(ch, victim)

        if victim.position > merc.POS_STUNNED:
            if not victim.fighting:
                set_fighting(victim, ch)
            victim.position = merc.POS_FIGHTING

        if victim.position > merc.POS_STUNNED:
            if not ch.fighting:
                set_fighting(ch, victim)

            # If victim is charmed, ch might attack victim's master.
            if ch.is_npc() and victim.is_npc() and victim.is_affected(merc.AFF_CHARM) and victim.master and \
                    instance.characters[victim.master].in_room == ch.in_room and game_utils.number_bits(3) == 0:
                stop_fighting(ch, False)
                multi_hit(ch, instance.characters[victim.master], merc.TYPE_UNDEFINED)
                return

        if instance.characters[victim.master] == ch:
            victim.stop_follower()

        if victim.is_affected(merc.AFF_SANCTUARY) and dam > 1:
            dam //= 2

        if victim.is_affeced(merc.AFF_PROTECT) and ch.is_evil() and dam > 1:
            dam -= dam // 4

        dam = max(0, int(dam))


def adv_spell_damage(ch, book, page, argument):
    mana_cost = page.points
    smin = page.value[1]
    smax = page.value[2]

    if ch.mana < mana_cost:
        ch.send("You have insufficient mana to chant this spell.\n")
        return

    if smin < 1 or smax < 1:
        ch.send("The spell failed.\n")
        return

    if page.spectype.is_set(merc.ADV_NEXT_PAGE) and page.spectype.is_set(merc.ADV_SPELL_FIRST):
        if not page.chpoweroff:
            ch.send("The spell failed.\n")
            return

        if page.spectype.is_set(merc.ADV_PARAMETER):
            if not page.chpoweron:
                ch.send("The spell failed.\n")
                return
            else:
                next_par = page.chpoweron
        else:
            next_par = ""

        if page.specpower < page.value[0]:
            ch.send("The spell failed.\n")
            return

        page_next = book.get_page(page.specpower)
        if not page_next:
            ch.send("The spell failed.\n")
            return

        if page_next.quest.is_set(merc.QUEST_MASTER_RUNE):
            if page_next.spectype.is_set(merc.ADV_DAMAGE):
                adv_spell_damage(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_AFFECT):
                adv_spell_affect(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_ACTION):
                adv_spell_action(ch, book, page_next, next_par)
            else:
                ch.send("The spell failed.\n")
                return
        else:
            ch.send("The spell failed.\n")
            return

    argument, arg = game_utils.read_word(argument)

    cast_message = page.victpoweron and page.victpoweroff
    area_affect = page.spectype.is_set(merc.ADV_AREA_AFFECT)
    victim_target = page.spectype.is_set(merc.ADV_VICTIM_TARGET)
    global_target = page.spectype.is_set(merc.ADV_GLOBAL_TARGET)
    not_caster = page.spectype.is_set(merc.ADV_NOT_CASTER)
    no_players = page.spectype.is_set(merc.ADV_NO_PLAYERS)
    is_reversed = page.spectype.is_set(merc.ADV_REVERSED)

    if victim_target:
        if not global_target:
            victim = ch.get_char_room(arg)
            if not victim:
                ch.not_here(arg)
                return
        else:
            victim = ch.get_char_world(arg)
            if not victim:
                ch.not_here(arg)
                return

        level = ch.spl[merc.BLUE_MAGIC if is_reversed else merc.RED_MAGIC]
        dam = game_utils.number_range(smin, smax) + level if ch.in_room == victim.in_room else 0

        if ch.spectype < 1000:
            ch.spectype += dam

            if victim.itemaff.is_set(merc.ITEMA_RESISTANCE) and dam > 1 and not is_reversed:
                dam = game_utils.number_range(1, dam)
            elif not victim.is_npc() and victim.is_demon() and not is_reversed:
                if victim.dempower.is_set(merc.DEM_TOUGH) and dam > 1:
                    dam = game_utils.number_range(1, dam)

                if victim.in_room and victim.in_room.vnum == merc.ROOM_VNUM_HELL:
                    if dam < 5:
                        dam = 1
                    else:
                        dam *= 0.2
        else:
            dam = 0
        dam = int(dam)

        old_room = ch.in_room
        if victim.in_room and victim.in_room != ch.in_room:
            ch.in_room.get(ch)
            victim.in_room.put(ch)

        if not is_reversed:
            if is_safe(ch, victim):
                ch.in_room.get(ch)
                old_room.put(ch)
                return
        elif victim.itemaff.is_set(merc.ITEMA_REFLECT):
            ch.send("You are unable to focus your spell on them.\n")
            ch.in_room.get(ch)
            old_room.put(ch)
            return

        ch.in_room.get(ch)
        old_room.put(ch)

        if cast_message:
            handler_game.act2(page.victpoweron, ch, None, victim, merc.TO_CHAR)
            handler_game.act2(page.victpoweroff, ch, None, victim, merc.TO_ROOM)

        if is_reversed:
            victim.hit += dam

            if victim.hit > victim.max_hit:
                victim.hit = victim.max_hit
        else:
            adv_damage(ch, victim, dam)
            handler_game.act2("Your $t strikes $N incredably hard!", ch, page.chpoweroff, victim, merc.TO_CHAR)
            handler_game.act2("$n's $t strikes $N incredably hard!", ch, page.chpoweroff, victim, merc.TO_NOTVICT)
            handler_game.act2("$n's $t strikes you incredably hard!", ch, page.chpoweroff, victim, merc.TO_VICT)
            hurt_person(ch, victim, dam)

        if not ch.is_immortal():
            ch.wait_state(merc.PULSE_VIOLENCE)
            ch.mana -= mana_cost
    elif area_affect:
        vch = ch
        level = ch.spl[merc.BLUE_MAGIC if is_reversed else merc.RED_MAGIC]
        dam = game_utils.number_range(smin, smax) + (level * 0.5)

        if ch.spectype < 1000:
            ch.spectype += dam
        else:
            dam = 0
        dam = int(dam)

        if ch.in_room.room_flags.is_set(merc.ROOM_SAFE) and not is_reversed:
            ch.send("You cannot fight in a safe room.\n")
            return

        if cast_message:
            handler_game.act2(page.victpoweron, ch, None, vch, merc.TO_CHAR)
            handler_game.act2(page.victpoweroff, ch, None, vch, merc.TO_ROOM)

        for vch in list(instance.characters.values()):
            if not vch.in_room or (ch == vch and not_caster) or (not vch.is_npc() and no_players):
                continue

            if not is_reversed and is_safe(ch, vch):
                continue

            if vch.itemaff.is_set(merc.ITEMA_REFLECT):
                ch.send("You are unable to focus your spell on them.\n")
                continue

            if vch.in_room == ch.in_room:
                if is_reversed:
                    vch.hit += dam
                    if vch.hit > vch.max_hit:
                        vch.hit = vch.max_hit
                else:
                    adv_damage(ch, vch, dam)
                    handler_game.act2("Your $t strikes $N incredably hard!", ch, page.chpoweroff, vch, merc.TO_CHAR)
                    handler_game.act2("$n's $t strikes $N incredably hard!", ch, page.chpoweroff, vch, merc.TO_NOTVICT)
                    handler_game.act2("$n's $t strikes you incredably hard!", ch, page.chpoweroff, vch, merc.TO_VICT)
                    hurt_person(ch, vch, game_utils.number_range(1, dam) if (vch.itemaff.is_set(merc.ITEMA_RESISTANCE) and dam > 1) else dam)
                continue

        if not ch.is_immortal():
            ch.wait_state(merc.PULSE_VIOLENCE)
            ch.mana -= mana_cost
    else:
        ch.send("The spell failed.\n")
        return

    if page.spectype.is_set(merc.ADV_NEXT_PAGE) and not page.spectype.is_set(merc.ADV_SPELL_FIRST):
        if not page.chpoweroff:
            ch.send("The spell failed.\n")
            return

        if page.spectype.is_set(merc.ADV_PARAMETER):
            if not page.chpoweron:
                ch.send("The spell failed.\n")
                return
            else:
                next_par = page.chpoweron
        else:
            next_par = ""

        if page.specpower < page.value[0]:
            ch.send("The spell failed.\n")
            return

        page_next = book.get_page(page.specpower)
        if not page_next:
            ch.send("The spell failed.\n")
            return

        if page_next.quest.is_set(merc.QUEST_MASTER_RUNE):
            if page_next.spectype.is_set(merc.ADV_DAMAGE):
                adv_spell_damage(ch, book, page_next, next_par)
            elif page_next.spectype(merc.ADV_AFFECT):
                adv_spell_affect(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_ACTION):
                adv_spell_action(ch, book, page_next, next_par)
            else:
                ch.send("The spell failed.\n")
                return
        else:
            ch.send("The spell failed.\n")
            return


def adv_spell_affect(ch, book, page, argument):
    mana_cost = page.points
    apply_bit = page.value[1]
    bonuses = page.value[2]
    affect_bit = page.value[3]
    level = page.level
    victim = ch
    any_affects = False
    cast_message = False
    message_one = False
    message_two = False

    if ch.mana < mana_cost:
        ch.send("You have insufficient mana to chant this spell.\n")
        return

    if page.spectype.is_set(merc.ADV_NEXT_PAGE) and page.spectype.is_set(merc.ADV_SPELL_FIRST):
        if not page.chpoweroff:
            ch.send("The spell failed.\n")
            return

        if page.spectype.is_set(merc.ADV_PARAMETER):
            if not page.chpoweron:
                ch.send("The spell failed.\n")
                return
            else:
                next_par = page.chpoweron
        else:
            next_par = argument

        if page.specpower < page.value[0]:
            ch.send("The spell failed.\n")
            return

        page_next = book.get_page(page.specpower)
        if not page_next:
            ch.send("The spell failed.\n")
            return

        if page_next.quest.is_set(merc.QUEST_MASTER_RUNE):
            if page_next.spectype.is_set(merc.ADV_DAMAGE):
                adv_spell_damage(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_AFFECT):
                adv_spell_affect(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_ACTION):
                adv_spell_action(ch, book, page_next, next_par)
            else:
                ch.send("The spell failed.\n")
                return
        else:
            ch.send("The spell failed.\n")
            return

    argument, arg = game_utils.read_word(argument)
    c_m = ""
    c_1 = ""
    c_2 = ""

    if page.chpoweroff:
        c_m = page.chpoweroff
        cast_message = True
    if page.victpoweron:
        c_1 = page.victpoweron
        message_one = True
    if page.victpoweroff:
        c_2 = page.victpoweroff
        message_two = True

    area_affect = page.spectype.is_set(merc.ADV_AREA_AFFECT)
    victim_target = page.spectype.is_set(merc.ADV_VICTIM_TARGET)
    object_target = page.spectype.is_set(merc.ADV_OBJECT_TARGET)
    global_target = page.spectype.is_set(merc.ADV_GLOBAL_TARGET)
    not_caster = page.spectype.is_set(merc.ADV_NOT_CASTER)
    no_players = page.spectype.is_set(merc.ADV_NO_PLAYERS)

    if page.spectype.is_set(merc.ADV_REVERSED):
        bonuses = 0 - bonuses

    if victim_target and not area_affect and not global_target and not object_target:
        victim = ch.get_char_room(arg)
        if not victim:
            ch.send("The spell failed.\n")
            return

        if not victim.in_room:
            ch.send("The spell failed.\n")
            return
    elif victim_target and area_affect and not global_target and not object_target:
        victim = ch.get_char_world(arg)
        if not victim:
            ch.send("The spell failed.\n")
            return

        if not victim.in_room or victim.in_room.area != ch.in_room.area:
            ch.send("The spell failed.\n")
            return
    elif victim_target and global_target and not object_target:
        victim = ch.get_char_world(arg)
        if not victim:
            ch.send("The spell failed.\n")
            return

        if not victim.in_room:
            ch.send("The spell failed.\n")
            return
    elif object_target and not area_affect and not global_target and not victim_target:
        item = ch.get_item_carry(arg)
        if not item:
            ch.send("The spell failed.\n")
            return
    elif object_target and area_affect and not global_target and not victim_target:
        item = ch.get_item_here(arg)
        if not item:
            ch.send("The spell failed.\n")
            return
    elif object_target and global_target and not victim_target:
        item = ch.get_item_world(arg)
        if not item:
            ch.send("The spell failed.\n")
            return

        if not item.in_room:
            ch.send("The spell failed.\n")
            return

    if page.toughness not in merc.irange(merc.PURPLE_MAGIC, merc.YELLOW_MAGIC):
        ch.send("The spell failed.\n")
        return

    color_list = [(merc.PURPLE_MAGIC, "purple sorcery"), (merc.RED_MAGIC, "red sorcery"), (merc.BLUE_MAGIC, "blue sorcery"),
                  (merc.GREEN_MAGIC, "green sorcery"), (merc.YELLOW_MAGIC, "yellow sorcery")]
    for (aa, bb) in color_list:
        if page.toughness == aa:
            if bb not in const.skill_table:
                ch.send("The spell failed.\n")
                return

            sn = bb
            break
    else:
        ch.send("The spell failed.\n")
        return

    if not victim_target and victim != ch:
        ch.send("The spell failed.\n")
        return

    if not_caster and ch == victim:
        ch.send("The spell failed.\n")
        return
    elif no_players and not victim.is_npc():
        ch.send("The spell failed.\n")
        return

    if victim.is_affected(sn):
        ch.send("They are already affected by a spell of that colour.\n")
        return

    if apply_bit == 0:
        ch.enhance_stat(sn, level, victim, merc.APPLY_NONE, bonuses, affect_bit)
        any_affects = True
    else:
        stat_list = [(merc.ADV_STR, merc.APPLY_STR, bonuses * 0.1), (merc.ADV_DEX, merc.APPLY_DEX, bonuses * 0.1),
                     (merc.ADV_INT, merc.APPLY_INT, bonuses * 0.1), (merc.ADV_WIS, merc.APPLY_WIS, bonuses * 0.1),
                     (merc.ADV_CON, merc.APPLY_CON, bonuses * 0.1), (merc.ADV_MANA, merc.APPLY_MANA, bonuses * 5),
                     (merc.ADV_HIT, merc.APPLY_HIT, bonuses * 5), (merc.ADV_MOVE, merc.APPLY_MOVE, bonuses * 5),
                     (merc.ADV_AC, merc.APPLY_AC, 0 - (bonuses * 5)), (merc.ADV_HITROLL, merc.APPLY_HITROLL, bonuses * 0.5),
                     (merc.ADV_DAMROLL, merc.APPLY_DAMROLL, bonuses * 0.5), (merc.ADV_SAVING_SPELL, merc.APPLY_SAVING_SPELL, bonuses * 0.2)]
        for (aa, bb, cc) in stat_list:
            if state_checks.is_set(apply_bit, aa):
                ch.enhance_stat(sn, level, victim, bb, cc, affect_bit)
                any_affects = True
                break

    if not any_affects:
        ch.send("The spell failed.\n")
        return

    if cast_message:
        handler_game.act2(c_m, ch, None, victim, merc.TO_CHAR)

    if message_one:
        handler_game.act2(c_1, ch, None, victim, merc.TO_VICT)

    if message_two:
        handler_game.act2(c_2, ch, None, victim, merc.TO_NOTVICT)

    if not ch.is_immortal():
        ch.wait_state(merc.PULSE_VIOLENCE)
        ch.mana -= mana_cost

    if page.spectype.is_set(merc.ADV_NEXT_PAGE) and not page.spectype.is_set(merc.ADV_SPELL_FIRST):
        if not page.chpoweroff:
            ch.send("The spell failed.\n")
            return

        if page.spectype.is_set(merc.ADV_PARAMETER):
            if not page.chpoweron:
                ch.send("The spell failed.\n")
                return
            else:
                next_par = page.chpoweron
        else:
            next_par = argument

        if page.specpower < page.value[0]:
            ch.send("The spell failed.\n")
            return

        page_next = book.get_page(page.specpower)
        if not page_next:
            ch.send("The spell failed.\n")
            return

        if page_next.quest.is_set(merc.QUEST_MASTER_RUNE):
            if page_next.spectype.is_set(merc.ADV_DAMAGE):
                adv_spell_damage(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_AFFECT):
                adv_spell_affect(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_ACTION):
                adv_spell_action(ch, book, page_next, next_par)
            else:
                ch.send("The spell failed.\n")
                return
        else:
            ch.send("The spell failed.\n")
            return


def adv_spell_action(ch, book, page, argument):
    old_room = ch.in_room
    mana_cost = page.points
    action_bit = page.value[1]
    action_type = page.value[2]
    cast_message = False
    message_one = False
    message_two = False
    victim1 = None
    victim2 = None
    item1 = None
    item2 = None

    if ch.mana < mana_cost:
        ch.send("You have insufficient mana to chant this spell.\n")
        return

    if page.spectype.is_set(merc.ADV_NEXT_PAGE) and page.spectype.is_set(merc.ADV_SPELL_FIRST):
        if not page.chpoweroff:
            ch.send("The spell failed.\n")
            return

        if page.spectype.is_set(merc.ADV_PARAMETER):
            if not page.chpoweron:
                ch.send("The spell failed.\n")
                return
            else:
                next_par = page.chpoweron
        else:
            next_par = argument

        if page.specpower < page.value[0]:
            ch.send("The spell failed.\n")
            return

        page_next = book.get_page(page.specpower)
        if not page_next:
            ch.send("The spell failed.\n")
            return

        if page_next.quest.is_set(merc.QUEST_MASTER_RUNE):
            if page_next.spectype.is_set(merc.ADV_DAMAGE):
                adv_spell_damage(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_AFFECT):
                adv_spell_affect(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_ACTION):
                adv_spell_action(ch, book, page_next, next_par)
            else:
                ch.send("The spell failed.\n")
                return
        else:
            ch.send("The spell failed.\n")
            return

    arg1, argument = game_utils.read_word(argument)
    arg2, argument = game_utils.read_word(argument)
    c_m = ""
    c_1 = ""
    c_2 = ""

    if page.chpoweroff:
        c_m = page.chpoweroff
        cast_message = True
    if page.victpoweron:
        c_1 = page.victpoweron
        message_one = True
    if page.victpoweroff:
        c_2 = page.victpoweroff
        message_two = True

    area_affect = page.spectype.is_set(merc.ADV_AREA_AFFECT)
    victim_target = page.spectype.is_set(merc.ADV_VICTIM_TARGET)
    object_target = page.spectype.is_set(merc.ADV_OBJECT_TARGET)
    global_target = page.spectype.is_set(merc.ADV_GLOBAL_TARGET)
    second_victim = page.spectype.is_set(merc.ADV_SECOND_VICTIM)
    second_object = page.spectype.is_set(merc.ADV_SECOND_OBJECT)
    is_reversed = page.spectype.is_set(merc.ADV_REVERSED)

    if victim_target and not area_affect and not global_target and not object_target:
        victim1 = ch.get_char_room(arg1)
        if not victim1:
            ch.send("The spell failed.\n")
            return

        if not victim1.in_room:
            ch.send("The spell failed.\n")
            return

        if victim1 == ch or (not victim1.is_npc() and not victim1.immune.is_set(merc.IMM_SUMMON)):
            ch.send("The spell failed.\n")
            return
    elif victim_target and area_affect and not global_target and not object_target:
        victim1 = ch.get_char_world(arg1)
        if not victim1:
            ch.send("The spell failed.\n")
            return

        if not victim1.in_room or victim1.in_room.area != ch.in_room.area:
            ch.send("The spell failed.\n")
            return

        if victim1 == ch or (not victim1.is_npc() and not victim1.immune.is_set(merc.IMM_SUMMON)):
            ch.send("The spell failed.\n")
            return
    elif victim_target and global_target and not object_target:
        victim1 = ch.get_char_world(arg1)
        if not victim1:
            ch.send("The spell failed.\n")
            return

        if not victim1.in_room:
            ch.send("The spell failed.\n")
            return

        if victim1 == ch or (not victim1.is_npc() and not victim1.immune.is_set(merc.IMM_SUMMON)):
            ch.send("The spell failed.\n")
            return
    elif object_target and not area_affect and not global_target and not victim_target:
        item1 = ch.get_item_carry(arg1)
        if not item1:
            ch.send("The spell failed.\n")
            return
    elif object_target and area_affect and not global_target and not victim_target:
        item1 = ch.get_item_here(arg1)
        if not item1:
            ch.send("The spell failed.\n")
            return
    elif object_target and global_target and not victim_target:
        item1 = ch.get_item_world(arg1)
        if not item1:
            ch.send("The spell failed.\n")
            return

        if not item1.in_room:
            ch.send("The spell failed.\n")
            return

    if not arg2 and (second_victim or second_object):
        ch.send("Please specify a target.\n")
        return
    elif second_victim and victim_target and not area_affect and not global_target and not object_target:
        victim2 = ch.get_char_room(arg2)
        if not victim1:
            ch.send("The spell failed.\n")
            return

        if not victim2.in_room:
            ch.send("The spell failed.\n")
            return

        if not victim1 or victim1.is_npc() or victim1.immune.is_set(merc.IMM_SUMMON):
            ch.send("The spell failed.\n")
            return

        if victim1 == victim2 or (not victim2.is_npc() and victim2.immune.is_set(merc.IMM_SUMMON)):
            ch.send("The spell failed.\n")
            return
    elif second_victim and victim_target and area_affect and not global_target and not object_target:
        victim2 = ch.get_char_world(arg2)
        if not victim2:
            ch.send("The spell failed.\n")
            return

        if not victim2.in_room or victim2.in_room.area != ch.in_room.area:
            ch.send("The spell failed.\n")
            return

        if not victim1 or victim1.is_npc() and victim1.immune.is_set(merc.IMM_SUMMON):
            ch.send("The spell failed.\n")
            return

        if victim1 == victim2 or (not victim2.is_npc() and not victim2.immune.is_set(merc.IMM_SUMMON)):
            ch.send("The spell failed.\n")
            return
    elif second_victim and victim_target and global_target and not object_target:
        victim2 = ch.get_char_world(arg2)
        if not victim2:
            ch.send("The spell failed.\n")
            return

        if not victim2.in_room:
            ch.send("The spell failed.\n")
            return

        if not victim1 or victim1.is_npc() or victim1.immune.is_set(merc.IMM_SUMMON):
            ch.send("The spell failed.\n")
            return

        if victim1 == victim2 or (not victim2.is_npc() and not victim2.immune.is_set(merc.IMM_SUMMON)):
            ch.send("The spell failed.\n")
            return
    elif second_object and object_target and not area_affect and not global_target and not victim_target:
        item2 = ch.get_item_carry(arg2)
        if not item2:
            ch.send("The spell failed.\n")
            return
    elif second_object and object_target and area_affect and not global_target and not victim_target:
        item2 = ch.get_item_here(arg2)
        if not item2:
            ch.send("The spell failed.\n")
            return
    elif second_object and object_target and global_target and not victim_target:
        item2 = ch.get_item_world(arg2)
        if not item2:
            ch.send("The spell failed.\n")
            return

    if victim1 and victim1.level > ch.spl[merc.PURPLE_MAGIC]:
        ch.send("The spell failed.\n")
        return

    if victim2 and victim2.level > ch.spl[merc.PURPLE_MAGIC]:
        ch.send("The spell failed.\n")
        return

    if action_bit == merc.ACTION_MOVE:
        if not victim_target and not second_victim and not object_target and not second_object:
            if cast_message:
                handler_game.act2(c_m, ch, None, None, merc.TO_CHAR)

            if message_one:
                handler_game.act2(c_1, ch, None, None, merc.TO_ROOM)

            ch.in_room.get(ch)
            old_room.put(ch)

            if message_two:
                handler_game.act2(c_2, ch, None, None, merc.TO_ROOM)
        elif not arg1:
            ch.send("Please specify a target.\n")
            return
        elif victim_target and not second_victim and not object_target and not second_object:
            if not victim1 or not victim1.in_room or victim1.in_room == ch.in_room:
                ch.send("The spell failed.\n")
                return

            if is_reversed:
                if victim1.position == merc.POS_FIGHTING:
                    ch.send("The spell failed.\n")
                    return

                if cast_message:
                    handler_game.act2(c_m, victim1, None, None, merc.TO_CHAR)

                if message_one:
                    handler_game.act2(c_1, victim1, None, None, merc.TO_ROOM)

                victim1.in_room.get(victim1)
                ch.in_room.put(victim1)

                if message_two:
                    handler_game.act2(c_2, victim1, None, None, merc.TO_ROOM)
                victim1.cmd_look("auto")
            else:
                if ch.position == merc.POS_FIGHTING:
                    ch.send("The spell failed.\n")
                    return

                if cast_message:
                    handler_game.act2(c_m, ch, None, None, merc.TO_CHAR)

                if message_one:
                    handler_game.act2(c_1, ch, None, None, merc.TO_ROOM)

                ch.in_room.get(ch)
                victim1.in_room.put(ch)

                if message_two:
                    handler_game.act2(c_2, ch, None, None, merc.TO_ROOM)
                ch.cmd_look("")
        elif not victim_target and not second_victim and object_target and not second_object:
            if not item1 or not item1.in_room or item1.in_room == ch.in_room:
                ch.send("The spell failed.\n")
                return

            if cast_message:
                handler_game.act2(c_m, ch, item1, None, merc.TO_CHAR)

            if message_one:
                handler_game.act2(c_1, ch, item1, None, merc.TO_ROOM)

            if is_reversed:
                item1.in_room.get(item1)
                ch.in_room.put(item1)
            else:
                ch.in_room.get(ch)
                item1.in_room.put(ch)
                ch.cmd_look("auto")

            if message_two:
                handler_game.act2(c_2, ch, item1, None, merc.TO_ROOM)
        elif victim_target and second_victim and not object_target and not second_object:
            if not victim1 or not victim1.in_room:
                ch.send("The spell failed.\n")
                return

            if not victim2 or not victim2.in_room or victim2.in_room == victim1.in_room:
                ch.send("The spell failed.\n")
                return

            if is_reversed:
                if victim2.position == merc.POS_FIGHTING:
                    ch.send("The spell failed.\n")
                    return

                if cast_message:
                    handler_game.act2(c_m, victim2, None, victim1, merc.TO_CHAR)

                if message_one:
                    handler_game.act2(c_1, victim2, None, victim1, merc.TO_ROOM)

                victim2.in_room.get(victim2)
                victim1.in_room.put(victim2)

                if message_two:
                    handler_game.act2(c_2, victim2, None, victim1, merc.TO_ROOM)
                victim2.cmd_look("auto")
            else:
                if victim1.position == merc.POS_FIGHTING:
                    ch.send("The spell failed.\n")
                    return

                if cast_message:
                    handler_game.act2(c_m, victim1, None, victim2, merc.TO_CHAR)

                if message_one:
                    handler_game.act2(c_1, victim1, None, victim2, merc.TO_ROOM)

                victim1.in_room.get(victim1)
                victim2.in_room.put(victim1)

                if message_two:
                    handler_game.act2(c_2, victim1, None, victim2, merc.TO_ROOM)
                victim1.cmd_look("auto")
        elif victim_target and not second_victim and not object_target and second_object:
            if not victim1 or not victim1.in_room:
                ch.send("The spell failed.\n")
                return

            if not item2 or not item2.in_room or item2.in_room == victim1.in_room:
                ch.send("The spell failed.\n")
                return

            if cast_message:
                handler_game.act2(c_m, victim1, None, None, merc.TO_CHAR)

            if message_one:
                handler_game.act2(c_1, victim1, item2, None, merc.TO_ROOM)

            if is_reversed:
                item2.in_room.get(item2)
                victim1.in_room.put(item2)
            else:
                if victim1.position == merc.POS_FIGHTING:
                    ch.send("The spell failed.\n")
                    return

                victim1.in_room.get(victim1)
                item2.in_room.put(victim1)
                victim1.cmd_look("auto")

            if message_two:
                handler_game.act2(c_2, victim1, item2, None, merc.TO_ROOM)
        elif not victim_target and not second_victim and object_target and second_object:
            if not item1 or not item1.in_room:
                ch.send("The spell failed.\n")
                return

            if not item2 or not item2.in_room or item2.in_room == item1.in_room:
                ch.send("The spell failed.\n")
                return

            if cast_message:
                handler_game.act2(c_m, ch, item1, None, merc.TO_CHAR)

            if is_reversed:
                old_room = ch.in_room

                if message_one:
                    handler_game.act2(c_1, ch, item2, None, merc.TO_ROOM)

                item2.in_room.get(item2)
                item1.in_room.put(item2)
                ch.in_room.get(ch)
                item1.in_room.put(ch)

                if message_two:
                    handler_game.act2(c_2, ch, item2, None, merc.TO_ROOM)

                ch.in_room.get(ch)
                old_room.put(ch)
            else:
                old_room = ch.in_room

                if message_one:
                    handler_game.act2(c_1, ch, item1, None, merc.TO_ROOM)

                item1.in_room.get(item1)
                item2.in_room.put(item1)
                ch.in_room.get(ch)
                item2.in_room.put(ch)

                if message_two:
                    handler_game.act2(c_2, ch, item1, None, merc.TO_ROOM)

                ch.in_room.put(ch)
                old_room.put(ch)
        elif not victim_target and second_victim and object_target and not second_object:
            if not victim2 or not victim2.in_room:
                ch.send("The spell failed.\n")
                return

            if not item1 or not item1.in_room or item1.in_room == victim2.in_room:
                ch.send("The spell failed.\n")
                return

            if cast_message:
                handler_game.act2(c_m, victim2, None, None, merc.TO_CHAR)

            if message_one:
                handler_game.act2(c_1, victim1, item2, None, merc.TO_ROOM)

            if is_reversed:
                if victim2.position == merc.POS_FIGHTING:
                    ch.send("The spell failed.\n")
                    return

                victim2.in_room.get(victim2)
                item1.in_room.put(victim2)
                victim2.cmd_look("")
            else:
                item1.in_room.get(item1)
                victim2.in_room.put(item1)

            if message_two:
                handler_game.act2(c_2, victim2, item1, None, merc.TO_ROOM)
        else:
            ch.send("The spell failed.\n")
            return
    elif action_bit == merc.ACTION_MOB:
        if action_type < 1:
            ch.send("The spell failed.\n")
            return

        if ch.is_npc() or ch.followers > 4:
            ch.send("The spell failed.\n")
            return

        victim = object_creator.create_mobile(instance.npc_templates[action_type])
        if not victim:
            ch.send("The spell failed.\n")
            return

        if cast_message:
            handler_game.act2(c_m, ch, None, victim, merc.TO_CHAR)

        if message_one:
            handler_game.act2(c_1, ch, None, victim, merc.TO_ROOM)

        ch.followers += 1
        ch.in_room.put(victim)
        victim.act.set_bit(merc.ACT_NOEXP)
        victim.lord = ch.name

        if victim.level > ch.spl[merc.PURPLE_MAGIC]:
            ch.send("The spell failed.\n")
            victim.extract(True)
            return
    elif action_bit == merc.ACTION_OBJECT:
        if action_type < 1:
            ch.send("The spell failed.\n")
            return

        item = object_creator.create_item(instance.item_templates[action_type], 0)
        if not item:
            ch.send("The spell failed.\n")
            return

        if cast_message:
            handler_game.act2(c_m, ch, item, None, merc.TO_CHAR)

        if message_one:
            handler_game.act2(c_1, ch, item, None, merc.TO_ROOM)

        item.questmaker = ch.name
        ch.in_room.put(item)
    else:
        ch.send("The spell failed.\n")
        return

    if not ch.is_immortal():
        ch.wait_state(merc.PULSE_VIOLENCE)
        ch.mana -= mana_cost

    if page.spectype.is_set(merc.ADV_NEXT_PAGE) and not page.spectype.is_set(merc.ADV_SPELL_FIRST):
        if not page.chpoweroff:
            ch.send("The spell failed.\n")
            return

        if page.spectype.is_set(merc.ADV_PARAMETER):
            if not page.chpoweron:
                ch.send("The spell failed.\n")
                return
            else:
                next_par = page.chpoweron
        else:
            next_par = argument

        if page.specpower < page.value[0]:
            ch.send("The spell failed.\n")
            return

        page_next = book.get_page(page.specpower)
        if not page_next:
            ch.send("The spell failed.\n")
            return

        if page_next.quest.is_set(merc.QUEST_MASTER_RUNE):
            if page_next.spectype.is_set(merc.ADV_DAMAGE):
                adv_spell_damage(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_AFFECT):
                adv_spell_affect(ch, book, page_next, next_par)
            elif page_next.spectype.is_set(merc.ADV_ACTION):
                adv_spell_action(ch, book, page_next, next_par)
            else:
                ch.send("The spell failed.\n")
                return
        else:
            ch.send("The spell failed.\n")
            return


def hurt_person(ch, victim, dam):
    is_npc = False

    # Hurt the victim.
    # Inform the victim of his new state.
    victim.hit -= dam

    if not victim.is_npc() and victim.is_immortal() and victim.hit < 1:
        victim.hit = 1
    update_pos(victim)

    if victim.position == merc.POS_MORTAL:
        handler_game.act("$n is mortally wounded, and spraying blood everywhere.", victim, None, None, merc.TO_ROOM)
        victim.send("You are mortally wounded, and spraying blood everywhere.\n")
    elif victim.position == merc.POS_INCAP:
        handler_game.act("$n is incapacitated, and bleeding badly.", victim, None, None, merc.TO_ROOM)
        victim.send("You are incapacitated, and bleeding badly.\n")
    elif victim.position == merc.POS_STUNNED:
        handler_game.act("$n is stunned, but will soon recover.", victim, None, None, merc.TO_ROOM)
        victim.send("You are stunned, but will soon recover.\n")
    elif victim.position == merc.POS_DEAD:
        handler_game.act("$n is DEAD!!", victim, None, None, merc.TO_ROOM)
        victim.send("You have been KILLED!!\n\n")
    else:
        if dam > victim.max_hit // 4:
            victim.send("That really did HURT!\n")

        if victim.hit < victim.max_hit // 4 and dam > 0:
            if not victim.is_npc() and victim.is_vampire() and game_utils.number_percent() < victim.beast:
                victim.vamp_rage()
            else:
                victim.send("You sure are BLEEDING!\n")

    # Sleep spells and extremely wounded folks.
    if not victim.is_awake():
        stop_fighting(victim, False)

    # Payoff for killing things.
    if victim.position == merc.POS_DEAD:
        group_gain(ch, victim)

        if not victim.is_npc():
            comm.notify("{} killed by {} at {}".format(victim.name, ch.short_descr if ch.is_npc() else ch.name, victim.in_room.vnum), merc.CONSOLE_INFO)

            # Dying penalty:
            # 1/2 your current exp.
            if victim.exp > 0:
                victim.exp //= 2

        if victim.is_npc() and not ch.is_npc():
            ch.mkill += 1

            if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION):
                vnum = victim.vnum
                if vnum > 29000:
                    if vnum not in [29600, 30001, 30006, 30007, 30008, 30009]:
                        ch.powers[merc.DEMON_CURRENT] += victim.level
                        ch.powers[merc.DEMON_TOTAL] += victim.level
                elif victim.is_npc() and not victim.act.is_set(merc.ACT_NOEXP):
                    ch.powers[merc.DEMON_CURRENT] += victim.level
                    ch.powers[merc.DEMON_TOTAL] += victim.level

            if ch.level == 1 and ch.mkill > 4:
                ch.level = 2
                ch.save(force=True)

        if not victim.is_npc() and ch.is_npc():
            victim.mdeath += 1

        raw_kill(victim)

        if not ch.is_npc():
            if ch.act.is_set(merc.PLR_AUTOLOOT):
                ch.cmd_get("all corpse")
            else:
                ch.cmd_look("in corpse")

            if is_npc and ch.act.is_set(merc.PLR_AUTOSAC):
                ch.cmd_sacrifice("corpse")
        return

    if victim == ch:
        return

    # Take care of link dead people.
    if not victim.is_npc() and not victim.desc:
        if game_utils.number_range(0, victim.wait) == 0:
            victim.cmd_recall("")
            return

    # Wimp out?
    if victim.is_npc() and dam > 0:
        if (victim.act.is_set(merc.ACT_WIMPY) and game_utils.number_bits(1) == 0 and victim.hit < victim.max_hit // 2) or \
                (victim.is_affected(merc.AFF_CHARM) and victim.master and instance.characters[victim.master].in_room != victim.in_room):
            victim.cmd_flee("")

    if not victim.is_npc() and victim.hit in merc.irange(1, victim.wimpy) and victim.wait == 0:
        victim.cmd_flee("")


def no_attack(ch, victim):
    # Ethereal people can only attack other ethereal people
    if ch.is_affected(merc.AFF_ETHEREAL) and not victim.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot while ethereal.\n")
        return True

    if not ch.is_affected(merc.AFF_ETHEREAL) and victim.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot fight an ethereal person.\n")
        return True

    # You cannot attack across planes
    if ch.is_affected(merc.AFF_SHADOWPLANE) and not victim.is_affected(merc.AFF_SHADOWPLANE):
        handler_game.act("You are too insubstantial!", ch, None, victim, merc.TO_CHAR)
        return True

    if not ch.is_affected(merc.AFF_SHADOWPLANE) and victim.is_affected(merc.AFF_SHADOWPLANE):
        handler_game.act("$E is too insubstantial!", ch, None, victim, merc.TO_CHAR)
        return True

    if ch.in_room.room_flags.is_set(merc.ROOM_SAFE):
        ch.send("You cannot fight in a safe room.\n")
        return True

    if ch.head.is_set(merc.LOST_HEAD) or ch.extra.is_set(merc.EXTRA_OSWITCH):
        ch.send("Objects cannot fight!\n")
        return True
    elif victim.head.is_set(merc.LOST_HEAD) or victim.extra.is_set(merc.EXTRA_OSWITCH):
        ch.send("You cannot attack objects.\n")
        return True
    return False


def is_safe(ch, victim):
    # Ethereal people can only attack other ethereal people
    if ch.is_affected(merc.AFF_ETHEREAL) and not victim.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot while ethereal.\n")
        return True

    if not ch.is_affected(merc.AFF_ETHEREAL) and victim.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot fight an ethereal person.\n")
        return True

    # You cannot attack across planes
    if ch.is_affected(merc.AFF_SHADOWPLANE) and not victim.is_affected(merc.AFF_SHADOWPLANE):
        handler_game.act("You are too insubstantial!", ch, None, victim, merc.TO_CHAR)
        return True

    if not ch.is_affected(merc.AFF_SHADOWPLANE) and victim.is_affected(merc.AFF_SHADOWPLANE):
        handler_game.act("$E is too insubstantial!", ch, None, victim, merc.TO_CHAR)
        return True

    if ch.in_room.room_flags.is_set(merc.ROOM_SAFE):
        ch.send("You cannot fight in a safe room.\n")
        return True

    if ch.head.is_set(merc.LOST_HEAD) or ch.extra.is_set(merc.EXTRA_OSWITCH):
        ch.send("Objects cannot fight!\n")
        return True
    elif victim.head.is_set(merc.LOST_HEAD) or victim.extra.is_set(merc.EXTRA_OSWITCH):
        ch.send("You cannot attack an object.\n")
        return True

    if ch.is_npc() or victim.is_npc():
        return False

    # Thx Josh!
    if victim.fighting == ch:
        return False

    if ch.itemaff.is_set(merc.ITEMA_PEACE):
        ch.send("You are unable to attack them.\n")
        return True

    if victim.itemaff.is_set(merc.ITEMA_PEACE):
        ch.send("You can't seem to attack them.\n")
        return True

    if ch.trust > merc.LEVEL_BUILDER:
        ch.send("You cannot fight if you have implementor powers!\n")
        return True

    if victim.trust > merc.LEVEL_BUILDER:
        ch.send("You cannot fight someone with implementor powers!\n")
        return True

    if not ch.can_pk() or not victim.can_pk():
        ch.send("Both players must be avatars to fight.\n")
        return True

    if (not ch.desc or not victim.desc) and victim.position != merc.POS_FIGHTING:
        ch.send("They are currently link dead.\n")
        return True

    return False


# See if an attack justifies a KILLER flag.
def check_killer(ch, victim):
    # Follow charm thread to responsible character.
    # Attacking someone's charmed char is hostile!
    while victim.is_affected(merc.AFF_CHARM) and victim.master:
        victim_id = victim.master
        victim = instance.characters[victim_id]

    # NPC's are fair game.
    # So are killers and thieves.
    if victim.is_npc():
        return

    # Charm-o-rama.
    if ch.affected_by.is_set(merc.AFF_CHARM):
        if not ch.master:
            ch.affect_strip("charm person")
            ch.affected_by.rem_bit(merc.AFF_CHARM)
            return

        handler_ch.stop_follower(ch)
        return


# Check for parry.
def check_parry(ch, victim, dt):
    chance = 0
    claws = False

    if not victim.is_awake():
        return False

    if victim.is_npc():
        item = None
    elif victim.is_werewolf() and victim.powers[merc.WPOWER_BEAR] > 2 and victim.vampaff.is_set(merc.VAM_CLAWS) and victim.get_eq("right_hand") and \
            victim.get_eq("left_hand"):
        item = None
        claws = True
    else:
        item = victim.get_eq("right_hand")
        if not item or item.item_type != merc.ITEM_WEAPON:
            item = victim.get_eq("left_hand")
            if not item or item.item_type != merc.ITEM_WEAPON:
                return False

    if dt not in merc.irange(1000, 1012):
        return False

    if not ch.is_npc():
        chance -= ch.wpn[dt - 1000] * 0.1
    else:
        chance -= ch.level * 0.2

    if not victim.is_npc():
        chance += victim.wpn[dt - 1000] * 0.5
    else:
        chance += victim.level

    if not victim.is_npc() and victim.stance[0] == merc.STANCE_CRANE and victim.stance[merc.STANCE_CRANE] > 0 and not can_counter(ch) and \
            not can_bypass(ch, victim):
        chance += victim.stance[merc.STANCE_CRANE] * 0.25
    elif not victim.is_npc() and victim.stance[0] == merc.STANCE_MANTIS and victim.stance[merc.STANCE_MANTIS] > 0 and not can_counter(ch) and \
            not can_bypass(ch, victim):
        chance += victim.stance[merc.STANCE_MANTIS] * 0.25

    chance -= ch.hitroll * 0.1

    if claws:
        if victim.powers[merc.WPOWER_LYNX] > 3:
            chance += victim.hitroll * 0.1
        else:
            chance += victim.hitroll * 0.075
    else:
        chance += victim.hitroll * 0.1

    if not ch.is_npc():
        if ch.vampaff.is_set(merc.VAM_CELERITY) and ch.is_vampire():
            chance -= 20
        elif ch.is_demon() and ch.dempower.is_set(merc.DEM_SPEED):
            chance -= 10
        elif ch.is_werewolf() and ch.powers[merc.WPOWER_MANTIS] < 5:
            chance -= ch.powers[merc.WPOWER_MANTIS] * 5

    if not victim.is_npc():
        if victim.vampaff.is_set(merc.VAM_CELERITY) and victim.is_vampire():
            chance += 20
        elif victim.is_demon() and victim.dempower.is_set(merc.DEM_SPEED):
            chance += 10

    chance = state_checks.urange(25, chance, 75)

    if not ch.is_npc() and ch.vampaff.is_set(merc.VAM_CELERITY) and ch.is_vampire():
        if ch.rank == merc.AGE_METHUSELAH:
            chance -= 15
        elif ch.rank == merc.AGE_ELDER:
            chance -= 10
        elif ch.rank == merc.AGE_ANCILLA:
            chance -= 5

    if not victim.is_npc() and victim.vampaff.is_set(merc.VAM_CELERITY) and victim.is_vampire():
        if victim.rank == merc.AGE_METHUSELAH:
            chance += 15
        elif victim.rank == merc.AGE_ELDER:
            chance += 10
        elif victim.rank == merc.AGE_ANCILLA:
            chance += 5

    if game_utils.number_percent(num_float=False) not in range(int(chance), 100):
        return False

    if claws:
        if victim.is_npc() or not victim.act.is_set(merc.PLR_BRIEF):
            handler_game.act("You parry $n's blow with your claws.", ch, None, victim, merc.TO_VICT)

        if ch.is_npc() or not ch.act.is_set(merc.PLR_BRIEF):
            handler_game.act("$N parries your blow with $S claws.", ch, None, victim, merc.TO_CHAR)
        return True

    if not victim.is_npc() and item and item.item_type == merc.ITEM_WEAPON and item.value[3] in merc.irange(0, 12):
        if victim.is_npc() or not victim.act.is_set(merc.PLR_BRIEF):
            handler_game.act("You parry $n's blow with $p.", ch, item, victim, merc.TO_VICT)

        if ch.is_npc() or not ch.act.is_set(merc.PLR_BRIEF):
            handler_game.act("$N parries your blow with $p.", ch, item, victim, merc.TO_CHAR)
        return True

    if victim.is_npc() or not victim.act.is_set(merc.PLR_BRIEF):
        handler_game.act("You parry $n's attack.", ch, None, victim, merc.TO_VICT)

    if ch.is_npc() or not ch.act.is_set(merc.PLR_BRIEF):
        handler_game.act("$N parries your attack.", ch, None, victim, merc.TO_CHAR)
    return True


# Check for dodge.
def check_dodge(ch, victim, dt):
    chance = 0

    if not victim.is_awake():
        return False

    if not ch.is_npc():
        chance -= ch.wpn[dt - 1000] * 0.1
    else:
        chance -= ch.level * 0.2

    if not victim.is_npc():
        chance += victim.wpn[0] * 0.5
    else:
        chance += victim.level

    if not victim.is_npc() and victim.stance[0] == merc.STANCE_MONGOOSE and victim.stance[merc.STANCE_MONGOOSE] > 0 and not can_counter(ch) and \
            not can_bypass(ch, victim):
        chance += victim.stance[merc.STANCE_MONGOOSE] * 0.25

    if not victim.is_npc() and victim.stance[0] == merc.STANCE_SWALLOW and victim.stance[merc.STANCE_SWALLOW] > 0 and not can_counter(ch) and \
            not can_bypass(ch, victim):
        chance += victim.stance[merc.STANCE_SWALLOW] * 0.25

    if not ch.is_npc():
        if ch.vampaff.is_set(merc.VAM_CELERITY) and not ch.is_vampire():
            chance -= 20
        elif ch.is_demon() and ch.dempower.is_set(merc.DEM_SPEED):
            chance -= 10
        elif ch.is_werewolf() and ch.powers[merc.WPOWER_MANTIS] < 5:
            chance -= ch.powers[merc.WPOWER_MANTIS] * 10

    if not victim.is_npc():
        if victim.vampaff.is_set(merc.VAM_CELERITY) and victim.is_vampire():
            chance += 20
        elif victim.is_demon() and victim.is_dempower.is_set(merc.DEM_SPEED):
            chance += 10

    chance = state_checks.urange(25, chance, 75)

    if not ch.is_npc() and ch.vampaff.is_set(merc.VAM_CELERITY) and ch.is_vampire():
        if ch.rank == merc.AGE_METHUSELAH:
            chance -= 15
        elif ch.rank == merc.AGE_ELDER:
            chance -= 10
        elif ch.rank == merc.AGE_ANCILLA:
            chance -= 5

    if not victim.is_npc() and victim.vampaff.is_set(merc.VAM_CELERITY) and victim.is_vampire():
        if victim.rank == merc.AGE_METHUSELAH:
            chance += 15
        elif victim.rank == merc.AGE_ELDER:
            chance += 10
        elif victim.rank == merc.AGE_ANCILLA:
            chance += 5

    if game_utils.number_percent(num_float=False) not in range(int(chance), 100):
        return False

    if victim.is_npc() or not victim.act.is_set(merc.PLR_BRIEF):
        handler_game.act("You dodge $n's attack.", ch, None, victim, merc.TO_VICT)

    if ch.is_npc() or not ch.act.is_set(merc.PLR_BRIEF):
        handler_game.act("$N dodges your attack.", ch, None, victim, merc.TO_CHAR)
    return True


# Set position of a victim.
def update_pos(victim):
    if victim.hit > 0:
        if victim.position <= merc.POS_STUNNED:
            gm_stance = False

            victim.position = merc.POS_STANDING
            if not victim.is_npc() and victim.stance[0] > 0:
                stance = victim.stance[0]
                if victim.stance[stance] >= 200:
                    gm_stance = True

            if victim.is_npc() or victim.max_hit * 0.25 > victim.hit or not gm_stance:
                handler_game.act("$n clambers back to $s feet.", victim, None, None, merc.TO_ROOM)
                handler_game.act("You clamber back to your feet.", victim, None, None, merc.TO_CHAR)
            else:
                handler_game.act("$n flips back up to $s feet.", victim, None, None, merc.TO_ROOM)
                handler_game.act("You flip back up to your feet.", victim, None, None, merc.TO_CHAR)
        return
    else:
        mount = victim.mount
        if mount:
            if victim.mounted == merc.IS_MOUNT:
                handler_game.act("$n rolls off $N.", mount, None, victim, merc.TO_ROOM)
                handler_game.act("You roll off $N.", mount, None, victim, merc.TO_CHAR)
            elif victim.mounted == merc.IS_RIDING:
                handler_game.act("$n falls off $N.", victim, None, mount, merc.TO_ROOM)
                handler_game.act("You fall off $N.", victim, None, mount, merc.TO_CHAR)

            mount.mount = None
            victim.mount = None
            mount.mounted = merc.IS_ON_FOOT
            victim.mounted = merc.IS_ON_FOOT

    if not victim.is_npc() and victim.hit <= -11 and victim.is_hero():
        victim.hit = -10

        if victim.position == merc.POS_FIGHTING:
            stop_fighting(victim, True)
        return

    if victim.is_npc() or victim.hit <= -11:
        victim.position = merc.POS_DEAD
        return

    if victim.hit <= -6:
        victim.position = merc.POS_MORTAL
    elif victim.hit <= -3:
        victim.position = merc.POS_INCAP
    else:
        victim.position = merc.POS_STUNNED


# Start fights.
def set_fighting(ch, victim):
    if ch.fighting:
        comm.notify("set_fighting: already fighting", merc.CONSOLE_WARNING)
        return

    if ch.is_affected(merc.AFF_SLEEP):
        ch.affect_strip("sleep")

    ch.fighting = victim
    ch.position = merc.POS_FIGHTING
    ch.damcap[merc.DAM_CHANGE] = 1


# Stop fights.
def stop_fighting(ch, fboth):
    for fch in instance.characters.values():
        if fch.instance_id == ch.instance_id or (fboth and fch.fighting == ch):
            fch.fighting = None
            fch.position = merc.POS_STANDING
            update_pos(fch)


def death_cry(ch):
    if ch.is_npc():
        msg = "You hear something's death cry."
    else:
        msg = "You hear someone's death cry."

    was_in_room = ch.in_room
    was_in_room.get(ch)
    for pexit in was_in_room.exit:
        if pexit and pexit.to_room and pexit.to_room != was_in_room.instance_id:
            instance.rooms[pexit.to_room].put(ch)
            handler_game.act(msg, ch, None, None, merc.TO_ROOM)
            instance.rooms[pexit.to_room].get(ch)
    was_in_room.put(ch)


def raw_kill(victim):
    stop_fighting(victim, True)
    death_cry(victim)
    object_creator.make_corpse(victim)

    mount = victim.mount
    if mount:
        if victim.mounted == merc.IS_MOUNT:
            handler_game.act("$n rolls off the corpse of $N.", mount, None, victim, merc.TO_ROOM)
            handler_game.act("You roll off the corpse of $N.", mount, None, victim, merc.TO_CHAR)
        elif victim.mounted == merc.IS_RIDING:
            handler_game.act("$n falls off $N.", victim, None, mount, merc.TO_ROOM)
            handler_game.act("You fall off $N.", victim, None, mount, merc.TO_CHAR)

        mount.mount = None
        victim.mount = None
        mount.mounted = merc.IS_ON_FOOT
        victim.mounted = merc.IS_ON_FOOT

    if victim.is_npc():
        instance.npc_templates[victim.vnum].killed += 1
        victim.extract(True)
        return

    victim.extract(False)

    for aff in victim.affected[:]:
        victim.affect_remove(aff)

    if victim.is_affected(merc.AFF_POLYMORPH) and victim.is_affected(merc.AFF_ETHEREAL):
        victim.affected_by.bits = merc.AFF_POLYMORPH + merc.AFF_ETHEREAL
    elif victim.is_affected(merc.AFF_POLYMORPH):
        victim.affected_by.bits = merc.AFF_POLYMORPH
    elif victim.is_affected(merc.AFF_ETHEREAL):
        victim.affected_by.bits = merc.AFF_ETHEREAL
    else:
        victim.affected_by.erase()

    victim.immune.rem_bit(merc.IMM_STAKE)
    victim.extra.rem_bit(merc.EXTRA_TIED_UP)
    victim.extra.rem_bit(merc.EXTRA_GAGGED)
    victim.extra.rem_bit(merc.EXTRA_BLINDFOLDED)
    victim.powers[merc.DEMON_POWER] = 0
    victim.itemaff.erase()
    victim.head.erase()
    victim.body.erase()
    victim.arm_left.erase()
    victim.arm_right.erase()
    victim.leg_left.erase()
    victim.leg_right.erase()
    victim.bleeding.erase()
    victim.armor = 100
    victim.position = merc.POS_RESTING
    victim.hit = max(1, victim.hit)
    victim.mana = max(1, victim.mana)
    victim.move = max(1, victim.move)
    victim.hitroll = 0
    victim.damroll = 0
    victim.saving_throw = 0
    victim.carry_weight = 0
    victim.carry_number = 0
    victim.cmd_call("all")
    victim.save(force=True)


def behead(victim):
    if victim.is_npc():
        return

    location = victim.in_room

    stop_fighting(victim, True)
    object_creator.make_corpse(victim)
    victim.extract(False)

    victim.in_room.get(victim)
    location.put(victim)

    if not victim:
        comm.notify("behead: victim no longer exists", merc.CONSOLE_WARNING)
        return

    object_creator.make_part(victim, "head")

    for aff in victim.affected[:]:
        victim.affect_remove(aff)

    if victim.is_affected(merc.AFF_POLYMORPH) and victim.is_affected(merc.AFF_ETHEREAL):
        victim.affected_by.bits = merc.AFF_POLYMORPH + merc.AFF_ETHEREAL
    elif victim.is_affected(merc.AFF_POLYMORPH):
        victim.affected_by.bits = merc.AFF_POLYMORPH
    elif victim.is_affected(merc.AFF_ETHEREAL):
        victim.affected_by.bits = merc.AFF_ETHEREAL
    else:
        victim.affected_by.erase()

    victim.immune.rem_bit(merc.IMM_STAKE)
    victim.extra.rem_bit(merc.EXTRA_TIED_UP)
    victim.extra.rem_bit(merc.EXTRA_GAGGED)
    victim.extra.rem_bit(merc.EXTRA_BLINDFOLDED)
    victim.powers[merc.DEMON_POWER] = 0
    victim.itemaff.erase()
    victim.head.erase()
    victim.body.erase()
    victim.arm_left.erase()
    victim.arm_right.erase()
    victim.leg_left.erase()
    victim.leg_right.erase()
    victim.bleeding.erase()
    victim.armor = 100
    victim.position = merc.POS_RESTING
    victim.hit = max(1, victim.hit)
    victim.mana = max(1, victim.mana)
    victim.move = max(1, victim.move)
    victim.hitroll = 0
    victim.damroll = 0
    victim.saving_throw = 0
    victim.carry_weight = 0
    victim.carry_number = 0
    victim.head.set_bit(merc.LOST_HEAD)
    victim.affected_by.set_bit(merc.AFF_POLYMORPH)
    victim.morph = "the severed head of {}".format(victim.name)
    victim.cmd_call("all")
    victim.save(force=True)


def group_gain(ch, victim):
    # Monsters don't get kill xp's or alignment changes.
    # P-killing doesn't help either.
    # Dying of mortal wounds or poison doesn't give xp to anyone!
    mount = ch.mount
    if (ch.is_npc() and not mount) or victim == ch:
        return

    members = 0
    for gch_id in ch.in_room.people[:]:
        gch = instance.characters[gch_id]

        if gch.is_same_group(ch):
            members += 1

    if members == 0:
        comm.notify("group_gain: members {}".format(members), merc.CONSOLE_WARNING)
        members = 1

    for gch_id in ch.in_room.people[:]:
        gch = instance.characters[gch_id]
        if not gch.is_same_group(ch):
            continue

        xp = xp_compute(gch, victim) // members
        gch.send("You receive {:,} experience points.\n".format(xp))

        mount = gch.mount
        if mount:
            mount.send("You receive {:,} experience points.\n".format(xp))
        update.gain_exp(gch, xp)

        for item_id in ch.equipped.values():
            if not item_id:
                continue

            item = instance.items[item_id]
            if (item.flags.anti_evil and ch.is_evil()) or (item.flags.anti_good and ch.is_good()) \
                    or (item.flags.anti_neutral and ch.is_neutral()):
                handler_game.act("You are zapped by $p.", ch, item, None, merc.TO_CHAR)
                handler_game.act("$n is zapped by $p.", ch, item, None, merc.TO_ROOM)
                ch.unequip(item.equipped_to, False)
                ch.get(item)
                ch.in_room.put(item)


# Compute xp for a kill.
# Also adjust alignment of killer.
# Edit this function to change xp computations.
def xp_compute(gch, victim):
    xp = 300 - state_checks.urange(-3, 3 - victim.level, 6) * 50
    align = gch.alignment - victim.alignment
    victim_level = 1000 if victim.level > 1000 else victim.level

    if gch.is_hero():
        # Avatars shouldn't be able to change their alignment
        gch.alignment = gch.alignment
    elif align > 500:
        gch.alignment = min(gch.alignment + (align - 500) // 4, 1000)
        xp = 5 * xp // 4
    elif align < -500:
        gch.alignment = max(gch.alignment + (align + 500) // 4, -1000)
    else:
        gch.alignment -= gch.alignment // 4
        xp = 3 * xp // 4

    # Put in mob vnum that you don't want players to gain exp for
    vnum = victim.vnum
    if victim.is_npc() and vnum > 29000:
        if vnum in [29600, 30001, 30006, 30007, 30008, 30009, 30000]:
            return 0

    if victim.is_npc() and (victim.act.is_set(merc.ACT_NOEXP) or gch.is_immortal()):
        return 0

    # Adjust for popularity of target:
    #   -1/8 for each target over  'par' (down to -100%)
    #   +1/8 for each target under 'par' (  up to + 25%)
    xp -= xp * game_utils.number_range(-2, 2) // 8
    xp = game_utils.number_range(xp * 3 // 4, xp * 5 // 4)
    xp = max(0, xp)
    xp = xp * (victim_level + 1) * 0.25
    xp = xp // 2  # Put in cause players compaling to much exp :P

    if not gch.is_npc():
        gch.score[merc.SCORE_TOTAL_LEVEL] += victim.level

        if victim.level > gch.score[merc.SCORE_HIGH_LEVEL]:
            gch.score[merc.SCORE_HIGH_LEVEL] += victim.level

        if victim.level > 950:
            return 0

        gch.score[merc.SCORE_TOTAL_XP] += xp
        if xp > gch.score[merc.SCORE_HIGH_XP]:
            gch.score[merc.SCORE_HIGH_XP] += xp
    return xp


def dam_message(ch, victim, dam, dt):
    critical = False

    if dam == 0:
        msg = {'vs': " miss", 'vp': " misses"}
    elif dam <= 25:
        msg = {'vs': " lightly", 'vp': " mauls"}
    elif dam <= 50:
        msg = {'vs': "", 'vp': ""}
    elif dam <= 100:
        msg = {'vs': " hard", 'vp': " hard"}
    elif dam <= 250:
        msg = {'vs': " very hard", 'vp': " very hard"}
    elif dam <= 500:
        msg = {'vs': " extremely hard", 'vp': " extremely hard"}
    else:
        msg = {'vs': " incredibly hard", 'vp': " incredibly hard"}

    vs = msg['vs']
    vp = msg['vp']
    damp = 0 if victim.is_npc() else -10

    if victim.hit - dam > damp or type(dt) == const.skill_type or (victim.is_npc() and victim.act.is_set(merc.ACT_NOPARTS)):
        punct = '.' if dam <= 250 else '!'

        if dt == merc.TYPE_HIT and not ch.vampaff.is_set(merc.VAM_CLAWS):
            if dam == 0:
                buf1 = "$n{} $N{}".format(vp, punct)
                buf2 = "You{} $N{}".format(vs, punct)
                buf3 = "$n{} you{}".format(vp, punct)
            else:
                buf1 = "$n hits $N{}{}".format(vp, punct)
                buf2 = "You hit $N{}{}".format(vs, punct)
                buf3 = "$n hits you{}{}".format(vp, punct)
        else:
            if dt == merc.TYPE_HIT and not ch.is_npc() and ch.vampaff.is_set(merc.VAM_CLAWS):
                attack1 = const.attack_table[dt - merc.TYPE_HIT + 5].noun
                attack2 = const.attack_table[dt - merc.TYPE_HIT + 5].noun
            elif type(dt) == const.skill_type:
                attack1 = dt.noun_damage
                attack2 = dt.noun_damage
            elif isinstance(dt, str):
                attack1 = dt
                attack2 = dt
            elif merc.TYPE_HIT <= dt < merc.TYPE_HIT + len(const.attack_table):
                attack1 = const.attack_table[dt - merc.TYPE_HIT].noun
                attack2 = const.attack_table[dt - merc.TYPE_HIT].noun
            else:
                comm.notify("dam_message: bad dt {}".format(dt), merc.CONSOLE_WARNING)
                dt = merc.TYPE_HIT
                attack1 = const.attack_table[0].name
                attack2 = const.attack_table[0].name

            if dam == 0:
                buf1 = "$n's {}{} $N{}".format(attack1, vp, punct)
                buf2 = "Your {}{} $N{}".format(attack1, vp, punct)
                buf3 = "$n's {}{} you{}".format(attack1, vp, punct)
            else:
                if type(dt) == const.skill_type:
                    buf1 = "$n's {} strikes $N{}{}".format(attack2, vp, punct)
                    buf2 = "Your {} strikes $N{}{}".format(attack1, vp, punct)
                    buf3 = "$n's {} strikes you{}{}".format(attack2, vp, punct)
                else:
                    buf1 = "$n {} $N{}{}".format(attack2, vp, punct)
                    buf2 = "You {} $N{}{}".format(attack1, vp, punct)
                    buf3 = "$n {} you{}{}".format(attack2, vp, punct)
                    critical = True

            # Check for weapon resistance - KaVir
            recover = 0
            if not victim.is_npc() and victim.immune.is_set(merc.IMM_SLASH) and attack1 in ["slash", "slice"] and dam > 0:
                recover = game_utils.number_range(1, dam)
            if not victim.is_npc() and victim.immune.is_set(merc.IMM_STAB) and attack1 in ["stab", "pierce"] and dam > 0:
                recover = game_utils.number_range(1, dam)
            if not victim.is_npc() and victim.immune.is_set(merc.IMM_SMASH) and attack1 in ["blast", "pound", "crush"] and dam > 0:
                recover = game_utils.number_range(1, dam)
            if not victim.is_npc() and victim.immune.is_set(merc.IMM_ANIMAL) and attack1 in ["bite", "claw"] and dam > 0:
                recover = game_utils.number_range(1, dam)
            if not victim.is_npc() and victim.immune.is_set(merc.IMM_MISC) and attack1 in ["grep", "suck", "whip"] and dam > 0:
                recover = game_utils.number_range(1, dam)

            # Check for fortitude - KaVir
            if not victim.is_npc() and victim.is_vampire() and victim.vampaff.is_set(merc.VAM_FORTITUDE) and (dam - recover) > 0:
                victim.hit += game_utils.number_range(1, (dam - recover))
            elif victim.itemaff.is_set(merc.ITEMA_RESISTANCE) and (dam - recover) > 0:
                victim.hit += game_utils.number_range(1, (dam - recover))
            elif not victim.is_npc() and victim.is_demon() and victim.dempower.is_set(merc.DEM_TOUGH) and (dam - recover) > 0:
                victim.hit += game_utils.number_range(1, (dam - recover))
            victim.hit += recover

        handler_game.act(buf1, ch, None, victim, merc.TO_NOTVICT)
        handler_game.act(buf2, ch, None, victim, merc.TO_CHAR)
        handler_game.act(buf3, ch, None, victim, merc.TO_VICT)

        if critical and isinstance(dt, int):
            ch.critical_hit(victim, dt, dam)
        return

    if dt == merc.TYPE_HIT and not ch.is_npc() and not ch.vampaff.is_set(merc.VAM_CLAWS) and not ch.vampaff.is_set(merc.VAM_FANGS):
        damp = game_utils.number_range(1, 5)
        if damp == 1:
            handler_game.act("You ram your fingers into $N's eye sockets and rip $S face off.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n rams $s fingers into $N's eye sockets and rips $S face off.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n rams $s fingers into your eye sockets and rips your face off.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "face")
        elif damp == 2:
            handler_game.act("You grab $N by the throat and tear $S windpipe out.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n grabs $N by the throat and tears $S windpipe out.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n grabs you by the throat and tears your windpipe out.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "windpipe")
        elif damp == 3:
            handler_game.act("You punch your fist through $N's stomach and rip out $S entrails.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n punches $s fist through $N's stomach and rips out $S entrails.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n punches $s fist through your stomach and rips out your entrails.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "entrails")
        elif damp == 4:
            victim.body.set_bit(merc.BROKEN_SPINE)
            handler_game.act("You hoist $N above your head and slam $M down upon your knee.\n"
                             "There is a loud cracking sound as $N's spine snaps.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n hoists $N above $s head and slams $M down upon $s knee.\n"
                             "There is a loud cracking sound as $N's spine snaps.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n hoists you above $s head and slams you down upon $s knee.\n"
                             "There is a loud cracking sound as your spine snaps.", ch, None, victim, merc.TO_VICT)
        elif damp == 5:
            handler_game.act("You lock your arm around $N's head, and give it a vicious twist.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n locks $s arm around $N's head, and gives it a vicious twist.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n locks $s arm around your head, and gives it a vicious twist.", ch, None, victim, merc.TO_VICT)

            if not victim.body.is_set(merc.BROKEN_NECK):
                handler_game.act("There is a loud snapping noise as your neck breaks.", victim, None, None, merc.TO_CHAR)
                handler_game.act("There is a loud snapping noise as $n's neck breaks.", victim, None, None, merc.TO_ROOM)
                victim.body.set_bit(merc.BROKEN_NECK)
        return

    if type(dt) == const.skill_type:
        attack1 = const.skill_table[dt].noun_damage
    elif isinstance(dt, str):
        attack1 = dt
    elif merc.TYPE_HIT <= dt < merc.TYPE_HIT + len(const.attack_table):
        attack1 = const.attack_table[dt - merc.TYPE_HIT].noun
    else:
        comm.notify("dam_message: bad dt {}".format(dt), merc.CONSOLE_WARNING)
        dt = merc.TYPE_HIT
        attack1 = const.attack_table[0].noun

    if attack1 in ["slash", "slice"]:
        damp = game_utils.number_range(1, 8)
        if damp == 1:
            handler_game.act("You swing your blade in a low arc, rupturing $N's abdominal cavity.\n"
                             "$S entrails spray out over a wide area.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n swings $s blade in a low arc, rupturing $N's abdominal cavity.\n"
                             "$S entrails spray out over a wide area.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n swings $s blade in a low arc, rupturing your abdominal cavity.\n"
                             "Your entrails spray out over a wide area.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "entrails")
        elif damp == 2:
            handler_game.act("You thrust your blade into $N's mouth and twist it viciously.\n"
                             "The end of your blade bursts through the back of $S head.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n thrusts $s blade into $N's mouth and twists it viciously.\n"
                             "The end of the blade bursts through the back of $N's head.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n thrusts $s blade into your mouth and twists it viciously.\n"
                             "You feel the end of the blade burst through the back of your head.", ch, None, victim, merc.TO_VICT)
        elif damp == 3:
            victim.body.set_bit(merc.CUT_THROAT)
            victim.bleeding.set_bit(merc.BLEEDING_THROAT)
            handler_game.act("Your blow slices open $N's carotid artery, spraying blood everywhere.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n's blow slices open $N's carotid artery, spraying blood everywhere.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's blow slices open your carotid artery, spraying blood everywhere.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "blood")
        elif damp == 4:
            victim.body.set_bit(merc.CUT_THROAT)
            victim.bleeding.set_bit(merc.BLEEDING_THROAT)
            handler_game.act("You swing your blade across $N's throat, showering the area with blood.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n swings $s blade across $N's throat, showering the area with blood.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n swings $s blade across your throat, showering the area with blood.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "blood")
        elif damp == 5:
            if not victim.head.is_set(merc.BROKEN_SKULL):
                handler_game.act("You swing your blade down upon $N's head, splitting it open.\n"
                                 "$N's brains pour out of $S forehead.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n swings $s blade down upon $N's head, splitting it open.\n"
                                 "$N's brains pour out of $S forehead.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n swings $s blade down upon your head, splitting it open.\n"
                                 "Your brains pour out of your forehead.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "brain")
                victim.head.set_bit(merc.BROKEN_SKULL)
            else:
                handler_game.act("You plunge your blade deep into $N's chest.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n plunges $s blade deep into $N's chest.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n plunges $s blade deep into your chest.", ch, None, victim, merc.TO_VICT)
        elif damp == 6:
            handler_game.act("You swing your blade between $N's legs, nearly splitting $M in half.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n swings $s blade between $N's legs, nearly splitting $M in half.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n swings $s blade between your legs, nearly splitting you in half.", ch, None, victim, merc.TO_VICT)
        elif damp == 7:
            if not victim.arm_left.is_set(merc.LOST_ARM):
                handler_game.act("You swing your blade in a wide arc, slicing off $N's arm.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n swings $s blade in a wide arc, slicing off $N's arm.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n swings $s blade in a wide arc, slicing off your arm.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "arm")
                victim.arm_left.set_bit(merc.LOST_ARM)
                victim.bleeding.set_bit(merc.BLEEDING_ARM_L)
                victim.bleeding.set_bit(merc.BLEEDING_HAND_L)
            elif not victim.arm_right.is_set(merc.LOST_ARM):
                handler_game.act("You swing your blade in a wide arc, slicing off $N's arm.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n swings $s blade in a wide arc, slicing off $N's arm.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n swings $s blade in a wide arc, slicing off your arm.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "arm")
                victim.arm_right.set_bit(merc.LOST_ARM)
                victim.bleeding.set_bit(merc.BLEEDING_ARM_R)
                victim.bleeding.set_bit(merc.BLEEDING_HAND_R)
            else:
                handler_game.act("You plunge your blade deep into $N's chest.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n plunges $s blade deep into $N's chest.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n plunges $s blade deep into your chest.", ch, None, victim, merc.TO_VICT)
        else:
            if not victim.leg_left.is_set(merc.LOST_LEG):
                handler_game.act("You swing your blade in a low arc, slicing off $N's leg at the hip.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n swings $s blade in a low arc, slicing off $N's leg at the hip.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n swings $s blade in a wide arc, slicing off your leg at the hip.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "leg")
                victim.leg_left.set_bit(merc.LOST_LEG)
                victim.bleeding.set_bit(merc.BLEEDING_LEG_L)
                victim.bleeding.set_bit(merc.BLEEDING_FOOT_L)
            elif not victim.leg_right.is_set(merc.LOST_LEG):
                handler_game.act("You swing your blade in a low arc, slicing off $N's leg at the hip.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n swings $s blade in a low arc, slicing off $N's leg at the hip.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n swings $s blade in a wide arc, slicing off your leg at the hip.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "leg")
                victim.leg_right.set_bit(merc.LOST_LEG)
                victim.bleeding.set_bit(merc.BLEEDING_LEG_R)
                victim.bleeding.set_bit(merc.BLEEDING_FOOT_R)
            else:
                handler_game.act("You plunge your blade deep into $N's chest.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n plunges $s blade deep into $N's chest.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n plunges $s blade deep into your chest.", ch, None, victim, merc.TO_VICT)
    elif attack1 in ["stab", "pierce"]:
        damp = game_utils.number_range(1, 5)
        if damp == 1:
            handler_game.act("You defty invert your weapon and plunge it point first into $N's chest.\n"
                             "A shower of blood sprays from the wound, showering the area.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n defty inverts $s weapon and plunge it point first into $N's chest.\n"
                             "A shower of blood sprays from the wound, showering the area.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n defty inverts $s weapon and plunge it point first into your chest.\n"
                             "A shower of blood sprays from the wound, showering the area.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "blood")
        elif damp == 2:
            handler_game.act("You thrust your blade into $N's mouth and twist it viciously.\n"
                             "The end of your blade bursts through the back of $S head.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n thrusts $s blade into $N's mouth and twists it viciously.\n"
                             "The end of the blade bursts through the back of $N's head.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n thrusts $s blade into your mouth and twists it viciously.\n"
                             "You feel the end of the blade burst through the back of your head.", ch, None, victim, merc.TO_VICT)
        elif damp == 3:
            handler_game.act("You thrust your weapon up under $N's jaw and through $S head.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n thrusts $s weapon up under $N's jaw and through $S head.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n thrusts $s weapon up under your jaw and through your head.", ch, None, victim, merc.TO_VICT)
        elif damp == 4:
            handler_game.act("You ram your weapon through $N's body, pinning $M to the ground.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n rams $s weapon through $N's body, pinning $M to the ground.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n rams $s weapon through your body, pinning you to the ground.", ch, None, victim, merc.TO_VICT)
        else:
            handler_game.act("You stab your weapon into $N's eye and out the back of $S head.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n stabs $s weapon into $N's eye and out the back of $S head.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n stabs $s weapon into your eye and out the back of your head.", ch, None, victim, merc.TO_VICT)
            if not victim.head.is_set(merc.LOST_EYE_L) and game_utils.number_percent() < 50:
                victim.head.set_bit(merc.LOST_EYE_L)
            elif not victim.head.is_set(merc.LOST_EYE_R):
                victim.head.set_bit(merc.LOST_EYE_R)
            elif not victim.head.is_set(merc.LOST_EYE_L):
                victim.head.set_bit(merc.LOST_EYE_L)
    elif attack1 in ["blast", "pound", "crush"]:
        damp = game_utils.number_range(1, 3)
        if damp == 1:
            handler_game.act("Your blow smashes through $N's chest, caving in half $S ribcage.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n's blow smashes through $N's chest, caving in half $S ribcage.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's blow smashes through your chest, caving in half your ribcage.", ch, None, victim, merc.TO_VICT)

            bodyloc = 0
            body_list = [(merc.BROKEN_RIBS_1, 1), (merc.BROKEN_RIBS_2, 2), (merc.BROKEN_RIBS_4, 4), (merc.BROKEN_RIBS_8, 8),
                         (merc.BROKEN_RIBS_16, 16)]
            for (aa, bb) in body_list:
                if victim.body.is_set(aa):
                    bodyloc += bb
                    victim.body.rem_bit(aa)

            bodyloc = min(bodyloc + game_utils.number_range(1, 3), 24)

            if bodyloc >= 16:
                bodyloc -= 16
                victim.body.set_bit(merc.BROKEN_RIBS_16)

            if bodyloc >= 8:
                bodyloc -= 8
                victim.body.set_bit(merc.BROKEN_RIBS_8)

            if bodyloc >= 4:
                bodyloc -= 4
                victim.body.set_bit(merc.BROKEN_RIBS_4)

            if bodyloc >= 2:
                bodyloc -= 2
                victim.body.set_bit(merc.BROKEN_RIBS_2)

            if bodyloc >= 1:
                bodyloc -= 1
                victim.body.set_bit(merc.BROKEN_RIBS_1)
        elif damp == 2:
            handler_game.act("Your blow smashes $N's spine, shattering it in several places.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n's blow smashes $N's spine, shattering it in several places.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's blow smashes your spine, shattering it in several places.", ch, None, victim, merc.TO_VICT)
            victim.body.set_bit(merc.BROKEN_SPINE)
        else:
            if not victim.head.is_set(merc.BROKEN_SKULL):
                handler_game.act("You swing your weapon down upon $N's head.\n"
                                 "$N's head cracks open like an overripe melon, leaking out brains.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n swings $s weapon down upon $N's head.\n"
                                 "$N's head cracks open like an overripe melon, covering you with brains.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n swings $s weapon down upon your head.\n"
                                 "Your head cracks open like an overripe melon, spilling your brains everywhere.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "brain")
                victim.head.set_bit(merc.BROKEN_SKULL)
            else:
                handler_game.act("You hammer your weapon into $N's side, crushing bone.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n hammers $s weapon into $N's side, crushing bone.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n hammers $s weapon into your side, crushing bone.", ch, None, victim, merc.TO_VICT)
    elif not ch.is_npc() and (attack1 == "bite" or ch.vampaff.is_set(merc.VAM_FANGS)):
        handler_game.act("You sink your teeth into $N's throat and tear out $S jugular vein.\n"
                         "You wipe the blood from your chin with one hand.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n sink $s teeth into $N's throat and tears out $S jugular vein.\n"
                         "$n wipes the blood from $s chin with one hand.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n sink $s teeth into your throat and tears out your jugular vein.\n"
                         "$n wipes the blood from $s chin with one hand.", ch, None, victim, merc.TO_VICT)
        object_creator.make_part(victim, "blood")
        victim.body.set_bit(merc.CUT_THROAT)
        victim.bleeding.set_bit(merc.BLEEDING_THROAT)
    elif not ch.is_npc() and (attack1 == "claw" or ch.vampaff.is_set(merc.VAM_CLAWS)):
        damp = game_utils.number_range(1, 2)
        if damp == 1:
            handler_game.act("You tear out $N's throat, showering the area with blood.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n tears out $N's throat, showering the area with blood.", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n tears out your throat, showering the area with blood.", ch, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "blood")
            victim.body.set_bit(merc.CUT_THROAT)
            victim.bleeding.set_bit(merc.BLEEDING_THROAT)
        else:
            if not victim.head.is_set(merc.LOST_EYE_L) and game_utils.number_percent() < 50:
                handler_game.act("You rip an eyeball from $N's face.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n rips an eyeball from $N's face.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n rips an eyeball from your face.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "eyeball")
                victim.head.set_bit(merc.LOST_EYE_L)
            elif not victim.head.is_set(merc.LOST_EYE_R):
                handler_game.act("You rip an eyeball from $N's face.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n rips an eyeball from $N's face.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n rips an eyeball from your face.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "eyeball")
                victim.head.set_bit(merc.LOST_EYE_R)
            elif not victim.head.is_set(merc.LOST_EYE_L):
                handler_game.act("You rip an eyeball from $N's face.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n rips an eyeball from $N's face.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n rips an eyeball from your face.", ch, None, victim, merc.TO_VICT)
                object_creator.make_part(victim, "eyeball")
                victim.head.set_bit(merc.LOST_EYE_L)
            else:
                handler_game.act("You claw open $N's chest.", ch, None, victim, merc.TO_CHAR)
                handler_game.act("$n claws open $N's chest.", ch, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n claws open $N's chest.", ch, None, victim, merc.TO_VICT)
    elif attack1 == "whip":
        handler_game.act("You entangle $N around the neck, and squeeze the life out of $S.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n entangle $N around the neck, and squeezes the life out of $S.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n entangles you around the neck, and squeezes the life out of you.", ch, None, victim, merc.TO_VICT)
        victim.body.set_bit(merc.BROKEN_NECK)
    elif attack1 in ["suck", "grep"]:
        handler_game.act("You place your weapon on $N's head and suck out $S brains.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n places $s weapon on $N's head and suck out $S brains.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n places $s weapon on your head and suck out your brains.", ch, None, victim, merc.TO_VICT)
    else:
        comm.notify("dam_message: bad dt {}".format(dt), merc.CONSOLE_WARNING)


# Disarm a creature.
# Caller must check for successful attack.
def disarm(ch, victim):
    # I'm fed up of being disarmed every 10 seconds - KaVir
    if ch.is_npc() and victim.level > 2 and game_utils.number_percent() > 5:
        return

    if not victim.is_npc() and victim.immune.is_set(merc.IMM_DISARM):
        return

    item = victim.get_eq("right_hand")
    if not item or item.item_type != merc.ITEM_WEAPON:
        item = victim.get_eq("left_hand")
        if not item or item.item_type != merc.ITEM_WEAPON:
            return

    handler_game.act("#W$n disarms you!#n", ch, None, victim, merc.TO_VICT)
    handler_game.act("#WYou disarm $N!#n", ch, None, victim, merc.TO_CHAR)
    handler_game.act("#W$n disarms $N!#n", ch, None, victim, merc.TO_NOTVICT)

    # Loyal weapons come back ;)  KaVir
    if item.flags.loyal and not victim.is_npc():
        handler_game.act("$p leaps back into your hand!", victim, item, None, merc.TO_CHAR)
        handler_game.act("$p leaps back into $n's hand!", victim, item, None, merc.TO_ROOM)
        return

    victim.unequip('main_hand')
    victim.get(item)
    victim.in_room.put(item)


# Trip a creature.
# Caller must check for successful attack.
def trip(ch, victim):
    if victim.is_affected(merc.AFF_FLYING):
        return

    if ch.is_npc() and victim.level > 2 and game_utils.number_percent() > 5:
        return

    if not victim.is_npc():
        if victim.is_vampire() and victim.vampaff.is_set(merc.VAM_FLYING):
            return

        if (victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION)) and victim.demaff.is_set(merc.DEM_UNFOLDED):
            return

    if victim.wait == 0:
        handler_game.act("#W$n trips you and you go down!#n", ch, None, victim, merc.TO_VICT)
        handler_game.act("#WYou trip $N and $E goes down!#n", ch, None, victim, merc.TO_CHAR)
        handler_game.act("#W$n trips $N and $E goes down!#n", ch, None, victim, merc.TO_NOTVICT)
        ch.wait_state(merc.PULSE_VIOLENCE * 2)
        victim.wait_state(merc.PULSE_VIOLENCE * 2)
        victim.position = merc.POS_RESTING


def dambonus(ch, victim, dam, stance):
    if dam < 1:
        return 0

    if stance < 1:
        return dam

    if not ch.is_npc() and not can_counter(victim):
        if ch.stance[0] == merc.STANCE_MONKEY:
            mindam = dam * 0.25
            dam *= ch.stance[merc.STANCE_MONKEY] + 1 // 200
            if dam < mindam:
                dam = mindam
        elif ch.stance[0] == merc.STANCE_BULL and ch.stance[merc.STANCE_BULL] > 100:
            dam += dam * ch.stance[merc.STANCE_BULL] // 100
        elif ch.stance[0] == merc.STANCE_DRAGON and ch.stance[merc.STANCE_DRAGON] > 100:
            dam += dam * ch.stance[merc.STANCE_DRAGON] // 100
        elif ch.stance[0] == merc.STANCE_TIGER and ch.stance[merc.STANCE_TIGER] > 100:
            dam += dam * ch.stance[merc.STANCE_TIGER] // 100
        elif ch.stance[0] > 0 and ch.stance[stance] < 100:
            dam *= 0.5

    if not victim.is_npc() and not can_counter(ch):
        if victim.stance[0] == merc.STANCE_CRAB and victim.stance[merc.STANCE_CRAB] > 100:
            dam //= victim.stance[merc.STANCE_CRAB] // 100
        elif victim.stance[0] == merc.STANCE_DRAGON and victim.stance[merc.STANCE_DRAGON] > 100:
            dam //= victim.stance[merc.STANCE_DRAGON] // 100
        elif victim.stance[0] == merc.STANCE_SWALLOW and victim.stance[merc.STANCE_SWALLOW] > 100:
            dam //= victim.stance[merc.STANCE_SWALLOW] // 100
    return int(dam)


def special_move(ch, victim):
    dam = game_utils.number_range(5, 10) + ch.damroll
    if dam < 10:
        dam = 10

    chance = game_utils.number_range(1, 7)
    if chance == 1:
        handler_game.act("You pull your hands into your waist then snap them into $N's stomach.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n pulls $s hands into $s waist then snaps them into your stomach.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n pulls $s hands into $s waist then snaps them into $N's stomach.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "punch")

        if not victim or victim.position == merc.POS_DEAD:
            return

        handler_game.act("You double over in agony, and fall to the ground gasping for breath.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n doubles over in agony, and falls to the ground gasping for breath.", victim, None, None, merc.TO_ROOM)
        stop_fighting(victim, True)
        victim.position = merc.POS_STUNNED
    elif chance == 2:
        handler_game.act("You spin in a low circle, catching $N behind $S ankle.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n spins in a low circle, catching you behind your ankle.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n spins in a low circle, catching $N behind $S ankle.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "sweep")

        if not victim or victim.position == merc.POS_DEAD:
            return

        if game_utils.number_percent() <= 25 and not victim.leg_left.is_set(merc.BROKEN_LEG) and not victim.leg_left.is_set(merc.LOST_LEG):
            handler_game.act("Your left leg shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's left leg shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.leg_left.set_bit(merc.BROKEN_LEG)
        elif game_utils.number_percent() <= 25 and not victim.leg_right.is_set(merc.BROKEN_LEG) and not victim.leg_right.set_bit(merc.LOST_LEG):
            handler_game.act("Your right leg shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's right leg shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.leg_right.set_bit(merc.BROKEN_LEG)

        handler_game.act("You crash to the ground, stunned.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n crashes to the ground, stunned.", victim, None, None, merc.TO_ROOM)
        stop_fighting(victim, True)
        victim.position = merc.POS_STUNNED
    elif chance == 3:
        handler_game.act("You roll between $N's legs and flip to your feet.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n rolls between your legs and flips to $s feet.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n rolls between $N's legs and flips to $s feet.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("You spin around and smash your elbow into the back of $N's head.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n spins around and smashes $s elbow into the back of your head.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n spins around and smashes $s elbow into the back of $N's head.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "elbow")

        if not victim or victim.position == merc.POS_DEAD:
            return

        handler_game.act("You fall to the ground, stunned.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n falls to the ground, stunned.", victim, None, None, merc.TO_ROOM)
        stop_fighting(victim, True)
        victim.position = merc.POS_STUNNED
    elif chance == 4:
        handler_game.act("You somersault over $N's head and land lightly on your toes.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n somersaults over your head and lands lightly on $s toes.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n somersaults over $N's head and lands lightly on $s toes.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("You roll back onto your shoulders and kick both feet into $N's back.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n rolls back onto $s shoulders and kicks both feet into your back.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n rolls back onto $s shoulders and kicks both feet into $N's back.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "kick")

        if not victim or victim.position == merc.POS_DEAD:
            return

        if game_utils.number_percent() <= 25 and not victim.body.is_set(merc.BROKEN_SPINE):
            handler_game.act("Your spine shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's spine shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.body.set_bit(merc.BROKEN_SPINE)

        handler_game.act("You fall to the ground, stunned.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n falls to the ground, stunned.", victim, None, None, merc.TO_ROOM)
        handler_game.act("You flip back up to your feet.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n flips back up to $s feet.", ch, None, None, merc.TO_ROOM)
        stop_fighting(victim, True)
        victim.position = merc.POS_STUNNED
    elif chance == 5:
        handler_game.act("You grab $N by the neck and slam your head into $S face.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n grabs $N by the neck and slams $s head into $S face.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n grabs you by the neck and slams $s head into your face.", ch, None, victim, merc.TO_VICT)
        damage(ch, victim, dam, "headbutt")

        if not victim or victim.position == merc.POS_DEAD:
            return

        if game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_NOSE) and not victim.head.is_set(merc.LOST_NOSE):
            handler_game.act("Your nose shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's nose shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_NOSE)
        elif game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_JAW):
            handler_game.act("Your jaw shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's jaw shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_JAW)
        elif game_utils.number_percent() <= 25 and not victim.body.is_set(merc.BROKEN_NECK):
            handler_game.act("Your neck shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's neck shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.body.set_bit(merc.BROKEN_NECK)

        handler_game.act("You grab $N by the waist and hoist $M above your head.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n grabs $N by the waist and hoists $M above $s head.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n grabs you by the waist and hoists you above $s head.", ch, None, victim, merc.TO_VICT)
        special_hurl(ch, victim)

        if not victim or victim.position == merc.POS_DEAD:
            return

        handler_game.act("You crash to the ground, stunned.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n crashes to the ground, stunned.", victim, None, None, merc.TO_ROOM)
        stop_fighting(victim, True)
        victim.position = merc.POS_STUNNED
    elif chance == 6:
        handler_game.act("You slam your fist into $N's stomach, who doubles over in agony.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n slams $s fist into your stomach, and you double over in agony.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n slams $s fist into $N's stomach, who doubles over in agony.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("You grab $N by the head and slam $S face into your knee.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n grabs you by the head and slams your face into $s knee.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n grabs $N by the head and slams $S face into $s knee.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "knee")

        if not victim or victim.position == merc.POS_DEAD:
            return

        if game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_NOSE) and not victim.head.is_set(merc.LOST_NOSE):
            handler_game.act("Your nose shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's nose shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_NOSE)
        elif game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_JAW):
            handler_game.act("Your jaw shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's jaw shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_JAW)
        elif game_utils.number_percent() <= 25 and not victim.body.is_set(merc.BROKEN_NECK):
            handler_game.act("Your neck shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's neck shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.body.set_bit(merc.BROKEN_NECK)

        handler_game.act("You roll onto your back and smash your feet into $N's chest.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n rolls onto $s back and smashes $s feet into your chest.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n rolls onto $s back and smashes $s feet into $N's chest.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "kick")

        if not victim or victim.position == merc.POS_DEAD:
            return

        handler_game.act("You crash to the ground, stunned.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n crashes to the ground, stunned.", victim, None, None, merc.TO_ROOM)
        handler_game.act("You flip back up to your feet.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n flips back up to $s feet.", ch, None, None, merc.TO_ROOM)
        stop_fighting(victim, True)
        victim.position = merc.POS_STUNNED
    elif chance == 7:
        handler_game.act("You duck under $N's attack and pound your fist into $S stomach.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n ducks under your attack and pounds $s fist into your stomach.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n ducks under $N's attack and pounds $s fist into $N's stomach.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "punch")

        if not victim or victim.position == merc.POS_DEAD:
            return

        handler_game.act("You double over in agony.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n doubles over in agony.", victim, None, None, merc.TO_ROOM)
        handler_game.act("You grab $M by the head and smash your knee into $S face.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n grabs you by the head and smashes $s knee into your face.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n grabs $M by the head and smashes $s knee into $N's face.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "knee")

        if not victim or victim.position == merc.POS_DEAD:
            return

        if game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_NOSE) and not victim.head.is_set(merc.LOST_NOSE):
            handler_game.act("Your nose shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's nose shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_NOSE)
        elif game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_JAW):
            handler_game.act("Your jaw shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's jaw shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_JAW)
        elif game_utils.number_percent() <= 25 and not victim.body.is_set(merc.BROKEN_NECK):
            handler_game.act("Your neck shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's neck shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.body.set_bit(merc.BROKEN_NECK)

        handler_game.act("You stamp on the back of $N's leg, forcing $M to drop to one knee.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n stamps on the back of your leg, forcing you to drop to one knee.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n stamps on the back of $N's leg, forcing $M to drop to one knee.", ch, None, victim, merc.TO_NOTVICT)

        handler_game.act("You grab $N by the hair and yank $S head back.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n grabs you by the hair and yank your head back.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n grabs $N by the hair and yank $S head back.", ch, None, victim, merc.TO_NOTVICT)

        handler_game.act("You hammer your elbow down into $N's face.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n hammers $s elbow down into your face.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n hammers $s elbow down into $N's face.", ch, None, victim, merc.TO_NOTVICT)
        damage(ch, victim, dam, "elbow")

        if not victim or victim.position == merc.POS_DEAD:
            return

        if game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_NOSE) and not victim.head.is_set(merc.LOST_NOSE):
            handler_game.act("Your nose shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's nose shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_NOSE)
        elif game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_JAW):
            handler_game.act("Your jaw shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's jaw shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.head.set_bit(merc.BROKEN_JAW)
        elif game_utils.number_percent() <= 25 and not victim.body.is_set(merc.BROKEN_NECK):
            handler_game.act("Your neck shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
            handler_game.act("$n's neck shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
            victim.body.set_bit(merc.BROKEN_NECK)

        handler_game.act("You crash to the ground, stunned.", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n crashes to the ground, stunned.", victim, None, None, merc.TO_ROOM)
        stop_fighting(victim, True)
        victim.position = merc.POS_STUNNED


def special_hurl(ch, victim):
    door = game_utils.number_range(0, 3)
    direction = merc.dir_name[door]
    rev_dir = merc.rev_dir[door]

    pexit = ch.in_room.exit[door]
    to_room = instance.rooms[pexit.to_room] if pexit else None
    if not pexit or not to_room:
        handler_game.act("$n hurls $N into the {} wall.".format(direction), ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("You hurl $N into the {} wall.".format(direction), ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n hurls you into the {} wall.".format(direction), ch, None, victim, merc.TO_VICT)
        dam = game_utils.number_range(ch.level, ch.level * 4)
        victim.hit -= dam
        update_pos(victim)

        if victim.is_npc() and not ch.is_npc():
            ch.mkill += 1

        if not victim.is_npc() and ch.is_npc():
            victim.mdeath += 1

        if victim.position == merc.POS_DEAD:
            raw_kill(victim)
        return

    pexit = victim.in_room.exit[door]
    if pexit.exit_info.is_set(merc.EX_CLOSED) and not victim.is_affected(merc.AFF_PASS_DOOR) and not victim.is_affected(merc.AFF_ETHEREAL):
        pexit.exit_info.rem_bit(merc.EX_LOCKED)
        pexit.exit_info.rem_bit(merc.EX_CLOSED)

        handler_game.act("$n hurls $N {}.".format(direction), ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("You hurl $N {}.".format(direction), ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n hurls you {}, smashing you through the {}.".format(direction, pexit.keyword), ch, None, victim, merc.TO_VICT)
        handler_game.act("There is a loud crash as $n smashes through the {}.", victim, None, pexit.keyword, merc.TO_ROOM)

        to_room = instance.rooms[pexit.to_room] if pexit else None
        pexit_rev = to_room.exit[rev_dir]
        if pexit and pexit_rev and pexit_rev.to_room == ch.in_room and pexit_rev.keyword:
            pexit_rev.exit_info.rem_bit(merc.EX_LOCKED)
            pexit_rev.exit_info.rem_bit(merc.EX_CLOSED)
            direction = merc.rev_dir[door]
            victim.in_room.get(victim)
            to_room.put(victim)
            handler_game.act("$n comes smashing in through the $t $d.", victim, direction, pexit.keyword, merc.TO_ROOM)

            dam = game_utils.number_range(ch.level, ch.level * 6)
            victim.hit -= dam
            update_pos(victim)

            if victim.is_npc() and not ch.is_npc():
                ch.mkill += 1

            if not victim.is_npc() and ch.is_npc():
                victim.mdeath += 1

            if victim.position == merc.POS_DEAD:
                raw_kill(victim)
                return
    else:
        handler_game.act("$n hurls $N $t.", ch, direction, victim, merc.TO_NOTVICT)
        handler_game.act("You hurl $N $t.", ch, direction, victim, merc.TO_CHAR)
        handler_game.act("$n hurls you $t.", ch, direction, victim, merc.TO_VICT)
        direction = merc.rev_dir[door]
        victim.in_room.get(victim)
        to_room.put(victim)
        handler_game.act("$n comes flying in from the $t.", victim, direction, None, merc.TO_ROOM)

        dam = game_utils.number_range(ch.level, ch.level * 2)
        victim.hit -= dam
        update_pos(victim)

        if victim.is_npc() and not ch.is_npc():
            ch.mkill += 1

        if not victim.is_npc() and ch.is_npc():
            victim.mdeath += 1

        if victim.position == merc.POS_DEAD:
            raw_kill(victim)
