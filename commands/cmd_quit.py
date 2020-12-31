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

import comm
import handler_ch
import handler_game
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_quit(ch, argument):
    if ch.is_npc():
        return

    if ch.position == merc.POS_FIGHTING:
        ch.send("No way! You are fighting.\n")
        return

    if ch.position < merc.POS_SLEEPING:
        ch.send("You're not DEAD yet.\n")
        return

    mount = ch.mount
    if mount:
        ch.cmd_dismount("")

    # After extract_char the ch is no longer valid!
    for item_id in ch.equipped.values():
        if not item_id:
            continue

        item = instance.items[item_id]

        if not ch.is_npc() and (item.chobj and not item.chobj.is_npc() and item.chobj.obj_vnum != 0) or item.item_type == merc.ITEM_KEY:
            ch.unequip(item.equipped_to, silent=True, forced=True)

    ch.save(logout=True, force=True)

    if ch.obj_vnum != 0:
        handler_game.act("$n slowly fades out of existance.", ch, None, None, merc.TO_ROOM)
    else:
        handler_game.act("$n has left the game.", ch, None, None, merc.TO_ROOM)

    comm.notify("{} has quit.".format(ch.name), merc.CONSOLE_INFO)
    if ch.obj_vnum == 0:
        comm.info("{} has left the God Wars.".format(ch.name))

    if ch.chobj:
        ch.chobj.extract()

    ch.send("\n           I'm a lean dog, a keen dog, a wild dog, and lone;\n"
            "           I'm a rough dog, a tough dog, hunting on my own;\n"
            "           I'm a bad dog, a mad dog, teasing silly sheep;\n"
            "           I love to sit and bay the moon, to keep fat souls from sleep.\n\n")

    d = ch.desc
    pid = ch.id
    ch.extract(True)

    if d:
        comm.close_socket(d)

    # toast evil cheating bastards
    for d in instance.descriptor_list[:]:
        tch = handler_ch.ch_desc(d)
        if tch and tch.id == pid:
            tch.extract(True)
            comm.close_socket(d)


# noinspection PyUnusedLocal
def cmd_qui(ch, argument):
    ch.send("If you want to QUIT, you have to spell it out.\n")


interp.register_command(
    interp.CmdType(
        name="quit",
        cmd_fun=cmd_quit,
        position=merc.POS_SLEEPING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="qui",
        cmd_fun=cmd_qui,
        position=merc.POS_SLEEPING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
