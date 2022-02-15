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
import equipment
import game_utils
import handler_game
import instance
import inventory
import item_flags
import merc
import object_creator
import physical
import settings
import type_bypass

'''Equip "Flags":
Keyword: internal identifier
Value: String Representation'''
equips_to_strings = {"left_finger": "Left Finger",
                     "right_finger": "Right Finger",
                     "neck_one": "Neck",
                     "neck_two": "Neck",
                     "body": "Body",
                     "head": "Head",
                     "legs": "Legs",
                     "feet": "Feet",
                     "hands": "Hands",
                     "arms": "Arms",
                     "about_body": "About Body",
                     "left_wrist": "Left Wrist",
                     "right_wrist": "Right Wrist",
                     "waist": "Waist",
                     "right_hand": "Right Hand",
                     "left_hand": "Left Hand",
                     "face": "Face",
                     "left_scabbard": "Left Scabbard",
                     "right_scabbard": "Right Scabbard",
                     "light": "Light"}


item_restriction_strings = {"keep": "Keep",
                            "no_drop": "No Drop",
                            "no_remove": "No Remove",
                            "anti_good": "Anti-Good",
                            "anti_evil": "Anti-Evil",
                            "anti_neutral": "Anti-Neutral",
                            "no_locate": "No Locate"}

item_attribute_strings = {"magic": "Magic",
                          "glow": "Glowing",
                          "hum": "Humming",
                          "thrown": "Thrown",
                          "vanish": "Vanish",
                          "invis": "Invisible",
                          "bless": "Bless",
                          "inventory": "Inventory",
                          "loyal": "Loyal",
                          "shadowplane": "Shadowplane",
                          "take": "Take",
                          "silver": "Silver",
                          "wolfweapon": "Wolfweapon",
                          "demonic": "Demonic",
                          "highlander": "Highlander",
                          "relic": "Relic",
                          "artifact": "Artifact",
                          "enchanted": "Enchanted"}


weapon_attribute_strings = {}


class Items(instance.Instancer, environment.Environment, physical.Physical, inventory.Inventory,
            equipment.Equipment, type_bypass.ObjectType):
    template_count = 0
    instance_count = 0

    def __init__(self, template=None, **kwargs):
        super().__init__()
        self.is_item = True
        self.vnum = 0
        self.instance_id = None
        self.valid = False
        self.chobj = None
        self.chpoweron = ""
        self.chpoweroff = ""
        self.chpoweruse = ""
        self.victpoweron = ""
        self.victpoweroff = ""
        self.victpoweruse = ""
        self.questmaker = ""
        self.questowner = ""

        self.count = 0
        self.reset_num = 0
        self.item_type = merc.ITEM_TRASH
        self.cost = 0
        self.level = 0
        self.condition = 0
        self.toughness = 0
        self.resistance = 0
        self.timer = 0
        self.points = 0
        self.specpower = 0

        self.extra_descr = []
        self.affected = []
        self.value = [0] * 5
        self.quest = bit.Bit(flagset_name="quest_flags")
        self.spectype = bit.Bit(flagset_name="spectype_flags")
        self.flags = item_flags.ItemFlags()

        if kwargs:
            [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

        if template:
            [setattr(self, k, copy.deepcopy(v)) for k, v in template.__dict__.items()]
            self.instancer()

        if self.instance_id:
            self.instance_setup()
            Items.instance_count += 1
        else:
            Items.template_count += 1

        self._last_saved = None
        self._md5 = None

    def __del__(self):
        try:
            if self.instance_id:
                Items.instance_count -= 1
                if instance.items.get(self.instance_id, None):
                    self.instance_destructor()
            else:
                Items.template_count -= 1
        except:
            return

    def __repr__(self):
        if not self.instance_id:
            return f"<Item Template: {self.short_descr} : {self.vnum}>"
        else:
            return f"<Item Instance: {self.short_descr} : ID {self.instance_id} VNUM {self.vnum}>"

    # Equipped/Equips To
    @property
    def equipped_to(self):
        """
        Find the slot this item is equipped to on a character and return str name, or return None

        :return: :rtype: str or None
        """
        if self.in_living:
            for k, v in self.in_living.equipped.items():
                if v == self.instance_id:
                    return k
        else:
            return None

    @property
    def equips_to_names(self, check_occupied=False):
        """
        return equips_to flags as string

        :param check_occupied:
        :return: :rtype: str
        """
        things = set({})
        used = self.equipped_to if check_occupied else None
        for name in self.equips_to:
            if used == name:
                continue
            things.add(equips_to_strings[name])
        return ", ".join(name for name in things)

    @property
    def equips_to(self):
        """
        Equips To getter

        :return: equips_to set, current slot list it can equip to
        :rtype: set
        """
        if self.is_item:
            return self.flags._equips_to
        else:
            return None

    @equips_to.setter
    # Default of the equippable flag is True, because the
    # caller will either want to set or clear that status.
    def equips_to(self, slots):
        """
        Clear, and re-set wear slot(s)

        :param slots: iterable
        """
        if self.flags._equips_to:
            self.flags._equips_to.clear()
        self.flags._equips_to |= set(slots)

    # Item Attributes
    @property
    def item_attribute_names(self):
        """
        return item_attributes flags as string

        :return: :rtype: str
        """
        attributes = set({})
        for astring in self.item_attributes:
            attributes.add(item_attribute_strings[astring])
        return ", ".join(name for name in attributes)

    @property
    def item_attributes(self):
        # Item Attribute getter
        """
        return the item_attributes set

        :return: :rtype: set
        """
        return self.flags._item_attributes

    @item_attributes.setter
    def item_attributes(self, attr_set):
        """
        Clear and re-set the attribute set.

        :param attr_set:
        :raise TypeError:
        """
        if self.flags._item_attributes:
            self.flags._item_attributes.clear()
        self.flags._item_attributes |= set(attr_set)

    # Restrictions
    @property
    def item_restriction_names(self):
        """
        return restriction flags as string

        :return: :rtype: str
        """
        restrictions = set({})
        for rstring in self.item_restrictions:
            restrictions.add(item_restriction_strings[rstring])
        return ", ".join(name for name in restrictions)

    @property
    def item_restrictions(self):
        # Item Restrictions getter
        """
        return item_restriction flags as set

        :return: :rtype: set
        """
        return self.flags._item_restrictions

    @item_restrictions.setter
    def item_restrictions(self, restrictions):
        """
        clear and re-set the restriction set

        :param restrictions: input flags
        """
        if self.flags._item_restrictions:
            self.flags._item_restrictions.clear()
        self.flags._item_restrictions |= set(restrictions)

    # Weapons
    @property
    def weapon_attribute_names(self):
        """
        return weapon_attribute flags as str

        :return: :rtype: str
        """
        attributes = set({})
        for wstring in self.item_restrictions:
            attributes.add(weapon_attribute_strings[wstring])
        return ", ".join(name for name in attributes)

    @property
    def weapon_attributes(self):
        """
        return weapon_attributes flags as set

        :return: :rtype: set
        """
        return self.flags._weapon_attributes

    @weapon_attributes.setter
    def weapon_attributes(self, weap_attr):
        """
        Clear and re-set weapon_attribute flags

        :param weap_attr: input data
        """
        if self.flags._weapon_attributes:
            self.flags._weapon_attributes.clear()
        self.flags._weapon_attributes |= set(weap_attr)

    def get(self, instance_object):
        if instance_object.is_item and instance_object.instance_id in self.inventory:
            self.inventory.remove(instance_object.instance_id)
            self.carry_number -= instance_object.get_number()
            self.carry_weight -= instance_object.get_weight()
            instance_object.environment = None
            return instance_object
        else:
            raise KeyError("Item to be removed from Item, not in inventory %d" % instance_object.instance_id)

    def put(self, instance_object):
        if instance_object.is_item and instance_object.instance_id not in self.inventory:
            self.inventory.insert(0, instance_object.instance_id)
            self.carry_weight += instance_object.get_weight()
            self.carry_number += instance_object.get_number()
            instance_object.environment = self.instance_id
            return instance_object
        else:
            raise KeyError("Item to be added to Item, already in inventory or wrong type "
                           "%d, %r" % (instance_object.instance_id, type(instance_object)))

    def instance_setup(self):
        instance.items[self.instance_id] = self
        instance.global_instances[self.instance_id] = self
        if self.vnum not in instance.instances_by_item.keys():
            instance.instances_by_item[self.vnum] = [self.instance_id]
        else:
            instance.instances_by_item[self.vnum] += [self.instance_id]

    def instance_destructor(self):
        instance.instances_by_item[self.vnum].remove(self.instance_id)
        del instance.items[self.instance_id]
        del instance.global_instances[self.instance_id]

    def apply_ac(self):
        if self.item_type != merc.ITEM_ARMOR:
            return 0

        multi = {"body": 3, "head": 2, "legs": 2, "about": 2, "left_scabbard": 0, "right_scabbard": 0}
        for worn_on in self.equipped_to:
            if worn_on in multi.keys():
                return multi[worn_on] * self.value[0]
        else:
            return self.value[0]

    def are_runes(self):
        return sum([self.value[1], self.value[2], self.value[3]]) > 0

    def get_page(self, page_num):
        if page_num < 1:
            return None

        for page_id in self.inventory[:]:
            page = instance.items[page_id]

            if page.value[0] == page_num:
                return page
        return None

    def quest_object(self):
        quest_selection = [102, 9201, 9225, 605, 1329, 2276, 5112, 6513, 6517, 6519, 5001,
                           5005, 5011, 5012, 5013, 2902, 1352, 2348, 2361, 3005, 5011,
                           5012, 5013, 2902, 1352, 2348, 2361, 3005, 300, 303, 307, 7216,
                           1100, 100, 30315, 5110, 6001, 3050, 301, 5230, 30302, 663,
                           7303, 2915, 2275, 8600, 8601, 8602, 8603, 5030, 9321, 6010,
                           1304, 1307, 1332, 1333, 1342, 1356, 1361, 2304, 2322, 2331,
                           2382, 8003, 8005, 5300, 5302, 5309, 5310, 5311, 4000, 601, 664,
                           900, 906, 923, 311, 7203, 7206, 1101, 5214, 5223, 5228, 2804,
                           1612, 5207, 9302, 5301, 5224, 7801, 9313, 6304, 2003, 3425,
                           3423, 608, 1109, 30319, 8903, 9317, 9307, 4050, 911, 2204, 4100,
                           3428, 310, 5113, 3402, 5319, 6512, 5114, 913, 30316, 2106, 8007,
                           6601, 2333, 3610, 2015, 5022, 1394, 2202, 1401, 6005, 1614, 647,
                           1388, 9311, 3604, 4701, 30325, 6106, 2003, 7190, 9322, 1384,
                           3412, 2342, 1374, 2210, 2332, 2901, 7200, 7824, 3410, 2013, 1510,
                           8306, 3414, 2005]
        if self.item_type != merc.ITEM_QUESTCARD:
            return

        selection = game_utils.number_range(self.level, self.level + 100)
        selection = 0 if selection not in range(1, 151) else selection
        self.value[0] = quest_selection[selection]

        selection = game_utils.number_range(self.level, self.level + 100)
        selection = 0 if selection not in range(1, 151) else selection
        self.value[1] = quest_selection[selection]

        selection = game_utils.number_range(self.level, self.level + 100)
        selection = 0 if selection not in range(1, 151) else selection
        self.value[2] = quest_selection[selection]

        selection = game_utils.number_range(self.level, self.level + 100)
        selection = 0 if selection not in range(1, 151) else selection
        self.value[3] = quest_selection[selection]

    # give an affect to an object
    def affect_add(self, paf):
        self.affected.append(paf)

    def affect_remove(self, paf):
        if not self.affected:
            comm.notify("affect_remove: no affect", merc.CONSOLE_WARNING)
            return

        if self.in_living and self.equipped_to:
            instance.characters[self.in_living].affect_modify(paf, False)

        where = paf.where
        vector = paf.bitvector

        if paf not in self.affected:
            comm.notify("affect_remove: cannot find paf")
            return

        self.affected.remove(paf)
        del paf
        if self.in_living and self.equipped_to:
            instance.characters[self.in_living].affect_check(where, vector)

    # Extract an obj from the world.
    def extract(self):
        item_template = instance.item_templates[self.vnum]
        item_template.count -= 1

        ch = self.chobj
        if ch and not ch.is_npc() and ch.chobj == self and ch.head.is_set(merc.LOST_HEAD):
            ch.head.rem_bit(merc.LOST_HEAD)
            ch.affected_by.rem_bit(merc.AFF_POLYMORPH)
            ch.morph = ""
            ch.hit = 1
            ch.in_room.get(ch)
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(ch)
            ch.chobj = None
            self.chobj = None
            ch.send("You have been KILLED!!\n")
            ch.cmd_look("auto")
            ch.position = merc.POS_RESTING
        else:
            ch = self.chobj
            if ch and not ch.is_npc() and ch.chobj == self and (ch.extra.is_set(merc.EXTRA_OSWITCH) or ch.obj_vnum != 0):
                if ch.obj_vnum != 0:
                    ch.send("You have been destroyed!\n")
                    ch.chobj = None
                    self.chobj = None
                else:
                    ch.extra.rem_bit(merc.EXTRA_OSWITCH)
                    ch.affected_by.rem_bit(merc.AFF_POLYMORPH)
                    ch.morph = ""
                    ch.in_room.get(ch)
                    room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
                    instance.rooms[room_id].put(ch)
                    ch.chobj = None
                    self.chobj = None
                    ch.send("You return to your body.\n")
            elif self.chobj:
                if not self.chobj.is_npc():
                    self.chobj.chobj = None
                self.chobj = None
                comm.notify(f"extract: obj {self.vnum} chobj invalid", merc.CONSOLE_WARNING)

        if self.environment:
            if self.equipped_to:
                self.in_living.raw_unequip(self)

            if self.environment.is_pc:
                self.environment.get(self, no_save=True)
            else:
                self.environment.get(self)

            for item_id in self.inventory[:]:
                if self.instance_id not in instance.items:
                    comm.notify(f"extract: obj {self.instance_id} not found in obj_instance dict", merc.CONSOLE_ERROR)
                    return
                tmp = instance.items[item_id]
                self.get(tmp)
                tmp.extract()

        self.instance_destructor()

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            elif str(k) in ("_last_saved", "_md5", "area", "available_light", "blood", "carry_number", "carry_weight", "chobj", "count",
                            "is_area", "is_item", "is_living", "is_room", "reset_num", "valid", "was_in_room", "zone", "zone_template"):
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

    def save(self, is_equipped: bool = False, in_inventory: bool = False, player_name: str = None, force: bool = False):
        if player_name is None:
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
            pathname = os.path.join(top_dir, "%d-%s" % (area_number, self.in_area.name), "items")
        else:
            top_dir = os.path.join(settings.PLAYER_DIR, player_name[0].lower(), player_name.capitalize())
            number = self.instance_id
            if is_equipped and in_inventory:
                raise ValueError("A player item cannot be BOTH equipped AND in their inventory!")
            if is_equipped:
                pathname = os.path.join(top_dir, "equipment")
            elif in_inventory:
                pathname = os.path.join(top_dir, "inventory")
            else:
                raise ValueError("Player items must specify if they are equipped or in their inventory!")

        os.makedirs(pathname, 0o755, True)
        filename = os.path.join(pathname, f"{number}-item{settings.DATA_EXTN}")

        js = json.dumps(self, default=instance.to_json, indent=2, sort_keys=True)
        md5 = hashlib.md5(js.encode("utf-8")).hexdigest()
        if self._md5 != md5:
            self._md5 = md5

            with open(filename, "w") as fp:
                fp.write(js)

        if self.inventory:
            for item_id in self.inventory[:]:
                if item_id not in instance.global_instances:
                    comm.notify(f"Item {item_id} is in Item {self.instance_id}'s inventory, but does not exist?", merc.CONSOLE_ERROR)
                    continue
                item = instance.global_instances[item_id]
                item.save(is_equipped=is_equipped, in_inventory=in_inventory, player_name=player_name, force=force)

    @classmethod
    def load(cls, instance_id: int = None, vnum: int = None, player_name: str = None):
        if not vnum and not instance_id:
            raise ValueError("You must provide either a vnum or an instance_id!")
        if vnum and instance_id:
            raise ValueError("You must provide either a vnum or an instance_id, not BOTH!")
        if instance_id and (instance_id in instance.items.keys()):
            comm.notify(f"Instance {instance_id} of item already loaded!", merc.CONSOLE_ERROR)
            return

        if not player_name:
            if instance_id:
                pathname = settings.INSTANCE_DIR
                number = instance_id
            else:
                pathname = settings.AREA_DIR
                number = vnum
        else:
            pathname = os.path.join(settings.PLAYER_DIR, player_name[0].lower(), player_name.capitalize())
            number = instance_id

        target_file = f"{number}-item{settings.DATA_EXTN}"

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
        if not isinstance(obj, Items):
            raise TypeError("Could not load instance %r!" % number)
        if obj.inventory:
            obj.load_inventory(player_name)
        if obj.environment:
            if obj.environment.is_room and obj.instance_id not in obj.environment.inventory:
                obj.environment.put(obj)
        return obj

    def load_inventory(self, player_name: str = None):
        for number in self.inventory[:]:
            if self.instance_id:
                obj = Items.load(instance_id=number, player_name=player_name)
            else:
                obj = Items.load(vnum=number, player_name=player_name)
            if not isinstance(obj, Items):
                raise TypeError("Could not load instance %r!" % number)


def get_item(ch, item, this_container):
    move_ch = False

    # Objects should only have a shadowplane flag when on the floor
    if ch.is_affected(merc.AFF_SHADOWPLANE) and item.in_room and not item.flags.shadowplane:
        ch.send("Your hand passes right through it!\n")
        return
    elif not ch.is_affected(merc.AFF_SHADOWPLANE) and item.in_room and item.flags.shadowplane:
        ch.send("Your hand passes right through it!\n")
        return

    if not item.flags.take:
        ch.send("You can't take that.\n")
        return

    if ch.carry_number + item.get_number() > ch.can_carry_n():
        handler_game.act("$d: you can't carry that many items.", ch, None, item.name, merc.TO_CHAR)
        return

    if ch.carry_weight + item.get_weight() > ch.can_carry_w():
        handler_game.act("$d: you can't carry that much weight.", ch, None, item.name, merc.TO_CHAR)
        return

    if this_container:
        if ch.is_affected(merc.AFF_SHADOWPLANE) and not this_container.flags.shadowplane and (not this_container.in_living or
                                                                                              this_container.in_living != ch):
            ch.send("Your hand passes right through it!\n")
            return
        elif not ch.is_affected(merc.AFF_SHADOWPLANE) and this_container.flags.shadowplane and (not this_container.in_living or
                                                                                                this_container.in_living != ch):
            ch.send("Your hand passes right through it!\n")
            return

        handler_game.act("You get $p from $P.", ch, item, this_container, merc.TO_CHAR)
        handler_game.act("$n gets $p from $P.", ch, item, this_container, merc.TO_ROOM)

        for item2_id in this_container.inventory[:]:
            item2 = instance.items[item2_id]

            if item2.chobj:
                handler_game.act("A hand reaches inside $P and takes $p out.", item2.chobj, item, this_container, merc.TO_CHAR)
                move_ch = True
        this_container.get(item)
    else:
        handler_game.act("You get $p.", ch, item, this_container, merc.TO_CHAR)
        handler_game.act("$n gets $p.", ch, item, this_container, merc.TO_ROOM)
        ch.in_room.get(item)

    if item.item_type == merc.ITEM_MONEY:
        ch.gold += item.value[0]
        ch.get(item)
        item.extract()
    else:
        if move_ch and item.chobj:
            if item.in_living and item.in_living != item.chobj:
                objroom = instance.rooms[item.in_living.in_room.vnum]
            else:
                objroom = None
            if objroom and instance.rooms[item.chobj.in_room.vnum] != objroom:
                item.chobj.in_room.get(item.chobj)
                objroom.put(item.chobj)
                item.chobj.cmd_look("auto")

        if ch.is_affected(merc.AFF_SHADOWPLANE) and item.flags.shadowplane:
            item.flags.shadowplane = False
        ch.put(item)


def format_item_to_char(item, ch, fshort):
    if type(item) == int:
        item = instance.items[item]

    buf = ""

    if item.flags.artifact:
        buf += "(Artifact) "
    elif item.flags.relic:
        buf += "(Relic) "
    elif item.points > 0:
        buf += "(Legendary) "

    if item.flags.invis:
        buf += "(Invis) "

    if ch.is_affected(merc.AFF_DETECT_EVIL) and not item.flags.anti_good and item.flags.anti_evil:
        buf += "(Blue Aura) "
    elif ch.is_affected(merc.AFF_DETECT_EVIL) and item.flags.anti_good and not item.flags.anti_evil:
        buf += "(Red Aura) "
    elif ch.is_affected(merc.AFF_DETECT_EVIL) and item.flags.anti_good and not item.flags.anti_neutral and item.flags.anti_evil:
        buf += "(Yellow Aura) "

    if ch.is_affected(merc.AFF_DETECT_MAGIC) and item.flags.magic:
        buf += "(Magical) "

    if item.flags.glow:
        buf += "(Glowing) "

    if item.flags.hum:
        buf += "(Humming) "

    if item.flags.shadowplane and item.in_room and not ch.is_affected(merc.AFF_SHADOWPLANE):
        buf += "(Shadowplane) "
    elif not item.flags.shadowplane and item.in_room and ch.is_affected(merc.AFF_SHADOWPLANE):
        buf += "(Normal plane) "

    if fshort:
        if item.short_descr:
            buf += item.short_descr

        if item.condition < 100:
            buf += " (damaged)"
    else:
        if item.description:
            buf += item.description
    return buf


# Count occurrences of an obj in a list.
def count_obj_list(item_instance, contents):
    count = 0
    for item_id in contents:
        if item_id:
            if instance.items[item_id].name == item_instance.name:
                count += 1
    return count


# for clone, to insure that cloning goes many levels deep
def recursive_clone(ch, item, clone):
    for c_item_id in item.inventory[:]:
        c_item = instance.items[c_item_id]

        t_obj = object_creator.create_item(instance.item_templates[c_item.vnum], 0)
        object_creator.clone_item(c_item, t_obj)
        clone.put(t_obj)
        recursive_clone(ch, c_item, t_obj)
