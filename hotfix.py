#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
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

import importlib
import os
import time
import traceback

import comm
import merc
import settings

# dictionary of files to track. will be key'd by file name and the value will be modified unix timestamp
tracked_files = {}
modified_files = {}
deleted_files = {}
untrack_files = {}
modunrel_files = {}


def init_file(path, modules, silent=False, reload=True):
    # called by init_monitoring to begin tracking a file.
    modules = [importlib.import_module(m) for m in modules]

    if reload:
        tracked_files[path] = [os.path.getmtime(path), modules]
    else:
        untrack_files[path] = [os.path.getmtime(path), modules]

    if not silent:
        comm.notify("    Tracking {}".format(path), merc.CONSOLE_INFO)


def init_directory(path, silent=False):
    ddir = os.listdir(path)
    files = [f for f in ddir if not f.startswith("__")]

    if not silent:
        comm.notify("Tracking {:,} files in {}".format(len(files), path), merc.CONSOLE_INFO)

    for file in files:
        full_path = os.path.join(path, file)
        module = full_path.split(".")[0].replace(os.sep, ".")
        init_file(full_path, [module], silent)


def init_monitoring():
    # Called in main function to begin tracking files.
    init_file("affects.py", ["affects"], silent=not settings.DEBUG)
    init_file("bit.py", ["bit"], silent=not settings.DEBUG)
    init_file("comm.py", ["comm"], silent=not settings.DEBUG)
    init_file("const.py", ["const"], silent=not settings.DEBUG)
    init_file("data_loader.py", ["data_loader"], silent=not settings.DEBUG)
    init_file("db.py", ["db"], silent=not settings.DEBUG)
    init_file("environment.py", ["environment"], silent=not settings.DEBUG)
    init_file("equipment.py", ["equipment"], silent=not settings.DEBUG)
    init_file("fight.py", ["fight"], silent=not settings.DEBUG)
    init_file("game_utils.py", ["game_utils"], silent=not settings.DEBUG)
    init_file("handler_ch.py", ["handler_ch"], silent=not settings.DEBUG)
    init_file("handler_game.py", ["handler_game"], silent=not settings.DEBUG)
    init_file("handler_item.py", ["handler_item"], silent=not settings.DEBUG)
    init_file("handler_log.py", ["handler_log"], silent=not settings.DEBUG)
    init_file("handler_magic.py", ["handler_magic"], silent=not settings.DEBUG)
    init_file("handler_npc.py", ["handler_npc"], silent=not settings.DEBUG)
    init_file("handler_pc.py", ["handler_pc"], silent=not settings.DEBUG, reload=False)
    init_file("handler_room.py", ["handler_room"], silent=not settings.DEBUG)
    init_file("hotfix.py", ["hotfix"], silent=not settings.DEBUG, reload=False)
    init_file("immortal.py", ["immortal"], silent=not settings.DEBUG, reload=False)
    init_file("instance.py", ["instance"], silent=not settings.DEBUG)
    init_file("interp.py", ["interp"], silent=not settings.DEBUG, reload=False)
    init_file("inventory.py", ["inventory"], silent=not settings.DEBUG)
    init_file("item_flags.py", ["item_flags"], silent=not settings.DEBUG)
    init_file("living.py", ["living"], silent=not settings.DEBUG, reload=False)
    init_file("magic.py", ["magic"], silent=not settings.DEBUG)
    init_file("merc.py", ["merc"], silent=not settings.DEBUG, reload=False)
    init_file("nanny.py", ["nanny"], silent=not settings.DEBUG)
    init_file("object_creator.py", ["object_creator"], silent=not settings.DEBUG)
    init_file("physical.py", ["physical"], silent=not settings.DEBUG)
    init_file("pywars.py", ["pywars"], silent=not settings.DEBUG)
    init_file("save.py", ["save"], silent=not settings.DEBUG)
    init_file("settings.py", ["settings"], silent=not settings.DEBUG, reload=False)
    init_file("shop_utils.py", ["shop_utils"], silent=not settings.DEBUG)
    init_file("special.py", ["special"], silent=not settings.DEBUG)
    init_file("state_checks.py", ["state_checks"], silent=not settings.DEBUG)
    init_file("sys_utils.py", ["sys_utils"], silent=not settings.DEBUG)
    init_file("tables.py", ["tables"], silent=not settings.DEBUG)
    init_file("type_bypass.py", ["type_bypass"], silent=not settings.DEBUG, reload=False)
    init_file("update.py", ["update"], silent=not settings.DEBUG)
    init_file("world_classes.py", ["world_classes"], silent=not settings.DEBUG, reload=False)

    init_directory(os.path.join("commands"), silent=not settings.DEBUG)
    init_directory(os.path.join("miniboa"), silent=not settings.DEBUG)
    init_directory(os.path.join("spells"), silent=not settings.DEBUG)


def poll_files():
    # Called in game_loop of program to check if files have been modified.
    for fp, pair in tracked_files.items():
        mod, modules = pair

        try:
            if mod != os.path.getmtime(fp):
                # File has been modified.
                comm.notify("{} has been modified".format(fp), merc.CONSOLE_INFO)
                tracked_files[fp][0] = os.path.getmtime(fp)
                modified_files[fp] = [os.path.getmtime(fp), modules]
        except FileNotFoundError:
            deleted_files[fp] = tracked_files[fp]
            del tracked_files[fp]

            if modified_files[fp]:
                del modified_files[fp]
            comm.notify("{} file is missing.".format(fp), merc.CONSOLE_WARNING)

    for fp, pair in untrack_files.items():
        mod, modules = pair

        try:
            if mod != os.path.getmtime(fp):
                # Unreloadable file has been modified.
                comm.notify("{} (unreloadable) has been modified".format(fp), merc.CONSOLE_INFO)
                untrack_files[fp][0] = os.path.getmtime(fp)
                modunrel_files[fp] = [os.path.getmtime(fp), modules]
        except FileNotFoundError:
            deleted_files[fp] = untrack_files[fp]
            del untrack_files[fp]

            if modunrel_files[fp]:
                del modunrel_files[fp]
            comm.notify("{} (unreloadable) file is missing.".format(fp), merc.CONSOLE_EXCEPTION)


def reload_files(ch):
    for fp, pair in modified_files.copy().items():
        mod, modules = pair

        comm.notify("Reloading {}".format(fp), merc.CONSOLE_INFO)
        for m in modules:
            try:
                merc.copy_time = int(time.time())
                importlib.reload(m)
            except Exception:
                ch.send(traceback.format_exc())
                comm.notify("Failed to reload {}".format(fp), merc.CONSOLE_EXCEPTION)

        del modified_files[fp]
