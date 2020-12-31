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
import os

import bit
import comm
import handler_item
import instance
import json
import living
import merc
import settings


class Npc(living.Living):
    template_count = 0
    instance_count = 0

    def __init__(self, template=None, **kwargs):
        super().__init__()
        # self.is_npc = True
        self.vnum = 0  # Needs to come before the template to setup the instance
        self.is_pc = False
        self.spec_fun = None
        self.area = ""
        self.powertype = ""
        self.poweraction = ""
        self.act = bit.Bit(flagset_name="act_flags")
        self.count = 0
        self.killed = 0
        self.pshop = None

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]
            self.instancer()

        if self.environment:
            if self._environment not in instance.global_instances.keys():
                self.environment = None

        if self.inventory:
            for instance_id in self.inventory[:]:
                handler_item.Items.load(instance_id=instance_id)

        for item_id in self.equipped.values():
            if item_id:
                handler_item.Items.load(instance_id=item_id)

        if self.instance_id:
            self.instance_setup()
            Npc.instance_count += 1
        else:
            Npc.template_count += 1

        self._last_saved = None
        self._md5 = None

    def __del__(self):
        try:
            if self.instance_id:
                Npc.instance_count -= 1
                if instance.characters.get(self.instance_id, None):
                    self.instance_destructor()
            else:
                Npc.template_count -= 1
        except:
            return

    def __repr__(self):
        if self.instance_id:
            return "<NPC Instance: {} ID {} template {}>".format(self.short_descr, self.instance_id, self.vnum)
        else:
            return "<NPC Template: {}:{}>".format(self.short_descr, self.vnum)

    def instance_setup(self):
        instance.global_instances[self.instance_id] = self
        instance.npcs[self.instance_id] = self
        instance.characters[self.instance_id] = self

        if self.vnum not in instance.instances_by_npc.keys():
            instance.instances_by_npc[self.vnum] = [self.instance_id]
        else:
            instance.instances_by_npc[self.vnum] += [self.instance_id]

    def instance_destructor(self):
        instance.instances_by_npc[self.vnum].remove(self.instance_id)
        del instance.npcs[self.instance_id]
        del instance.characters[self.instance_id]
        del instance.global_instances[self.instance_id]

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            elif str(k) in ("desc", "send"):
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
        pathname = os.path.join(top_dir, "%d-%s" % (area_number, self.in_area.name), "npcs")

        os.makedirs(pathname, 0o755, True)
        filename = os.path.join(pathname, "%d-npc%s" % (number, settings.DATA_EXTN))

        comm.notify("Saving {}".format(filename), merc.CONSOLE_INFO)
        js = json.dumps(self, default=instance.to_json, indent=2, sort_keys=True)
        md5 = hashlib.md5(js.encode("utf-8")).hexdigest()
        if self._md5 != md5:
            self._md5 = md5

            with open(filename, "w") as fp:
                fp.write(js)

        if self.inventory:
            for item_id in self.inventory[:]:
                if item_id not in instance.items:
                    comm.notify("Item {} is in NPC {}'s inventory, but does not exist?".format(item_id, self.instance_id), merc.CONSOLE_ERROR)
                    continue

                item = instance.items[item_id]
                item.save(in_inventory=True, force=force)
        for item_id in self.equipped.values():
            if item_id:
                if item_id not in instance.items:
                    comm.notify("Item {} is in NPC {}'s equipment, but does not exist?".format(item_id, self.instance_id), merc.CONSOLE_ERROR)
                    continue

                item = instance.items[item_id]
                item.save(is_equipped=True, force=force)

    @classmethod
    def load(cls, vnum: int = None, instance_id: int = None):
        if instance_id:
            if instance_id in instance.characters:
                comm.notify("Instance {} of npc already loaded!".format(instance_id), merc.CONSOLE_WARNING)
                return

            pathname = settings.INSTANCE_DIR
            number = instance_id
        elif vnum:
            pathname = settings.AREA_DIR
            number = vnum
        else:
            raise ValueError("To load an NPC, you must provide either a VNUM or an Instance_ID!")

        target_file = "%d-item%s" % (number, settings.DATA_EXTN)

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
        if isinstance(obj, Npc):
            # This just ensures that all items the player has are actually loaded.
            if obj.inventory:
                for item_id in obj.inventory[:]:
                    handler_item.Items.load(instance_id=item_id)
            return obj
        else:
            comm.notify("Could not load npc data for {}".format(number), merc.CONSOLE_INFO)
            return None
