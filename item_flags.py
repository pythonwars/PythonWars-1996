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

import json
import sys


class ItemFlags:
    def __init__(self, et_data: set = None, iaf_data: set = None, ir_data: set = None, wa_data: set = None):
        self._equips_to = set({})
        if et_data:
            self._equips_to |= set(et_data)

        self._item_attributes = set({})
        if iaf_data:
            self._item_attributes |= set(iaf_data)

        self._item_restrictions = set({})
        if ir_data:
            self._item_restrictions |= set(ir_data)

        self._weapon_attributes = set({})
        if wa_data:
            self._weapon_attributes |= set(wa_data)

    @property
    def head(self):

        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @head.setter
    def head(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def legs(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @legs.setter
    def legs(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def feet(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @feet.setter
    def feet(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def hands(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @hands.setter
    def hands(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def face(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @face.setter
    def face(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def left_finger(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @left_finger.setter
    def left_finger(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def right_finger(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @right_finger.setter
    def right_finger(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def right_wrist(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @right_wrist.setter
    def right_wrist(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def left_wrist(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @left_wrist.setter
    def left_wrist(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def waist(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @waist.setter
    def waist(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def about_body(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @about_body.setter
    def about_body(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def light(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @light.setter
    def light(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def body(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @body.setter
    def body(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def neck_one(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @neck_one.setter
    def neck_one(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def neck_two(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @neck_two.setter
    def neck_two(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def arms(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @arms.setter
    def arms(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def off_hand(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @off_hand.setter
    def off_hand(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def right_hand(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @right_hand.setter
    def right_hand(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    @property
    def left_hand(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._equips_to else False

    @left_hand.setter
    def left_hand(self, is_equippable):
        func_name = sys._getframe().f_code.co_name
        if is_equippable:
            self._equips_to |= {func_name}
        else:
            self._equips_to -= {func_name}

    # Item Attribute Flags
    @property
    def magic(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @magic.setter
    def magic(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def glow(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @glow.setter
    def glow(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def hum(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @hum.setter
    def hum(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def dark(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @dark.setter
    def dark(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def silver(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @silver.setter
    def silver(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def wolfweapon(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @wolfweapon.setter
    def wolfweapon(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def demonic(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @demonic.setter
    def demonic(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def highlander(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @highlander.setter
    def highlander(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def relic(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @relic.setter
    def relic(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def enchanted(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @enchanted.setter
    def enchanted(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def artifact(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @artifact.setter
    def artifact(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def vanish(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @vanish.setter
    def vanish(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def loyal(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @loyal.setter
    def loyal(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def shadowplane(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @shadowplane.setter
    def shadowplane(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def spellproof(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @spellproof.setter
    def spellproof(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def lock(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @lock.setter
    def lock(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def evil(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @evil.setter
    def evil(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def invis(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @invis.setter
    def invis(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def bless(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @bless.setter
    def bless(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def had_timer(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @had_timer.setter
    def had_timer(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def take(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @take.setter
    def take(self, has_attr):
        func_name = sys._getframe().f_code.co_name
        if has_attr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    @property
    def shop_inventory(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_attributes else False

    @shop_inventory.setter
    def shop_inventory(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_attributes |= {func_name}
        else:
            self._item_attributes -= {func_name}

    # Item Restriction Flags
    @property
    def no_drop(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @no_drop.setter
    def no_drop(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def no_sac(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @no_sac.setter
    def no_sac(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def no_remove(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @no_remove.setter
    def no_remove(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def no_uncurse(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @no_uncurse.setter
    def no_uncurse(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def no_purge(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @no_purge.setter
    def no_purge(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def anti_good(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @anti_good.setter
    def anti_good(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def anti_evil(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @anti_evil.setter
    def anti_evil(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def anti_neutral(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @anti_neutral.setter
    def anti_neutral(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    @property
    def no_locate(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._item_restrictions else False

    @no_locate.setter
    def no_locate(self, has_restr):
        func_name = sys._getframe().f_code.co_name
        if has_restr:
            self._item_restrictions |= {func_name}
        else:
            self._item_restrictions -= {func_name}

    # Weapon Attributes
    @property
    def flaming(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._weapon_attributes else False

    @flaming.setter
    def flaming(self, weap_attr):
        func_name = sys._getframe().f_code.co_name
        if weap_attr:
            self._weapon_attributes |= {func_name}
        else:
            self._weapon_attributes -= {func_name}

    @property
    def sharp(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._weapon_attributes else False

    @sharp.setter
    def sharp(self, weap_attr):
        func_name = sys._getframe().f_code.co_name
        if weap_attr:
            self._weapon_attributes |= {func_name}
        else:
            self._weapon_attributes -= {func_name}

    @property
    def frost(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._weapon_attributes else False

    @frost.setter
    def frost(self, weap_attr):
        func_name = sys._getframe().f_code.co_name
        if weap_attr:
            self._weapon_attributes |= {func_name}
        else:
            self._weapon_attributes -= {func_name}

    @property
    def vampiric(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._weapon_attributes else False

    @vampiric.setter
    def vampiric(self, weap_attr):
        func_name = sys._getframe().f_code.co_name
        if weap_attr:
            self._weapon_attributes |= {func_name}
        else:
            self._weapon_attributes -= {func_name}

    @property
    def vorpal(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._weapon_attributes else False

    @vorpal.setter
    def vorpal(self, weap_attr):
        func_name = sys._getframe().f_code.co_name
        if weap_attr:
            self._weapon_attributes |= {func_name}
        else:
            self._weapon_attributes -= {func_name}

    @property
    def shocking(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._weapon_attributes else False

    @shocking.setter
    def shocking(self, weap_attr):
        func_name = sys._getframe().f_code.co_name
        if weap_attr:
            self._weapon_attributes |= {func_name}
        else:
            self._weapon_attributes -= {func_name}

    @property
    def poison(self):
        func_name = sys._getframe().f_code.co_name
        return func_name if func_name in self._weapon_attributes else False

    @poison.setter
    def poison(self, weap_attr):
        func_name = sys._getframe().f_code.co_name
        if weap_attr:
            self._weapon_attributes |= {func_name}
        else:
            self._weapon_attributes -= {func_name}

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        cls_name = "__class__/" + __name__ + "." + self.__class__.__name__
        return {
            cls_name: {
                "equips_to": outer_encoder(self._equips_to),
                "item_attributes": outer_encoder(self._item_attributes),
                "item_restrictions": outer_encoder(self._item_restrictions),
                "weapon_attributes": outer_encoder(self._weapon_attributes),
            }
        }

    @classmethod
    def from_json(cls, data, outer_decoder=None):
        if outer_decoder is None:
            outer_decoder = json.JSONDecoder.decode

        cls_name = "__class__/" + __name__ + "." + cls.__name__
        if cls_name in data:
            return cls(et_data=outer_decoder(data[cls_name]["equips_to"]),
                       iaf_data=outer_decoder(data[cls_name]["item_attributes"]),
                       ir_data=outer_decoder(data[cls_name]["item_restrictions"]),
                       wa_data=outer_decoder(data[cls_name]["weapon_attributes"]))
        return data
