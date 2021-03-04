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
import hashlib
import json
import os

import bit
import comm
import environment
import game_utils
import instance
import merc
import settings
import type_bypass


class Area(instance.Instancer, type_bypass.ObjectType, environment.Environment):
    template_count = 0
    instance_count = 0

    def __init__(self, template=None, **kwargs):
        super().__init__()
        self.is_area = True
        self.index = 0
        self.name = ""
        self.no_save = False  # TODO: This should be true for instances
        self.instance_id = None
        self.reset_list = []
        self.file_name = ""
        self.credits = ""
        self.age = 15
        self.character = 0
        self.low_range = 0
        self.high_range = 0
        self.min_vnum = 0
        self.max_vnum = 0
        # Empty is a check for if the area contains player_characters or not for use in resets, should default True
        # As in, this area is just loaded and has no PC objects, True
        self.empty = False
        self.player_chars = []

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items() if k not in instance.not_to_instance]
            self.instancer()

        if self.instance_id:
            self.instance_setup()
            Area.instance_count += 1
        else:
            Area.template_count += 1

        self._last_saved = None
        self._md5 = None

    def __del__(self):
        try:
            if self.instance_id:
                Area.instance_count -= 1
                if instance.areas.get(self.instance_id, None):
                    self.instance_destructor()
            else:
                Area.template_count -= 1
                del instance.area_templates[self.name]
        except:
            return

    def __repr__(self):
        if self.instance_id:
            return "<Instance: %d %d %s(%s): %d-%d>" % (self.instance_id, self.index, self.name,
                                                        self.file_name,
                                                        self.min_vnum,
                                                        self.max_vnum)
        else:
            return "<Template: %d %s(%s): %d-%d>" % (self.index, self.name,
                                                     self.file_name,
                                                     self.min_vnum,
                                                     self.max_vnum)

    @property
    def player_count(self):
        return len(self.player_chars)

    def add_pc(self, player_char):
        if player_char.is_living and not player_char.is_npc():
            if player_char.instance_id not in self.player_chars:
                # Transition an empty area, to an occupied one, for Resets
                if self.empty:
                    self.empty = False
                    self.age = 0
                self.player_chars += [player_char.instance_id]
            else:
                raise ValueError("Player Character already in player_chars list! %d" % player_char.instance_id)
        else:
            raise KeyError("Entity not a player character, or is an NPC on area addition! %r" % type(player_char))

    def remove_pc(self, player_char):
        if player_char.is_living and not player_char.is_npc():
            if player_char.instance_id in self.player_chars:
                self.player_chars.remove(player_char.instance_id)
            else:
                raise ValueError("Player Character not in player_chars list! %d" % player_char.instance_id)
        else:
            raise KeyError("Entity not a player character, or is an NPC on area removal! %r" % type(player_char))

    def instance_setup(self):
        instance.global_instances[self.instance_id] = self
        instance.areas[self.instance_id] = self
        if self.name not in instance.instances_by_area.keys():
            instance.instances_by_area[self.name] = [self.instance_id]
        else:
            instance.instances_by_area[self.name] += [self.instance_id]

    def instance_destructor(self):
        instance.instances_by_area[self.name].remove(self.instance_id)
        del instance.areas[self.instance_id]
        del instance.global_instances[self.instance_id]

    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            elif str(k) in ("_last_saved", "_md5"):
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

    def save(self):
        if self.instance_id:
            top_dir = settings.INSTANCE_DIR
            number = self.instance_id
        else:
            top_dir = settings.AREA_DIR
            number = self.index
        pathname = os.path.join(top_dir, "%d-%s" % (number, self.name))

        os.makedirs(pathname, 0o755, True)
        filename = os.path.join(pathname, "%d-area%s" % (number, settings.DATA_EXTN))

        comm.notify("Saving {}".format(filename), merc.CONSOLE_INFO)
        js = json.dumps(self, default=instance.to_json, indent=2, sort_keys=True)
        md5 = hashlib.md5(js.encode("utf-8")).hexdigest()
        if self._md5 != md5:
            self._md5 = md5

            with open(filename, "w") as fp:
                fp.write(js)

    @classmethod
    def load(cls, index: int = None, instance_id: int = None):
        if instance_id:
            if instance_id in instance.characters:
                comm.notify("Instance {} of npc already loaded!".format(instance_id), merc.CONSOLE_INFO)
                return
            top_dir = settings.INSTANCE_DIR
            number = instance_id
        else:
            top_dir = settings.AREA_DIR
            number = index

        target_file = "%d-area%s" % (number, settings.DATA_EXTN)

        filename = None
        for a_path, a_directory, i_files in os.walk(top_dir):
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
        if isinstance(obj, Area):
            return obj
        else:
            comm.notify("Could not load area data for {}".format(number), merc.CONSOLE_ERROR)
            return None


class Ban:
    def __init__(self, **kwargs):
        self.name = ""

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]


class ExtraDescrData:
    def __init__(self, **kwargs):
        self.keyword = ""  # Keyword in look/examine
        self.description = ""
        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

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


class Exit:
    def __init__(self, template=None, **kwargs):
        self.name = ""
        self.to_room_vnum = None
        self.to_room = None
        self.exit_info = bit.Bit(flagset_name="exit_flags")
        self.key = 0
        self.keyword = ""
        self.description = ""
        self.is_broken = False

        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]

            if self.to_room_vnum != -1 and not None and self.to_room_vnum in instance.instances_by_room:
                self.to_room = instance.instances_by_room[self.to_room_vnum][0]
            elif self.to_room_vnum == -1 or None:
                # This is a case where
                self.to_room = None
            elif self.to_room_vnum not in instance.instances_by_room:
                self.is_broken = True
                comm.notify("Exit: bad to_room_vnum {}".format(self.to_room_vnum), merc.CONSOLE_ERROR)
            else:
                self.to_room = None

            if self.key <= 0:
                self.key = None

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

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


class Note:
    def __init__(self, **kwargs):
        self.sender = ""
        self.date = ""
        self.to_list = ""
        self.subject = ""
        self.text = ""

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

    # Serialization
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

    @classmethod
    def save(cls):
        with open(settings.NOTE_FILE, "w") as fp:
            for note in instance.note_list:
                buf = "{}~\n{}~\n{}~\n{}~\n{}~\n\n".format(note.sender, note.date, note.to_list, note.subject, note.text)
                fp.write(buf)

    @classmethod
    def load(cls):
        if os.path.isfile(settings.NOTE_FILE):
            word = ""
            with open(settings.NOTE_FILE, "r") as fp:
                for wline in fp:
                    word += wline

            while True:
                word = word.strip()
                if not word:
                    break

                note = Note()
                word, note.sender = game_utils.read_string(word)
                word, note.date = game_utils.read_string(word)
                word, note.to_list = game_utils.read_string(word)
                word, note.subject = game_utils.read_string(word)
                word, note.text = game_utils.read_string(word)
                instance.note_list.append(note)


class Reset:
    load_count = 0

    def __init__(self, template=None, **kwargs):
        Reset.load_count += 1
        self.name = ""
        self.area = ""
        self.instance_id = None
        self.room = None
        self.command = ""
        self.arg1 = 0
        self.arg2 = 0
        self.arg3 = 0

        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]
            self.room = instance.instances_by_room[self.room][0]

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

    def __repr__(self):
        if not self.instance_id:
            return "Reset Area: %s Room: %d Type: %s" % (instance.room_templates[self.room].area,
                                                         self.room, self.command)

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


class Shop:
    def __init__(self, template=None, **kwargs):
        self.keeper = None
        self.keeper_template = None
        self.room = None
        self.buy_type = {}
        self.profit_buy = 0
        self.profit_sell = 0
        self.open_hour = 0
        self.close_hour = 0

        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

    def __repr__(self):
        return "Shop Mob: %s Room: %d" % (instance.characters[self.keeper].name, self.room)

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
