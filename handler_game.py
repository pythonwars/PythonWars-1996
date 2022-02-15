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

import copy
import json
from string import Template

import comm
import handler_ch
import handler_item
import instance
import living
import merc


# An affect.
class AffectData:
    load_count = 0

    def __init__(self, **kwargs):
        self.type = ""
        self.duration = 0
        self.location = 0
        self.modifier = 0
        self.bitvector = 0

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

        AffectData.load_count += 1

    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            else:
                tmp_dict[k] = v

        cls_name = "__class__/" + __name__ + "." + self.__class__.__name__
        return {cls_name: outer_encoder(tmp_dict)}

    @classmethod
    def from_json(cls, data, outer_decoder=None):
        if outer_decoder is None:
            outer_decoder = json.JSONDecoder.decode

        cls_name = "__class__/" + __name__ + "." + cls.__name__
        if cls_name in data:
            tmp_data = outer_decoder(data[cls_name])
            return cls(**tmp_data)
        return data


class HelpData:
    def __init__(self):
        self.level = 0
        self.keyword = ""
        self.text = ""

    def __repr__(self):
        return "<%s:%d>" % (self.keyword, self.level)


class TimeInfoData:
    def __init__(self):
        self.hour = 0
        self.day = 0
        self.month = 0
        self.year = 0


class WeatherData:
    def __init__(self):
        self.mmhg = 0
        self.change = 0
        self.sky = 0
        self.sunlight = 0


time_info = TimeInfoData()
weather_info = WeatherData()


def act(fmt, ch, arg1=None, arg2=None, send_to=merc.TO_ROOM, min_pos=merc.POS_MEDITATING):
    if not fmt or not ch or not ch.in_room:
        return

    vch = arg2
    obj1 = arg1
    obj2 = arg2

    he_she = ["it",  "he",  "she"]
    him_her = ["it",  "him", "her"]
    his_her = ["its", "his", "her"]

    to_players = [instance.characters[instance_id] for instance_id in ch.in_room.people[:]]

    if send_to is merc.TO_VICT:
        if not vch or not vch.in_room:
            comm.notify("act: null vict with TO_VICT", merc.CONSOLE_WARNING)
            return

        to_players = [instance.characters[instance_id] for instance_id in vch.in_room.people[:]]

    for to in to_players:
        if not to.desc or to.position < min_pos:
            continue
        if send_to is merc.TO_CHAR and to is not ch:
            continue
        if send_to is merc.TO_VICT and (to is not vch or to is ch):
            continue
        if send_to is merc.TO_ROOM and to is ch:
            continue
        if send_to is merc.TO_NOTVICT and (to is ch or to is vch):
            continue

        if ch.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT:
            is_ok = (not ch.is_npc() and ch.chobj and ch.chobj.in_item and not to.is_npc() and to.chobj and to.chobj.in_item and ch.chobj.in_item == to.chobj.in_item)

            if not is_ok:
                continue

        act_trans = {}
        if arg1:
            act_trans["t"] = str(arg1)

        if arg2 and type(arg2) == str:
            act_trans["T"] = str(arg2)

        if ch:
            act_trans["n"] = ch.pers(to)
            act_trans["e"] = he_she[ch.sex]
            act_trans["m"] = him_her[ch.sex]
            act_trans["s"] = his_her[ch.sex]

        if vch and isinstance(vch, living.Living):
            act_trans["N"] = vch.pers(to)
            act_trans["E"] = he_she[vch.sex]
            act_trans["M"] = him_her[vch.sex]
            act_trans["S"] = his_her[vch.sex]

        if obj1 and obj1.__class__ == handler_item.Items:
            act_trans["p"] = "something" if not to.can_see_item(obj1) else "you" if (obj1.chobj and obj1.chobj == to) else obj1.short_descr

        if obj2 and obj2.__class__ == handler_item.Items:
            act_trans["P"] = "something" if not to.can_see_item(obj2) else "you" if (obj2.chobj and obj2.chobj == to) else obj2.short_descr

        act_trans["d"] = arg2 if not arg2 else "door"

        msg = Template(fmt).safe_substitute(act_trans)
        msg = msg[0].upper() + msg[1:]
        to.send(msg + "\n")


def act2(fmt, ch, arg1=None, arg2=None, send_to=merc.TO_ROOM, min_pos=merc.POS_MEDITATING):
    if not fmt or not ch or not ch.in_room:
        return

    vch = arg2
    obj1 = arg1
    obj2 = arg2

    he_she = ["it",  "he",  "she"]
    him_her = ["it",  "him", "her"]
    his_her = ["its", "his", "her"]

    to_players = [instance.characters[instance_id] for instance_id in ch.in_room.people[:]]

    if send_to is merc.TO_VICT:
        if not vch or not vch.in_room:
            comm.notify("act: null vict with TO_VICT", merc.CONSOLE_WARNING)
            return

        to_players = [instance.characters[instance_id] for instance_id in ch.in_room.people[:]]

    for to in to_players:
        if not to.desc or to.position < min_pos:
            continue
        if send_to is merc.TO_CHAR and to is not ch:
            continue
        if send_to is merc.TO_VICT and (to is not vch or to is ch):
            continue
        if send_to is merc.TO_ROOM and to is ch:
            continue
        if send_to is merc.TO_NOTVICT and (to is ch or to is vch):
            continue

        if ch.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT:
            is_ok = (not ch.is_npc() and ch.chobj and ch.chobj.in_item and not to.is_npc() and to.chobj and to.chobj.in_item and ch.chobj.in_item == to.chobj.in_item)

            if not is_ok:
                continue

        act_trans = {}
        if arg1:
            act_trans["t"] = str(arg1)

        if arg2 and type(arg2) == str:
            act_trans["T"] = str(arg2)

        if ch:
            act_trans["n"] = ch.pers(to)
            act_trans["e"] = he_she[ch.sex]
            act_trans["m"] = him_her[ch.sex]
            act_trans["s"] = his_her[ch.sex]

        if vch and isinstance(vch, living.Living):
            act_trans["N"] = vch.pers(to)
            act_trans["E"] = he_she[vch.sex]
            act_trans["M"] = him_her[vch.sex]
            act_trans["S"] = his_her[vch.sex]

        if obj1 and obj1.__class__ == handler_item.Items:
            act_trans["p"] = "something" if not to.can_see_item(obj1) else "you" if (obj1.chobj and obj1.chobj == to) else obj1.short_descr

        if obj2 and obj2.__class__ == handler_item.Items:
            act_trans["P"] = "something" if not to.can_see_item(obj2) else "you" if (obj2.chobj and obj2.chobj == to) else obj2.short_descr

        msg = Template(fmt).safe_substitute(act_trans)
        msg = msg[0].upper() + msg[1:]
        to.send(msg + "\n")


def kavitem(fmt, ch, arg1=None, arg2=None, send_to=merc.TO_ROOM, min_pos=merc.POS_MEDITATING):
    if not fmt or not ch or not ch.in_room:
        return

    vch = arg2
    obj1 = arg1

    he_she = ["it",  "he",  "she"]
    him_her = ["it",  "him", "her"]
    his_her = ["its", "his", "her"]

    to_players = [instance.characters[instance_id] for instance_id in ch.in_room.people[:]]

    if send_to is merc.TO_VICT:
        if not vch or not vch.in_room:
            comm.notify("act: null vict with TO_VICT", merc.CONSOLE_WARNING)
            return

        to_players = [instance.characters[instance_id] for instance_id in ch.in_room.people[:]]

    for to in to_players:
        if not to.desc or to.position < min_pos:
            continue
        if send_to is merc.TO_CHAR and to is not ch:
            continue
        if send_to is merc.TO_VICT and (to is not vch or to is ch):
            continue
        if send_to is merc.TO_ROOM and to is ch:
            continue
        if send_to is merc.TO_NOTVICT and (to is ch or to is vch):
            continue

        if ch.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT:
            is_ok = (not ch.is_npc() and ch.chobj and ch.chobj.in_item and not to.is_npc() and to.chobj and to.chobj.in_item and ch.chobj.in_item == to.chobj.in_item)

            if not is_ok:
                continue

        act_trans = {}

        if ch:
            act_trans["n"] = ch.pers(to)
            act_trans["e"] = he_she[ch.sex]
            act_trans["m"] = him_her[ch.sex]
            act_trans["s"] = his_her[ch.sex]

        if obj1 and obj1.__class__ == handler_item.Items:
            buf = f"{obj1.short_descr}'s"
            act_trans["o"] = "something's" if not to.can_see_item(obj1) else "your" if (obj1.chobj and obj1.chobj == to) else buf
            act_trans["p"] = "something" if not to.can_see_item(obj1) else "you" if (obj1.chobj and obj1.chobj == to) else obj1.short_descr

        msg = Template(fmt).safe_substitute(act_trans)
        msg = msg[0].upper() + msg[1:]
        to.send(msg + "\n")


# does aliasing and other fun stuff
def substitute_alias(d, argument):
    ch = handler_ch.ch_desc(d)
    stop_idling(ch)
    ch.interpret(argument)


def stop_idling(ch):
    if not ch or not ch.desc or not ch.was_in_room or ch.in_room != instance.rooms[merc.ROOM_VNUM_LIMBO]:
        return

    ch.timer = 0
    ch.in_room.get(ch)
    ch.was_in_room.put(ch)
    ch.was_in_room = None
    act("$n has returned from the void.", ch, None, None, merc.TO_ROOM)
