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

import comm
import fight
import game_utils
import handler_magic
import instance
import interp
import merc


def cmd_cast(ch, argument):
    # Switched NPC's can cast spells, but others can't.
    if ch.is_npc() and not ch.desc:
        return

    # Polymorphed players cannot cast spells
    if not ch.is_npc() and ch.is_affected(merc.AFF_POLYMORPH) and not ch.vampaff.is_set(merc.VAM_DISGUISED):
        if not ch.is_obj():
            ch.send("You cannot cast spells in this form.\n")
            return

    if ch.itemaff.is_set(merc.ITEMA_REFLECT):
        ch.send("You are unable to focus your spell.\n")
        return

    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    handler_magic.target_name = arg2

    if not arg1:
        ch.send("Cast which what where?\n")
        return

    sn = handler_magic.find_spell(ch, arg1)
    if not sn or not sn.spell_fun or (not ch.is_npc() and ch.level < sn.skill_level or ch.learned.get(sn.name, 0) == 0):
        ch.send("You don't know any spells of that name.\n")
        return

    if ch.position < sn.minimum_position:
        if not ch.is_npc() and not ch.is_vampire() and ch.vampaff.is_set(merc.VAM_CELERITY):
            if ch.move < 25:
                ch.send("You can't concentrate enough.\n")
                return

            ch.move -= 25
        else:
            if ch.move < 50:
                ch.send("You can't concentrate enough.\n")
                return

            ch.move -= 50

    mana = 0 if ch.is_npc() else max(sn.min_mana, 100 // (2 + (ch.level * 12) - sn.skill_level))

    if not ch.is_npc() and ch.special.is_set(merc.SPC_WOLFMAN):
        if ch.powers[merc.WPOWER_OWL] < 4:
            mana *= 2

    # Locate targets.
    victim = None
    vo = None

    target = merc.TARGET_NONE
    if sn.target == merc.TAR_IGNORE:
        pass
    elif sn.target == merc.TAR_CHAR_OFFENSIVE:
        if not arg2:
            victim = ch.fighting
            if not victim:
                ch.send("Cast the spell on whom?\n")
                return
        else:
            victim = ch.get_char_room(arg2)
            if not victim:
                ch.not_here(arg2)
                return

        if ch == victim:
            ch.send("Cast this on yourself? Ok...\n")

        if victim.itemaff.is_set(merc.ITEMA_REFLECT):
            ch.send("You are unable to focus your spell upon them.\n")
            return

        if not victim.is_npc() and (not ch.can_pk() or not victim.can_pk()) and victim != ch:
            ch.send("You are unable to affect them.\n")
            return

        if not ch.is_npc():
            if ch.is_affected(merc.AFF_CHARM) and instance.characters[ch.master] == victim:
                ch.send("You can't do that on your own follower.\n")
                return

        vo = victim
        target = merc.TARGET_CHAR
    elif sn.target == merc.TAR_CHAR_DEFENSIVE:
        if not arg2:
            victim = ch
        else:
            victim = ch.get_char_room(handler_magic.target_name)
            if not victim:
                ch.not_here(handler_magic.target_name)
                return

        if victim.itemaff.is_set(merc.ITEMA_REFLECT):
            ch.send("You are unable to focus your spell upon them.\n")
            return

        vo = victim
        target = merc.TARGET_CHAR
    elif sn.target == merc.TAR_CHAR_SELF:
        if arg2 and game_utils.is_name(handler_magic.target_name, ch.name):
            ch.send("You can't cast this spell on another.\n")
            return

        vo = ch
        target = merc.TARGET_CHAR
    elif sn.target == merc.TAR_OBJ_INV:
        if not arg2:
            ch.send("What should the spell be cast upon?\n")
            return

        obj = ch.get_item_carry(handler_magic.target_name)
        if not obj:
            ch.send("You are not carrying that.\n")
            return

        vo = obj
        target = merc.TARGET_ITEM
    else:
        comm.notify("cmd_cast: bad target for sn {}".format(sn), merc.CONSOLE_ERROR)
        return

    if not ch.is_npc() and ch.mana < mana:
        ch.send("You don't have enough mana.\n")
        return

    if not game_utils.str_cmp(sn.name, "ventriloquate"):
        handler_magic.say_spell(ch, sn)

    ch.wait_state(sn.beats)

    if not ch.is_npc() and game_utils.number_percent() > ch.learned[sn.name]:
        ch.send("You lost your concentration.\n")
        ch.mana -= mana // 2
        ch.improve_spl(sn.target)
    else:
        ch.mana -= mana

        if ch.is_npc():
            sn.spell_fun(sn.name, int(ch.level), ch, vo, target)
        else:
            sn.spell_fun(sn.name, int(ch.spl[sn.target] * 0.25), ch, vo, target)
            ch.improve_spl(sn.target)

    if sn.target == merc.TAR_CHAR_OFFENSIVE and victim != ch and (victim.master and instance.characters[victim.master] != ch):
        for vch_id in ch.in_room.people[:]:
            vch = instance.characters[vch_id]

            if victim == vch and not victim.fighting:
                fight.multi_hit(victim, ch, merc.TYPE_UNDEFINED)
                break


interp.register_command(
    interp.CmdType(
        name="cast",
        cmd_fun=cmd_cast,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
