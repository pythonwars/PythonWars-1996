#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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
import hashlib
import json
import os
import random

import bit
import comm
import const
import environment
import game_utils
import handler_game
import instance
import inventory
import merc
import object_creator
import settings
import state_checks
import type_bypass


class Room(instance.Instancer, environment.Environment, inventory.Inventory, type_bypass.ObjectType):
    template_count = 0
    instance_count = 0

    def __init__(self, template=None, **kwargs):
        super().__init__()
        self.is_pc = False
        self.is_room = True
        self.vnum = 0
        self.area = ""
        self.name = ""
        self.description = ""

        self.available_light = 0
        self.sector_type = 0
        self.blood = 0

        self.extra_descr = []
        self.roomtext = []
        self.special_inventory = []
        self.track = [[""] * 10] * merc.MAX_DIR
        self.track_dir = [0] * merc.MAX_DIR
        self.exit = [None] * merc.MAX_DIR

        self.room_flags = bit.Bit(flagset_name="room_flags")

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]
            self.instancer()

        if self.environment:
            if self._environment not in instance.global_instances.keys():
                self.environment = None

        if self.special_inventory:
            for t in self.special_inventory[:]:
                self.inventory += t[0]
                import importlib
                words = t[1].split(".")
                class_name = words[-1]
                module_name = ".".join(words[0:-1])
                if module_name != "" and class_name != "":
                    module_ref = importlib.import_module(module_name)
                    class_ref = getattr(module_ref, class_name)
                    if hasattr(class_ref, "load"):
                        return class_ref.load(t[0])
            del self.special_inventory

        if self.instance_id:
            self.instance_setup()
            Room.instance_count += 1
        else:
            Room.template_count += 1

        self._last_saved = None
        self._md5 = None

    def __del__(self):
        try:
            if self.instance_id:
                Room.instance_count -= 1
                if instance.rooms.get(self.instance_id, None):
                    self.instance_destructor()
            else:
                Room.template_count -= 1
        except:
            return

    def __repr__(self):
        if not self.instance_id:
            return "<Room Template: %d>" % self.vnum
        else:
            return "<Room Instance ID: %d - Template: %d >" % (self.instance_id, self.vnum)

    def put(self, instance_object):
        if instance_object.instance_id not in self.inventory:
            self.inventory.insert(0, instance_object.instance_id)
            instance_object._room_vnum = self.vnum
        else:
            raise ValueError("Instance already present in room inventory %d" % instance_object.instance_id)

        if instance_object.is_living:
            if not instance_object.is_npc():
                self.in_area.add_pc(instance_object)

            item1 = instance_object.slots.right_hand
            item2 = instance_object.slots.left_hand
            if item1 and item1.item_type == merc.ITEM_LIGHT and item1.value[2] != 0:
                self.available_light += 1
            elif item2 and item2.item_type == merc.ITEM_LIGHT and item2.value[2] != 0:
                self.available_light += 1

            if not instance_object.bleeding.empty() and self.blood < 1000:
                self.blood += 1

            if not instance_object.is_npc() and instance_object.is_affected(merc.AFF_DARKNESS):
                self.room_flags.set_bit(merc.ROOM_TOTAL_DARKNESS)

        if instance_object.is_item:
            if instance_object.flags.light and instance_object.value[2] != 0:
                self.available_light += 1
        try:
            self.carry_number += 1
            self.carry_weight += instance_object.get_weight()
        except:
            pass
        instance_object.environment = self.instance_id
        return instance_object

    def get(self, instance_object):
        if instance_object.instance_id in self.inventory:
            self.inventory.remove(instance_object.instance_id)
            instance_object._room_vnum = None
        else:
            raise KeyError("Instance is not in room inventory, trying to be removed %d" % instance_object.instance_id)

        if instance_object.is_living:
            if not instance_object.is_npc():
                self.in_area.remove_pc(instance_object)

            item1 = instance_object.slots.right_hand
            item2 = instance_object.slots.left_hand
            if item1 and item1.item_type == merc.ITEM_LIGHT and item1.value[2] != 0 and self.available_light > 0:
                self.available_light -= 1
            elif item2 and item2.item_type == merc.ITEM_LIGHT and item2.value[2] != 0 and self.available_light > 0:
                self.available_light -= 1

            if not instance_object.is_npc() and instance_object.is_affected(merc.AFF_DARKNESS):
                self.in_room.room_flags.rem_bit(merc.ROOM_TOTAL_DARKNESS)
        elif instance_object.is_item:
            if instance_object.flags.light and instance_object.value[2] != 0 and self.available_light > 0:
                self.available_light -= 1
        else:
            raise TypeError("Unknown instance type trying to be removed from Room %r" % type(instance_object))

        instance_object.environment = None
        try:
            self.carry_number -= 1
            self.carry_weight -= instance_object.get_weight()
        except:
            pass
        return instance_object

    def instance_setup(self):
        instance.global_instances[self.instance_id] = self
        instance.rooms[self.instance_id] = self
        if self.vnum not in instance.instances_by_room.keys():
            instance.instances_by_room[self.vnum] = [self.instance_id]
        else:
            instance.instances_by_room[self.vnum] += [self.instance_id]

    def instance_destructor(self):
        instance.instances_by_room[self.vnum].remove(self.instance_id)
        del instance.rooms[self.instance_id]
        del instance.global_instances[self.instance_id]

    def is_dark(self):
        if self.available_light > 0:
            return False

        if self.room_flags.is_set(merc.ROOM_DARK):
            return True

        if self.sector_type in [merc.SECT_INSIDE, merc.SECT_CITY]:
            return False

        if handler_game.weather_info.sunlight in [merc.SUN_SET, merc.SUN_DARK]:
            return True
        return False

    # True if room is private.
    def is_private(self):
        count = len(self.people)
        if self.room_flags.is_set(merc.ROOM_PRIVATE) and count >= 2:
            return True

        if self.room_flags.is_set(merc.ROOM_SOLITARY) and count >= 1:
            return True
        return False

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            elif str(k) in ("_last_saved", "_md5"):
                continue
            elif str(k) == "inventory" and v is not None:
                # We need to save the inventory special to keep the type data with it.
                t = "special_inventory"
                tmp_dict[t] = []
                for i in v:
                    if i in instance.players:
                        pass
                    elif i in instance.rooms:
                        pass
                    elif i in instance.areas:
                        pass
                    else:
                        tmp_dict[t].append(tuple((i, instance.global_instances[i].__module__ + "."
                                                  + instance.global_instances[i].__class__.__name__)))
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

    def save(self, force: bool = False):
        if self.instance_id:
            top_dir = settings.INSTANCE_DIR
            number = self.instance_id
        else:
            top_dir = settings.AREA_DIR
            number = self.vnum
        if self.in_area.instance_id:
            area_number = self.in_area.instance_id
        else:
            area_number = self.in_area.index
        pathname = os.path.join(top_dir, "%d-%s" % (area_number, self.in_area.name), "rooms")

        os.makedirs(pathname, 0o755, True)
        filename = os.path.join(pathname, "%d-room%s" % (number, settings.DATA_EXTN))

        comm.notify("Saving {}".format(filename), merc.CONSOLE_INFO)
        js = json.dumps(self, default=instance.to_json, indent=2, sort_keys=True)
        md5 = hashlib.md5(js.encode("utf-8")).hexdigest()
        if self._md5 != md5:
            self._md5 = md5

            with open(filename, "w") as fp:
                fp.write(js)

        if self.inventory:
            for item_id in self.items[:]:
                if item_id not in instance.items:
                    comm.notify("Item {} is in Room {}'s inventory, but does not exist?".format(item_id, self.instance_id), merc.CONSOLE_ERROR)
                    continue

                item = instance.items[item_id]
                item.save(in_inventory=True, force=force)

    @classmethod
    def load(cls, vnum: int = None, instance_id: int = None):
        if instance_id:
            if instance_id in instance.rooms:
                comm.notify("Instance {} of room already loaded!".format(instance_id), merc.CONSOLE_ERROR)
                return

            pathname = settings.INSTANCE_DIR
            number = instance_id
        elif vnum:
            pathname = settings.AREA_DIR
            number = vnum
        else:
            raise ValueError("To load a Room, you must provide either a VNUM or an Instance_ID!")

        target_file = "%d-room%s" % (number, settings.DATA_EXTN)

        filename = None
        for a_path, a_directory, i_files in os.walk(pathname):
            if target_file in i_files:
                filename = os.path.join(a_path, target_file)
                break
        if not filename:
            raise ValueError("Cannot find %s" % target_file)
        jso = ""

        with open(filename, "r+") as f:
            for line in f:
                jso += line

        obj = json.loads(jso, object_hook=instance.from_json)
        if isinstance(obj, Room):
            # Inventory is already loaded by Room's __init__ function.
            return obj
        else:
            comm.notify("Could not load room data for {}".format(number), merc.CONSOLE_ERROR)
            return None


class Roomtext:
    def __init__(self, **kwargs):
        super().__init__()
        self.input = ""
        self.output = ""
        self.choutput = ""
        self.name = ""
        self.type = 0
        self.power = 0
        self.mob = 0

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]


def get_room_by_vnum(vnum):
    room_id = instance.instances_by_room[vnum][0]
    return instance.rooms[room_id]


def number_door():
    return random.randint(0, 5)


def find_door(ch, arg):
    arg_list = [(["n", "north"], merc.DIR_NORTH), (["e", "east"], merc.DIR_EAST), (["s", "south"], merc.DIR_SOUTH),
                (["w", "west"], merc.DIR_WEST), (["u", "up"], merc.DIR_UP), (["d", "down"], merc.DIR_DOWN)]
    for (aa, bb) in arg_list:
        if game_utils.str_cmp(arg, aa):
            door = bb
            break
    else:
        for door in range(merc.MAX_DIR):
            pexit = ch.in_room.exit[door]
            if pexit and pexit.exit_info.is_set(merc.EX_ISDOOR) and pexit.keyword and game_utils.is_name(arg, pexit.keyword):
                return door

        handler_game.act("I see no $T here.", ch, None, arg, merc.TO_CHAR)
        return -1

    pexit = ch.in_room.exit[door]
    if not pexit:
        handler_game.act("I see no door $T here.", ch, None, arg, merc.TO_CHAR)
        return -1

    if not pexit.exit_info.is_set(merc.EX_ISDOOR):
        ch.send("You can't do that.\n")
        return -1
    return door


def room_text(ch, argument):
    for rt in ch.in_room.roomtext:
        if game_utils.str_cmp(argument, rt.input) or game_utils.is_in(argument, rt.input) or game_utils.all_in(argument, rt.input):
            if rt.name and not game_utils.str_cmp(rt.name, ["all", "|all*"]):
                if not game_utils.is_in(ch.name, rt.name):
                    continue

            mobfound = True
            if rt.mob != 0:
                mobfound = False
                for vch_id in ch.in_room.people[:]:
                    vch = instance.characters[vch_id]

                    if not vch.is_npc():
                        continue

                    if vch.vnum == rt.mob:
                        mobfound = True
                        break

            if not mobfound:
                continue

            hop = False
            rtype = rt.type % merc.RT_RETURN
            if rtype == merc.RT_SAY:
                pass
            elif rtype == merc.RT_LIGHTS:
                ch.cmd_changelight("")
            elif rtype == merc.RT_LIGHT:
                ch.in_room.room_flags.rem_bit(merc.ROOM_DARK)
            elif rtype == merc.RT_DARK:
                ch.in_room.room_flags.set_bit(merc.ROOM_DARK)
            elif rtype == merc.RT_OBJECT:
                obj_index = instance.item_templates[rt.power]
                if not obj_index:
                    return

                item = object_creator.create_item(obj_index, ch.level)

                if state_checks.is_set(rt.type, merc.RT_TIMER):
                    item.timer = 1

                if item.flags.take:
                    ch.put(item)
                else:
                    ch.in_room.put(item)

                if game_utils.str_cmp(rt.choutput, "copy"):
                    handler_game.act(rt.output, ch, item, None, merc.TO_CHAR)
                else:
                    handler_game.act(rt.choutput, ch, item, None, merc.TO_CHAR)

                if not state_checks.is_set(rt.type, merc.RT_PERSONAL):
                    handler_game.act(rt.output, ch, item, None, merc.TO_ROOM)
                hop = True
            elif rtype == merc.RT_MOBILE:
                mob_index = instance.npc_templates[rt.power]
                if not mob_index:
                    return

                mob = object_creator.create_mobile(mob_index)
                ch.in_room.put(mob)

                if game_utils.str_cmp(rt.choutput, "copy"):
                    handler_game.act(rt.output, ch, None, mob, merc.TO_CHAR)
                else:
                    handler_game.act(rt.choutput, ch, None, mob, merc.TO_CHAR)

                if not state_checks.is_set(rt.type, merc.RT_PERSONAL):
                    handler_game.act(rt.output, ch, None, mob, merc.TO_ROOM)
                hop = True
            elif rtype == merc.RT_SPELL:
                const.skill_table[rt.power].spell_fun(rt.power, game_utils.number_range(20, 30), ch, ch, merc.TARGET_CHAR)
            elif rtype == merc.RT_PORTAL:
                if merc.OBJ_VNUM_PORTAL not in instance.item_templates:
                    return

                item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PORTAL], 0)
                item.timer = 1
                item.value[0] = rt.power
                item.value[1] = 1
                ch.in_room.put(item)
            elif rtype == merc.RT_TELEPORT:
                room = instance.rooms[rt.power]
                if not room:
                    return

                if game_utils.str_cmp(rt.choutput, "copy"):
                    handler_game.act(rt.output, ch, None, None, merc.TO_CHAR)
                else:
                    handler_game.act(rt.choutput, ch, None, None, merc.TO_CHAR)

                if not state_checks.is_set(rt.type, merc.RT_PERSONAL):
                    handler_game.act(rt.output, ch, None, None, merc.TO_ROOM)
                ch.in_room.get(ch)
                room.put(ch)
                handler_game.act("$n appears in the room.", ch, None, None, merc.TO_ROOM)
                ch.cmd_look("auto")
                hop = True
            elif rtype == merc.RT_ACTION:
                arg = argument
                argument, arg1 = game_utils.read_word(arg)
                argument, arg2 = game_utils.read_word(arg)

                mob = ch.get_char_room(arg2)
                if not mob:
                    return

                mob.interpret(rt.output)
            elif rtype == merc.RT_OPEN_LIFT:
                open_lift(ch)
            elif rtype == merc.RT_CLOSE_LIFT:
                close_lift(ch)
            elif rtype == merc.RT_MOVE_LIFT:
                move_lift(ch, rt.power)

            if hop and state_checks.is_set(rt.type, merc.RT_RETURN):
                return
            elif hop:
                continue

            if game_utils.str_cmp(rt.choutput, "copy") and not state_checks.is_set(rt.type, merc.RT_ACTION):
                handler_game.act(rt.output, ch, None, None, merc.TO_CHAR)
            elif not state_checks.is_set(rt.type, merc.RT_ACTION):
                handler_game.act(rt.choutput, ch, None, None, merc.TO_CHAR)

            if not state_checks.is_set(rt.type, merc.RT_PERSONAL) and not state_checks.is_set(rt.type, merc.RT_ACTION):
                handler_game.act(rt.output, ch, None, None, merc.TO_ROOM)

            if state_checks.is_set(rt.type, merc.RT_RETURN):
                return


def open_lift(ch):
    in_room = ch.in_room.vnum
    location = instance.rooms[in_room]

    if is_open(ch):
        return

    handler_game.act("The doors open.", ch, None, None, merc.TO_CHAR)
    handler_game.act("The doors open.", ch, None, None, merc.TO_ROOM)
    move_door(ch)

    if is_open(ch):
        handler_game.act("The doors close.", ch, None, None, merc.TO_ROOM)

    if not same_floor(ch, in_room):
        handler_game.act("The lift judders suddenly.", ch, None, None, merc.TO_ROOM)

    if is_open(ch):
        handler_game.act("The doors open.", ch, None, None, merc.TO_ROOM)

    move_door(ch)
    open_door(ch, False)
    ch.in_room.get(ch)
    location.put(ch)
    open_door(ch, True)
    move_door(ch)
    open_door(ch, True)
    thru_door(ch, in_room)
    ch.in_room.get(ch)
    location.put(ch)


def close_lift(ch):
    in_room = ch.in_room.vnum
    location = instance.rooms[in_room]

    if not is_open(ch):
        return

    handler_game.act("The doors close.", ch, None, None, merc.TO_CHAR)
    handler_game.act("The doors close.", ch, None, None, merc.TO_ROOM)
    open_door(ch, False)
    move_door(ch)
    open_door(ch, False)
    ch.in_room.get(ch)
    location.put(ch)


def move_lift(ch, to_room):
    in_room = ch.in_room.vnum
    location = instance.rooms[in_room]

    if is_open(ch):
        handler_game.act("The doors close.", ch, None, None, merc.TO_CHAR)

    if is_open(ch):
        handler_game.act("The doors close.", ch, None, None, merc.TO_ROOM)

    if not same_floor(ch, to_room):
        handler_game.act("The lift judders suddenly.", ch, None, None, merc.TO_CHAR)

    if not same_floor(ch, to_room):
        handler_game.act("The lift judders suddenly.", ch, None, None, merc.TO_ROOM)

    move_door(ch)
    open_door(ch, False)
    ch.in_room.get(ch)
    location.put(ch)
    open_door(ch, False)
    thru_door(ch, to_room)


def same_floor(ch, cmp_room):
    for item_id in ch.in_room.inventory[:]:
        item = instance.items[item_id]

        if item.item_type != merc.ITEM_PORTAL or item.vnum == 30001:
            continue

        if item.value[0] == cmp_room:
            return True
    return False


def is_open(ch):
    for item_id in ch.in_room.inventory[:]:
        item = instance.items[item_id]

        if item.item_type != merc.ITEM_PORTAL or item.vnum == 30001:
            continue

        if item.value[2] == 0:
            return True
    return False


def move_door(ch):
    for item_id in ch.in_room.inventory[:]:
        item = instance.items[item_id]

        if item.item_type != merc.ITEM_PORTAL or item.vnum == 30001:
            continue

        room_index = instance.rooms[item.value[0]]
        ch.in_room.get(ch)
        room_index.put(ch)
        return


def thru_door(ch, doorexit):
    for item_id in ch.in_room.inventory[:]:
        item = instance.items[item_id]

        if item.item_type != merc.ITEM_PORTAL or item.vnum == 30001:
            continue

        item.value[0] = doorexit
        return


def open_door(ch, be_open):
    for item_id in ch.in_room.inventory[:]:
        item = instance.items[item_id]

        if item.item_type != merc.ITEM_PORTAL or item.vnum == 30001:
            continue

        if item.value[2] == 0 and not be_open:
            item.value[2] = 3
        elif item.value[2] == 3 and be_open:
            item.value[2] = 0
        return
