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
#   Ported to Python by Davion of MudBytes.net using Miniboa
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
import handler_room
import instance
import interp
import merc
import settings


def cmd_say(ch, argument):
    if ch.head.is_set(merc.LOST_TONGUE):
        ch.send("You can't speak without a tongue!\n")
        return

    if ch.extra.is_set(merc.EXTRA_GAGGED):
        ch.send("You can't speak with a gag on!\n")
        return

    if len(argument) > settings.MAX_INPUT_LENGTH:
        ch.send("Line too long.\n")
        return

    if not argument:
        ch.send("Say what?\n")
        return

    endbit = argument[-1]
    secbit = argument[-2] if len(argument) > 1 else ""

    if ch.body.is_set(merc.CUT_THROAT):
        speak1 = "rasp"
        speak2 = "rasps"
    elif not ch.is_npc() and (ch.special.is_set(merc.SPC_WOLFMAN) or ch.polyaff.is_set(merc.POLY_WOLF) or
                              (game_utils.str_cmp(ch.ch_class.name, "vampire") and ch.powers[merc.UNI_RAGE] > 0)):
        if game_utils.number_percent() > 50:
            speak1 = "growl"
            speak2 = "growls"
        else:
            speak1 = "snarl"
            speak2 = "snarls"
    elif not ch.is_npc() and ch.polyaff.is_set(merc.POLY_BAT):
        speak1 = "squeak"
        speak2 = "squeaks"
    elif not ch.is_npc() and ch.polyaff.is_set(merc.POLY_SERPENT):
        speak1 = "hiss"
        speak2 = "hisses"
    elif (not ch.is_npc() and ch.polyaff.is_set(merc.POLY_FROG)) or (ch.is_npc() and ch.vnum == merc.MOB_VNUM_FROG):
        speak1 = "croak"
        speak2 = "croaks"
    elif (not ch.is_npc() and ch.polyaff.is_set(merc.POLY_RAVEN)) or (ch.is_npc() and ch.vnum == merc.MOB_VNUM_RAVEN):
        speak1 = "squark"
        speak2 = "squarks"
    elif ch.is_npc() and ch.vnum == merc.MOB_VNUM_CAT:
        speak1 = "purr"
        speak2 = "purrs"
    elif ch.is_npc() and ch.vnum == merc.MOB_VNUM_DOG:
        speak1 = "bark"
        speak2 = "barks"
    elif game_utils.str_cmp(endbit, "!"):
        speak1 = "exclaim"
        speak2 = "exclaims"
    elif game_utils.str_cmp(endbit, "?"):
        speak1 = "ask"
        speak2 = "asks"
    elif secbit and not game_utils.str_cmp(secbit, ".") and game_utils.str_cmp(endbit, "."):
        speak1 = "state"
        speak2 = "states"
    elif secbit and game_utils.str_cmp(secbit, ".") and game_utils.str_cmp(endbit, "."):
        speak1 = "mutter"
        speak2 = "mutters"
    else:
        speak1 = "say"
        speak2 = "says"

    handler_game.act("You $t '$T'.", ch, speak1, argument, merc.TO_CHAR)

    poly = "$n {} '$T'.".format(speak2)
    if ch.in_room.vnum != merc.ROOM_VNUM_IN_OBJECT:
        handler_game.act(poly, ch, None, argument, merc.TO_ROOM)
        handler_room.room_text(ch, argument.lower())
        return

    to_players = [instance.characters[instance_id] for instance_id in ch.in_room.people[:]]
    for to in to_players:
        if not to.desc or not to.is_awake() or ch == to:
            continue

        if not ch.is_npc() and ch.chobj and ch.chobj.in_obj and not to.is_npc() and to.chobj and to.chobj.in_obj and ch.chobj.in_obj == to.chobj.in_obj:
            is_ok = True
        else:
            is_ok = False

        if not is_ok:
            continue

        if ch.is_npc():
            name = ch.short_descr
        elif not ch.is_npc() and ch.affected_by.is_set(merc.AFF_POLYMORPH):
            name = ch.morph
        else:
            name = ch.name
        name = name[0].upper() + name[1:]
        to.send("{} {} '{}'.\n".format(name, speak2, argument))

    handler_room.room_text(ch, argument.lower())


interp.register_command(
    interp.CmdType(
        name="say",
        cmd_fun=cmd_say,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="'",
        cmd_fun=cmd_say,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
