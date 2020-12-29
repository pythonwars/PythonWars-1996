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
import instance
import interp
import merc


def cmd_rstat(ch, argument):
    argument, arg = game_utils.read_word(argument)

    location = ch.in_room if not arg else game_utils.find_location(ch, arg)
    if not location:
        ch.send("No such location.\n")
        return

    if ch.in_room != location and location.is_private():
        ch.send("That room is private right now.\n")
        return

    buf = ["Name: '{}.'\nArea: '{}'.\n".format(location.name, location.area.name)]
    buf += "Vnum: {}.  Sector: {}.  Light: {}.\n".format(location.vnum, location.sector_type, location.available_light)
    buf += "Room flags: {}.\nDescription:\n{}".format(repr(location.room_flags), location.description)

    if location.extra_descr:
        buf += "Extra description keywords: '"
        buf += [edd.keyword + " " for edd in location.extra_descr]
        buf += "'.\n"

    buf += "Characters:"
    for rch_id in location.people:
        rch = instance.characters[rch_id]
        buf += "'{}' ".format(rch.name if not rch.is_npc() else rch.short_descr)

    buf += ".\nObjects:   "
    for obj_id in location.inventory[:]:
        obj = instance.global_instances[obj_id]
        buf += "'{}' ".format(obj.name)
    buf += ".\n"

    for door, pexit in enumerate(location.exit):
        if pexit:
            ch.send("Door: {}.  To: {}.  Key: {}.  Exit flags: {}.\nKeyword: '{}'.  Description: {}".format(
                door,  # TODO:  come back and fix this
                -1 if pexit.to_room is None else instance.rooms[pexit.to_room].vnum,
                -1 if pexit.key is None else pexit.key,
                pexit.exit_info,
                pexit.keyword,
                pexit.description if pexit.description else "(none).\n"))


interp.register_command(
    interp.CmdType(
        name="rstat",
        cmd_fun=cmd_rstat,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
