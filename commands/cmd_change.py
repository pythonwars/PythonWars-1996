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
import handler_game
import interp
import merc


def cmd_change(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_PROTEAN):
        ch.send("You are not trained in the Protean discipline.\n")
        return

    if not arg:
        ch.send("You can change between 'human', 'bat', 'wolf' and 'mist' forms.\n")
        return

    if game_utils.str_cmp(arg, "bat"):
        if ch.is_affected(merc.AFF_POLYMORPH):
            ch.send("You can only polymorph from human form.\n")
            return

        if ch.blood < 50:
            ch.send("You have insufficient blood.\n")
            return

        if ch.stance[0] != -1:
            ch.cmd_stance("")

        if ch.mounted == merc.IS_RIDING:
            ch.cmd_dismount("")

        ch.blood -= game_utils.number_range(40, 50)
        ch.clear_stats()
        handler_game.act("You transform into bat form.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n transforms into a bat.", ch, None, None, merc.TO_ROOM)
        ch.vampaff.set_bit(merc.VAM_FLYING)
        ch.vampaff.set_bit(merc.VAM_SONIC)
        ch.polyaff.set_bit(merc.POLY_BAT)
        ch.vampaff.set_bit(merc.VAM_CHANGED)
        ch.affected_by.set_bit(merc.AFF_POLYMORPH)
        ch.morph = "{} the vampire bat".format(ch.name)
    elif game_utils.str_cmp(arg, "wolf"):
        if ch.is_affected(merc.AFF_POLYMORPH):
            ch.send("You can only polymorph from human form.\n")
            return

        if ch.blood < 50:
            ch.send("You have insufficient blood.\n")
            return

        if ch.stance[0] != -1:
            ch.cmd_stance("")

        if ch.mounted == merc.IS_RIDING:
            ch.cmd_dismount("")

        ch.blood -= game_utils.number_range(40, 50)
        handler_game.act("You transform into wolf form.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n transforms into a dire wolf.", ch, None, None, merc.TO_ROOM)
        ch.clear_stats()
        ch.mod_str = 10
        ch.polyaff.set_bit(merc.POLY_WOLF)
        ch.affected_by.set_bit(merc.AFF_POLYMORPH)
        ch.vampaff.set_bit(merc.VAM_CHANGED)
        ch.morph = "{} the dire wolf".format(ch.name)
    elif game_utils.str_cmp(arg, "mist"):
        if ch.is_affected(merc.AFF_POLYMORPH):
            ch.send("You can only polymorph from human form.\n")
            return

        if ch.blood < 50:
            ch.send("You have insufficient blood.\n")
            return

        if ch.stance[0] != -1:
            ch.cmd_stance("")

        if ch.mounted == merc.IS_RIDING:
            ch.cmd_dismount("")

        ch.blood -= game_utils.number_range(40, 50)
        handler_game.act("You transform into mist form.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n transforms into a white mist.", ch, None, None, merc.TO_ROOM)

        if ch.extra.is_set(merc.EXTRA_TIED_UP):
            handler_game.act("The ropes binding you fall through your ethereal form.", ch, None, None, merc.TO_CHAR)
            handler_game.act("The ropes binding $n fall through $s ethereal form.", ch, None, None, merc.TO_ROOM)
            ch.extra.rem_bit(merc.EXTRA_TIED_UP)
            ch.extra.rem_bit(merc.EXTRA_GAGGED)
            ch.extra.rem_bit(merc.EXTRA_BLINDFOLDED)

        if ch.is_affected("web"):
            handler_game.act("The webbing entrapping $n falls through $s ethereal form.", ch, None, None, merc.TO_ROOM)
            ch.send("The webbing entrapping you falls through your ethereal form.\n")
            ch.affect_strip("web")

        ch.clear_stats()
        ch.polyaff.set_bit(merc.POLY_MIST)
        ch.polyaff.set_bit(merc.VAM_CHANGED)
        ch.affected_by.set_bit(merc.AFF_POLYMORPH)
        ch.affected_by.set_bit(merc.AFF_ETHEREAL)
        ch.morph = "{} the white mist".format(ch.name)
    elif game_utils.str_cmp(arg, "human"):
        if not ch.is_affected(merc.AFF_POLYMORPH):
            ch.send("You are already in human form.\n")
            return

        if ch.vampaff.is_set(merc.VAM_CHANGED) and ch.polyaff.is_set(merc.POLY_BAT):
            ch.vampaff.rem_bit(merc.VAM_FLYING)
            ch.vampaff.rem_bit(merc.VAM_SONIC)
            ch.polyaff.rem_bit(merc.POLY_BAT)
        elif ch.vampaff.is_set(merc.VAM_CHANGED) and ch.polyaff.is_set(merc.POLY_WOLF):
            ch.polyaff.rem_bit(merc.POLY_WOLF)
        elif ch.vampaff.is_set(merc.VAM_CHANGED) and ch.polyaff.is_set(merc.POLY_MIST):
            ch.polyaff.rem_bit(merc.POLY_MIST)
            ch.affected_by.rem_bit(merc.AFF_ETHEREAL)
        else:
            # In case they try to change to human from a non-vamp form
            ch.send("You seem to be stuck in this form.\n")
            return

        handler_game.act("You transform into human form.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n transforms into human form.", ch, None, None, merc.TO_ROOM)
        ch.affected_by.rem_bit(merc.AFF_POLYMORPH)
        ch.polyaff.rem_bit(merc.VAM_CHANGED)
        ch.clear_stats()
        ch.morph = ""
    else:
        ch.send("You can change between 'human', 'bat', 'wolf' and 'mist' forms.\n")


interp.register_command(
    interp.CmdType(
        name="change",
        cmd_fun=cmd_change,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
