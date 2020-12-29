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
import handler_game
import interp
import merc
import settings
import state_checks


def cmd_write(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    arg3 = argument

    if ch.is_npc():
        return

    if not arg1 or not arg2 or not arg3:
        ch.send("Syntax: Write <page> <title/line> <text>.\n")
        return

    item = ch.get_eq("left_hand")
    if not item or (item.item_type != merc.ITEM_TOOL or not state_checks.is_set(item.value[0], merc.TOOL_PEN)):
        item = ch.get_eq("right_hand")
        if not item or (item.item_type != merc.ITEM_TOOL or not state_checks.is_set(item.value[0], merc.TOOL_PEN)):
            ch.send("You are not holding a pen.\n")
            return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    if item.item_type not in [merc.ITEM_PAGE, merc.ITEM_BOOK]:
        ch.send("You cannot write on that.\n")
        return

    if game_utils.str_cmp(arg2, "title"):
        item.victpoweruse = arg3
        ch.send("Ok.\n")
        handler_game.act("$n writes something on $p.", ch, item, None, merc.TO_ROOM)
        return

    if not game_utils.str_cmp(arg2, "line"):
        ch.send("You can write a TITLE or a LINE.\n")
        return

    if item.item_type == merc.ITEM_BOOK:
        ch.send("You can only write a title on the book.\n")
        return

    if not item.chpoweruse:
        return

    buf = item.chpoweruse

    if not buf:
        item.chpoweruse = arg3.capitalize()
        ch.send("Ok.\n")
        handler_game.act("$n writes something on $p.", ch, item, None, merc.TO_ROOM)

        if not ch.is_mage() and not ch.is_immortal() and not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_FAILED)
        elif game_utils.str_cmp(arg3, "start.damage.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
            item.spectype.set_bit(merc.ADV_DAMAGE)
        elif game_utils.str_cmp(arg3, "start.affect.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
            item.spectype.set_bit(merc.ADV_AFFECT)
        elif game_utils.str_cmp(arg3, "start.action.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
            item.spectype.set_bit(merc.ADV_ACTION)
        elif game_utils.str_cmp(arg3, "start.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
        elif not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_FAILED)
        return

    if item.chpoweruse and buf:
        if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
            ch.send("Line too long.\n")
            return

        item.chpoweruse = buf + "\n" + arg3

        argument, arg1 = game_utils.read_word(argument)
        arg2 = argument

        if not ch.is_mage() and not ch.is_immortal() and not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_FAILED)
        elif game_utils.str_cmp(arg1, "start.damage.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
            item.spectype.set_bit(merc.ADV_DAMAGE)
        elif game_utils.str_cmp(arg1, "start.affect.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
            item.spectype.set_bit(merc.ADV_AFFECT)
        elif game_utils.str_cmp(arg1, "start.action.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
            item.spectype.set_bit(merc.ADV_ACTION)
        elif game_utils.str_cmp(arg1, "start.spell") and item.spectype.empty():
            item.spectype.set_bit(merc.ADV_STARTED)
        elif game_utils.str_cmp(arg1, "end.spell") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_FINISHED)
            item.toughness = ch.powers[merc.MPOWER_RUNE0]
            item.points += 1
        elif game_utils.str_cmp(arg1, "damage.spell") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_DAMAGE) and \
                not item.spectype.is_set(merc.ADV_AFFECT) and not item.spectype.is_set(merc.ADV_ACTION) and not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_DAMAGE)
        elif game_utils.str_cmp(arg1, "affect.spell") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_DAMAGE) and \
                not item.spectype.is_set(merc.ADV_AFFECT) and not item.spectype.is_set(merc.ADV_ACTION) and not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_AFFECT)
        elif game_utils.str_cmp(arg1, "action.spell") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_DAMAGE) and \
                not item.spectype.is_set(merc.ADV_AFFECT) and not item.spectype.is_set(merc.ADV_ACTION) and not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_AFFECT)
        elif game_utils.str_cmp(arg1, "area.affect") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_AREA_AFFECT) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_AREA_AFFECT)
            item.points += 100
        elif game_utils.str_cmp(arg1, "victim.target") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_VICTIM_TARGET) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_VICTIM_TARGET)
            item.points += 5
        elif game_utils.str_cmp(arg1, "object.target") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_OBJECT_TARGET) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_OBJECT_TARGET)
            item.points += 5
        elif game_utils.str_cmp(arg1, "global.target") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_GLOBAL_TARGET) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_GLOBAL_TARGET)
            item.points += 50
        elif game_utils.str_cmp(arg1, "next.page") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_NEXT_PAGE) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_NEXT_PAGE)
            item.points += 5
        elif game_utils.str_cmp(arg1, "parameter:") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_PARAMETER) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2:
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.spectype.set_bit(merc.ADV_PARAMETER)
                item.chpoweron = arg2
        elif game_utils.str_cmp(arg1, "spell.first") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_SPELL_FIRST) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_SPELL_FIRST)
        elif game_utils.str_cmp(arg1, "not.caster") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_NOT_CASTER) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_NOT_CASTER)
        elif game_utils.str_cmp(arg1, "no.players") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_NO_PLAYERS) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_NO_PLAYERS)
        elif game_utils.str_cmp(arg1, "second.victim") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_SECOND_VICTIM) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_SECOND_VICTIM)
            item.points += 5
        elif game_utils.str_cmp(arg1, "second.object") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_SECOND_OBJECT) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_SECOND_OBJECT)
            item.points += 5
        elif game_utils.str_cmp(arg1, "reversed") and item.spectype.is_set(merc.ADV_STARTED) and not item.spectype.is_set(merc.ADV_REVERSED) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_REVERSED)
        elif game_utils.str_cmp(arg1, "min.damage:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_DAMAGE) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2 or not arg2.isdigit() or int(arg2) not in merc.irange(0, 500):
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.value[1] = int(arg2)
                item.points += int(arg2) * 0.5
        elif game_utils.str_cmp(arg1, "max.damage:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_DAMAGE) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2 or not arg2.isdigit() or int(arg2) not in merc.irange(0, 1000):
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.value[2] = int(arg2)
                item.points += int(arg2) * 0.5
        elif game_utils.str_cmp(arg1, "move") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_ACTION) and \
                item.value[1] == merc.ACTION_NONE and not item.spectype.is_set(merc.ADV_FINISHED):
            item.value[1] = merc.ACTION_MOVE
            item.points += 500
        elif game_utils.str_cmp(arg1, "mob:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_ACTION) and \
                item.value[1] == merc.ACTION_NONE and not item.specytpe.is_set(merc.ADV_FINISHED):
            item.value[1] = merc.ACTION_MOB

            mobile = ch.get_char_world2(arg2)
            if not arg2 or not mobile:
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.value[2] = mobile.vnum
                item.points += 500
        elif game_utils.str_cmp(arg1, "object:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_ACTION) and \
                item.value[1] == merc.ACTION_NONE and not item.spectype.is_set(merc.ADV_FINISHED):
            item.value[1] = merc.ACTION_OBJECT

            obj = ch.get_char_world2(arg2)
            if not arg2 or not obj or obj.flags.artifact or obj.questowner:
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.value[2] = obj.vnum
                item.points += 500
        elif game_utils.str_cmp(arg1, "apply:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_AFFECT) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2:
                item.spectype.set_bit(merc.ADV_FAILED)
            elif game_utils.str_cmp(arg2, ["strength", "str"]) and not state_checks.is_set(item.value[1], merc.ADV_STR):
                state_checks.set_bit(item.value[1], merc.ADV_STR)
            elif game_utils.str_cmp(arg2, ["dexterity", "dex"]) and not state_checks.is_set(item.value[1], merc.ADV_DEX):
                state_checks.set_bit(item.value[1], merc.ADV_DEX)
            elif game_utils.str_cmp(arg2, ["intelligence", "int"]) and not state_checks.is_set(item.value[1], merc.ADV_INT):
                state_checks.set_bit(item.value[1], merc.ADV_INT)
            elif game_utils.str_cmp(arg2, ["wisdom", "wis"]) and not state_checks.is_set(item.value[1], merc.ADV_WIS):
                state_checks.set_bit(item.value[1], merc.ADV_WIS)
            elif game_utils.str_cmp(arg2, ["constitution", "con"]) and not state_checks.is_set(item.value[1], merc.ADV_CON):
                state_checks.set_bit(item.value[1], merc.ADV_CON)
            elif game_utils.str_cmp(arg2, "mana") and not state_checks.is_set(item.value[1], merc.ADV_MANA):
                state_checks.set_bit(item.value[1], merc.ADV_MANA)
            elif game_utils.str_cmp(arg2, ["hp", "hits", "hitpoints"]) and not state_checks.is_set(item.value[1], merc.ADV_HIT):
                state_checks.set_bit(item.value[1], merc.ADV_HIT)
            elif game_utils.str_cmp(arg2, ["move", "movement"]) and not state_checks.is_set(item.value[1], merc.ADV_MOVE):
                state_checks.set_bit(item.value[1], merc.ADV_MOVE)
            elif game_utils.str_cmp(arg2, ["ac", "armour", "armor"]) and not state_checks.is_set(item.value[1], merc.ADV_AC):
                state_checks.set_bit(item.value[1], merc.ADV_AC)
            elif game_utils.str_cmp(arg2, ["hr", "hit", "hitroll"]) and not state_checks.is_set(item.value[1], merc.ADV_HITROLL):
                state_checks.set_bit(item.value[1], merc.ADV_HITROLL)
            elif game_utils.str_cmp(arg2, ["dr", "dam", "damroll"]) and not state_checks.is_set(item.value[1], merc.ADV_DAMROLL):
                state_checks.set_bit(item.value[1], merc.ADV_DAMROLL)
            elif game_utils.str_cmp(arg2, ["save", "save.spell", "save_spell"]) and not state_checks.is_set(item.value[1], merc.ADV_SAVING_SPELL):
                state_checks.set_bit(item.value[1], merc.ADV_SAVING_SPELL)
            else:
                item.spectype.set_bit(merc.ADV_FAILED)
                return

            item.points += 25
        elif game_utils.str_cmp(arg1, "affect:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_AFFECT) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2:
                item.spectype.set_bit(merc.ADV_FAILED)
            elif game_utils.str_cmp(arg2, ["blind", "blindness"]) and not state_checks.is_set(item.value[3], merc.AFF_BLIND):
                state_checks.set_bit(item.value[3], merc.AFF_BLIND)
            elif game_utils.str_cmp(arg2, ["invis", "invisible", "invisibility"]) and not state_checks.is_set(item.value[3], merc.AFF_BLIND):
                state_checks.set_bit(item.value[3], merc.AFF_INVISIBLE)
            elif game_utils.str_cmp(arg2, "detect.evil") and not state_checks.is_set(item.value[3], merc.AFF_DETECT_EVIL):
                state_checks.set_bit(item.value[3], merc.AFF_DETECT_EVIL)
            elif game_utils.str_cmp(arg2, ["detect.invis", "detect.invisible", "detect.invisibility"]) and not state_checks.is_set(item.value[3], merc.AFF_DETECT_INVIS):
                state_checks.set_bit(item.value[3], merc.AFF_DETECT_INVIS)
            elif game_utils.str_cmp(arg2, "detect.magic") and not state_checks.is_set(item.value[3], merc.AFF_DETECT_MAGIC):
                state_checks.set_bit(item.value[3], merc.AFF_DETECT_MAGIC)
            elif game_utils.str_cmp(arg2, "detect.hidden") and not state_checks.is_set(item.value[3], merc.AFF_DETECT_HIDDEN):
                state_checks.set_bit(item.value[3], merc.AFF_DETECT_HIDDEN)
            elif game_utils.str_cmp(arg2, ["shadowplane", "shadow.plane"]) and not state_checks.is_set(item.value[3], merc.AFF_SHADOWPLANE):
                state_checks.set_bit(item.value[3], merc.AFF_SHADOWPLANE)
            elif game_utils.str_cmp(arg2, ["sanct", "sanctuary"]) and not state_checks.is_set(item.value[3], merc.AFF_SANCTUARY):
                state_checks.set_bit(item.value[3], merc.AFF_SANCTUARY)
            elif game_utils.str_cmp(arg2, "faerie.fire") and not state_checks.is_set(item.value[3], merc.AFF_FAERIE_FIRE):
                state_checks.set_bit(item.value[3], merc.AFF_FAERIE_FIRE)
            elif game_utils.str_cmp(arg2, ["infravision", "infrared", "infra"]) and not state_checks.is_set(item.value[3], merc.AFF_SANCTUARY):
                state_checks.set_bit(item.value[3], merc.AFF_SANCTUARY)
            elif game_utils.str_cmp(arg2, "curse") and not state_checks.is_set(item.value[3], merc.AFF_CURSE):
                state_checks.set_bit(item.value[3], merc.AFF_CURSE)
            elif game_utils.str_cmp(arg2, ["flaming", "burning"]) and not state_checks.is_set(item.value[3], merc.AFF_FLAMING):
                state_checks.set_bit(item.value[3], merc.AFF_FLAMING)
            elif game_utils.str_cmp(arg2, "poison") and not state_checks.is_set(item.value[3], merc.AFF_POISON):
                state_checks.set_bit(item.value[3], merc.AFF_POISON)
            elif game_utils.str_cmp(arg2, ["protect", "protection"]) and not state_checks.is_set(item.value[3], merc.AFF_PROTECT):
                state_checks.set_bit(item.value[3], merc.AFF_PROTECT)
            elif game_utils.str_cmp(arg2, "ethereal") and not state_checks.is_set(item.value[3], merc.AFF_ETHEREAL):
                state_checks.set_bit(item.value[3], merc.AFF_ETHEREAL)
            elif game_utils.str_cmp(arg2, "sneak") and not state_checks.is_set(item.value[3], merc.AFF_SNEAK):
                state_checks.set_bit(item.value[3], merc.AFF_SNEAK)
            elif game_utils.str_cmp(arg2, "hide") and not state_checks.is_set(item.value[3], merc.AFF_HIDE):
                state_checks.set_bit(item.value[3], merc.AFF_HIDE)
            elif game_utils.str_cmp(arg2, "sleep") and not state_checks.is_set(item.value[3], merc.AFF_SLEEP):
                state_checks.set_bit(item.value[3], merc.AFF_SLEEP)
            elif game_utils.str_cmp(arg2, "charm") and not state_checks.is_set(item.value[3], merc.AFF_CHARM):
                state_checks.set_bit(item.value[3], merc.AFF_CHARM)
            elif game_utils.str_cmp(arg2, ["fly", "flying"]) and not state_checks.is_set(item.value[3], merc.AFF_FLYING):
                state_checks.set_bit(item.value[3], merc.AFF_FLYING)
            elif game_utils.str_cmp(arg2, ["passdoor", "pass.door"]) and not state_checks.is_set(item.value[3], merc.AFF_PASS_DOOR):
                state_checks.set_bit(item.value[3], merc.AFF_PASS_DOOR)
            elif game_utils.str_cmp(arg2, ["shadowsight", "shadow.sight"]) and not state_checks.is_set(item.value[3], merc.AFF_SHADOWSIGHT):
                state_checks.set_bit(item.value[3], merc.AFF_SHADOWSIGHT)
            elif game_utils.str_cmp(arg2, ["web", "webbed"]) and not state_checks.is_set(item.value[3], merc.AFF_WEBBED):
                state_checks.set_bit(item.value[3], merc.AFF_WEBBED)
            else:
                item.spectype.set_bit(merc.ADV_FAILED)
                return

            item.points += 25
        elif game_utils.str_cmp(arg1, "bonus:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_AFFECT) and \
                not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2 or not arg2.isdigit() or int(arg2) not in merc.irange(0, 100):
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.value[2] = int(arg2)
                item.points += int(arg2) * 15
        elif game_utils.str_cmp(arg1, "duration:") and item.spectype.is_set(merc.ADV_STARTED) and item.spectype.is_set(merc.ADV_AFFECT) and \
                item.level == 0 and not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2 or not arg2.isdigit() or int(arg2) not in merc.irange(1, 60):
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.level = int(arg2)
                item.points += int(arg2) * 10
        elif game_utils.str_cmp(arg1, ["message.one:", "message.1:"]) and item.spectype.is_set(merc.ADV_STARTED) and \
                not item.spectype.is_set(merc.ADV_MESSAGE_1) and not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2:
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.spectype.set_bit(merc.ADV_MESSAGE_1)
                item.chpoweroff = arg2
        elif game_utils.str_cmp(arg1, ["message.two:", "message.2:"]) and item.spectype.is_set(merc.ADV_STARTED) and \
                not item.spectype.is_set(merc.ADV_MESSAGE_2) and not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2:
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.spectype.set_bit(merc.ADV_MESSAGE_2)
                item.victpoweron = arg2
        elif game_utils.str_cmp(arg1, ["message.three:", "message.3:"]) and item.spectype.is_set(merc.ADV_STARTED) and \
                not item.spectype.is_set(merc.ADV_MESSAGE_3) and not item.spectype.is_set(merc.ADV_FINISHED):
            if not arg2:
                item.spectype.set_bit(merc.ADV_FAILED)
            else:
                item.spectype.set_bit(merc.ADV_MESSAGE_3)
                item.victpoweroff = arg2
        elif not item.spectype.is_set(merc.ADV_FINISHED):
            item.spectype.set_bit(merc.ADV_FAILED)
    else:
        return

    handler_game.act("$n writes something on $p.", ch, item, None, merc.TO_ROOM)
    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="write",
        cmd_fun=cmd_write,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
