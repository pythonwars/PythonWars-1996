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
import interp
import merc
import settings


def cmd_qset(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    arg3 = argument

    if not arg1 or not arg2 or not arg3:
        ch.send("You can change the following fields...\n"
                "chwear   = Message to owner when item is worn.\n"
                "chrem    = Message to owner when item is removed.\n"
                "chuse    = Message to owner when item is used.\n"
                "victwear = Message to others in room when item is worn.\n"
                "victrem  = Message to others in room when item is removed.\n"
                "victuse  = Message to others in room when item is used.\n"
                "type       activate     = Item can be activated.\n"
                "           twist        = Item can be twisted.\n"
                "           press        = Item can be pressed.\n"
                "           pull         = Item can be pulled.\n"
                "           target       = Item can target people (for spell, etc).\n"
                "           spell        = Item can cast spells.\n"
                "           transporter  = Owner can transport freely between two locations.\n"
                "           teleporter   = Owner can transport to target location at will.\n"
                "           object       = Owner can create the specified object.\n"
                "           mobile       = Owner can create the specified mobile.\n"
                "           action       = Target must perform an action.\n"
                "           delay1       = Sets a delay of half a round on spell items.\n"
                "           delay2       = Sets a delay of one round on spell items.\n"
                "power      <value>      = Spell number/transporter room number.\n")
        return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    value = int(arg3) if arg3.isdigit() else -1

    if game_utils.str_cmp(arg2, "chwear"):
        buf = item.chpoweron if item.chpoweron else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.chpoweron = ""
        elif item.chpoweron and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.chpoweron = buf + "\n" + arg3
        else:
            item.chpoweron = arg3
    elif game_utils.str_cmp(arg2, "chrem"):
        buf = item.chpoweroff if item.chpoweroff else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.chpoweroff = ""
        elif item.chpoweroff and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.chpoweroff = buf + "\n" + arg3
        else:
            item.chpoweroff = arg3
    elif game_utils.str_cmp(arg2, "chuse"):
        buf = item.chpoweruse if item.chpoweruse else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.chpoweruse = ""
        elif item.chpoweruse and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.chpoweruse = buf + "\n" + arg3
        else:
            item.chpoweruse = arg3
    elif game_utils.str_cmp(arg2, "victwear"):
        buf = item.victpoweron if item.victpoweron else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.victpoweron = ""
        elif item.victpoweron and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.victpoweron = buf + "\n" + arg3
        else:
            item.victpoweron = arg3
    elif game_utils.str_cmp(arg2, "victrem"):
        buf = item.victpoweroff if item.victpoweroff else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.victpoweroff = ""
        elif item.victpoweroff and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.victpoweroff = buf + "\n" + arg3
        else:
            item.victpoweroff = arg3
    elif game_utils.str_cmp(arg2, "victuse"):
        buf = item.victpoweruse if item.victpoweruse else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.victpoweruse = ""
        elif item.victpoweruse and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.victpoweruse = buf + "\n" + arg3
        else:
            item.victpoweruse = arg3
    elif game_utils.str_cmp(arg2, "type"):
        sitem_list = [("activate", merc.SITEM_ACTIVATE), ("twist", merc.SITEM_TWIST), ("press", merc.SITEM_PRESS), ("pull", merc.SITEM_PULL),
                      ("target", merc.SITEM_TARGET), ("spell", merc.SITEM_SPELL), ("transporter", merc.SITEM_TRANSPORTER),
                      ("teleporter", merc.SITEM_TELEPORTER), ("object", merc.SITEM_OBJECT), ("mobile", merc.SITEM_MOBILE),
                      ("action", merc.SITEM_ACTION), ("delay1", merc.SITEM_DELAY1), ("delay2", merc.SITEM_DELAY2)]
        for (aa, bb) in sitem_list:
            if game_utils.str_cmp(arg3, aa):
                item.spectype.tog_bit(bb)
                ch.send("{} flag toggled.\n".format(arg3.capitalize()))
                return
        else:
            ch.send("No such flag to set.\n")
            return
    elif game_utils.str_cmp(arg2, "power"):
        item.specpower = value
    else:
        ch.send("No such flag.\n")
        return

    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="qset",
        cmd_fun=cmd_qset,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
