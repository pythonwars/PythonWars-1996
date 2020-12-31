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

import os

import comm
import game_utils
import handler_game
import handler_pc
import handler_room
import instance
import merc
import save
import settings
import sys_utils


class CharDummy:
    def __init__(self):
        self.name = ""
        self.pwd = None
        self.desc = None
        self.stub = None

    def send(self, pstr):
        pass


ch_selections = {}


def licheck(c):
    return not c.lower() in ["l", "i"]


def check_parse_name(name):
    bad_names = ["All", "Auto", "Immortal", "Self", "Someone", "Gaia"]
    if name.title() in bad_names:
        return False
    
    if len(name) not in merc.irange(3, 12):
        return False

    if not name.isalpha():
        return False

    checked = [licheck(c) for c in name]
    if True not in checked:
        return False
    return True


def con_get_name(self):
    argument = self.get_command()
    name = argument.title()

    if not check_parse_name(name):
        self.send("Illegal name, try another.\n"
                  "Name: ")
        return

    if not self.character:
        ch_dummy = CharDummy()
        ch_dummy.desc = self
        self.character = ch_dummy
        ch_dummy.send = self.send
    else:
        ch_dummy = self.character

    ch_dummy.name = name
    comm.notify("{} trying to connect".format(name), merc.CONSOLE_INFO)

    ch_dummy.stub = handler_pc.Pc.load_stub(name)
    if ch_dummy.stub:
        found = True
        if ch_dummy.stub["is_banned"]:
            comm.notify("Denying access to {}@{}".format(ch_dummy.stub["name"], self.addrport()), merc.CONSOLE_INFO)
            self.send("You are denied access.\n")
            comm.close_socket(self)
            return

        if settings.WIZLOCK and not ch_dummy.stub["is_immortal"]:
            self.send("The game is wizlocked.\n")
            comm.close_socket(self)
            return

        if comm.is_reconnecting(self, name):
            found = True
    else:
        found, ch_dummy = save.legacy_load_char_obj(self, name)
        ch_dummy.send = self.send
        ch_dummy.desc = self
        self.character = ch_dummy

    if found:
        ch_dummy.send("Please enter password: ")
        ch_dummy.desc.password_mode_on()
        self.set_connected(con_get_old_password)
        return
    else:
        ch_dummy.send("You want {} engraved on your tombstone (Y/N)? ".format(ch_dummy.name))
        self.set_connected(con_confirm_new_name)


def con_confirm_new_name(self):
    argument = self.get_command()[:1].upper()
    ch_dummy = self.character

    if argument == "Y":
        ch_dummy.send("New character.\n"
                      "Give me a password for {}: ".format(ch_dummy.name))
        ch_dummy.desc.password_mode_on()
        self.set_connected(con_get_new_password)
    elif argument == "N":
        ch_dummy.send("Ok, what IS it, then? ")
        del self.character
        self.character = None
        self.set_connected(con_get_name)
    else:
        ch_dummy.send("Please type Yes or No? ")


def con_get_new_password(self):
    argument = self.get_command()
    ch_dummy = self.character
    ch_dummy.send("\n")

    if len(argument) < 5:
        ch_dummy.send("Password must be at least five characters long.\n"
                      "Password: ")
        return

    ch_dummy.pwd = argument
    ch_dummy.send("Please retype password: ")
    ch_dummy.desc.password_mode_on()
    self.set_connected(con_confirm_new_password)


def con_confirm_new_password(self):
    argument = self.get_command()
    ch_dummy = self.character
    ch_dummy.send("\n")

    if argument != ch_dummy.pwd:
        ch_dummy.send("Passwords don't match.\n"
                      "Retype password: ")
        ch_dummy.desc.password_mode_on()
        self.set_connected(con_get_new_password)
        return

    ch = handler_pc.Pc(ch_dummy.name)
    ch.pwd = ch_dummy.pwd
    del ch_dummy
    ch.desc = self
    ch.send = self.send
    self.character = ch
    ch.desc.password_mode_off()
    ch.send("What is your sex (M/F)? ")
    self.set_connected(con_get_new_sex)


def con_get_new_sex(self):
    argument = self.get_command()[:1].upper()
    ch = self.character

    if argument == "M":
        ch.sex = merc.SEX_MALE
    elif argument == "F":
        ch.sex = merc.SEX_FEMALE
    else:
        ch.send("That's not a sex.\n"
                "What IS your sex? ")
        return

    ch.perm_stat = [game_utils.number_range(10, 16) for _ in range(merc.MAX_STATS)]
    comm.notify("{}@{} new player.".format(ch.name, self.addrport()), merc.CONSOLE_INFO)
    ch.send("\n")
    ch.cmd_help("motd")
    self.set_connected(con_read_motd)


def con_get_old_password(self):
    argument = self.get_command()
    ch_dummy = self.character
    ch_dummy.send("\n")
    ch_dummy.desc.password_mode_off()

    pwdcmp = argument
    if pwdcmp != ch_dummy.stub["pwd"]:
        ch_dummy.send("Wrong password.\n")
        comm.close_socket(self)
        return

    ch_dummy.desc.password_mode_on()
    if comm.check_reconnect(self, ch_dummy.name, True):
        return

    if comm.check_playing(self, ch_dummy.name):
        return

    ch = handler_pc.Pc.load(ch_dummy.name)
    del ch_dummy
    ch.send = self.send
    ch.desc = self
    self.character = ch
    comm.notify("{}@{} has connected.".format(ch.name, self.addrport()), merc.CONSOLE_INFO)

    # In case we have level 4+ players from another merc mud, or
    # players who have somehow got file access and changed their pfiles.
    if ch.level > 3 and ch.trust == 0:
        ch.level = 3
    else:
        ch.level = min(ch.level, merc.MAX_LEVEL)
        ch.trust = min(ch.trust, merc.MAX_LEVEL)

    if ch.is_hero():
        ch.cmd_help("imotd")
    ch.cmd_help("motd")
    self.set_connected(con_read_motd)


def con_read_motd(self):
    ch = self.character

    ch.send("\nWelcome to God Wars Mud.  May thy blade stay ever sharp, thy soul ever dark.\n")
    self.set_connected(con_playing)

    if ch.position == merc.POS_FIGHTING:
        ch.position = merc.POS_STANDING

    if ch.is_vampire() and (ch.special.is_set(merc.SPC_PRINCE) or ch.powers[merc.UNI_GEN] < 3 or ch.rank > merc.AGE_CHILDE):
        ch_age = ch.years_old()
        if ch_age >= 100:
            ch.rank = merc.AGE_METHUSELAH
        elif ch_age >= 75:
            ch.rank = merc.AGE_ELDER
        elif ch_age >= 50:
            ch.rank = merc.AGE_ANCILLA
        else:
            ch.rank = merc.AGE_NEONATE

    if ch.level == 0:
        ch.level = 1
        ch.id = game_utils.get_mob_id(npc=False)
        ch.hit = ch.max_hit
        ch.mana = ch.max_mana
        ch.move = ch.max_move
        ch.title = "the mortal"
        ch.position = merc.POS_STANDING

        # TODO: create a player manifest that we can use/check, instead of needing to walk the dir.
        player_files = list(sys_utils.flatten([x[2] for x in os.walk(settings.PLAYER_DIR)]))
        if len([x for x in player_files if not x.startswith(".")]) < 1:
            ch.level = merc.MAX_LEVEL
            ch.trust = merc.MAX_LEVEL
            ch.send("\n\nCongratulations!  As the first player to log into this MUD, you are now\n"
                    "the IMPLEMENTOR, the sucker in charge, the place where the buck stops.\n"
                    "Enjoy!\n\n")

        ch.send("--------------------------------------------------------------------------------\n"
                "If you need help, try talking to the spirit of mud school!\n"
                "--------------------------------------------------------------------------------\n")

        school_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
        school = instance.rooms[school_id]
        school.put(ch)
        ch.cmd_look("auto")
    else:
        if ch.obj_vnum != 0:
            to_instance_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL if not ch._room_vnum else ch._room_vnum][0]
            to_instance = instance.rooms[to_instance_id]
            to_instance.put(ch)
            ch.bind_char()
            return
        elif ch._room_vnum:
            room_id = instance.instances_by_room.get(merc.ROOM_VNUM_TEMPLE if ch._room_vnum == merc.ROOM_VNUM_LIMBO else ch._room_vnum, None)[0]
            if room_id:
                instance.global_instances[room_id].put(ch)
        elif ch.is_immortal():
            to_instance_id = instance.instances_by_room[merc.ROOM_VNUM_CHAT][0]
            to_instance = instance.rooms[to_instance_id]
            to_instance.put(ch)
        elif ch._environment in instance.global_instances.keys():
            room = instance.global_instances.get(ch._environment, None)
            if room and ch._environment == room.instance_id:
                room.put(ch)
        elif ch._saved_room_vnum:
            room_id = instance.instances_by_room.get(ch._saved_room_vnum, None)[0]
            if room_id:
                instance.global_instances[room_id].put(ch)
        else:
            to_instance_id = instance.instances_by_room[merc.ROOM_VNUM_TEMPLE][0]
            to_instance = instance.rooms[to_instance_id]
            to_instance.put(ch)

    ch.update_skills()
    comm.notify("{} has entered the God Wars.".format(ch.name))
    handler_game.act("$n has entered the game.", ch, None, None, merc.TO_ROOM)
    ch.cmd_look("auto")
    self.send("\n\n" + self.show_terminal_type())
    handler_room.room_text(ch, ">ENTER<")


def con_playing(self):
    # TODO: Remove the is_immortal() check here, and possibly roll that into a new "nolag" flag or similar.
    if self.character and self.character.wait > 0 and not self.character.is_immortal():
        return

    command = self.get_command()
    if not command.strip():
        return

    handler_game.substitute_alias(self, command)
