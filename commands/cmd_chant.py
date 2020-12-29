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

import const
import fight
import game_utils
import handler_game
import interp
import merc
import state_checks


def cmd_chant(ch, argument):
    argument, arg = game_utils.read_word(argument)

    book = ch.get_eq("right_hand")
    if not book or book.item_type != merc.ITEM_BOOK:
        book = ch.get_eq("left_hand")
        if not book or book.item_type != merc.ITEM_BOOK:
            ch.send("First you must hold a spellbook.\n")
            return

    if state_checks.is_set(book.value[1], merc.CONT_CLOSED):
        ch.send("First you better open the book.\n")
        return

    if book.value[2] < 1:
        ch.send("There are no spells on the index page!\n")
        return

    page = book.get_page(book.value[2])
    if not page:
        ch.send("The current page seems to have been torn out!\n")
        return

    spellcount = (page.value[1] * 10000) + (page.value[2] * 10) + page.value[3]
    handler_game.act("You chant the arcane words from $p.", ch, book, None, merc.TO_CHAR)
    handler_game.act("$n chants some arcane words from $p.", ch, book, None, merc.TO_ROOM)

    if page.quest.is_set(merc.QUEST_MASTER_RUNE):
        ch.spectype = 0

        if page.spectype.is_set(merc.ADV_FAILED) or not page.spectype.is_set(merc.ADV_FINISHED) or page.points < 1:
            ch.send("The spell failed.\n")
        elif page.spectype.is_set(merc.ADV_DAMAGE):
            fight.adv_spell_damage(ch, book, page, argument)
        elif page.spectype.is_set(merc.ADV_AFFECT):
            fight.adv_spell_affect(ch, book, page, argument)
        elif page.spectype.is_set(merc.ADV_ACTION):
            fight.adv_spell_action(ch, book, page, argument)
        else:
            ch.send("The spell failed.\n")
        return

    spellno = 1
    victim_target = False
    object_target = False
    global_target = False

    if spellcount == 10022:  # FIRE + DESTRUCTION + TARGETING
        sn = "fireball"
        victim_target = True
        spellno = 2
    elif spellcount == 640322:  # LIFE + ENHANCEMENT + TARGETING
        sn = "heal"
        victim_target = True
        spellno = 2
    elif spellcount == 1280044:  # DEATH + SUMMONING + AREA
        sn = "guardian"
        spellno = 3
    elif spellcount == 2565128:  # MIND + INFORMATION + OBJECT
        sn = "identify"
        object_target = True
        global_target = True
    else:
        ch.send("Nothing happens.\n")
        return

    if not arg and (victim_target or object_target):
        ch.send("Please specify a target.\n")
        return

    if victim_target and sn in const.skill_table:
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

        if victim.itemaff.is_set(merc.ITEMA_REFLECT):
            ch.send("You are unable to focus your spell on them.\n")
            return

        spelltype = const.skill_table[sn].target
        level = ch.spl[spelltype] * 0.25
        const.skill_table[sn].spell_fun(sn, level, ch, victim, merc.TARGET_CHAR)

        if spellno > 1:
            const.skill_table[sn].spell_fun(sn, level, ch, victim, merc.TARGET_CHAR)

        if spellno > 2:
            const.skill_table[sn].spell_fun(sn, level, ch, victim, merc.TARGET_CHAR)
        ch.wait_state(const.skill_table[sn].beats)
    elif object_target and sn in const.skill_table:
        if not global_target:
            item = ch.get_item_carry(arg)
            if not item:
                ch.send("You are not carrying that object.\n")
                return
        else:
            item = ch.get_item_world(arg)
            if not item:
                ch.send("You cannot find any object like that.\n")
                return

        spelltype = const.skill_table[sn].target
        level = ch.spl[spelltype] * 0.25
        const.skill_table[sn].spell_fun(sn, level, ch, item, merc.TARGET_ITEM)

        if spellno > 1:
            const.skill_table[sn].spell_fun(sn, level, ch, item, merc.TARGET_ITEM)

        if spellno > 2:
            const.skill_table[sn].spell_fun(sn, level, ch, item, merc.TARGET_ITEM)
        ch.wait_state(const.skill_table[sn].beats)
    elif sn in const.skill_table:
        spelltype = const.skill_table[sn].target
        if spelltype == merc.TAR_OBJ_INV:
            ch.send("Nothing happens.\n")
            return

        level = ch.spl[spelltype] * 0.25
        const.skill_table[sn].spell_fun(sn, level, ch, ch, merc.TARGET_CHAR)

        if spellno > 1:
            const.skill_table[sn].spell_fun(sn, level, ch, ch, merc.TARGET_CHAR)

        if spellno > 2:
            const.skill_table[sn].spell_fun(sn, level, ch, ch, merc.TARGET_CHAR)
        ch.wait_state(const.skill_table[sn].beats)
    else:
        ch.send("Nothing happens.\n")


interp.register_command(
    interp.CmdType(
        name="chant",
        cmd_fun=cmd_chant,
        position=merc.POS_FIGHTING, level=4,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
