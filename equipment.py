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

import collections
import json
import sys

import instance


class Equipment:
    def __init__(self):
        super().__init__()
        self._equipped = None
        self._equips_to = None
        self._equipped_to = None

    def equip(self, item, replace: bool = False, verbose: bool = True, verbose_all: bool = True, to_loc: str = None):
        pass

    def unequip(self, unequip_from, replace: bool = True):
        pass


class Equipped:
    def __init__(self, equip_dict: dict = None):
        self._equipped = collections.OrderedDict([("light", None),
                                                  ("left_finger", None),
                                                  ("right_finger", None),
                                                  ("neck_one", None),
                                                  ("neck_two", None),
                                                  ("body", None),
                                                  ("head", None),
                                                  ("legs", None),
                                                  ("feet", None),
                                                  ("hands", None),
                                                  ("arms", None),
                                                  ("about_body", None),
                                                  ("waist", None),
                                                  ("left_wrist", None),
                                                  ("right_wrist", None),
                                                  ("right_hand", None),
                                                  ("left_hand", None),
                                                  ("face", None),
                                                  ("left_scabbard", None),
                                                  ("right_scabbard", None)])
        if equip_dict:
            for k, v in equip_dict.items():
                self._equipped[k] = v

    @property
    def available(self):
        return {slot for slot in self._equipped.keys() if not self._equipped[slot]}

    @property
    def light(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def head(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def neck_one(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def neck_two(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def left_finger(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def right_finger(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def body(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def waist(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def arms(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def legs(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def left_wrist(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def right_wrist(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def hands(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def feet(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def about(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def right_hand(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def left_hand(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def face(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def left_scabbard(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    @property
    def right_scabbard(self):
        func_name = sys._getframe().f_code.co_name
        return instance.global_instances.get(self._equipped[func_name], None)

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        cls_name = "__class__/" + __name__ + "." + self.__class__.__name__
        return {cls_name: {"equipped": outer_encoder(self._equipped)}}

    @classmethod
    def from_json(cls, data, outer_decoder=None):
        if outer_decoder is None:
            outer_decoder = json.JSONDecoder.decode

        cls_name = "__class__/" + __name__ + "." + cls.__name__
        if cls_name in data:
            return cls(equip_dict=outer_decoder(data[cls_name]["equipped"]))
        return data
