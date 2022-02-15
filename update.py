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

import time

import comm
import const
import db
import fight
import game_utils
import handler_ch
import handler_game
import hotfix
import instance
import merc
import nanny
import object_creator
import settings
import state_checks


def gain_exp(ch, gain):
    mount = ch.mount
    if ch.is_npc() and mount and not mount.is_npc():
        master = ch.master
        if not master or instance.characters[master] != mount:
            mount.exp += gain

    if not ch.is_npc() and not ch.is_immortal():
        ch.exp += gain

    if ch.is_npc() or ch.level >= merc.LEVEL_HERO:
        return


# Regeneration stuff.
def hit_gain(ch):
    if ch.is_npc():
        gain = ch.level
    else:
        if ch.is_vampire():
            return 0

        gain = game_utils.number_range(10, 20)

        conamount = ch.stat(merc.STAT_CON) + 1
        if conamount > 1:
            if ch.position in [merc.POS_MEDITATING, merc.POS_RESTING]:
                gain *= conamount * 0.5
            elif ch.position == merc.POS_SLEEPING:
                gain *= conamount

    if ch.is_affected(merc.AFF_POISON) or ch.is_affected(merc.AFF_FLAMING):
        gain *= 0.25

    return int(min(gain, ch.max_hit - ch.hit))


def mana_gain(ch):
    if ch.is_npc():
        gain = ch.level
    else:
        if ch.is_vampire():
            return 0

        gain = game_utils.number_range(10, 20)

        intamount = ch.stat(merc.STAT_INT) + 1
        if intamount > 1:
            if ch.position == merc.POS_MEDITATING:
                gain *= intamount * ch.level
            elif ch.position == merc.POS_SLEEPING:
                gain *= intamount
            elif ch.position == merc.POS_RESTING:
                gain *= intamount * 0.5

    if ch.is_affected(merc.AFF_POISON) or ch.is_affected(merc.AFF_FLAMING):
        gain *= 0.25

    return int(min(gain, ch.max_mana - ch.mana))


def move_gain(ch):
    if ch.is_npc():
        gain = ch.level
    else:
        if ch.is_vampire():
            return 0

        gain = game_utils.number_range(10, 20)

        dexamount = ch.stat(merc.STAT_DEX) + 1
        if dexamount > 1:
            if ch.position in [merc.POS_MEDITATING, merc.POS_RESTING]:
                gain *= dexamount * 0.5
            elif ch.position == merc.POS_SLEEPING:
                gain *= dexamount

    if ch.is_affected(merc.AFF_POISON) or ch.is_affected(merc.AFF_FLAMING):
        gain *= 4

    return int(min(gain, ch.max_move - ch.move))


def gain_condition(ch, value):
    if value == 0 or ch.is_npc() or not ch.is_vampire():
        return

    condition = ch.blood
    ch.blood = state_checks.urange(0, condition + value, 48)

    if ch.blood == 0:
        ch.send("You are DYING from lack of blood!\n")
        handler_game.act("$n gets a hungry look in $s eyes.", ch, None, None, merc.TO_ROOM)
        ch.hit -= game_utils.number_range(2, 5)

        if game_utils.number_percent() <= ch.beast and ch.beast > 0:
            ch.vamp_rage()

        if not ch.vampaff.is_set(merc.VAM_FANGS):
            ch.cmd_fangs("")
    elif ch.blood < 10:
        ch.send("You crave blood.\n")

        if game_utils.number_range(1, 1000) <= ch.beast and ch.beast > 0:
            ch.vamp_rage()

        if game_utils.number_percent() > ch.blood + 75 and not ch.vampaff.is_set(merc.VAM_FANGS):
            ch.cmd_fangs("")


# Mob autonomous action.
# This function takes 25% to 35% of ALL Merc cpu time.
# -- Furey
def npc_update():
    # Examine all mobs.
    for npc in list(instance.characters.values()):
        if not npc.in_room:
            continue

        if not npc.is_npc():
            if npc.is_vampire() and npc.is_hero():
                if npc.position == merc.POS_FIGHTING and npc.powers[merc.UNI_RAGE] in merc.irange(1, 24) and not npc.itemaff.is_set(merc.ITEMA_RAGER):
                    npc.power[merc.UNI_RAGE] += 1
                elif npc.powers[merc.UNI_RAGE] > 0 and not npc.itemaff.is_set(merc.ITEMA_RAGER):
                    npc.powers[merc.UNI_RAGE] -= 1

                if npc.powers[merc.UNI_RAGE] < 1:
                    continue

                if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                    npc.werewolf_regen()

                if not npc.bleeding.empty():
                    sn = "clot"
                    const.skill_table[sn].spell_fun(sn, npc.level, npc, npc)
                else:
                    if not npc.head.empty() and not npc.body.empty() and not npc.arm_left.empty() and not npc.arm_right.empty() and \
                            not npc.leg_left.empty() and not npc.leg_right.empty():
                        npc.reg_mend()
            elif npc.is_werewolf() and npc.is_hero():
                if npc.position == merc.POS_FIGHTING and not npc.itemaff.is_set(merc.ITEMA_RAGER):
                    if npc.powers[merc.UNI_RAGE] < 300:
                        npc.powers[merc.UNI_RAGE] += game_utils.number_range(5, 10)

                    if npc.powers[merc.UNI_RAGE] < 300 and npc.powers[merc.WPOWER_WOLF] > 3:
                        npc.powers[merc.UNI_RAGE] += game_utils.number_range(5, 10)

                    if not npc.special.is_set(merc.SPC_WOLFMAN) and npc.powers[merc.UNI_RAGE] >= 100:
                        npc.werewolf()
                elif npc.powers[merc.UNI_RAGE] > 0 and not npc.itemaff.is_set(merc.ITEMA_RAGER):
                    npc.powers[merc.UNI_RAGE] -= 1

                    if npc.powers[merc.UNI_RAGE] < 100:
                        npc.unwerewolf()

                if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                    npc.werewolf_regen()

                if npc.is_werewolf() and npc.position == merc.POS_SLEEPING and npc.powers[merc.WPOWER_BEAR] > 3 and npc.hit > 0:
                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                if not npc.bleeding.empty():
                    sn = "clot"
                    const.skill_table[sn].spell_fun(sn, npc.level, npc, npc)
                else:
                    if not npc.head.empty() and not npc.body.empty() and not npc.arm_left.empty() and not npc.arm_right.empty() and \
                            not npc.leg_left.empty() and not npc.leg_right.empty():
                        npc.reg_mend()
            elif npc.itemaff.is_set(merc.ITEMA_REGENERATE) or npc.is_highlander():
                if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                    npc.werewolf_regen()

                if not npc.bleeding.empty():
                    sn = "clot"
                    const.skill_table[sn].spell_fun(sn, npc.level, npc, npc)
                else:
                    if not npc.head.empty() and not npc.body.empty() and not npc.arm_left.empty() and not npc.arm_right.empty() and \
                            not npc.leg_left.empty() and not npc.leg_right.empty():
                        npc.reg_mend()
            elif (npc.is_demon() or npc.special.is_set(merc.SPC_CHAMPION)) and npc.is_hero() and npc.in_room and npc.in_room.vnum == merc.ROOM_VNUM_HELL:
                if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                    npc.werewolf_regen()

                if npc.hit > 0:
                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                    if npc.hit < npc.max_hit or npc.mana < npc.max_mana or npc.move < npc.max_move:
                        npc.werewolf_regen()

                if not npc.bleeding.empty():
                    sn = "clot"
                    const.skill_table[sn].spell_fun(sn, npc.level, npc, npc)
                else:
                    if not npc.head.empty() and not npc.body.empty() and not npc.arm_left.empty() and not npc.arm_right.empty() and \
                            not npc.leg_left.empty() and not npc.leg_right.empty():
                        npc.reg_mend()
            continue

        if npc.is_affected(merc.AFF_CHARM):
            continue

        # Examine call for special procedure
        if npc.spec_fun:
            if npc.spec_fun(npc):
                continue

        # That's all for sleeping / busy monster, and empty zones
        if npc.position != merc.POS_STANDING:
            continue

        # Scavenge
        """
        if npc.act.is_set(merc.ACT_SCAVENGER) and npc.in_room.items and game_utils.number_bits(2) == 0:
            top = 1
            item_best = None
            for item_id in npc.in_room.items:
                item = instance.items[item_id]
                if item.flags.take and item.cost > top:
                    item_best = item
                    top = item.cost

            if item_best:
                item_best.from_environment()
                item_best.to_environment(npc.instance_id)
                handler_game.act("$n picks $p up.", npc, item_best, None, merc.TO_ROOM)
                handler_game.act("You pick $p up.", npc, item_best, None, merc.TO_CHAR)
        
        # Wander
        door = game_utils.number_bits(5)
        if door <= 5:
            pexit = npc.in_room.exit[door]
            if not npc.act.is_set(merc.ACT_SENTINEL) and pexit and pexit.to_room and not pexit.exit_info.is_set(merc.EX_CLOSED) and \
                    not instance.rooms[pexit.to_room].room_flags.is_set(merc.ROOM_NO_MOB) and not npc.hunting and \
                    ((not npc.act.is_set(merc.ACT_STAY_AREA) and npc.level < 900) or instance.rooms[pexit.to_room].area == npc.in_room.area):
                handler_ch.move_char(npc, door)

        # Flee
        door = game_utils.number_bits(3)
        if door <= 5:
            pexit = npc.in_room.exit[door]
            if npc.hit < npc.max_hit // 2 and pexit and pexit.to_room and not npc.is_affected(merc.AFF_WEBBED) and npc.level <= 900 and \
                    not pexit.exit_info.is_set(merc.EX_CLOSED) and not instance.rooms[pexit.to_room].room_flags.is_set(merc.ROOM_NO_MOB):
                found = False
                for rch_id in instance.rooms[pexit.to_room].people[:]:
                    rch = instance.characters[rch_id]
                    if not rch.is_npc():
                        found = True
                        break

                if not found:
                    handler_ch.move_char(npc, door)
        """


# Update the weather.
def weather_update():
    buf = ""
    handler_game.time_info.hour += 1
    if handler_game.time_info.hour == 5:
        handler_game.weather_info.sunlight = merc.SUN_LIGHT
        buf = "The day has begun.\n"
    elif handler_game.time_info.hour == 6:
        handler_game.weather_info.sunlight = merc.SUN_RISE
        buf = "The sun rises in the east.\n"
    elif handler_game.time_info.hour == 19:
        handler_game.weather_info.sunlight = merc.SUN_SET
        buf = "The sun slowly disappears in the west.\n"
    elif handler_game.time_info.hour == 20:
        handler_game.weather_info.sunlight = merc.SUN_DARK
        buf = "The night has begun.\n"
    elif handler_game.time_info.hour == 24:
        handler_game.time_info.hour = 0
        handler_game.time_info.day += 1
        buf = "You hear a clock in the distance strike midnight.\n"

        import nanny
        for wch in list(instance.players.values()):
            char_up = False
            if wch.desc.is_connected(nanny.con_playing) and wch.is_vampire():
                if wch.hit < wch.max_hit:
                    wch.hit = wch.max_hit
                    char_up = True
                if wch.mana < wch.max_mana:
                    wch.mana = wch.max_mana
                    char_up = True
                if wch.move < wch.max_move:
                    wch.move = wch.max_move
                    char_up = True

                if char_up:
                    wch.send("You feel the strength of the kindred flow through your veins!\n")

    if handler_game.time_info.day >= 35:
        handler_game.time_info.day = 0
        handler_game.time_info.month += 1
    if handler_game.time_info.month >= 17:
        handler_game.time_info.month = 0
        handler_game.time_info.year += 1

    # Weather change.
    if 9 <= handler_game.time_info.month <= 16:
        diff = -2 if handler_game.weather_info.mmhg > 985 else 2
    else:
        diff = -2 if handler_game.weather_info.mmhg > 1015 else 2

    handler_game.weather_info.change += diff * game_utils.dice(1, 4) + game_utils.dice(2, 6) - game_utils.dice(2, 6)
    handler_game.weather_info.change = max(handler_game.weather_info.change, -12)
    handler_game.weather_info.change = min(handler_game.weather_info.change, 12)

    handler_game.weather_info.mmhg += handler_game.weather_info.change
    handler_game.weather_info.mmhg = max(handler_game.weather_info.mmhg, 960)
    handler_game.weather_info.mmhg = min(handler_game.weather_info.mmhg, 1040)

    if handler_game.weather_info.sky == merc.SKY_CLOUDLESS:
        if handler_game.weather_info.mmhg < 990 or (handler_game.weather_info.mmhg < 1010 and game_utils.number_bits(2) == 0):
            buf += "The sky is getting cloudy.\n"
            handler_game.weather_info.sky = merc.SKY_CLOUDY
    elif handler_game.weather_info.sky == merc.SKY_CLOUDY:
        if handler_game.weather_info.mmhg < 970 or (handler_game.weather_info.mmhg < 990 and game_utils.number_bits(2) == 0):
            buf += "It starts to rain.\n"
            handler_game.weather_info.sky = merc.SKY_RAINING

        if handler_game.weather_info.mmhg > 1030 and game_utils.number_bits(2) == 0:
            buf += "The clouds disappear.\n"
            handler_game.weather_info.sky = merc.SKY_CLOUDLESS
    elif handler_game.weather_info.sky == merc.SKY_RAINING:
        if handler_game.weather_info.mmhg < 970 and game_utils.number_bits(2) == 0:
            buf += "Lightning flashes in the sky.\n"
            handler_game.weather_info.sky = merc.SKY_LIGHTNING

        if handler_game.weather_info.mmhg > 1030 or (handler_game.weather_info.mmhg > 1010 and game_utils.number_bits(2) == 0):
            buf += "The rain stopped.\n"
            handler_game.weather_info.sky = merc.SKY_CLOUDY
    elif handler_game.weather_info.sky == merc.SKY_LIGHTNING:
        if handler_game.weather_info.mmhg > 1010 or (handler_game.weather_info.mmhg > 990 and game_utils.number_bits(2) == 0):
            buf += "The lightning has stopped.\n"
            handler_game.weather_info.sky = merc.SKY_RAINING
    else:
        comm.notify(f"weather_update: bad sky {handler_game.weather_info.sky}", merc.CONSOLE_WARNING)
        handler_game.weather_info.sky = merc.SKY_CLOUDLESS

    if buf:
        import nanny
        for wch in list(instance.players.values()):
            if wch.desc.is_connected(nanny.con_playing) and wch.is_outside() and wch.is_awake():
                wch.send(buf)


save_number = 0


# Update all chars, including mobs.
def char_update():
    drop_out = False
    save_time = merc.current_time
    ch_save = None
    ch_quit = []

    id_list = [instance_id for instance_id in instance.characters.keys()]
    for character_id in id_list:
        ch = instance.characters[character_id]

        if not ch.environment:
            continue

        if not ch.is_npc() and (ch.head.is_set(merc.LOST_HEAD) or ch.extra.is_set(merc.EXTRA_OSWITCH)):
            is_obj = True
        elif not ch.is_npc() and ch.obj_vnum != 0:
            is_obj = True
            ch.extra.set_bit(merc.EXTRA_OSWITCH)
        else:
            is_obj = False

        # Find dude with oldest save time.
        if not ch.is_npc() and (not ch.desc or ch.desc.is_connected(nanny.con_playing)) and ch.level >= 2 and ch.save_time < save_time:
            ch_save = ch
            save_time = ch.save_time

        if ch.position > merc.POS_STUNNED and not is_obj:
            if ch.hit < ch.max_hit:
                ch.hit += hit_gain(ch)
            else:
                ch.hit = ch.max_hit

            if ch.mana < ch.max_mana:
                ch.mana += mana_gain(ch)
            else:
                ch.mana = ch.max_mana

            if ch.move < ch.max_move:
                ch.move += move_gain(ch)
            else:
                ch.move = ch.max_move

        if ch.position == merc.POS_STUNNED and not is_obj:
            ch.hit += game_utils.number_range(2, 4)
            fight.update_pos(ch)

        if not ch.is_npc() and ch.level < merc.LEVEL_IMMORTAL and not is_obj:
            item1 = ch.get_eq("right_hand")
            item2 = ch.get_eq("left_hand")
            if (item1 and item1.item_type == merc.ITEM_LIGHT and item1.value[2] > 0) or \
                    (item2 and item2.item_type == merc.ITEM_LIGHT and item2.value[2] > 0):
                if item1:
                    item1.value[2] -= 1
                    if item1.value[2] == 0 and ch.in_room:
                        ch.in_room.available_light -= 1
                        handler_game.act("$p goes out.", ch, item1, None, merc.TO_ROOM)
                        handler_game.act("$p goes out.", ch, item1, None, merc.TO_CHAR)
                        item1.extract()
                elif item2:
                    item2.value[2] -= 1
                    if item2.value[2] == 0 and ch.in_room:
                        ch.in_room.available_light -= 1
                        handler_game.act("$p goes out.", ch, item2, None, merc.TO_ROOM)
                        handler_game.act("$p goes out.", ch, item2, None, merc.TO_CHAR)
                        item2.extract()

            if ch.is_immortal():
                ch.timer = 0
            ch.timer += 1
            if ch.timer >= 12:
                if not ch.was_in_room and ch.in_room:
                    ch.was_in_room = ch.in_room
                    if ch.fighting:
                        fight.stop_fighting(ch, True)
                    handler_game.act("$n disappears into the void.", ch, None, None, merc.TO_ROOM)
                    ch.send("You disappear into the void.\n")
                    ch.save(force=True)
                    limbo_id = instance.instances_by_room[merc.ROOM_VNUM_LIMBO][0]
                    limbo = instance.rooms[limbo_id]
                    ch.in_room.get(ch)
                    limbo.put(ch)

            if ch.timer > 30:
                ch_quit.append(ch)

            if ch.is_vampire():
                blood = -1

                if ch.beast > 0:
                    if ch.vampaff.is_set(merc.VAM_CLAWS):
                        blood -= game_utils.number_range(1, 3)

                    if ch.vampaff.is_set(merc.VAM_FANGS):
                        blood -= 1

                    if ch.vampaff.is_set(merc.VAM_NIGHTSIGHT):
                        blood -= 1

                    if ch.vampaff.is_set(merc.AFF_SHADOWSIGHT):
                        blood -= game_utils.number_range(1, 3)

                    if ch.act.is_set(merc.PLR_HOLYLIGHT):
                        blood -= game_utils.number_range(1, 5)

                    if ch.vampaff.is_set(merc.VAM_DISGUISED):
                        blood -= game_utils.number_range(5, 10)

                    if ch.vampaff.is_set(merc.VAM_CHANGED):
                        blood -= game_utils.number_range(5, 10)

                    if ch.immune.is_set(merc.IMM_SHIELDED):
                        blood -= game_utils.number_range(1, 3)

                    if ch.polyaff.is_set(merc.POLY_SERPENT):
                        blood -= game_utils.number_range(1, 3)

                    if ch.beast == 100:
                        blood *= 2
                gain_condition(ch, blood)

        for aff in ch.affected[:]:
            if aff.duration > 0:
                aff.duration -= 1
            elif aff.duration < 0:
                pass
            else:
                multi = [a for a in ch.affected if a.type == aff.type and a is not aff and a.duration > 0]
                if not multi and aff.type and const.skill_table[aff.type].msg_off:
                    ch.send(const.skill_table[aff.type].msg_off + "\n")
                ch.affect_remove(aff)

        # Careful with the damages here,
        #   MUST NOT refer to ch after damage taken,
        #   as it may be lethal damage (on NPC).
        if not ch.bleeding.empty() and not is_obj and ch.in_room:
            dam = 0
            minhit = 0 if ch.is_npc() else -11

            if ch.bleeding.is_set(merc.BLEEDING_HEAD) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's neck.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your neck.\n")
                dam += game_utils.number_range(20, 50)

            if ch.bleeding.is_set(merc.BLEEDING_THROAT) and ch.hit - dam > minhit:
                handler_game.act("Blood pours from the slash in $n's throat.", ch, None, None, merc.TO_ROOM)
                ch.send("Blood pours from the slash in your throat.\n")
                dam += game_utils.number_range(10, 20)

            if ch.bleeding.is_set(merc.BLEEDING_ARM_L) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's left arm.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your left arm.\n")
                dam += game_utils.number_range(10, 20)
            elif ch.bleeding.is_set(merc.BLEEDING_HAND_L) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's left wrist.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your left wrist.\n")
                dam += game_utils.number_range(5, 10)

            if ch.bleeding.is_set(merc.BLEEDING_ARM_R) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's right arm.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your right arm.\n")
                dam += game_utils.number_range(10, 20)
            elif ch.bleeding.is_set(merc.BLEEDING_HAND_R) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's right wrist.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your right wrist.\n")
                dam += game_utils.number_range(5, 10)

            if ch.bleeding.is_set(merc.BLEEDING_LEG_L) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's left leg.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your left leg.\n")
                dam += game_utils.number_range(10, 20)
            elif ch.bleeding.is_set(merc.BLEEDING_FOOT_L) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's left ankle.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your left ankle.\n")
                dam += game_utils.number_range(5, 10)

            if ch.bleeding.is_set(merc.BLEEDING_LEG_R) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's right leg.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your right leg.\n")
                dam += game_utils.number_range(10, 20)
            elif ch.bleeding.is_set(merc.BLEEDING_FOOT_R) and ch.hit - dam > minhit:
                handler_game.act("A spray of blood shoots from the stump of $n's right ankle.", ch, None, None, merc.TO_ROOM)
                ch.send("A spray of blood shoots from the stump of your right ankle.\n")
                dam += game_utils.number_range(5, 10)

            ch.hit -= dam
            if ch.is_hero() and ch.hit < 1:
                ch.hit = 1
            fight.update_pos(ch)
            ch.in_room.blood += dam
            if ch.in_room.blood > 1000:
                ch.in_room.blood = 1000

            if ch.hit <= -11 or (ch.is_npc() and ch.hit < 1):
                ch.killperson(ch)
                drop_out = True

        if ch.is_affected(merc.AFF_FLAMING) and not is_obj and not drop_out and ch.in_room:
            if not (not ch.is_npc() and (ch.is_hero() or (ch.immune.is_set(merc.IMM_HEAT) and not ch.is_vampire()))):
                handler_game.act("$n's flesh burns and crisps.", ch, None, None, merc.TO_ROOM)
                ch.send("Your flesh burns and crisps.\n")
                dam = game_utils.number_range(10, 20)

                if not ch.is_npc():
                    if ch.immune.is_set(merc.IMM_HEAT):
                        dam //= 2

                    if ch.is_vampire():
                        dam *= 2

                ch.hit -= dam
                fight.update_pos(ch)

                if ch.hit <= -11:
                    ch.killperson(ch)
                    drop_out = True
        elif not ch.is_npc() and ch.is_vampire() and not ch.is_affected(merc.AFF_SHADOWPLANE) and not ch.immune.is_set(merc.IMM_SUNLIGHT) and \
                ch.in_room and ch.in_room.sector_type != merc.SECT_INSIDE and not is_obj and not ch.in_room.is_dark() and \
                handler_game.weather_info.sunlight != merc.SUN_DARK:
            handler_game.act("$n's flesh smolders in the sunlight!", ch, None, None, merc.TO_ROOM)
            ch.send("Your flesh smolders in the sunlight!\n")

            # This one's to keep Zarkas quiet ;)
            if ch.polyaff.is_set(merc.POLY_SERPENT):
                ch.hit -= game_utils.number_range(2, 4)
            else:
                ch.hit -= game_utils.number_range(5, 10)
            fight.update_pos(ch)

            if ch.hit <= -11:
                ch.killperson(ch)
                drop_out = True
        elif ch.is_affected(merc.AFF_POISON) and not is_obj and not drop_out:
            handler_game.act("$n shivers and suffers.", ch, None, None, merc.TO_ROOM)
            ch.send("You shiver and suffer.\n")
            fight.damage(ch, ch, 2, "poison")
        elif ch.position == merc.POS_INCAP and not is_obj and not drop_out:
            if ch.is_hero():
                ch.hit += game_utils.number_range(2, 4)
            else:
                ch.hit += game_utils.number_range(1, 2)
            fight.update_pos(ch)

            if ch.position > merc.POS_INCAP:
                handler_game.act("$n's wounds stop bleeding and seal up.", ch, None, None, merc.TO_ROOM)
                ch.send("Your wounds stop bleeding and seal up.\n")

            if ch.position > merc.POS_STUNNED:
                handler_game.act("$n clambers back to $s feet.", ch, None, None, merc.TO_ROOM)
                ch.send("You clamber back to your feet.\n")
        elif ch.position == merc.POS_MORTAL and not is_obj and not drop_out:
            drop_out = False

            if ch.is_hero():
                ch.hit += game_utils.number_range(2, 4)
            else:
                ch.hit -= game_utils.number_range(1, 2)

                if not ch.is_npc() and ch.hit <= -11:
                    ch.killperson(ch)
                drop_out = True

            if not drop_out:
                fight.update_pos(ch)

                if ch.position == merc.POS_INCAP:
                    handler_game.act("$n's wounds begin to close, and $s bones pop back into place.", ch, None, None, merc.TO_ROOM)
                    ch.send("Your wounds begin to close, and your bones pop back into place.\n")
        elif ch.position == merc.POS_DEAD and not is_obj and not drop_out:
            fight.update_pos(ch)
            if not ch.is_npc():
                ch.killperson(ch)
        drop_out = False

    # Autosave and autoquit.
    # Check that these chars still exist.
    if ch_quit or ch_save:
        for ch in list(instance.players.values()):
            if ch == ch_save:
                ch.save()

        for ch in ch_quit[:]:
            ch.cmd_quit("")


# Update all items.
# This function is performance sensitive.
def item_update():
    for item in list(instance.items.values()):
        if item:
            if item.timer <= 0:
                continue

            item.timer -= 1
            if item.timer > 0:
                continue

            if item.item_type == merc.ITEM_FOUNTAIN:
                message = "$p dries up."
            elif item.item_type in [merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC]:
                message = "$p decays into dust."
            elif item.item_type == merc.ITEM_FOOD:
                message = "$p decomposes."
            elif item.item_type == merc.ITEM_TRASH:
                message = "$p crumbles into dust."
            elif item.item_type == merc.ITEM_EGG:
                message = "$p cracks open."
            elif item.item_type == merc.ITEM_WEAPON:
                message = "The poison on $p melts through it."
            else:
                message = "$p vanishes."

            if item.in_living:
                handler_game.act(message, instance.characters[item.in_living], item, None, merc.TO_CHAR)
            elif item.in_room and item.in_room.people:
                ch = instance.characters[item.in_room.people[0]]
                handler_game.act(message, ch, item, None, merc.TO_ROOM)

            # If the item is an egg, we need to create a mob and shell! KaVir
            if item.item_type == merc.ITEM_EGG:
                mob_index = instance.npc_templates[item.value[0]]
                if mob_index:
                    if item.in_living and item.in_living.in_room:
                        creature = object_creator.create_mobile(mob_index)
                        item.in_living.in_room.put(creature)
                    elif item.in_room:
                        creature = object_creator.create_mobile(mob_index)
                        item.in_room.put(creature)
                    else:
                        creature = object_creator.create_mobile(mob_index)
                        room_id = instance.instances_by_room[merc.ROOM_VNUM_HELL][0]
                        instance.rooms[room_id].put(creature)
                    egg = object_creator.clone_item(instance.item_templates[merc.OBJ_VNUM_EMPTY_EGG], 0)
                    egg.timer = 2
                    creature.in_room.put(egg)
                    handler_game.act("$n clambers out of $p.", creature, item, None, merc.TO_ROOM)
                elif item.in_room:
                    egg = object_creator.clone_item(instance.item_templates[merc.OBJ_VNUM_EMPTY_EGG], 0)
                    egg.timer = 2
                    item.in_room.put(egg)
            item.extract()


# Aggress.
#
# for each mortal PC
#     for each mob in room
#         aggress on some random PC
#
# This function takes 25% to 35% of ALL Merc cpu time.
# Unfortunately, checking on each PC move is too tricky,
#   because we don't the mob to just attack the first PC
#   who leads the party into the room.
#
# -- Furey
def aggr_update():
    for wch in list(instance.players.values()):
        item = wch.chobj
        if item and not wch.is_npc():
            # noinspection PyUnresolvedReferences
            if item.in_room:
                # noinspection PyUnresolvedReferences
                itemroom = item.in_room
            elif item.in_item:
                itemroom = instance.rooms[merc.ROOM_VNUM_IN_OBJECT]
            elif item.in_living:
                # noinspection PyUnresolvedReferences
                if item.in_living != wch and item.in_living.in_room:
                    # noinspection PyUnresolvedReferences
                    itemroom = item.in_living.in_room
                else:
                    continue
            else:
                continue
            if itemroom and wch.in_room != itemroom:
                wch.in_room.get(wch)
                itemroom.put(wch)
                wch.cmd_look("auto")
        elif not wch.is_npc() and (wch.head.is_set(merc.LOST_HEAD) or wch.extra.is_set(merc.EXTRA_OSWITCH) or wch.obj_vnum != 0):
            if wch.obj_vnum != 0:
                wch.bind_char()
                continue

            if wch.head.is_set(merc.LOST_HEAD):
                wch.head.rem_bit(merc.LOST_HEAD)
                wch.send("You are able to regain a body.\n")
                wch.position = merc.POS_RESTING
                wch.hit = 1
            else:
                wch.send("You return to your body.\n")
                wch.extra.rem_bit(merc.EXTRA_OSWITCH)

            wch.affected_by.rem_bit(merc.AFF_POLYMORPH)
            wch.morph = ""
            wch.in_room.get(wch)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(wch)

            item = wch.chobj
            if item:
                item.chobj = None
            wch.chobj = None
            wch.cmd_look("auto")
        continue

    for wch in list(instance.characters.values()):
        item = wch.chobj
        if wch.is_npc() or (wch.desc and wch.desc.is_connected(nanny.con_playing)) or wch.position <= merc.POS_STUNNED or wch.is_immortal() or \
                item or not wch.in_room:
            continue

        for ch_id in wch.in_room.people[:]:
            ch = instance.characters[ch_id]
            if not ch.is_npc() or not ch.act.is_set(merc.ACT_AGGRESSIVE) or fight.no_attack(ch, wch) or ch.fighting or \
                    ch.is_affected(merc.AFF_CHARM) or not ch.is_awake() or (ch.act.is_set(merc.ACT_WIMPY) and wch.is_awake()) or not ch.can_see(wch):
                continue

            # Ok we have a 'wch' player character and a 'ch' npc aggressor.
            # Now make the aggressor fight a RANDOM pc victim in the room,
            #   giving each 'vch' an equal chance of selection.
            count = 0
            victim = None
            for vch_id in wch.in_room.people[:]:
                vch = instance.characters[vch_id]
                item = vch.chobj
                if not vch.is_npc() and not fight.no_attack(ch, vch) and not item and vch.level < merc.LEVEL_IMMORTAL and \
                        vch.position > merc.POS_STUNNED and (not ch.act.is_set(merc.ACT_WIMPY) or not vch.is_awake()) and ch.can_see(vch):
                    if game_utils.number_range(0, count) == 0:
                        victim = vch
                    count += 1

            if not victim:
                continue

            fight.multi_hit(ch, victim, merc.TYPE_UNDEFINED)


def instance_number_save():
    if instance.max_instance_id > instance.previous_max_instance_id:
        instance.previous_max_instance_id = instance.max_instance_id

        with open(settings.INSTANCE_FILE, "w") as fp:
            fp.write(str(instance.max_instance_id))
        comm.notify(f"Saved the current instance number: {instance.max_instance_id,}", merc.CONSOLE_INFO)


def ww_update():
    for victim in list(instance.characters.values()):
        if victim.is_npc() or victim.is_immortal() or not victim.in_room or victim.chobj or victim.is_werewolf():
            continue

        if not victim.in_room.room_flags.is_set(merc.ROOM_BLADE_BARRIER):
            continue

        handler_game.act("The scattered blades on the ground fly up into the air ripping into you.", victim, None, None, merc.TO_CHAR)
        handler_game.act("The scattered blades on the ground fly up into the air ripping into $n.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The blades drop to the ground inert.", victim, None, None, merc.TO_CHAR)
        handler_game.act("The blades drop to the ground inert.", victim, None, None, merc.TO_ROOM)

        dam = game_utils.number_range(7, 14)
        dam = dam // 100
        dam = victim.hit * dam
        dam = max(dam, 100)
        victim.hit -= dam
        if victim.hit < -10:
            victim.hit = -10
        fight.update_pos(victim)


# Handle all kinds of updates.
# Called once per pulse from game loop.
# Random times to defeat tick-timing clients and players.
previous_pulse = -1
pulse_area = 0
pulse_npc = 0
pulse_point = 0
pulse_violence = 0
pulse_ww = 0


def update_handler():
    global previous_pulse
    global pulse_area
    global pulse_npc
    global pulse_point
    global pulse_violence
    global pulse_ww

    current_time = get_precise_time()
    if previous_pulse == -1:
        previous_pulse = current_time-1

    while current_time >= previous_pulse + merc.MILLISECONDS_PER_PULSE:
        previous_pulse += merc.MILLISECONDS_PER_PULSE

        pulse_area -= 1
        pulse_npc -= 1
        pulse_point -= 1
        pulse_violence -= 1
        pulse_ww -= 1

        for ch in instance.characters.values():
            if ch.wait > 0:
                ch.wait -= 1

        if pulse_ww <= 0:
            pulse_ww = merc.PULSE_WW
            ww_update()

        if pulse_area <= 0:
            pulse_area = game_utils.number_range(merc.PULSE_AREA // 2, 3 * merc.PULSE_AREA // 2)
            db.area_update()
            instance_number_save()  # Piggyback on area updates to save the instance number.

        if pulse_npc <= 0:
            pulse_npc = merc.PULSE_MOBILE
            npc_update()

        if pulse_violence <= 0:
            hotfix.poll_files()
            pulse_violence = merc.PULSE_VIOLENCE
            fight.violence_update()

        if pulse_point <= 0:
            pulse_point = game_utils.number_range(merc.PULSE_TICK // 2, 3 * merc.PULSE_TICK // 2)
            weather_update()
            char_update()
            item_update()

        aggr_update()


def get_precise_time():
    return int(round(time.time()*1000))
