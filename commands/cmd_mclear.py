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

import game_utils
import instance
import interp
import merc


def cmd_mclear(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Syntax: mclear <char>.\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    for item_id in ch.equipped.values():
        if not item_id:
            continue

        item = instance.items[item_id]
        victim.unequip(item.equipped_to, silent=True, forced=True)

    for aff in victim.affected[:]:
        victim.affect_remove(aff)

    if victim.is_affected(merc.AFF_POLYMORPH) and victim.is_affected(merc.AFF_ETHEREAL):
        victim.affected_by.bits = merc.AFF_POLYMORPH + merc.AFF_ETHEREAL
    elif victim.is_affected(merc.AFF_POLYMORPH):
        victim.affected_by.bits = merc.AFF_POLYMORPH
    elif victim.is_affected(merc.AFF_ETHEREAL):
        victim.affected_by.bits = merc.AFF_ETHEREAL
    else:
        victim.affected_by.clear()

    victim.armor = 100
    victim.hit = max(1, victim.hit)
    victim.mana = max(1, victim.mana)
    victim.move = max(1, victim.move)
    victim.hitroll = 0
    victim.damroll = 0
    victim.saving_throw = 0
    victim.mod_stat = [0 for _ in merc.MAX_STATS]
    victim.followers = 0
    victim.save(force=True)
    victim.send("Your stats have been cleared.  Please rewear your equipment.\n")
    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="mclear",
        cmd_fun=cmd_mclear,
        position=merc.POS_DEAD, level=9,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
