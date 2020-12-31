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

import collections

import comm
import game_utils
import handler_game
import handler_item
import handler_room
import instance
import merc


def ch_desc(d):
    return d.original if d.original else d.character


def move_char(ch, door):
    if door not in range(merc.MAX_DIR):
        comm.notify("move_char: bad door {}".format(door), merc.CONSOLE_ERROR)
        return

    in_room = ch.in_room
    if not ch._room_vnum:
        ch._room_vnum = in_room.vnum

    pexit = in_room.exit[door]
    to_room = pexit.to_room if pexit else None
    if not pexit or not to_room:
        ch.send("Alas, you cannot go that way.\n")
        return

    to_room = instance.rooms[pexit.to_room]
    if pexit.exit_info.is_set(merc.EX_CLOSED) and not ch.is_affected(merc.AFF_PASS_DOOR) and not ch.is_affected(merc.AFF_ETHEREAL) and \
            not ch.is_affected(merc.AFF_SHADOWPLANE):
        if not ch.is_npc() and ch.is_werewolf() and ch.powers[merc.WPOWER_BOAR] > 0:
            handler_game.act("You smash open the $d.", ch, None, pexit.keyword, merc.TO_CHAR)
            handler_game.act("$n smashes open the $d.", ch, None, pexit.keyword, merc.TO_ROOM)
            pexit.exit_info.rem_bit(merc.EX_CLOSED)
        else:
            handler_game.act("The $d is closed.", ch, None, pexit.keyword, merc.TO_CHAR)
            return

    if ch.is_affected(merc.AFF_CHARM) and ch.master and in_room == instance.characters[ch.master].in_room:
        ch.send("What?  And leave your beloved master?\n")
        return

    mount = ch.mount
    if ch.is_npc() and mount and ch.mounted == merc.IS_MOUNT:
        ch.send("You better wait for instructions from your rider.\n")
        return

    if to_room.is_private():
        if ch.is_npc() or ch.trust < merc.MAX_LEVEL:
            ch.send("That room is private right now.\n")
            return
        else:
            ch.send("That room is private (Access granted).\n")

    if (ch.leg_left.is_set(merc.BROKEN_LEG) or ch.leg_left.is_set(merc.LOST_LEG)) and (ch.leg_right.is_set(merc.BROKEN_LEG) or
                                                                                       ch.leg_right.is_set(merc.LOST_LEG)) and \
            (ch.arm_left.is_set(merc.BROKEN_ARM) or ch.arm_left.is_set(merc.LOST_ARM) or ch.get_eq("left_hand")) and \
            (ch.arm_right.is_set(merc.BROKEN_ARM) or ch.arm_right.is_set(merc.LOST_ARM) or ch.get_eq("right_hand")):
        ch.send("You need at least one free arm to drag yourself with.\n")
        return
    elif ch.body.is_set(merc.BROKEN_SPINE) and (ch.arm_left.is_set(merc.BROKEN_ARM) or ch.arm_left.is_set(merc.LOST_ARM) or
                                                ch.get_eq("left_hand")) and (ch.arm_right.is_set(merc.BROKEN_ARM) or
                                                                             ch.arm_right.is_set(merc.LOST_ARM) or ch.get_eq("right_hand")):
        ch.send("You cannot move with a broken spine.\n")
        return

    if not ch.is_npc():
        mount = ch.mount
        if in_room.sector_type == merc.SECT_AIR or to_room.sector_type == merc.SECT_AIR:
            if not ch.is_affected(merc.AFF_FLYING) and (not ch.is_npc() and not ch.vampaff.is_set(merc.VAM_FLYING) and
                                                        not ch.demaff.is_set(merc.DEM_UNFOLDED)) and \
                    (not mount or (ch.mounted == merc.IS_RIDING and not mount.is_affected(merc.AFF_FLYING))):
                ch.send("You can't fly.\n")
                return

        if in_room.sector_type == merc.SECT_WATER_NOSWIM or to_room.sector_type == merc.SECT_WATER_NOSWIM:
            # Look for a boat.
            found = False
            if not ch.is_npc() and ch.is_vampire():
                if ch.vampaff.is_set(merc.VAM_FLYING):
                    found = True
                elif ch.polyaff.is_set(merc.POLY_SERPENT):
                    found = True
                elif ch.is_affected(merc.AFF_SHADOWPLANE):
                    found = True
                else:
                    mount = ch.mount
                    if mount and ch.mounted == merc.IS_RIDING and mount.is_affected(merc.AFF_FLYING):
                        found = True
                    else:
                        ch.send("You are unable to cross running water.\n")
                        return

            if ch.is_affected(merc.AFF_FLYING) or (not ch.is_npc() and ch.demaff.is_set(merc.DEM_UNFOLDED)):
                found = True

            if not found:
                boats = [item_id for item_id in ch.inventory if instance.items[item_id].item_type == merc.ITEM_BOAT]
                if not boats and not ch.is_immortal():
                    ch.send("You need a boat to go there.\n")
                    return
        elif not ch.is_affected(merc.AFF_FLYING) and ch.polyaff.is_set(merc.POLY_FISH):
            from_ok = in_room.sector_type in [merc.SECT_WATER_NOSWIM, merc.SECT_WATER_SWIM]
            to_ok = to_room.sector_type in [merc.SECT_WATER_NOSWIM, merc.SECT_WATER_SWIM]
            if not from_ok or not to_ok:
                ch.send("You cannot cross land.\n")
                return

        move = merc.movement_loss[min(merc.SECT_MAX - 1, in_room.sector_type)] + merc.movement_loss[min(merc.SECT_MAX - 1, to_room.sector_type)]

        if ch.is_hero():
            move = 0

        if ch.mounted != merc.IS_RIDING:
            if ch.move < move or ch.move < 1:
                ch.send("You are too exhausted.\n")
                return

            ch.move -= move
        ch.wait_state(1)

    # Check for mount message - KaVir
    mount = ch.mount
    if mount and ch.mounted == merc.IS_RIDING:
        mount2 = " on {}.".format(mount.short_descr if mount.is_npc() else mount.name)
    else:
        mount2 = "."

    if ch.head.is_set(merc.LOST_HEAD) or ch.extra.is_set(merc.EXTRA_OSWITCH):
        leave = "rolls"
    elif ch.is_affected(merc.AFF_ETHEREAL):
        leave = "floats"
    elif ch.in_room.sector_type == merc.SECT_WATER_SWIM or ch.polyaff.is_set(merc.POLY_FISH):
        leave = "swims"
    elif ch.polyaff.is_set(merc.POLY_SERPENT):
        leave = "slithers"
    elif ch.polyaff.is_set(merc.POLY_WOLF):
        leave = "stalks"
    elif ch.polyaff.is_set(merc.POLY_FROG):
        leave = "hops"
    elif not ch.is_npc() and ch.demaff.is_set(merc.DEM_UNFOLDED):
        leave = "flies"
    elif ch.body.is_set(merc.BROKEN_SPINE) or (ch.leg_left.is_set(merc.LOST_LEG) and ch.leg_right.is_set(merc.LOST_LEG)):
        leave = "drags $mself"
    elif ((ch.leg_left.is_set(merc.BROKEN_LEG) or ch.leg_left.is_set(merc.LOST_LEG) or ch.leg_left.is_set(merc.LOST_FOOT)) and
            (ch.leg_right.is_set(merc.BROKEN_LEG) or ch.leg_right.is_set(merc.LOST_LEG) or ch.leg_right.is_set(merc.LOST_FOOT))) or \
            ch.hit < ch.max_hit // 4:
        leave = "crawls"
    elif ((ch.leg_right.is_set(merc.LOST_LEG) or ch.leg_right.is_set(merc.LOST_FOOT)) and (not ch.leg_left.is_set(merc.BROKEN_LEG) and
                                                                                           not ch.leg_left.is_set(merc.LOST_LEG) and
                                                                                           not ch.leg_left.is_set(merc.LOST_FOOT))) or \
            ((ch.leg_left.is_set(merc.LOST_LEG) or ch.leg_left.is_set(merc.LOST_FOOT)) and (not ch.leg_right.is_set(merc.BROKEN_LEG) and
                                                                                            not ch.leg_right.is_set(merc.LOST_LEG) and
                                                                                            not ch.leg_right.is_set(merc.LOST_FOOT))):
        leave = "hops"
    elif ((ch.leg_left.is_set(merc.BROKEN_LEG) or ch.leg_left.is_set(merc.LOST_FOOT)) and (not ch.leg_right.is_set(merc.BROKEN_LEG) and
                                                                                           not ch.leg_right.is_set(merc.LOST_LEG) and
                                                                                           not ch.leg_right.is_set(merc.LOST_FOOT))) or \
            ((ch.leg_right.is_set(merc.BROKEN_LEG) or ch.leg_right.is_set(merc.LOST_FOOT)) and (not ch.leg_left.is_set(merc.BROKEN_LEG) and
                                                                                                not ch.leg_left.is_set(merc.LOST_LEG) and
                                                                                                not ch.leg_left.is_set(merc.LOST_FOOT))) or \
            ch.hit < ch.max_hit // 3:
        leave = "limps"
    elif ch.hit < ch.max_hit // 2:
        leave = "staggers"
    else:
        leave = "walks"

    if not ch.is_npc() and ch.stance[0] != -1:
        ch.cmd_stance("")

    for victim in list(instance.characters.values()):
        if not ch.in_room or not victim.in_room or ch == victim or ch.in_room != victim.in_room or not ch.can_see(victim):
            continue

        if not ch.is_npc() and not ch.is_affected(merc.AFF_SNEAK) and ch.is_affected(merc.AFF_POLYMORPH) and (ch.is_npc() or
                                                                                                              not ch.act.is_set(merc.PLR_WIZINVIS) or
                                                                                                              ch.invis_level < merc.LEVEL_IMMORTAL) and \
                victim.can_see(ch):
            mount = ch.mount
            if (mount and ch.mounted == merc.IS_RIDING and mount.is_affected(merc.AFF_FLYING)) or ch.is_affected(merc.AFF_FLYING) or \
                    (not ch.is_npc() and ch.vampaff.is_set(merc.VAM_FLYING)):
                poly = "{} flies $T{}".format(ch.morph, mount2)
            elif mount and ch.mounted == merc.IS_RIDING:
                poly = "{} rides $T{}".format(ch.morph, mount2)
            else:
                poly = "{} {} $T{}".format(ch.morph, leave, mount2)
            handler_game.act(poly, victim, None, merc.dir_name[door], merc.TO_CHAR)
        elif not ch.is_affected(merc.AFF_SNEAK) and (ch.is_npc() or not ch.act.is_set(merc.PLR_WIZINVIS) and ch.invis_level < merc.LEVEL_IMMORTAL) and \
                victim.can_see(ch):
            mount = ch.mount
            if (mount and ch.mounted == merc.IS_RIDING and mount.is_affected(merc.AFF_FLYING)) or ch.is_affected(merc.AFF_FLYING) or \
                    (not ch.is_npc() and ch.vampaff.is_set(merc.VAM_FLYING)):
                poly = "$n flies {}{}".format(merc.dir_name[door], mount2)
            elif mount and ch.mounted == merc.IS_RIDING:
                poly = "$n rides {}{}".format(merc.dir_name[door], mount2)
            else:
                poly = "$n {} {}{}".format(leave, merc.dir_name[door], mount2)
            handler_game.act(poly, ch, None, victim, merc.TO_VICT)

    ch.in_room.get(ch)
    to_room.put(ch)

    dir_list = [(merc.DIR_NORTH, "the south"), (merc.DIR_EAST, "the west"), (merc.DIR_SOUTH, "the north"), (merc.DIR_WEST, "the east"),
                (merc.DIR_UP, "below")]
    for (aa, bb) in dir_list:
        if door == aa:
            buf = bb
            break
    else:
        buf = "above"

    for victim in list(instance.characters.values()):
        if not ch.in_room or not victim.in_room or ch == victim or ch.in_room != victim.in_room or not ch.can_see(victim):
            continue

        if not ch.is_npc() and not ch.is_affected(merc.AFF_SNEAK) and ch.is_affected(merc.AFF_POLYMORPH) and (ch.is_npc() or
                                                                                                              not ch.act.is_set(merc.PLR_WIZINVIS) or
                                                                                                              ch.invis_level < merc.LEVEL_IMMORTAL) and \
                victim.can_see(ch):
            mount = ch.mount
            if (mount and ch.mounted == merc.IS_RIDING and mount.is_affected(merc.AFF_FLYING)) or ch.is_affected(merc.AFF_FLYING) or \
                    (not ch.is_npc() and ch.vampaff.is_set(merc.VAM_FLYING)):
                poly = "{} flies in from {}{}".format(ch.morph, buf, mount2)
            elif mount and ch.mounted == merc.IS_RIDING:
                poly = "{} rides in from {}{}".format(ch.morph, buf, mount2)
            else:
                poly = "{} {} in from {}{}".format(ch.morph, leave, buf, mount2)
            handler_game.act(poly, ch, None, victim, merc.TO_VICT)
        elif not ch.is_affected(merc.AFF_SNEAK) and (ch.is_npc() or not ch.act.is_set(merc.PLR_WIZINVIS) and ch.invis_level < merc.LEVEL_IMMORTAL) and \
                victim.can_see(ch):
            mount = ch.mount
            if (mount and ch.mounted == merc.IS_RIDING and mount.is_affected(merc.AFF_FLYING)) or ch.is_affected(merc.AFF_FLYING) or \
                    (not ch.is_npc() and ch.vampaff.is_set(merc.VAM_FLYING)):
                poly = "$n flies in from {}{}".format(buf, mount2)
            elif mount and ch.mounted == merc.IS_RIDING:
                poly = "$n rides in from {}{}".format(buf, mount2)
            else:
                poly = "$n {} in from {}{}".format(leave, buf, mount2)
            handler_game.act(poly, ch, None, victim, merc.TO_VICT)

    ch.cmd_look("auto")

    if in_room.instance_id == to_room.instance_id:  # no circular follows
        return

    for fch_id in in_room.people[:]:
        fch = instance.characters[fch_id]

        mount = fch.mount
        if mount and mount == ch and fch.mounted == merc.IS_MOUNT:
            handler_game.act("$N digs $S heels into you.", fch, None, ch, merc.TO_CHAR)
            fch.in_room.get(fch)
            ch.in_room.put(fch)

        if fch.master == ch.instance_id and fch.position == merc.POS_STANDING and fch.in_room != ch.in_room:
            handler_game.act("You follow $N.", fch, None, ch, merc.TO_CHAR)
            move_char(fch, door)
    handler_room.room_text(ch, ">ENTER<")


def add_follower(ch, master):
    if ch.master:
        comm.notify("add_follower: non-null master.", merc.CONSOLE_WARNING)
        return

    ch.master = master.instance_id
    ch.leader = None

    if master.can_see(ch):
        handler_game.act("$n now follows you.", ch, None, master, merc.TO_VICT)

    handler_game.act("You now follow $N.", ch, None, master, merc.TO_CHAR)


def die_followers(ch):
    if ch.master:
        stop_follower(ch)

    ch.leader = None

    for fch in instance.characters.values():
        if fch.master == ch.instance_id:
            stop_follower(fch)

        if fch.leader == ch.instance_id:
            fch.leader = fch.instance_id


def stop_follower(ch):
    if not ch.master:
        comm.notify("stop_follower: null master", merc.CONSOLE_WARNING)
        return

    if ch.is_affected(merc.AFF_CHARM):
        ch.affected_by.rem_bit(merc.AFF_CHARM)
        ch.affect_strip("charm person")

    if instance.characters[ch.master].can_see(ch):
        handler_game.act("$n stops following you.", ch, None, instance.characters[ch.master], merc.TO_VICT)

    handler_game.act("You stop following $N.", ch, None, instance.characters[ch.master], merc.TO_CHAR)
    ch.master = None
    ch.leader = None


# Show a list to a character.
# Can coalesce duplicated items.
def show_list_to_char(clist, ch, fshort, fshownothing):
    if not ch.desc:
        return

    item_dict = collections.OrderedDict()
    for item_id in clist:
        item = instance.items[item_id]

        if not ch.is_npc() and ch.chobj and item.chobj and item.chobj == ch:
            continue

        if ch.can_see_item(item):
            frmt = handler_item.format_item_to_char(item, ch, fshort)
            if frmt not in item_dict:
                item_dict[frmt] = 1
            else:
                item_dict[frmt] += 1

    if not item_dict and fshownothing:
        if ch.is_npc() or ch.act.is_set(merc.PLR_COMBINE):
            ch.send("     ")
        ch.send("Nothing.\n")

    # Output the formatted list.
    for desc, count in item_dict.items():
        if (ch.is_npc() or ch.act.is_set(merc.PLR_COMBINE)) and count > 1:
            ch.send("({:2}) {}\n".format(count, desc))
        else:
            for i in range(count):
                ch.send("     {}\n".format(desc))


def show_char_to_char_0(victim, ch):
    if not victim.is_npc() and victim.chobj:
        return

    mount = victim.mount
    if mount and victim.mounted == merc.IS_MOUNT:
        return

    buf = []
    if victim.head.is_set(merc.LOST_HEAD) and victim.is_affected(merc.AFF_POLYMORPH):
        buf += "     "
    else:
        if not victim.is_npc() and not victim.desc:
            buf += "(Link-Dead) "

        if victim.is_affected(merc.AFF_INVISIBLE):
            buf += "(Invis) "

        if victim.is_affected(merc.AFF_HIDE):
            buf += "(Hide) "

        if victim.is_affected(merc.AFF_CHARM):
            buf += "(Charmed) "

        if victim.is_affected(merc.AFF_PASS_DOOR) or victim.is_affected(merc.AFF_ETHEREAL):
            buf += "(Translucent) "

        if victim.is_affected(merc.AFF_FAERIE_FIRE):
            buf += "(Pink Aura) "

        if victim.is_evil() and ch.is_affected(merc.AFF_DETECT_EVIL):
            buf += "(Red Aura) "

        if victim.is_affected(merc.AFF_SANCTUARY):
            buf += "(White Aura) "

    if ch.is_affected(merc.AFF_SHADOWPLANE) and not victim.is_affected(merc.AFF_SHADOWPLANE):
        buf += "(Normal plane) "
    elif not ch.is_affected(merc.AFF_SHADOWPLANE) and victim.is_affected(merc.AFF_SHADOWPLANE):
        buf += "(Shadowplane) "

    # Vampires and werewolves can recognise each other - KaVir
    if victim.is_hero() and ch.is_hero() and not ch.is_human():
        if victim.is_vampire():
            buf += "(Vampire) "
        elif victim.is_werewolf():
            buf += "(Werewolf) "
        elif victim.is_demon():
            if victim.special.is_set(merc.SPC_DEMON_LORD):
                buf += "(Demon Lord) "
            elif victim.special.is_set(merc.SPC_SIRE) or victim.special.is_set(merc.SPC_PRINCE):
                buf += "(Demon) "
            else:
                buf += "(Champion) "
        elif victim.is_highlander():
            buf += "(Highlander) "
        elif victim.is_mage():
            if victim.level == merc.LEVEL_APPRENTICE:
                buf += "(Apprentice) "
            elif victim.level == merc.LEVEL_MAGE:
                buf += "(Mage) "
            elif victim.level == merc.LEVEL_ARCHMAGE:
                buf += "(Archmage) "

    if not ch.is_npc() and ch.vampaff.is_set(merc.VAM_AUSPEX) and not victim.is_npc() and victim.is_vampire() and \
            victim.vampaff.is_set(merc.VAM_DISGUISED):
        buf += "({}) ".format(victim.name)

    buf2 = ""
    vname = victim.short_descr if victim.is_npc() else victim.morph if victim.is_affected(merc.AFF_POLYMORPH) else victim.short_descr

    if victim.is_affected(merc.AFF_FLAMING):
        buf2 += "\n...{} is engulfed in blazing flames!".format(vname)

    if not victim.is_npc() and victim.head.is_set(merc.LOST_HEAD) and victim.is_affected(merc.AFF_POLYMORPH):
        if victim.extra.is_set(merc.EXTRA_GAGGED) and victim.extra.is_set(merc.EXTRA_BLINDFOLDED):
            buf2 += "\n...{} is gagged and blindfolded!".format(victim.morph)
        elif victim.extra.is_set(merc.EXTRA_GAGGED):
            buf2 += "\n...{} is gagged!".format(victim.morph)
        elif victim.extra.is_set(merc.EXTRA_BLINDFOLDED):
            buf2 += "\n...{} is blindfolded!".format(victim.morph)

    if victim.head.is_set(merc.LOST_HEAD) and victim.is_affected(merc.AFF_POLYMORPH):
        buf += "{} is lying here.".format(victim.morph[0].upper() + victim.morph[1:])
        buf += buf2 + "\n"
        ch.send("".join(buf))
        return

    if victim.extra.is_set(merc.EXTRA_TIED_UP):
        buf2 += "\n...{} is tied up".format(vname)

        if victim.extra.is_set(merc.EXTRA_GAGGED) and victim.extra.is_set(merc.EXTRA_BLINDFOLDED):
            buf2 += ", gagged and blindfolded!"
        elif victim.extra.is_set(merc.EXTRA_GAGGED):
            buf2 += " and gagged!"
        elif victim.extra.is_set(merc.EXTRA_BLINDFOLDED):
            buf2 += " and blindfolded!"
        else:
            buf2 += "!"

    if victim.is_affected(merc.AFF_WEBBED):
        buf2 += "\n...{} is coated in a sticky web.".format(vname)

    if not victim.is_npc() and victim.is_affected(merc.AFF_POLYMORPH):
        buf += victim.morph
    else:
        mount = victim.mount
        if victim.position == merc.POS_STANDING and victim.long_descr and not mount:
            ch.send("".join(buf) + victim.long_descr)

            if ch.is_npc() or not ch.act.is_set(merc.PLR_BRIEF):
                if victim.itemaff.is_set(merc.ITEMA_SHOCKSHIELD):
                    handler_game.act("...$N is surrounded by a crackling shield of lightning.", ch, None, victim, merc.TO_CHAR)
                if victim.itemaff.is_set(merc.ITEMA_FIRESHIELD):
                    handler_game.act("...$N is surrounded by a burning shield of fire.", ch, None, victim, merc.TO_CHAR)
                if victim.itemaff.is_set(merc.ITEMA_ICESHIELD):
                    handler_game.act("...$N is surrounded by a shimmering shield of ice.", ch, None, victim, merc.TO_CHAR)
                if victim.itemaff.is_set(merc.ITEMA_ACIDSHIELD):
                    handler_game.act("...$N is surrounded by a bubbling shield of acid.", ch, None, victim, merc.TO_CHAR)
                if victim.itemaff.is_set(merc.ITEMA_CHAOSSHIELD):
                    handler_game.act("...$N is surrounded by a swirling shield of chaos.", ch, None, victim, merc.TO_CHAR)
                if victim.itemaff.is_set(merc.ITEMA_REFLECT):
                    handler_game.act("...$N is surrounded by a flickering shield of darkness.", ch, None, victim, merc.TO_CHAR)
            return
        else:
            buf += victim.pers(ch)

    mount = victim.mounted
    if mount and victim.mounted == merc.IS_RIDING:
        buf += " is here riding {}".format(mount.short_descr if mount.is_npc() else mount.name)

        if victim.position == merc.POS_FIGHTING:
            buf += ", fighting "

            if not victim.fighting:
                buf += "thin air??"
            elif victim.fighting == ch:
                buf += "YOU!"
            elif victim.in_room == victim.fighting.in_room:
                buf += victim.fighting.pers(ch) + "."
            else:
                buf += "somone who left??"
        else:
            buf += "."
    elif victim.position == merc.POS_STANDING and (victim.is_affected(merc.AFF_FLYING) or (not victim.is_npc() and victim.vampaff.is_set(merc.VAM_FLYING))):
        buf += " is hovering here"
    else:
        pos = victim.position
        if pos == merc.POS_DEAD:
            buf += " is DEAD!!"
        elif pos == merc.POS_MORTAL:
            buf += " is mortally wounded."
        elif pos == merc.POS_INCAP:
            buf += " is incapacitated."
        elif pos == merc.POS_STUNNED:
            buf += " is lying here stunned."
        elif pos == merc.POS_SLEEPING:
            buf += " is sleeping here."
        elif pos == merc.POS_RESTING:
            buf += " is resting here."
        elif pos == merc.POS_MEDITATING:
            buf += " is meditating here."
        elif pos == merc.POS_SITTING:
            buf += " is sitting here."
        elif pos == merc.POS_STANDING:
            if not victim.is_npc():
                stance_list = [(merc.STANCE_VIPER, "viper"), (merc.STANCE_CRANE, "crane"), (merc.STANCE_CRAB, "crab"),
                               (merc.STANCE_MONGOOSE, "mongoose"), (merc.STANCE_BULL, "bull"), (merc.STANCE_MANTIS, "mantis"),
                               (merc.STANCE_DRAGON, "dragon"), (merc.STANCE_TIGER, "tiger"), (merc.STANCE_MONKEY, "monkey"),
                               (merc.STANCE_SWALLOW, "swallow")]
                for (aa, bb) in stance_list:
                    if victim.stance[0] == aa:
                        buf += " is here, crouched in a {} fighting stance.".format(bb)
                        break
                else:
                    buf += " is here, crouched in a fighting stance."
            else:
                buf += " is here."
        elif pos == merc.POS_FIGHTING:
            buf += " is here, fighting "
            if not victim.fighting:
                buf += "thin air??"
            elif victim.fighting == ch:
                buf += "YOU!"
            elif victim.in_room == victim.fighting.in_room:
                buf += victim.fighting.pers(ch) + "."
            else:
                buf += "somone who left??"

    ch.send("".join(buf) + buf2 + "\n")

    if ch.is_npc() or not ch.act.is_set(merc.PLR_BRIEF):
        if victim.itemaff.is_set(merc.ITEMA_SHOCKSHIELD):
            handler_game.act("...$N is surrounded by a crackling shield of lightning.", ch, None, victim, merc.TO_CHAR)
        if victim.itemaff.is_set(merc.ITEMA_FIRESHIELD):
            handler_game.act("...$N is surrounded by a burning shield of fire.", ch, None, victim, merc.TO_CHAR)
        if victim.itemaff.is_set(merc.ITEMA_ICESHIELD):
            handler_game.act("...$N is surrounded by a shimmering shield of ice.", ch, None, victim, merc.TO_CHAR)
        if victim.itemaff.is_set(merc.ITEMA_ACIDSHIELD):
            handler_game.act("...$N is surrounded by a bubbling shield of acid.", ch, None, victim, merc.TO_CHAR)
        if victim.itemaff.is_set(merc.ITEMA_CHAOSSHIELD):
            handler_game.act("...$N is surrounded by a swirling shield of chaos.", ch, None, victim, merc.TO_CHAR)
        if victim.itemaff.is_set(merc.ITEMA_REFLECT):
            handler_game.act("...$N is surrounded by a flickering shield of darkness.", ch, None, victim, merc.TO_CHAR)


def show_char_to_char_1(victim, ch):
    if victim.can_see(ch):
        handler_game.act("$n looks at you.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n looks at $N.", ch, None, victim, merc.TO_NOTVICT)

    if not ch.is_npc() and victim.head.is_set(merc.LOST_HEAD):
        handler_game.act("$N is lying here.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.description:
        ch.send(victim.description + "\n")
    else:
        handler_game.act("You see nothing special about $M.", ch, None, victim, merc.TO_CHAR)

    if victim.max_hit > 0:
        percent = (100 * victim.hit) // victim.max_hit
    else:
        percent = -1

    buf = victim.pers(ch)
    if percent >= 100:
        buf += " is in perfect health.\n"
    elif percent >= 90:
        buf += " is slightly scratched.\n"
    elif percent >= 80:
        buf += " has a few bruises.\n"
    elif percent >= 70:
        buf += " has some cuts.\n"
    elif percent >= 60:
        buf += " has several wounds.\n"
    elif percent >= 50:
        buf += " has many nasty wounds.\n"
    elif percent >= 40:
        buf += " is bleeding freely.\n"
    elif percent >= 30:
        buf += " is covered in blood.\n"
    elif percent >= 20:
        buf += " is leaking guts.\n"
    elif percent >= 10:
        buf += " is almost dead.\n"
    else:
        buf += " is DYING.\n"

    buf = buf[0].upper() + buf[1:]
    ch.send(buf)

    if not victim.is_npc():
        if victim.is_affected(merc.AFF_INFRARED) or victim.vampaff.is_set(merc.VAM_NIGHTSIGHT):
            handler_game.act("$N's eyes are glowing bright red.", ch, None, victim, merc.TO_CHAR)

        if victim.is_affected(merc.AFF_FLYING):
            handler_game.act("$N is hovering in the air.", ch, None, victim, merc.TO_CHAR)

        if victim.vampaff.is_set(merc.VAM_FANGS):
            handler_game.act("$N has a pair of long, pointed fangs.", ch, None, victim, merc.TO_CHAR)

        if victim.is_vampire() and victim.vampaff.is_set(merc.VAM_CLAWS):
            handler_game.act("$N has razer sharp claws protruding from under $S finger nails.", ch, None, victim, merc.TO_CHAR)
        elif victim.vampaff.is_set(merc.VAM_CLAWS):
            handler_game.act("$N has razer sharp talons extending from $S fingers.", ch, None, victim, merc.TO_CHAR)

        if victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION):
            if victim.demaff.is_set(merc.DEM_HORNS):
                handler_game.act("$N has a pair of pointed horns extending from $S head.", ch, None, victim, merc.TO_CHAR)

            if victim.demaff.is_set(merc.DEM_WINGS):
                if victim.demaff.is_set(merc.DEM_UNFOLDED):
                    handler_game.act("$N has a pair of batlike wings spread out from behind $S back.", ch, None, victim, merc.TO_CHAR)
                else:
                    handler_game.act("$N has a pair of batlike wings folded behind $S back.", ch, None, victim, merc.TO_CHAR)

    found = False
    for location, instance_id in victim.equipped.items():
        if not instance_id:
            continue

        item = instance.items[instance_id]
        if item and ch.can_see_item(item):
            if not found:
                handler_game.act("\n$N is using:", ch, None, victim, merc.TO_CHAR)
                found = True

            ch.send(merc.eq_slot_strings[location])
            if ch.is_npc() or not ch.chobj or ch.chobj != item:
                ch.send(handler_item.format_item_to_char(item, ch, True) + "\n")
            else:
                ch.send("you\n")

    if victim != ch and not ch.is_npc() and not victim.head.is_set(merc.LOST_HEAD) and game_utils.number_percent() < ch.learned["peek"]:
        ch.send("\nYou peek at the inventory:\n")
        show_list_to_char(victim.inventory, ch, True, True)


def show_char_to_char(plist, ch):
    for rch_id in plist:
        rch = instance.characters[rch_id]

        if rch == ch:
            continue

        if ch.is_immortal() or rch.is_immortal():
            if not rch.is_npc() and rch.act.is_set(merc.PLR_WIZINVIS) and ch.trust < rch.invis_level:
                continue
        else:
            if not rch.is_npc() and (rch.act.is_set(merc.PLR_WIZINVIS) or rch.itemaff.is_set(merc.ITEMA_VANISH)) and \
                    not ch.act.is_set(merc.PLR_HOLYLIGHT) and not ch.itemaff.is_set(merc.ITEMA_VISION):
                continue

        if not rch.is_npc() and (rch.head.is_set(merc.LOST_HEAD) or rch.extra.is_set(merc.EXTRA_OSWITCH)):
            continue

        if ch.can_see(rch):
            show_char_to_char_0(rch, ch)
            ch.send("\n")
        elif ch.in_room.is_dark() and (rch.is_affected(merc.AFF_INFRARED) or (not rch.is_npc() and rch.vampaff.is_set(merc.VAM_NIGHTSIGHT))):
            ch.send("You see glowing red eyes watching YOU!\n")


def add_tracks(ch, direction):
    if ch.is_npc() or ch.itemaff.is_set(merc.ITEMA_STALKER) or (ch.is_werewolf() and ch.powers[merc.WPOWER_LYNX] > 0):
        return

    ch.in_room.track[direction] = list(map(lambda s: s.replace(ch.name, ""), ch.in_room.track[direction]))
    ch.in_room.track.pop(0)
    ch.in_room.track.append(ch.name)
