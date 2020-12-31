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
import settings
import sys_utils
import world_classes


def is_note_to(ch, note):
    if game_utils.str_cmp(ch.name, note.sender):
        return True

    if game_utils.is_name("all", note.to_list):
        return True

    if ch.is_immortal():
        if game_utils.is_name("imm", note.to_list):
            return True

        if game_utils.is_name("immortal", note.to_list):
            return True

    return game_utils.is_name(ch.name, note.to_list)


def note_attach(ch):
    if ch.pnote:
        return

    ch.pnote = world_classes.Note(sender=ch.name)


def note_remove(ch, note):
    # Build a new to_list.
    # Strip out this recipient.
    to_new = ""

    to_list = note.to_list
    while to_list:
        to_list, to_one = game_utils.read_word(to_list)

        if to_one and not game_utils.str_cmp(ch.name, to_one):
            to_new += " " + to_one

    # Just a simple recipient removal?
    if not game_utils.str_cmp(ch.name, note.sender) and to_new:
        note.to_list = to_new
        return

    # Remove note from linked list.
    instance.note_list.remove(note)
    del note

    # Rewrite entire list.
    world_classes.Note.save()


def cmd_note(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if game_utils.str_cmp(arg, "list"):
        if not instance.note_list:
            ch.send("There are no notes.\n")
            return

        buf = []
        vnum = 0
        for note in instance.note_list:
            if is_note_to(ch, note):
                buf += "[{:>3}] {}: {}\n".format(vnum, note.sender, note.subject)
                vnum += 1
        ch.send("".join(buf))
        return

    if game_utils.str_cmp(arg, "read"):
        if game_utils.str_cmp(argument, "all"):
            fall = True
            anum = 0
        elif argument.isdigit():
            fall = False
            anum = int(argument)
        else:
            ch.send("Note read which number?\n")
            return

        vnum = 0
        for note in instance.note_list:
            if is_note_to(ch, note) and (vnum == anum or fall):
                buf = ["[{:>3}] {}: {}\n{}\nTo: {}\n\n".format(vnum, note.sender, note.subject, note.date, note.to_list)]
                buf += note.text + "\n"
                ch.send("".join(buf))
                return

            vnum += 1
        ch.send("No such note.\n")
        return

    if game_utils.str_cmp(arg, "+"):
        note_attach(ch)
        buf = ch.pnote.text

        if len(buf) + len(argument) >= settings.MAX_STRING_LENGTH - 4:
            ch.send("Note too long.\n")
            return

        ch.pnote.text += argument + "\n"
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg, "subject"):
        note_attach(ch)
        ch.pnote.subject = argument
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg, "to"):
        note_attach(ch)
        ch.pnote.to_list = argument
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg, "clear"):
        if ch.pnote:
            del ch.pnote
            ch.pnote = None
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg, "show"):
        if not ch.pnote:
            ch.send("You have no note in progress.\n")
            return

        ch.send("{}: {}\n"
                "To: {}\n".format(ch.pnote.sender, ch.pnote.subject, ch.pnote.to_list))
        ch.send(ch.pnote.text)
        return

    if game_utils.str_cmp(arg, "post"):
        if not ch.pnote:
            ch.send("You have no note in progress.\n")
            return

        if not ch.extra.is_set(merc.EXTRA_NOTE_TRUST):
            ch.send("Due to abuse you must now get note trusted.\n")
            return

        ch.pnote.date = sys_utils.systimestamp(merc.current_time)
        instance.note_list.append(ch.pnote)
        del ch.pnote
        ch.pnote = None
        world_classes.Note.save()
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg, "remove"):
        if not argument.isdigit():
            ch.send("Note remove which number?\n")
            return

        anum = int(argument)
        vnum = 0
        for note in instance.note_list:
            if is_note_to(ch, note) and vnum == anum:
                note_remove(ch, note)
                ch.send("Ok.\n")
                return

            vnum += 1

        ch.send("No such note.\n")
        return

    ch.send("Huh?  Type 'help note' for usage.\n")


interp.register_command(
    interp.CmdType(
        name="note",
        cmd_fun=cmd_note,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
