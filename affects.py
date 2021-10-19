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

import bit
import comm
import const
import fight
import handler_game
import merc
import state_checks

depth = 0


class Affects:
    def __init__(self, **kwargs):
        super().__init__()
        self.affected = []
        self.affected_by = bit.Bit(flagset_name="affect_flags")
        self.itemaff = bit.Bit(flagset_name="itemaff_flags")
        self.immune = bit.Bit(flagset_name="immune_flags")
        self.polyaff = bit.Bit(flagset_name="polyaff_flags")

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

    def is_affected(self, aff):
        if isinstance(aff, const.skill_type):
            aff = aff.name

        if type(aff) == str:
            return True if [paf for paf in self.affected if paf.type == aff][:1] else False

        return self.affected_by.is_set(aff)

    def affect_add(self, paf):
        paf_new = handler_game.AffectData()
        paf_new.__dict__ = paf.__dict__.copy()
        self.affected.append(paf_new)
        self.affect_modify(paf_new, True)

    # Add or enhance an affect.
    def affect_join(self, paf):
        for paf_old in self.affected:
            if paf_old.type == paf.type:
                paf.duration += paf_old.duration
                paf.modifier += paf_old.modifier
                self.affect_remove(paf_old)
                break

        self.affect_add(paf)

    def enhance_stat(self, level, victim, apply_bit, bonuses, affect_bit):
        if victim.itemaff.is_set(merc.ITEMA_REFLECT):
            # noinspection PyUnresolvedReferences
            self.send("You are unable to focus your spell.\n")
            return

        if state_checks.is_set(affect_bit, merc.AFF_WEBBED) and victim.is_affected(merc.AFF_WEBBED):
            state_checks.remove_bit(affect_bit, merc.AFF_WEBBED)
        elif state_checks.is_set(affect_bit, merc.AFF_WEBBED) and fight.is_safe(self, victim):
            state_checks.remove_bit(affect_bit, merc.AFF_WEBBED)

        if state_checks.is_set(affect_bit, merc.AFF_CHARM) and not victim.is_affected(merc.AFF_CHARM):
            if victim.level <= 50 and (victim.is_npc() or not victim.immune.is_set(merc.IMM_CHARM)):
                if victim.master:
                    victim.stop_follower()
                victim.add_follower(self)
            else:
                # noinspection PyUnresolvedReferences
                self.send("The spell failed.\n")
                return

        aff = handler_game.AffectData(type="reserved", duration=level, location=apply_bit, modifier=bonuses, bitvector=affect_bit)
        victim.affect_join(aff)

    # Remove an affect from a char.
    def affect_remove(self, paf):
        if not self.affected:
            comm.notify("affect_remove: no affect", merc.CONSOLE_ERROR)
            return

        self.affect_modify(paf, False)

        if paf not in self.affected:
            comm.notify("affect_remove: cannot find paf", merc.CONSOLE_ERROR)
            return

        self.affected.remove(paf)
        del paf

    # Apply or remove an affect to a character.
    def affect_modify(self, paf, fadd):
        mod = paf.modifier
        if fadd:
            self.affected_by.set_bit(paf.bitvector)
        else:
            self.affected_by.rem_bit(paf.bitvector)
            mod = 0 - mod

        # noinspection PyUnresolvedReferences
        if self.is_npc():
            loc = paf.location
            if loc == merc.APPLY_NONE:
                pass
            elif loc == merc.APPLY_MANA:
                # noinspection PyUnresolvedReferences
                self.max_mana += mod
            elif loc == merc.APPLY_HIT:
                # noinspection PyUnresolvedReferences
                self.max_hit += mod
            elif loc == merc.APPLY_MOVE:
                # noinspection PyUnresolvedReferences
                self.max_move += mod
            elif loc == merc.APPLY_HITROLL:
                # noinspection PyUnresolvedReferences
                self.hitroll += mod
            elif loc == merc.APPLY_DAMROLL:
                # noinspection PyUnresolvedReferences
                self.damroll += mod
            elif paf.location in [merc.APPLY_SAVING_ROD, merc.APPLY_SAVING_PETRI, merc.APPLY_SAVING_BREATH, merc.APPLY_SAVING_SPELL]:
                # noinspection PyUnresolvedReferences
                self.saving_throw += mod
            return

        # noinspection PyUnresolvedReferences
        if self.is_highlander():
            return

        loc = paf.location
        if loc in [merc.APPLY_NONE, merc.APPLY_SEX, merc.APPLY_CLASS, merc.APPLY_LEVEL, merc.APPLY_AGE, merc.APPLY_HEIGHT, merc.APPLY_WEIGHT,
                   merc.APPLY_GOLD, merc.APPLY_EXP]:
            pass
        elif loc == merc.APPLY_STR:
            # noinspection PyUnresolvedReferences
            self.mod_stat[merc.STAT_STR] += mod
        elif loc == merc.APPLY_DEX:
            # noinspection PyUnresolvedReferences
            self.mod_stat[merc.STAT_DEX] += mod
        elif loc == merc.APPLY_INT:
            # noinspection PyUnresolvedReferences
            self.mod_stat[merc.STAT_INT] += mod
        elif loc == merc.APPLY_WIS:
            # noinspection PyUnresolvedReferences
            self.mod_stat[merc.STAT_WIS] += mod
        elif loc == merc.APPLY_CON:
            # noinspection PyUnresolvedReferences
            self.mod_stat[merc.STAT_CON] += mod
        elif loc == merc.APPLY_MANA:
            # noinspection PyUnresolvedReferences
            self.max_mana += mod
        elif loc == merc.APPLY_HIT:
            # noinspection PyUnresolvedReferences
            self.max_hit += mod
        elif loc == merc.APPLY_MOVE:
            # noinspection PyUnresolvedReferences
            self.max_move += mod
        elif loc == merc.APPLY_AC:
            # noinspection PyUnresolvedReferences
            self.armor += mod
        elif loc == merc.APPLY_HITROLL:
            # noinspection PyUnresolvedReferences
            self.hitroll += mod
        elif loc == merc.APPLY_DAMROLL:
            # noinspection PyUnresolvedReferences
            self.damroll += mod
        elif loc in [merc.APPLY_SAVING_ROD, merc.APPLY_SAVING_PETRI, merc.APPLY_SAVING_BREATH, merc.APPLY_SAVING_SPELL]:
            # noinspection PyUnresolvedReferences
            self.saving_throw += mod
        elif paf.location == merc.APPLY_POLY:
            self.polyaff.bits += mod
        else:
            comm.notify("affect_modify: unknown location {}".format(paf.location), merc.CONSOLE_ERROR)
            return

        # Check for weapon wielding.
        # Guard against recursion (for weapons with affects).
        # noinspection PyUnresolvedReferences
        wield = self.slots.right_hand
        # noinspection PyUnresolvedReferences
        if wield and wield.item_type == merc.ITEM_WEAPON and wield.get_weight() > const.str_app[self.stat(merc.STAT_STR)].wield:
            global depth
            if depth == 0:
                depth += 1
                handler_game.act("You drop $p.", self, wield, None, merc.TO_CHAR)
                handler_game.act("$n drops $p.", self, wield, None, merc.TO_ROOM)
                # noinspection PyUnresolvedReferences
                self.get(wield)
                # noinspection PyUnresolvedReferences
                self.in_room.put(wield)
                depth -= 1

    # Strip all affects of a given sn.
    def affect_strip(self, sn):
        for paf in self.affected[:]:
            if paf.type == sn:
                self.affect_remove(paf)
