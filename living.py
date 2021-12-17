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

import json
import time

import affects
import bit
import comm
import const
import environment
import equipment
import fight
import game_utils
import handler_ch
import handler_game
import immortal
import instance
import inventory
import merc
import object_creator
import physical
import state_checks
import type_bypass


class Grouping:
    def __init__(self):
        super().__init__()
        self.master = None
        self.leader = None
        self.followers = 0
        self.clan = ""
        self.lord = ""

    # It is very important that this be an equivalence relation:
    # (1) A ~ A
    # (2) if A ~ B then B ~ A
    # (3) if A ~ B  and B ~ C, then A ~ C
    def is_same_group(self, bch):
        ach = self
        if not ach or not bch:
            return False

        if ach.leader:
            ach = ach.leader
        if bch.leader:
            bch = bch.leader

        return ach == bch

    def stop_follower(self):
        if not self.master:
            comm.notify("stop_follower: null master", merc.CONSOLE_ERROR)
            return

        # noinspection PyUnresolvedReferences
        if self.is_affected(merc.AFF_CHARM):
            # noinspection PyUnresolvedReferences
            self.affected_by.rem_bit(merc.AFF_CHARM)
            # noinspection PyUnresolvedReferences
            self.affect_strip("charm person")

        # noinspection PyUnresolvedReferences
        if instance.characters[self.master].can_see(self) and self.in_room:
            handler_game.act("$n stops following you.", self, None, instance.characters[self.master], merc.TO_VICT)
            handler_game.act("You stop following $N.", self, None, instance.characters[self.master], merc.TO_CHAR)

        self.master = None
        self.leader = None


class BodyParts:
    def __init__(self):
        super().__init__()
        self.head = bit.Bit(flagset_name="blochead_flags")
        self.body = bit.Bit(flagset_name="blocbody_flags")
        self.arm_left = bit.Bit(flagset_name="blocarm_flags")
        self.arm_right = bit.Bit(flagset_name="blocarm_flags")
        self.leg_left = bit.Bit(flagset_name="blocleg_flags")
        self.leg_right = bit.Bit(flagset_name="blocleg_flags")
        self.bleeding = bit.Bit(flagset_name="blocbleed_flags")

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

    # JINPOINT - 11/30/2020 @ 1:03 PM - Must be a more pythonic way to handle this function.  Have seen fixes to large elif functions,
    #                                   but nothing that quite mathes this setup (multiple class variables).
    def reg_mend(self):
        ribs = 0
        body_table = [(merc.BROKEN_RIBS_1, 1), (merc.BROKEN_RIBS_2, 2), (merc.BROKEN_RIBS_4, 4), (merc.BROKEN_RIBS_8, 8),
                      (merc.BROKEN_RIBS_16, 16)]
        for (aa, bb) in body_table:
            if self.body.is_set(aa):
                ribs += bb

        teeth = 0
        body_table = [(merc.LOST_TOOTH_1, 1), (merc.LOST_TOOTH_2, 2), (merc.LOST_TOOTH_4, 4), (merc.LOST_TOOTH_8, 8),
                      (merc.LOST_TOOTH_16, 16)]
        for (aa, bb) in body_table:
            if self.head.is_set(aa):
                teeth += bb

        if ribs > 0:
            self.mend_broken_ribs(ribs)
        elif self.head.is_set(merc.LOST_EYE_L):
            self.mend_lost_eye(False)
        elif self.head.is_set(merc.LOST_EYE_R):
            self.mend_lost_eye(True)
        elif self.head.is_set(merc.LOST_EAR_L):
            self.mend_lost_ear(False)
        elif self.head.is_set(merc.LOST_EAR_R):
            self.mend_lost_ear(True)
        elif self.head.is_set(merc.LOST_NOSE):
            self.mend_lost_nose()
        elif teeth > 0:
            self.mend_missing_teeth(teeth)
        elif self.head.is_set(merc.BROKEN_NOSE):
            self.mend_broken_nose()
        elif self.head.is_set(merc.BROKEN_JAW):
            self.mend_broken_jaw()
        elif self.head.is_set(merc.BROKEN_SKULL):
            self.mend_broken_skull()
        elif self.body.is_set(merc.BROKEN_SPINE):
            self.mend_broken_spine()
        elif self.body.is_set(merc.BROKEN_NECK):
            self.mend_broken_neck()
        elif self.arm_left.is_set(merc.LOST_ARM):
            self.mend_lost_arm(right=False)
        elif self.arm_right.is_set(merc.LOST_ARM):
            self.mend_lost_arm(right=True)
        elif self.leg_left.is_set(merc.LOST_LEG):
            self.mend_lost_leg(False)
        elif self.leg_right.is_set(merc.LOST_LEG):
            self.mend_lost_leg(True)
        elif self.arm_left.is_set(merc.BROKEN_ARM):
            self.mend_broken_arm(right=False)
        elif self.arm_right.is_set(merc.BROKEN_ARM):
            self.mend_broken_arm(right=True)
        elif self.leg_left.is_set(merc.BROKEN_LEG):
            self.mend_broken_leg(False)
        elif self.leg_right.is_set(merc.BROKEN_LEG):
            self.mend_broken_leg(True)
        elif self.arm_left.is_set(merc.LOST_HAND):
            self.mend_lost_hand(right=False)
        elif self.arm_right.is_set(merc.LOST_HAND):
            self.mend_lost_hand(right=True)
        elif self.leg_left.is_set(merc.LOST_FOOT):
            self.mend_lost_foot(False)
        elif self.leg_right.is_set(merc.LOST_FOOT):
            self.mend_lost_foot(True)
        elif self.arm_left.is_set(merc.LOST_THUMB):
            self.mend_lost_finger_t(right=False)
        elif self.arm_left.is_set(merc.BROKEN_THUMB):
            self.mend_broken_finger_t(right=False)
        elif self.arm_left.is_set(merc.LOST_FINGER_I):
            self.mend_lost_finger_i(right=False)
        elif self.arm_left.is_set(merc.BROKEN_FINGER_I):
            self.mend_broken_finger_i(right=False)
        elif self.arm_left.is_set(merc.LOST_FINGER_M):
            self.mend_lost_finger_m(right=False)
        elif self.arm_left.is_set(merc.BROKEN_FINGER_M):
            self.mend_broken_finger_m(right=False)
        elif self.arm_left.is_set(merc.LOST_FINGER_R):
            self.mend_lost_finger_r(right=False)
        elif self.arm_left.is_set(merc.BROKEN_FINGER_R):
            self.mend_broken_finger_r(right=False)
        elif self.arm_left.is_set(merc.LOST_FINGER_L):
            self.mend_lost_finger_l(right=False)
        elif self.arm_left.is_set(merc.BROKEN_FINGER_L):
            self.mend_broken_finger_l(right=False)
        elif self.arm_right.is_set(merc.LOST_THUMB):
            self.mend_lost_finger_t(right=True)
        elif self.arm_right.is_set(merc.BROKEN_THUMB):
            self.mend_broken_finger_t(right=True)
        elif self.arm_right.is_set(merc.LOST_FINGER_I):
            self.mend_lost_finger_i(right=True)
        elif self.arm_right.is_set(merc.BROKEN_FINGER_I):
            self.mend_broken_finger_i(right=True)
        elif self.arm_right.is_set(merc.LOST_FINGER_M):
            self.mend_lost_finger_m(right=True)
        elif self.arm_right.is_set(merc.BROKEN_FINGER_M):
            self.mend_broken_finger_m(right=True)
        elif self.arm_right.is_set(merc.LOST_FINGER_R):
            self.mend_lost_finger_r(right=True)
        elif self.arm_right.is_set(merc.BROKEN_FINGER_R):
            self.mend_broken_finger_r(right=True)
        elif self.arm_right.is_set(merc.LOST_FINGER_L):
            self.mend_lost_finger_l(right=True)
        elif self.arm_right.is_set(merc.BROKEN_FINGER_L):
            self.mend_broken_finger_l(right=True)
        elif self.body.is_set(merc.CUT_THROAT):
            self.mend_cut_throat()
        else:
            comm.notify("reg_mend: bad body location found.", merc.CONSOLE_ERROR)

    def mend_broken_ribs(self, ribs):
        self.body.rem_bit(merc.BROKEN_RIBS_1)
        self.body.rem_bit(merc.BROKEN_RIBS_2)
        self.body.rem_bit(merc.BROKEN_RIBS_4)
        self.body.rem_bit(merc.BROKEN_RIBS_8)
        self.body.rem_bit(merc.BROKEN_RIBS_16)

        ribs -= 1

        if ribs >= 16:
            ribs -= 16
            self.body.set_bit(merc.BROKEN_RIBS_16)

        if ribs >= 8:
            ribs -= 8
            self.body.set_bit(merc.BROKEN_RIBS_8)

        if ribs >= 4:
            ribs -= 4
            self.body.set_bit(merc.BROKEN_RIBS_4)

        if ribs >= 2:
            ribs -= 2
            self.body.set_bit(merc.BROKEN_RIBS_2)

        if ribs >= 1:
            ribs -= 1
            self.body.set_bit(merc.BROKEN_RIBS_1)

        handler_game.act("One of your ribs snap back into place.", self, None, None, merc.TO_CHAR)
        handler_game.act("One of $n's ribs snap back into place.", self, None, None, merc.TO_ROOM)

    def mend_lost_eye(self, right):
        if right:
            handler_game.act("An eyeball appears in $n's right eye socket.", self, None, None, merc.TO_ROOM)
            handler_game.act("An eyeball appears in your right eye socket.", self, None, None, merc.TO_CHAR)
            self.head.rem_bit(merc.LOST_EYE_R)
        else:
            handler_game.act("An eyeball appears in $n's left eye socket.", self, None, None, merc.TO_ROOM)
            handler_game.act("An eyeball appears in your left eye socket.", self, None, None, merc.TO_CHAR)
            self.head.rem_bit(merc.LOST_EYE_L)

    def mend_lost_ear(self, right):
        if right:
            handler_game.act("An ear grows on the right side of $n's head.", self, None, None, merc.TO_ROOM)
            handler_game.act("An ear grows on the right side of your head.", self, None, None, merc.TO_CHAR)
            self.head.rem_bit(merc.LOST_EAR_R)
        else:
            handler_game.act("An ear grows on the left side of $n's head.", self, None, None, merc.TO_ROOM)
            handler_game.act("An ear grows on the left side of your head.", self, None, None, merc.TO_CHAR)
            self.head.rem_bit(merc.LOST_EAR_L)

    def mend_lost_nose(self):
        handler_game.act("A nose grows on the front of $n's face.", self, None, None, merc.TO_ROOM)
        handler_game.act("A nose grows on the front of your face.", self, None, None, merc.TO_CHAR)
        self.head.rem_bit(merc.LOST_NOSE)
        self.head.rem_bit(merc.BROKEN_NOSE)

    def mend_missing_teeth(self, teeth):
        self.head.rem_bit(merc.LOST_TOOTH_1)
        self.head.rem_bit(merc.LOST_TOOTH_2)
        self.head.rem_bit(merc.LOST_TOOTH_4)
        self.head.rem_bit(merc.LOST_TOOTH_8)
        self.head.rem_bit(merc.LOST_TOOTH_16)

        teeth -= 1

        if teeth >= 16:
            teeth -= 16
            self.head.set_bit(merc.LOST_TOOTH_16)

        if teeth >= 8:
            teeth -= 8
            self.head.set_bit(merc.LOST_TOOTH_8)

        if teeth >= 4:
            teeth -= 4
            self.head.set_bit(merc.LOST_TOOTH_4)

        if teeth >= 2:
            teeth -= 2
            self.head.set_bit(merc.LOST_TOOTH_2)

        if teeth >= 1:
            teeth -= 1
            self.head.set_bit(merc.LOST_TOOTH_1)

        handler_game.act("A missing tooth grows in your mouth.", self, None, None, merc.TO_CHAR)
        handler_game.act("A missing tooth grows in $n's mouth.", self, None, None, merc.TO_ROOM)

    def mend_broken_nose(self):
        handler_game.act("$n's nose snaps back into place.", self, None, None, merc.TO_ROOM)
        handler_game.act("Your nose snaps back into place.", self, None, None, merc.TO_CHAR)
        self.head.rem_bit(merc.BROKEN_NOSE)

    def mend_broken_jaw(self):
        handler_game.act("$n's jaw snaps back into place.", self, None, None, merc.TO_ROOM)
        handler_game.act("Your jaw snaps back into place.", self, None, None, merc.TO_CHAR)
        self.head.rem_bit(merc.BROKEN_JAW)

    def mend_broken_skull(self):
        handler_game.act("$n's skull knits itself back together.", self, None, None, merc.TO_ROOM)
        handler_game.act("Your skull knits itself back together.", self, None, None, merc.TO_CHAR)
        self.head.rem_bit(merc.BROKEN_SKULL)

    def mend_broken_spine(self):
        handler_game.act("$n's spine knits itself back together.", self, None, None, merc.TO_ROOM)
        handler_game.act("Your spine knits itself back together.", self, None, None, merc.TO_CHAR)
        self.body.rem_bit(merc.BROKEN_SPINE)

    def mend_broken_neck(self):
        handler_game.act("$n's neck snaps back into place.", self, None, None, merc.TO_ROOM)
        handler_game.act("Your neck snaps back into place.", self, None, None, merc.TO_CHAR)
        self.body.rem_bit(merc.BROKEN_NECK)

    def mend_lost_arm(self, right):
        if right:
            handler_game.act("An arm grows from the stump of $n's right shoulder.", self, None, None, merc.TO_ROOM)
            handler_game.act("An arm grows from the stump of your right shoulder.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.LOST_ARM)
            self.arm_right.rem_bit(merc.BROKEN_ARM)
            self.arm_right.set_bit(merc.LOST_HAND)
        else:
            handler_game.act("An arm grows from the stump of $n's left shoulder.", self, None, None, merc.TO_ROOM)
            handler_game.act("An arm grows from the stump of your left shoulder.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.LOST_ARM)
            self.arm_left.rem_bit(merc.BROKEN_ARM)
            self.arm_left.set_bit(merc.LOST_HAND)

    def mend_lost_leg(self, right):
        if right:
            handler_game.act("A leg grows from the stump of $n's right hip.", self, None, None, merc.TO_ROOM)
            handler_game.act("A leg grows from the stump of your right hip.", self, None, None, merc.TO_CHAR)
            self.leg_right.rem_bit(merc.LOST_LEG)
            self.leg_right.rem_bit(merc.BROKEN_LEG)
            self.leg_right.set_bit(merc.LOST_FOOT)
        else:
            handler_game.act("A leg grows from the stump of $n's left hip.", self, None, None, merc.TO_ROOM)
            handler_game.act("A leg grows from the stump of your left hip.", self, None, None, merc.TO_CHAR)
            self.leg_left.rem_bit(merc.LOST_LEG)
            self.leg_left.rem_bit(merc.BROKEN_LEG)
            self.leg_left.set_bit(merc.LOST_FOOT)

    def mend_broken_arm(self, right):
        if right:
            handler_game.act("$n's right arm snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your right arm snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.BROKEN_ARM)
        else:
            handler_game.act("$n's left arm snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your left arm snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.BROKEN_ARM)

    def mend_broken_leg(self, right):
        if right:
            handler_game.act("$n's right leg snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your right leg snaps back into place.", self, None, None, merc.TO_CHAR)
            self.leg_right.rem_bit(merc.BROKEN_LEG)
        else:
            handler_game.act("$n's left leg snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your left leg snaps back into place.", self, None, None, merc.TO_CHAR)
            self.leg_left.rem_bit(merc.BROKEN_LEG)

    def mend_lost_hand(self, right):
        if right:
            handler_game.act("A hand grows from the stump of $n's right wrist.", self, None, None, merc.TO_ROOM)
            handler_game.act("A hand grows from the stump of your right wrist.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.LOST_HAND)
            self.arm_right.set_bit(merc.LOST_THUMB)
            self.arm_right.set_bit(merc.LOST_FINGER_I)
            self.arm_right.set_bit(merc.LOST_FINGER_M)
            self.arm_right.set_bit(merc.LOST_FINGER_R)
            self.arm_right.set_bit(merc.LOST_FINGER_L)
        else:
            handler_game.act("A hand grows from the stump of $n's left wrist.", self, None, None, merc.TO_ROOM)
            handler_game.act("A hand grows from the stump of your left wrist.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.LOST_HAND)
            self.arm_left.set_bit(merc.LOST_THUMB)
            self.arm_left.set_bit(merc.LOST_FINGER_I)
            self.arm_left.set_bit(merc.LOST_FINGER_M)
            self.arm_left.set_bit(merc.LOST_FINGER_R)
            self.arm_left.set_bit(merc.LOST_FINGER_L)

    def mend_lost_foot(self, right):
        if right:
            handler_game.act("A foot grows from the stump of $n's right ankle.", self, None, None, merc.TO_ROOM)
            handler_game.act("A foot grows from the stump of your right ankle.", self, None, None, merc.TO_CHAR)
            self.leg_right.rem_bit(merc.LOST_FOOT)
        else:
            handler_game.act("A foot grows from the stump of $n's left ankle.", self, None, None, merc.TO_ROOM)
            handler_game.act("A foot grows from the stump of your left ankle.", self, None, None, merc.TO_CHAR)
            self.leg_left.rem_bit(merc.LOST_FOOT)

    def mend_lost_finger_t(self, right):
        if right:
            handler_game.act("A thumb slides out of $n's right hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A thumb slides out of your right hand.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.LOST_THUMB)
            self.arm_right.rem_bit(merc.BROKEN_THUMB)
        else:
            handler_game.act("A thumb slides out of $n's left hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A thumb slides out of your left hand.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.LOST_THUMB)
            self.arm_left.rem_bit(merc.BROKEN_THUMB)

    def mend_broken_finger_t(self, right):
        if right:
            handler_game.act("$n's right thumb snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your right thumb snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.BROKEN_THUMB)
        else:
            handler_game.act("$n's left thumb snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your left thumb snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.BROKEN_THUMB)

    def mend_lost_finger_i(self, right):
        if right:
            handler_game.act("An index finger slides out of $n's right hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("An index finger slides out of your right hand.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.LOST_FINGER_I)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_I)
        else:
            handler_game.act("An index finger slides out of $n's left hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("An index finger slides out of your left hand.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.LOST_FINGER_I)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_I)

    def mend_broken_finger_i(self, right):
        if right:
            handler_game.act("$n's right index finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your right index finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_I)
        else:
            handler_game.act("$n's left index finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your left index finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_I)

    def mend_lost_finger_m(self, right):
        if right:
            handler_game.act("A middle finger slides out of $n's right hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A middle finger slides out of your right hand.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.LOST_FINGER_M)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_M)
        else:
            handler_game.act("A middle finger slides out of $n's left hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A middle finger slides out of your left hand.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.LOST_FINGER_M)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_M)

    def mend_broken_finger_m(self, right):
        if right:
            handler_game.act("$n's right middle finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your right middle finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_M)
        else:
            handler_game.act("$n's left middle finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your left middle finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_M)

    def mend_lost_finger_r(self, right):
        if right:
            handler_game.act("A ring finger slides out of $n's right hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A ring finger slides out of your right hand.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.LOST_FINGER_R)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_R)
        else:
            handler_game.act("A ring finger slides out of $n's left hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A ring finger slides out of your left hand.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.LOST_FINGER_R)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_R)

    def mend_broken_finger_r(self, right):
        if right:
            handler_game.act("$n's right ring finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your right ring finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_R)
        else:
            handler_game.act("$n's left ring finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your left ring finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_R)

    def mend_lost_finger_l(self, right):
        if right:
            handler_game.act("A little finger slides out of $n's right hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A little finger slides out of your right hand.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.LOST_FINGER_L)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_L)
        else:
            handler_game.act("A little finger slides out of $n's left hand.", self, None, None, merc.TO_ROOM)
            handler_game.act("A little finger slides out of your left hand.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.LOST_FINGER_L)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_L)

    def mend_broken_finger_l(self, right):
        if right:
            handler_game.act("$n's right little finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your right little finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_right.rem_bit(merc.BROKEN_FINGER_L)
        else:
            handler_game.act("$n's left little finger snaps back into place.", self, None, None, merc.TO_ROOM)
            handler_game.act("Your left little finger snaps back into place.", self, None, None, merc.TO_CHAR)
            self.arm_left.rem_bit(merc.BROKEN_FINGER_L)

    def mend_cut_throat(self):
        if self.bleeding.is_set(merc.BLEEDING_THROAT):
            return

        handler_game.act("The wound in $n's throat closes up.", self, None, None, merc.TO_ROOM)
        handler_game.act("The wound in your throat closes up.", self, None, None, merc.TO_CHAR)
        self.body.rem_bit(merc.CUT_THROAT)

    def is_ok_to_wear(self, slot, wolf_ok, success):
        if slot == "head":
            if self.head.is_set(merc.LOST_HEAD):
                return False
        elif slot == "face":
            if self.head.is_set(merc.LOST_HEAD):
                return False
        elif slot == "left_hand":
            # noinspection PyUnresolvedReferences
            if not self.is_npc() and self.special.is_set(merc.SPC_WOLFMAN) and not wolf_ok:
                return False

            part_list = [merc.LOST_ARM, merc.BROKEN_ARM, merc.LOST_HAND, merc.BROKEN_THUMB, merc.LOST_THUMB]
            for item in part_list:
                if self.arm_left.is_set(item):
                    return False

            count = 0
            part_list = [merc.LOST_FINGER_I, merc.LOST_FINGER_M, merc.LOST_FINGER_R, merc.LOST_FINGER_L, merc.BROKEN_FINGER_I,
                         merc.BROKEN_FINGER_M, merc.BROKEN_FINGER_R, merc.BROKEN_FINGER_L]
            for item in part_list:
                if self.arm_left.is_set(item):
                    count += 1

            if count > 2:
                return False
        elif slot == "right_hand":
            # noinspection PyUnresolvedReferences
            if not self.is_npc() and self.special.is_set(merc.SPC_WOLFMAN) and not wolf_ok:
                return False

            part_list = [merc.LOST_ARM, merc.BROKEN_ARM, merc.LOST_HAND, merc.BROKEN_THUMB, merc.LOST_THUMB]
            for item in part_list:
                if self.arm_right.is_set(item):
                    return False

            count = 0
            part_list = [merc.LOST_FINGER_I, merc.LOST_FINGER_M, merc.LOST_FINGER_R, merc.LOST_FINGER_L, merc.BROKEN_FINGER_I,
                         merc.BROKEN_FINGER_M, merc.BROKEN_FINGER_R, merc.BROKEN_FINGER_L]
            for item in part_list:
                if self.arm_right.is_set(item):
                    count += 1

            if count > 2:
                return False
        elif slot == "left_wrist":
            if self.arm_left.is_set(merc.LOST_ARM) or self.arm_left.is_set(merc.LOST_HAND):
                return False
        elif slot == "right_wrist":
            if self.arm_right.is_set(merc.LOST_ARM) or self.arm_right.is_set(merc.LOST_HAND):
                return False
        elif slot == "left_finger":
            part_list = [merc.LOST_ARM, merc.LOST_HAND, merc.LOST_FINGER_R]
            for item in part_list:
                if self.arm_left.is_set(item):
                    return False
        elif slot == "right_finger":
            part_list = [merc.LOST_ARM, merc.LOST_HAND, merc.LOST_FINGER_R]
            for item in part_list:
                if self.arm_right.is_set(item):
                    return False
        elif slot == "arms":
            if self.arm_left.is_set(merc.LOST_ARM) and self.arm_right.is_set(merc.LOST_ARM):
                return False
        elif slot == "hands":
            if self.arm_left.is_set(merc.LOST_ARM) and self.arm_right.is_set(merc.LOST_ARM):
                return False

            if self.arm_left.is_set(merc.LOST_HAND) or self.arm_right.is_set(merc.LOST_HAND):
                return False
        elif slot == "legs":
            if self.leg_left.is_set(merc.LOST_LEG) and self.leg_right.is_set(merc.LOST_LEG):
                return False
        elif slot == "feet":
            if self.leg_left.is_set(merc.LOST_LEG) and self.leg_right.is_set(merc.LOST_LEG):
                return False

            if self.leg_left.is_set(merc.LOST_FOOT) or self.leg_right.is_set(merc.LOST_FOOT):
                return False

        return success


class Fight:
    def __init__(self):
        super().__init__()
        self._fighting = None
        self.hunting = ""
        self._hitroll = 0
        self._damroll = 0
        self._armor = 100
        self.wimpy = 0
        self.saving_throw = 0
        self.timer = 0
        self.wait = 0
        self.mkill = 0
        self.mdeath = 0
        self.pkill = 0
        self.pdeath = 0
        self.race = 0
        self.damcap = [1000, 0]
        self.wpn = [0] * merc.MAX_WPN
        self.spl = [0] * merc.MAX_MAGIC
        self.stance = [0] * merc.MAX_STANCE
        self.cmbt = [0] * 8

    def send(self, pstr):
        pass

    @property
    def hitroll(self):
        from const import str_app
        # noinspection PyUnresolvedReferences
        value = self._hitroll + str_app[self.stat(merc.STAT_STR)].tohit

        # noinspection PyUnresolvedReferences
        if not self.is_npc():
            # noinspection PyUnresolvedReferences
            if self.is_vampire() and self.powers[merc.UNI_RAGE] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.UNI_RAGE]
            # noinspection PyUnresolvedReferences
            elif self.special.is_set(merc.SPC_WOLFMAN) and self.powers[merc.UNI_RAGE] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.UNI_RAGE]
            elif self.is_demon() and self.powers[merc.DEMON_POWER] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.DEMON_POWER] * self.powers[merc.DEMON_POWER]
            elif self.special.is_set(merc.SPC_CHAMPION) and self.powers[merc.DEMON_POWER] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.DEMON_POWER] * self.powers[merc.DEMON_POWER]
            elif self.is_highlander() and self.itemaff.is_set(merc.ITEMA_HIGHLANDER):
                # noinspection PyUnresolvedReferences
                wpn = self.powers[merc.HPOWER_WPNSKILL]
                if wpn in [1, 3]:
                    if self.wpn[wpn] >= 500:
                        value += 500
                    else:
                        value += self.wpn[wpn]
        return value

    @hitroll.setter
    def hitroll(self, value):
        self._hitroll = value

    @property
    def damroll(self):
        from const import str_app
        # noinspection PyUnresolvedReferences
        value = self._damroll + str_app[self.stat(merc.STAT_STR)].todam

        # noinspection PyUnresolvedReferences
        if not self.is_npc():
            # noinspection PyUnresolvedReferences
            if self.is_vampire() and self.powers[merc.UNI_RAGE] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.UNI_RAGE]
            # noinspection PyUnresolvedReferences
            elif self.special.is_set(merc.SPC_WOLFMAN) and self.powers[merc.UNI_RAGE] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.UNI_RAGE]
            # noinspection PyUnresolvedReferences
            elif self.is_demon() and self.powers[merc.DEMON_POWER] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.DEMON_POWER] * self.powers[merc.DEMON_POWER]
            # noinspection PyUnresolvedReferences
            elif self.special.is_set(merc.SPC_CHAMPION) and self.powers[merc.DEMON_POWER] > 0:
                # noinspection PyUnresolvedReferences
                value += self.powers[merc.DEMON_POWER] * self.powers[merc.DEMON_POWER]
            # noinspection PyUnresolvedReferences
            elif self.is_highlander() and self.itemaff.is_set(merc.ITEMA_HIGHLANDER):
                # noinspection PyUnresolvedReferences
                wpn = self.powers[merc.HPOWER_WPNSKILL]
                if self.wpn[wpn] >= 500:
                    value += 500
                else:
                    value += self.wpn[wpn]
        return value

    @damroll.setter
    def damroll(self, value):
        self._damroll = value

    @property
    def armor(self):
        from const import dex_app
        # noinspection PyUnresolvedReferences
        value = self._armor + (dex_app[self.stat(merc.STAT_DEX)].defensive if self.is_awake() else 0)

        # noinspection PyUnresolvedReferences
        if not self.is_npc():
            # noinspection PyUnresolvedReferences
            if self.is_highlander() and self.itemaff.is_set(merc.ITEMA_HIGHLANDER):
                # noinspection PyUnresolvedReferences
                wpn = self.powers[merc.HPOWER_WPNSKILL]
                if wpn in [1, 3]:
                    value += self.wpn[wpn]
        return value

    @armor.setter
    def armor(self, value):
        self._armor = value

    @property
    def fighting(self):
        return instance.characters.get(self._fighting, None)

    @fighting.setter
    def fighting(self, value):
        if type(value) is int:
            value = instance.characters.get(value, None)  # Ensure fighting exists.
        if value and not isinstance(value, Fight):
            # noinspection PyUnresolvedReferences
            comm.notify("Instance fighting non combat. {} fighting {}".format(self.name, value.name), merc.CONSOLE_ERROR)
            return

        if value:
            # noinspection PyUnresolvedReferences
            value = value.instance_id

        if type(value) is None:
            value = None

        self._fighting = value  # None or instance_id

    def wait_state(self, npulse):
        self.wait = max(self.wait, npulse)

    def can_pk(self):
        return self.trust in merc.irange(merc.LEVEL_AVATAR, merc.LEVEL_MAGE)

    def fightaction(self, victim, actype, dtype, wpntype):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or actype not in merc.irange(1, 20) or not victim:
            return

        if actype == 1:  # Trip
            if game_utils.number_percent() <= self.wpn[merc.WPN_UNARMED]:
                fight.trip(self, victim)
        elif actype == 2 and game_utils.number_percent() < 75:
            # noinspection PyUnresolvedReferences
            self.cmd_kick("")
        elif actype == 7:
            if game_utils.number_percent() < 25:
                fight.disarm(self, victim)
        elif actype == 9:
            handler_game.act("You kick a spray of dirt into $N's face.", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n kicks a spray of dirt into your face.", self, None, victim, merc.TO_VICT)
            handler_game.act("$n kicks a spray of dirt into $N's face.", self, None, victim, merc.TO_NOTVICT)

            if victim.is_affected(merc.AFF_BLIND) or game_utils.number_percent() < 25:
                return

            aff = handler_game.AffectData(type="blindness", location=merc.APPLY_HITROLL, modifier=-4, duration=1, bitvector=merc.AFF_BLIND)
            victim.affect_add(aff)
            handler_game.act("$n is blinded!", victim, None, None, merc.TO_ROOM)
            victim.send("You are blinded!\n")
        elif actype == 12:
            handler_game.act("You gouge your fingers into $N's eyes.", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n gouges $s fingers into your eyes.", self, None, victim, merc.TO_VICT)
            handler_game.act("$n gouges $s fingers into $N's eyes.", self, None, victim, merc.TO_NOTVICT)

            if victim.is_affected(merc.AFF_BLIND) or game_utils.number_percent() < 75:
                fight.one_hit(self, victim, dtype, wpntype)
            else:
                aff = handler_game.AffectData(type="blindness", location=merc.APPLY_HITROLL, modifier=-4, duration=1, bitvector=merc.AFF_BLIND)
                victim.affect_add(aff)
                handler_game.act("$n is blinded!", victim, None, None, merc.TO_ROOM)
                victim.send("You are blinded!\n")
        elif actype == 14:
            if victim.move > 0:
                handler_game.act("You leap in the air and stamp on $N's feet.", self, None, victim, merc.TO_CHAR)
                handler_game.act("$n leaps in the air and stamps on your feet.", self, None, victim, merc.TO_VICT)
                handler_game.act("$n leaps in the air and stamps on $N's feet.", self, None, victim, merc.TO_NOTVICT)
                victim.move -= game_utils.number_range(25, 50)
                if victim.move < 0:
                    victim.move = 0

    def critical_hit(self, victim, dt, dam):
        critical = 0

        dtype = dt - 1000
        if dtype not in merc.irange(0, 12):
            return

        # noinspection PyUnresolvedReferences
        if self.is_npc():
            # noinspection PyUnresolvedReferences
            critical += (self.level + 1) // 5
        else:
            critical += (self.wpn[dtype] + 1) // 10

        if victim.is_npc():
            critical -= (victim.level + 1) // 5
        else:
            dtype = merc.TYPE_HIT
            item = victim.get_eq("right_hand")
            if item and item.item_type == merc.ITEM_WEAPON:
                dtype += item.value[3]

            wpn1 = dtype - 1000
            if wpn1 not in merc.irange(0, 12):
                wpn1 = 0

            dtype = merc.TYPE_HIT
            item = victim.get_eq("left_hand")
            if item and item.item_type == merc.ITEM_WEAPON:
                dtype += item.value[3]

            wpn2 = dtype - 1000
            if wpn2 not in merc.irange(0, 12):
                wpn2 = 0

            if victim.wpn[wpn1] > victim.wpn[wpn2]:
                critical -= (victim.wpn[wpn1] + 1) // 10
            else:
                critical -= (victim.wpn[wpn2] + 1) // 10

            critical = state_checks.urange(1, critical, 5)
            if game_utils.number_percent() > critical:
                return

        critical = game_utils.number_range(1, 23)
        if critical == 1:
            if victim.head.is_set(merc.LOST_EYE_L) and victim.head.is_set(merc.LOST_EYE_R):
                return

            damaged = victim.get_eq("face")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevents you from loosing an eye.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevents $n from loosing an eye.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= (dam - damaged.toughness)
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.head.is_set(merc.LOST_EYE_L) and game_utils.number_percent() < 50:
                victim.head.set_bit(merc.LOST_EYE_L)
            elif not victim.head.is_set(merc.LOST_EYE_R):
                victim.head.set_bit(merc.LOST_EYE_R)
            elif not victim.head.is_set(merc.LOST_EYE_L):
                victim.head.set_bit(merc.LOST_EYE_L)
            else:
                return

            handler_game.act("Your skillful blow takes out $N's eye!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow takes out $N's eye!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow takes out your eye!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "eyeball")
        elif critical == 2:
            if victim.head.is_set(merc.LOST_EAR_L) and victim.head.is_set(merc.LOST_EAR_R):
                return

            damaged = victim.get_eq("head")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevents you from loosing an ear.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevents $n from loosing an ear.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.head.is_set(merc.LOST_EAR_L) and game_utils.number_percent() < 50:
                victim.head.set_bit(merc.LOST_EAR_L)
            elif not victim.head.is_set(merc.LOST_EAR_R):
                victim.head.set_bit(merc.LOST_EAR_R)
            elif not victim.head.is_set(merc.LOST_EAR_L):
                victim.head.set_bit(merc.LOST_EAR_L)
            else:
                return

            handler_game.act("Your skillful blow cuts off $N's ear!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's ear!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your ear!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "ear")
        elif critical == 3:
            if victim.head.is_set(merc.LOST_NOSE):
                return

            damaged = victim.get_eq("face")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevents you from loosing your nose.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevents $n from loosing $s nose.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            victim.head.set_bit(merc.LOST_NOSE)
            handler_game.act("Your skillful blow cuts off $N's nose!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's nose!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your nose!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "nose")
        elif critical == 4:
            if victim.head.is_set(merc.LOST_NOSE) or victim.head.is_set(merc.BROKEN_NOSE):
                return

            damaged = victim.get_eq("face")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevents you from breaking your nose.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevents $n from breaking $s nose.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.head.is_set(merc.LOST_NOSE) and not victim.head.is_set(merc.BROKEN_NOSE):
                victim.head.set_bit(merc.BROKEN_NOSE)
            else:
                return

            handler_game.act("Your skillful blow breaks $N's nose!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow breaks $N's nose!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow breaks your nose!", self, None, victim, merc.TO_VICT)
        elif critical == 5:
            if victim.head.is_set(merc.BROKEN_JAW):
                return

            damaged = victim.get_eq("face")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevents you from breaking your jaw.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevents $n from breaking $s jaw.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.head.is_set(merc.BROKEN_JAW):
                victim.head.set_bit(merc.BROKEN_JAW)
            else:
                return

            handler_game.act("Your skillful blow breaks $N's jaw!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow breaks $N's jaw!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow breaks your jaw!", self, None, victim, merc.TO_VICT)
        elif critical == 6:
            if victim.arm_left.is_set(merc.LOST_ARM):
                return

            damaged = victim.get_eq("arms")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your left arm.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s left arm.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.arm_left.is_set(merc.LOST_ARM):
                victim.arm_left.set_bit(merc.LOST_ARM)
            else:
                return

            victim.bleeding.set_bit(merc.BLEEDING_ARM_L)
            victim.bleeding.rem_bit(merc.BLEEDING_HAND_L)
            handler_game.act("Your skillful blow cuts off $N's left arm!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's left arm!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your left arm!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "arm")

            if victim.arm_left.is_set(merc.LOST_ARM) and victim.arm_right.is_set(merc.LOST_ARM):
                item = victim.get_eq("arms")
                if item:
                    victim.take_item(item)

            item = victim.get_eq("left_hand")
            if item:
                victim.take_item(item)

            item = victim.get_eq("hands")
            if item:
                victim.take_item(item)

            item = victim.get_eq("left_wrist")
            if item:
                victim.take_item(item)

            item = victim.get_eq("left_finger")
            if item:
                victim.take_item(item)
        elif critical == 7:
            if victim.arm_right.is_set(merc.LOST_ARM):
                return

            damaged = victim.get_eq("arms")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your right arm.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s right arm.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.arm_right.is_set(merc.LOST_ARM):
                victim.arm_right.set_bit(merc.LOST_ARM)
            else:
                return

            victim.bleeding.set_bit(merc.BLEEDING_ARM_R)
            victim.bleeding.rem_bit(merc.BLEEDING_HAND_R)
            handler_game.act("Your skillful blow cuts off $N's right arm!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's right arm!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your right arm!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "arm")

            if victim.arm_left.is_set(merc.LOST_ARM) and victim.arm_right.is_set(merc.LOST_ARM):
                item = victim.get_eq("arms")
                if item:
                    victim.take_item(item)

            item = victim.get_eq("right_hand")
            if item:
                victim.take_item(item)

            item = victim.get_eq("hands")
            if item:
                victim.take_item(item)

            item = victim.get_eq("right_wrist")
            if item:
                victim.take_item(item)

            item = victim.get_eq("right_finger")
            if item:
                victim.take_item(item)
        elif critical == 8:
            if victim.arm_left.is_set(merc.LOST_ARM) or victim.arm_left.is_set(merc.BROKEN_ARM):
                return

            damaged = victim.get_eq("arms")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from breaking your left arm.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from breaking $s left arm.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.arm_left.is_set(merc.BROKEN_ARM) and not victim.arm_left.is_set(merc.LOST_ARM):
                victim.arm_left.set_bit(merc.BROKEN_ARM)
            else:
                return

            handler_game.act("Your skillful blow breaks $N's left arm!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow breaks $N's left arm!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow breaks your left arm!", self, None, victim, merc.TO_VICT)

            item = victim.get_eq("left_hand")
            if item:
                victim.take_item(item)
        elif critical == 9:
            if victim.arm_right.is_set(merc.LOST_ARM) or victim.arm_right.is_set(merc.BROKEN_ARM):
                return

            damaged = victim.get_eq("arms")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from breaking your right arm.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from breaking $s right arm.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.arm_right.is_set(merc.BROKEN_ARM) and not victim.arm_right.is_set(merc.LOST_ARM):
                victim.arm_right.set_bit(merc.BROKEN_ARM)
            else:
                return

            handler_game.act("Your skillful blow breaks $N's right arm!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow breaks $N's right arm!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow breaks your right arm!", self, None, victim, merc.TO_VICT)

            item = victim.get_eq("right_hand")
            if item:
                victim.take_item(item)
        elif critical == 10:
            if victim.arm_left.is_set(merc.LOST_HAND) or victim.arm_left.is_set(merc.LOST_ARM):
                return

            damaged = victim.get_eq("hands")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your left hand.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s left hand.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.arm_left.is_set(merc.LOST_HAND) and not victim.arm_left.is_set(merc.LOST_ARM):
                victim.arm_left.set_bit(merc.LOST_HAND)
            else:
                return

            victim.bleeding.rem_bit(merc.BLEEDING_ARM_L)
            victim.bleeding.set_bit(merc.BLEEDING_HAND_L)
            handler_game.act("Your skillful blow cuts off $N's left hand!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's left hand!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your left hand!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "hand")

            item = victim.get_eq("left_hand")
            if item:
                victim.take_item(item)

            item = victim.get_eq("hands")
            if item:
                victim.take_item(item)

            item = victim.get_eq("left_wrist")
            if item:
                victim.take_item(item)

            item = victim.get_eq("left_finger")
            if item:
                victim.take_item(item)
        elif critical == 11:
            if victim.arm_right.is_set(merc.LOST_HAND) or victim.arm_right.is_set(merc.LOST_ARM):
                return

            damaged = victim.get_eq("hands")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your right hand.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s right hand.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.arm_right.is_set(merc.LOST_HAND) and not victim.arm_right.is_set(merc.LOST_ARM):
                victim.arm_right.set_bit(merc.LOST_HAND)
            else:
                return

            victim.arm_right.rem_bit(merc.BLEEDING_ARM_R)
            victim.arm_right.set_bit(merc.BLEEDING_HAND_R)
            handler_game.act("Your skillful blow cuts off $N's right hand!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's right hand!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your right hand!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "hand")

            item = victim.get_eq("left_hand")
            if item:
                victim.take_item(item)

            item = victim.get_eq("hands")
            if item:
                victim.take_item(item)

            item = victim.get_eq("left_wrist")
            if item:
                victim.take_item(item)

            item = victim.get_eq("left_finger")
            if item:
                victim.take_item(item)
        elif critical == 12:
            if victim.arm_left.is_set(merc.LOST_ARM) or victim.arm_left.is_set(merc.LOST_HAND):
                return

            if victim.arm_left.is_set(merc.LOST_THUMB) and victim.arm_left.is_set(merc.LOST_FINGER_I) and victim.arm_left.is_set(merc.LOST_FINGER_M) and \
                    victim.arm_left.is_set(merc.LOST_FINGER_R) and victim.arm_left.is_set(merc.LOST_FINGER_L):
                return

            damaged = victim.get_eq("hands")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing some fingers from your left hand.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing some fingers from $s left hand.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            count1 = 0
            count2 = 0

            if not victim.arm_left.is_set(merc.LOST_THUMB) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.LOST_THUMB)
                count2 += 1
                object_creator.make_part(victim, "thumb")

            if not victim.arm_left.is_set(merc.LOST_FINGER_I) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.LOST_FINGER_I)
                count1 += 1
                object_creator.make_part(victim, "index")

            if not victim.arm_left.is_set(merc.LOST_FINGER_M) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.LOST_FINGER_M)
                count1 += 1
                object_creator.make_part(victim, "middle")

            if not victim.arm_left.is_set(merc.LOST_FINGER_R) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.LOST_FINGER_R)
                count1 += 1
                object_creator.make_part(victim, "ring")

                item = victim.get_eq("left_finger")
                if item:
                    victim.take_item(item)

            if not victim.arm_left.is_set(merc.LOST_FINGER_L) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.LOST_FINGER_L)
                count1 += 1
                object_creator.make_part(victim, "little")

            buf2 = "finger{}".format("" if count1 == 1 else "s")
            if count1 > 0 and count2 > 0:
                handler_game.act("Your skillful blow cuts off {} {} and the thumb from $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow cuts off {} {} and the thumb from $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow cuts off {} {} and the thumb from your left hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("left_hand")
                if item:
                    victim.take_item(item)
            elif count1 > 0:
                handler_game.act("Your skillful blow cuts off {} {} from $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow cuts off {} {} from $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow cuts off {} {} from your left hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("left_hand")
                if item:
                    victim.take_item(item)
            elif count2 > 0:
                handler_game.act("Your skillful blow cuts off the thumb from $N's left hand.", self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow cuts off the thumb from $N's left hand.", self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow cuts off the thumb from your left hand.", self, None, victim, merc.TO_VICT)

                item = victim.get_eq("left_hand")
                if item:
                    victim.take_item(item)
        elif critical == 13:
            if victim.arm_left.is_set(merc.LOST_ARM) or victim.arm_left.is_set(merc.LOST_HAND):
                return

            if (victim.arm_left.is_set(merc.LOST_THUMB) or victim.arm_left.is_set(merc.BROKEN_THUMB)) and \
                    (victim.arm_left.is_set(merc.LOST_FINGER_I) or victim.arm_left.is_set(merc.BROKEN_FINGER_I)) and \
                    (victim.arm_left.is_set(merc.LOST_FINGER_M) or victim.arm_left.is_set(merc.BROKEN_FINGER_M)) and \
                    (victim.arm_left.is_set(merc.LOST_FINGER_R) or victim.arm_left.is_set(merc.BROKEN_FINGER_R)) and \
                    (victim.arm_left.is_set(merc.LOST_FINGER_L) or victim.arm_left.is_set(merc.BROKEN_FINGER_L)):
                return

            damaged = victim.get_eq("hands")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from breaking some fingers on your left hand.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from breaking some fingers on $s left hand.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            count1 = 0
            count2 = 0

            if not victim.arm_left.is_set(merc.BROKEN_THUMB) and not victim.arm_left.is_set(merc.LOST_THUMB) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.BROKEN_THUMB)
                count2 += 1

            if not victim.arm_left.is_set(merc.BROKEN_FINGER_I) and not victim.arm_left.is_set(merc.LOST_FINGER_I) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.BROKEN_FINGER_I)
                count1 += 1

            if not victim.arm_left.is_set(merc.BROKEN_FINGER_M) and not victim.arm_left.is_set(merc.LOST_FINGER_M) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.BROKEN_FINGER_M)
                count1 += 1

            if not victim.arm_left.is_set(merc.BROKEN_FINGER_R) and not victim.arm_left.is_set(merc.LOST_FINGER_R) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.BROKEN_FINGER_R)
                count1 += 1

            if not victim.arm_left.is_set(merc.BROKEN_FINGER_L) and not victim.arm_left.is_set(merc.LOST_FINGER_L) and game_utils.number_percent() < 25:
                victim.arm_left.set_bit(merc.BROKEN_FINGER_L)
                count1 += 1

            buf2 = "finger{}".format("" if count1 == 1 else "s")
            if count1 > 0 and count2 > 0:
                handler_game.act("Your skillful breaks %d %s and the thumb on $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow breaks %d %s and the thumb on $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow breaks %d %s and the thumb on your left hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("left_hand")
                if item:
                    victim.take_item(item)
            elif count1 > 0:
                handler_game.act("Your skillful blow breaks %d %s on $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow breaks %d %s on $N's left hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow breaks %d %s on your left hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("left_hand")
                if item:
                    victim.take_item(item)
            elif count2 > 0:
                handler_game.act("Your skillful blow breaks the thumb on $N's left hand.", self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow breaks the thumb on $N's left hand.", self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow breaks the thumb on your left hand.", self, None, victim, merc.TO_VICT)

                item = victim.get_eq("left_hand")
                if item:
                    victim.take_item(item)
        elif critical == 14:
            if victim.arm_right.is_set(merc.LOST_ARM) or victim.arm_right.is_set(merc.LOST_HAND):
                return

            if victim.arm_right.is_set(merc.LOST_THUMB) and victim.arm_right.is_set(merc.LOST_FINGER_I) and victim.arm_right.is_set(merc.LOST_FINGER_M) and \
                    victim.arm_right.is_set(merc.LOST_FINGER_R) and victim.arm_right.is_set(merc.LOST_FINGER_L):
                return

            damaged = victim.get_eq("hands")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing some fingers from your right hand.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing some fingers from $s right hand.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            count1 = 0
            count2 = 0

            if not victim.arm_right.is_set(merc.LOST_THUMB) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.LOST_THUMB)
                count2 += 1
                object_creator.make_part(victim, "thumb")

            if not victim.arm_right.is_set(merc.LOST_FINGER_I) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.LOST_FINGER_I)
                count1 += 1
                object_creator.make_part(victim, "index")

            if not victim.arm_right.is_set(merc.LOST_FINGER_M) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.LOST_FINGER_M)
                count1 += 1
                object_creator.make_part(victim, "middle")

            if not victim.arm_right.is_set(merc.LOST_FINGER_R) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.LOST_FINGER_R)
                count1 += 1
                object_creator.make_part(victim, "ring")

                item = victim.get_eq("right_finger")
                if item:
                    victim.take_item(item)

            if not victim.arm_right.is_set(merc.LOST_FINGER_L) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.LOST_FINGER_L)
                count1 += 1
                object_creator.make_part(victim, "little")

            buf2 = "finger{}".format("" if count1 == 1 else "s")
            if count1 > 0 and count2 > 0:
                handler_game.act("Your skillful blow cuts off {} {} and the thumb from $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow cuts off {} {} and the thumb from $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow cuts off {} {} and the thumb from your right hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("right_hand")
                if item:
                    victim.take_item(item)
            elif count1 > 0:
                handler_game.act("Your skillful blow cuts off {} {} from $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow cuts off {} {} from $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow cuts off {} {} from your right hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("right_hand")
                if item:
                    victim.take_item(item)
            elif count2 > 0:
                handler_game.act("Your skillful blow cuts off the thumb from $N's right hand.", self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow cuts off the thumb from $N's right hand.", self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow cuts off the thumb from your right hand.", self, None, victim, merc.TO_VICT)

                item = victim.get_eq("right_hand")
                if item:
                    victim.take_item(item)
        elif critical == 15:
            if victim.arm_right.is_set(merc.LOST_ARM) or victim.arm_right.is_set(merc.LOST_HAND):
                return

            if (victim.arm_right.is_set(merc.LOST_THUMB) or victim.arm_right.is_set(merc.BROKEN_THUMB)) and \
                    (victim.arm_right.is_set(merc.LOST_FINGER_I) or victim.arm_right.is_set(merc.BROKEN_FINGER_I)) and \
                    (victim.arm_right.is_set(merc.LOST_FINGER_M) or victim.arm_right.is_set(merc.BROKEN_FINGER_M)) and \
                    (victim.arm_right.is_set(merc.LOST_FINGER_R) or victim.arm_right.is_set(merc.BROKEN_FINGER_R)) and \
                    (victim.arm_right.is_set(merc.LOST_FINGER_L) or victim.arm_right.is_set(merc.BROKEN_FINGER_L)):
                return

            damaged = victim.get_eq("hands")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from breaking some fingers on your right hand.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from breaking some fingers on $s right hand.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            count1 = 0
            count2 = 0

            if not victim.arm_right.is_set(merc.BROKEN_THUMB) and not victim.arm_right.is_set(merc.LOST_THUMB) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.BROKEN_THUMB)
                count2 += 1

            if not victim.arm_right.is_set(merc.BROKEN_FINGER_I) and not victim.arm_right.is_set(merc.LOST_FINGER_I) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.BROKEN_FINGER_I)
                count1 += 1

            if not victim.arm_right.is_set(merc.BROKEN_FINGER_M) and not victim.arm_right.is_set(merc.LOST_FINGER_M) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.BROKEN_FINGER_M)
                count1 += 1

            if not victim.arm_right.is_set(merc.BROKEN_FINGER_R) and not victim.arm_right.is_set(merc.LOST_FINGER_R) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.BROKEN_FINGER_R)
                count1 += 1

            if not victim.arm_right.is_set(merc.BROKEN_FINGER_L) and not victim.arm_right.is_set(merc.LOST_FINGER_L) and game_utils.number_percent() < 25:
                victim.arm_right.set_bit(merc.BROKEN_FINGER_L)
                count1 += 1

            buf2 = "finger{}".format("" if count1 == 1 else "s")
            if count1 > 0 and count2 > 0:
                handler_game.act("Your skillful breaks %d %s and the thumb on $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow breaks %d %s and the thumb on $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow breaks %d %s and the thumb on your right hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("right_hand")
                if item:
                    victim.take_item(item)
            elif count1 > 0:
                handler_game.act("Your skillful blow breaks %d %s on $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow breaks %d %s on $N's right hand.".format(count1, buf2), self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow breaks %d %s on your right hand.".format(count1, buf2), self, None, victim, merc.TO_VICT)

                item = victim.get_eq("right_hand")
                if item:
                    victim.take_item(item)
            elif count2 > 0:
                handler_game.act("Your skillful blow breaks the thumb on $N's right hand.", self, None, victim, merc.TO_CHAR)
                handler_game.act("$n's skillful blow breaks the thumb on $N's right hand.", self, None, victim, merc.TO_NOTVICT)
                handler_game.act("$n's skillful blow breaks the thumb on your right hand.", self, None, victim, merc.TO_VICT)

                item = victim.get_eq("right_hand")
                if item:
                    victim.take_item(item)
        elif critical == 16:
            if victim.leg_left.is_set(merc.LOST_LEG):
                return

            damaged = victim.get_eq("legs")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your left leg.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s left leg.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.leg_left.is_set(merc.LOST_LEG):
                victim.leg_left.set_bit(merc.LOST_LEG)
            else:
                return

            victim.bleeding.set_bit(merc.BLEEDING_LEG_L)
            victim.bleeding.rem_bit(merc.BLEEDING_FOOT_L)
            handler_game.act("Your skillful blow cuts off $N's left leg!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's left leg!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your left leg!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "leg")

            if victim.leg_left.is_set(merc.LOST_LEG) and victim.leg_right.is_set(merc.LOST_LEG):
                item = victim.get_eq("legs")
                if item:
                    victim.take_item(item)

            item = victim.get_eq("feet")
            if item:
                victim.take_item(item)
        elif critical == 17:
            if victim.leg_right.is_set(merc.LOST_LEG):
                return

            damaged = victim.get_eq("legs")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your right leg.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s right leg.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.leg_right.is_set(merc.LOST_LEG):
                victim.leg_right.set_bit(merc.LOST_LEG)
            else:
                return

            victim.bleeding.set_bit(merc.BLEEDING_LEG_R)
            victim.bleeding.rem_bit(merc.BLEEDING_FOOT_R)
            handler_game.act("Your skillful blow cuts off $N's right leg!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's right leg!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your right leg!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "leg")

            if victim.leg_left.is_set(merc.LOST_LEG) and victim.leg_right.is_set(merc.LOST_LEG):
                item = victim.get_eq("legs")
                if item:
                    victim.take_item(item)

            item = victim.get_eq("feet")
            if item:
                victim.take_item(item)
        elif critical == 18:
            if victim.leg_left.is_set(merc.BROKEN_LEG) or victim.leg_left.is_set(merc.LOST_LEG):
                return

            damaged = victim.get_eq("legs")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from breaking your left leg.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from breaking $s left leg.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.leg_left.is_set(merc.BROKEN_LEG) and not victim.leg_left.is_set(merc.LOST_LEG):
                victim.leg_left.set_bit(merc.BROKEN_LEG)
            else:
                return

            handler_game.act("Your skillful blow breaks $N's left leg!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow breaks $N's left leg!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow breaks your left leg!", self, None, victim, merc.TO_VICT)
        elif critical == 19:
            if victim.leg_right.is_set(merc.BROKEN_LEG) or victim.leg_right.is_set(merc.LOST_LEG):
                return

            damaged = victim.get_eq("legs")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from breaking your right leg.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from breaking $s right leg.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.leg_right.is_set(merc.BROKEN_LEG) and not victim.leg_right.is_set(merc.LOST_LEG):
                victim.leg_right.set_bit(merc.BROKEN_LEG)
            else:
                return

            handler_game.act("Your skillful blow breaks $N's right leg!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow breaks $N's right leg!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow breaks your right leg!", self, None, victim, merc.TO_VICT)
        elif critical == 20:
            if victim.leg_left.is_set(merc.LOST_LEG) or victim.leg_left.is_set(merc.LOST_FOOT):
                return

            damaged = victim.get_eq("feet")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your left foot.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s left foot.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.leg_left.is_set(merc.LOST_LEG) and not victim.leg_left.is_set(merc.LOST_FOOT):
                victim.leg_left.set_bit(merc.LOST_FOOT)
            else:
                return

            victim.bleeding.rem_bit(merc.BLEEDING_LEG_L)
            victim.bleeding.set_bit(merc.BLEEDING_FOOT_L)
            handler_game.act("Your skillful blow cuts off $N's left foot!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's left foot!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your left foot!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "foot")

            item = victim.get_eq("feet")
            if item:
                victim.take_item(item)
        elif critical == 21:
            if victim.leg_right.is_set(merc.LOST_LEG) or victim.leg_right.is_set(merc.LOST_FOOT):
                return

            damaged = victim.get_eq("feet")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevent you from loosing your right foot.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevent $n from loosing $s right foot.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            if not victim.leg_right.is_set(merc.LOST_LEG) and not victim.leg_right.is_set(merc.LOST_FOOT):
                victim.leg_right.set_bit(merc.LOST_FOOT)
            else:
                return

            victim.bleeding.rem_bit(merc.BLEEDING_LEG_R)
            victim.bleeding.set_bit(merc.BLEEDING_FOOT_R)
            handler_game.act("Your skillful blow cuts off $N's right foot!", self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow cuts off $N's right foot!", self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow cuts off your right foot!", self, None, victim, merc.TO_VICT)
            object_creator.make_part(victim, "foot")

            item = victim.get_eq("feet")
            if item:
                victim.take_item(item)
        elif critical == 22:
            bodyloc = 0
            broken = game_utils.number_range(1, 3)

            part_list = [(merc.BROKEN_RIBS_1, 1), (merc.BROKEN_RIBS_2, 2), (merc.BROKEN_RIBS_4, 4), (merc.BROKEN_RIBS_8, 8),
                         (merc.BROKEN_RIBS_16, 16)]
            for (aa, bb) in part_list:
                if victim.body.is_set(aa):
                    bodyloc += bb

            if bodyloc >= 24:
                return

            damaged = victim.get_eq("body")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and not self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevents you from breaking some ribs.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevents $n from breaking some ribs.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            for (aa, bb) in part_list:
                if victim.body.is_set(aa):
                    victim.body.rem_bit(aa)

            if bodyloc + broken > 24:
                broken -= 1
            if bodyloc + broken > 24:
                broken -= 1
            bodyloc += broken

            if bodyloc >= 16:
                bodyloc -= 16
                victim.body.set_bit(merc.BROKEN_RIBS_16)
            if bodyloc >= 8:
                bodyloc -= 8
                victim.body.set_bit(merc.BROKEN_RIBS_8)
            if bodyloc >= 4:
                bodyloc -= 4
                victim.body.set_bit(merc.BROKEN_RIBS_4)
            if bodyloc >= 2:
                bodyloc -= 2
                victim.body.set_bit(merc.BROKEN_RIBS_2)
            if bodyloc >= 1:
                bodyloc -= 1
                victim.body.set_bit(merc.BROKEN_RIBS_1)

            handler_game.act("Your skillful blow breaks {} of $N's ribs!".format(broken), self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow breaks {} of $N's ribs!".format(broken), self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow breaks {} of your ribs!".format(broken), self, None, victim, merc.TO_VICT)
        elif critical == 23:
            bodyloc = 0
            broken = game_utils.number_range(1, 3)

            part_list = [(merc.LOST_TOOTH_1, 1), (merc.LOST_TOOTH_2, 2), (merc.LOST_TOOTH_4, 4), (merc.LOST_TOOTH_8, 8),
                         (merc.LOST_TOOTH_16, 16)]
            for (aa, bb) in part_list:
                if victim.head.is_set(aa):
                    bodyloc += bb

            if bodyloc >= 28:
                return

            damaged = victim.get_eq("face")
            # noinspection PyUnresolvedReferences
            if damaged and damaged.toughness > 0 and self.itemaff.is_set(merc.ITEMA_VORPAL):
                handler_game.act("$p prevents you from loosing some teeth.", victim, damaged, None, merc.TO_CHAR)
                handler_game.act("$p prevents $n from loosing some teeth.", victim, damaged, None, merc.TO_ROOM)

                if dam - damaged.toughness < 0:
                    return

                if dam - damaged.toughness > damaged.resistance:
                    damaged.condition -= damaged.resistance
                else:
                    damaged.condition -= dam - damaged.toughness
                if damaged.condition < 1:
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_CHAR)
                    handler_game.act("$p falls broken to the ground.", self, damaged, None, merc.TO_ROOM)
                    victim.get(damaged)
                    damaged.extract()
                return

            for (aa, bb) in part_list:
                if victim.head.is_set(aa):
                    victim.head.rem_bit(aa)

            if bodyloc + broken > 28:
                broken -= 1
            if bodyloc + broken > 28:
                broken -= 1
            bodyloc += broken

            if bodyloc >= 16:
                bodyloc -= 16
                victim.head.set_bit(merc.LOST_TOOTH_16)
            if bodyloc >= 8:
                bodyloc -= 8
                victim.head.set_bit(merc.LOST_TOOTH_8)
            if bodyloc >= 4:
                bodyloc -= 4
                victim.head.set_bit(merc.LOST_TOOTH_4)
            if bodyloc >= 2:
                bodyloc -= 2
                victim.head.set_bit(merc.LOST_TOOTH_2)
            if bodyloc >= 1:
                bodyloc -= 1
                victim.head.set_bit(merc.LOST_TOOTH_1)

            handler_game.act("Your skillful blow knocks out {} of $N's teeth!".format(broken), self, None, victim, merc.TO_CHAR)
            handler_game.act("$n's skillful blow knocks out {} of $N's teeth!".format(broken), self, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n's skillful blow knocks out {} of your teeth!".format(broken), self, None, victim, merc.TO_VICT)

            if broken >= 1:
                object_creator.make_part(victim, "tooth")
            if broken >= 2:
                object_creator.make_part(victim, "tooth")
            if broken >= 3:
                object_creator.make_part(victim, "tooth")

    def killperson(self, victim):
        victim.send("You have been KILLED!!\n\n")

        # noinspection PyUnresolvedReferences
        if victim.is_npc() and not self.is_npc():
            self.mkill += 1

        # noinspection PyUnresolvedReferences
        if not victim.is_npc() and self.is_npc():
            victim.mdeath += 1
        fight.raw_kill(victim)

    def skillstance(self, victim):
        stance = victim.stance[0]
        if stance not in merc.irange(1, 10):
            return

        buf_list = [(0, "completely unskilled in"), (25, "an apprentice of"), (50, "a trainee of"), (75, "a student of"),
                    (100, "fairly experienced in"), (125, "well trained in"), (150, "highly skilled in"), (175, "an expert of"),
                    (199, "a master of")]
        for (aa, bb) in buf_list:
            if victim.stance[stance] >= aa:
                bufskill = bb
                break
        else:
            bufskill = "a grand master of"

        buf_list = [(merc.STANCE_VIPER, "viper"), (merc.STANCE_CRANE, "crane"), (merc.STANCE_CRAB, "crab"), (merc.STANCE_MONGOOSE, "mongoose"),
                    (merc.STANCE_BULL, "bull"), (merc.STANCE_MANTIS, "mantis"), (merc.STANCE_DRAGON, "dragon"), (merc.STANCE_TIGER, "tiger"),
                    (merc.STANCE_MONKEY, "monkey"), (merc.STANCE_SWALLOW, "swallow")]
        for (aa, bb) in buf_list:
            if stance == aa:
                stancename = bb
                break
        else:
            return

        if self == victim:
            handler_game.act("You are {} the {} stance.".format(bufskill, stancename), self, None, victim, merc.TO_CHAR)
        else:
            handler_game.act("$N is {} the {} stance.".format(bufskill, stancename), self, None, victim, merc.TO_CHAR)

    # Improve ability at a certain spell type.  KaVir.
    def improve_spl(self, dtype):
        # noinspection PyUnresolvedReferences
        max_spl = 200 if not self.is_mage() else 240
        if self.spl[dtype] >= max_spl:
            return

        dice1 = game_utils.number_percent()
        dice2 = game_utils.number_percent()

        if (dice1 > self.spl[dtype] or dice2 > self.spl[dtype]) or (dice1 == 100 or dice2 == 100):
            self.spl[dtype] += 1
        else:
            return

        buf_list = [(1, "an apprentice of"), (26, "a student at"), (51, "a scholar at"), (76, "a magus at"), (101, "an adept at"),
                    (126, "a mage at"), (151, "a warlock at"), (176, "a master wizard at"), (200, "a grand sorcerer at"),
                    (240, "the complete master of")]
        for (aa, bb) in buf_list:
            if self.spl[dtype] == aa:
                bufskill = bb
                break
        else:
            return

        buf_list = [(merc.PURPLE_MAGIC, "purple"), (merc.RED_MAGIC, "red"), (merc.BLUE_MAGIC, "blue"), (merc.GREEN_MAGIC, "green"),
                    (merc.YELLOW_MAGIC, "yellow")]
        for (aa, bb) in buf_list:
            if dtype == aa:
                buftype = bb
                break
        else:
            return

        self.send("#WYou are now {} {} magic.#n\n".format(bufskill, buftype))

    def improve_wpn(self, dtype, right_hand):
        # noinspection PyUnresolvedReferences
        if self.is_npc():
            return

        # noinspection PyUnresolvedReferences
        max_skl = 200 if not self.is_highlander() else 1000
        # noinspection PyUnresolvedReferences
        wield = self.get_eq("right_hand" if right_hand else "left_hand")
        if not wield:
            dtype = merc.TYPE_HIT

        if dtype == merc.TYPE_UNDEFINED:
            dtype = merc.TYPE_HIT
            if wield and wield.item_type == merc.ITEM_WEAPON:
                dtype += wield.value[3]

        if dtype not in merc.irange(1000, 1012):
            return

        dtype -= 1000
        if self.wpn[dtype] >= max_skl:
            return

        dice1 = game_utils.number_percent()
        dice2 = game_utils.number_percent()

        trapper = self.wpn[dtype]
        if (dice1 > self.wpn[dtype] and dice2 > self.wpn[dtype]) or (dice1 == 100 or dice2 == 100):
            self.wpn[dtype] += 1
        else:
            return

        if trapper == self.wpn[dtype]:
            return

        wpn_list = [(1, "slightly skilled"), (26, "reasonable"), (51, "fairly competent"), (76, "highly skilled"), (101, "very dangerous"),
                    (126, "extremely deadly"), (151, "an expert"), (176, "a master"), (200, "a grand master"), (201, "supremely skilled")]
        for (aa, bb) in wpn_list:
            if self.wpn[dtype] == aa:
                bufskill = bb
                break
        else:
            return

        if not wield or dtype == 0:
            buf = "#WYou are now {} at unarmed combat.#n\n".format(bufskill)
        else:
            buf = "#WYou are now {} with {}.#n\n".format(bufskill, wield.short_descr)
        self.send(buf)

    def improve_stance(self):
        dice1 = game_utils.number_percent()
        dice2 = game_utils.number_percent()

        # noinspection PyUnresolvedReferences
        if self.is_npc():
            return

        stance = self.stance[0]
        if stance not in merc.irange(0, 10):
            return

        if self.stance[stance] >= 200:
            self.stance[stance] = 200
            return

        if (dice1 > self.stance[stance] and dice2 > self.stance[stance]) or (any([dice1, dice2]) == 100):
            self.stance[stance] += 1
        else:
            return

        if stance == self.stance[stance]:
            return

        stance_list = [(1, "an apprentice of"), (26, "a trainee of"), (51, "a student of"), (76, "fairly experienced in"),
                       (101, "well trained in"), (126, "highly skilled in"), (151, "an expert of"), (176, "a master of"),
                       (200, "a grand master of")]
        for (aa, bb) in stance_list:
            if self.stance[stance] == aa:
                bufskill = bb
                break
        else:
            return

        stance_list = [(merc.STANCE_VIPER, "viper"), (merc.STANCE_CRANE, "crane"), (merc.STANCE_CRAB, "crab"),
                       (merc.STANCE_MONGOOSE, "mongoose"), (merc.STANCE_BULL, "bull"), (merc.STANCE_MANTIS, "mantis"),
                       (merc.STANCE_DRAGON, "dragon"), (merc.STANCE_TIGER, "tiger"), (merc.STANCE_MONKEY, "monkey"),
                       (merc.STANCE_SWALLOW, "swallow")]
        for (aa, bb) in stance_list:
            if stance == aa:
                stancename = bb
                break
        else:
            return

        self.send("#WYou are now {} the {} stance.#n\n".format(bufskill, stancename))


class ClassStuff:
    def __init__(self):
        super().__init__()
        self.vampaff = bit.Bit(flagset_name="vampaff_flags")
        self.demaff = bit.Bit(flagset_name="demon_flags")
        self.dempower = bit.Bit(flagset_name="demon_flags")
        self.special = bit.Bit(flagset_name="special_flags")
        self._ch_class = "human"
        self.morph = ""
        self.blood = 48
        self.beast = 15
        self.obj_vnum = 0
        self.powers = [0] * merc.MAX_POWERS
        self.fake_skill = 0
        self.fake_stance = 0
        self.fake_hit = 0
        self.fake_dam = 0
        self.fake_hp = 0
        self.fake_mana = 0
        self.fake_move = 0
        self.fake_ac= 0

    def send(self, pstr):
        pass

    @property
    def ch_class(self):
        return const.class_table.get(self._ch_class, None)

    @ch_class.setter
    def ch_class(self, value):
        if isinstance(value, const.class_type):
            self._ch_class = value.name
        else:
            self._ch_class = value

    def is_human(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.ch_class:
            return True

        return game_utils.str_cmp(self.ch_class.name, "human")

    def is_demon(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.ch_class:
            return False

        return game_utils.str_cmp(self.ch_class.name, "demon")

    def is_werewolf(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.ch_class:
            return False

        return game_utils.str_cmp(self.ch_class.name, "werewolf")

    def is_mage(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.ch_class:
            return False

        return game_utils.str_cmp(self.ch_class.name, "mage")

    def is_vampire(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.ch_class:
            return False

        return game_utils.str_cmp(self.ch_class.name, "vampire")

    def is_highlander(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.ch_class:
            return False

        return game_utils.str_cmp(self.ch_class.name, "highlander")

    def is_obj(self):
        # noinspection PyUnresolvedReferences
        item = self.chobj
        if not item:
            # noinspection PyUnresolvedReferences
            self.huh()
            return False

        if not item.chobj or item.chobj != self:
            # noinspection PyUnresolvedReferences
            self.huh()
            return False

        if not self.is_demon() and not self.special.is_set(merc.SPC_CHAMPION):
            # noinspection PyUnresolvedReferences
            self.huh()
            return False

        if not self.dempower.is_set(merc.DEM_MAGIC):
            self.send("You haven't been granted the gift of magic.\n")
            return False
        return True

    def humanity(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc():
            return

        if self.is_vampire() and self.beast in merc.irange(1, 99) and game_utils.number_range(1, 500) <= self.beast:
            if self.beast == 1:
                self.send("You have attained Golconda!\n")
                # noinspection PyUnresolvedReferences
                self.exp += 1000000
                # noinspection PyUnresolvedReferences
                self.immune.set_bit(merc.IMM_SUNLIGHT)
            else:
                self.send("You feel slightly more in control of your beast.\n")
            self.beast -= 1

    def beastlike(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc():
            return

        if self.is_vampire() and self.beast in merc.irange(1, 99) and game_utils.number_range(1, 500) <= self.beast:
            if self.beast < 99:
                self.send("You feel your beast take more control over your actions.\n")
            else:
                self.send("Your beast has fully taken over control of your actions!\n")

            self.beast += 1

            blood = self.blood
            self.blood = 666

            if (self.vampaff.is_set(merc.VAM_PROTEAN) or self.vampaff.is_set(merc.VAM_OBTENEBRATION)) and not self.vampaff.is_set(merc.VAM_NIGHTSIGHT):
                # noinspection PyUnresolvedReferences
                self.cmd_nightsight("")

            if not self.vampaff.is_set(merc.VAM_FANGS):
                # noinspection PyUnresolvedReferences
                self.cmd_fangs("")

            if self.vampaff.is_set(merc.VAM_PROTEAN) and not self.vampaff.is_set(merc.VAM_CLAWS):
                # noinspection PyUnresolvedReferences
                self.cmd_claws("")

            self.blood = blood

    def vamp_rage(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc():
            return

        self.send("You scream with rage as the beast within consumes you!\n")
        handler_game.act("$n screams with rage as $s inner beast consumes $m!.", self, None, None, merc.TO_ROOM)
        self.beastlike()
        # noinspection PyUnresolvedReferences
        self.cmd_rage("")

    def unwerewolf(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.is_werewolf() or not self.special.is_set(merc.SPC_WOLFMAN):
            return

        self.special.rem_bit(merc.SPC_WOLFMAN)
        # noinspection PyUnresolvedReferences
        self.affected_by.rem_bit(merc.AFF_POLYMORPH)
        self.vampaff.rem_bit(merc.VAM_DISGUISED)
        self.morph = ""

        if self.vampaff.is_set(merc.VAM_CLAWS):
            self.send("Your talons slide back into your fingers.\n")
            handler_game.act("$n's talons slide back into $s fingers.", self, None, None, merc.TO_ROOM)
            self.vampaff.rem_bit(merc.VAM_CLAWS)

        if self.vampaff.is_set(merc.VAM_FANGS):
            self.send("Your fangs slide back into your mouth.\n")
            handler_game.act("$n's fangs slide back into $s mouth.", self, None, None, merc.TO_ROOM)
            self.vampaff.rem_bit(merc.VAM_FANGS)

        if self.vampaff.is_set(merc.VAM_NIGHTSIGHT):
            self.send("The red glow in your eyes fades.\n")
            handler_game.act("The red glow in $n's eyes fades.", self, None, None, merc.TO_ROOM)
            self.vampaff.rem_bit(merc.VAM_NIGHTSIGHT)

        self.send("Your coarse hair shrinks back into your body.\n")
        handler_game.act("$n's coarse hair shrinks back into $s body.", self, None, None, merc.TO_ROOM)
        self.powers[merc.UNI_RAGE] -= 25
        if self.powers[merc.UNI_RAGE] < 0:
            self.powers[merc.UNI_RAGE] = 0

    def werewolf(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc() or not self.is_werewolf() or self.special.is_set(merc.SPC_WOLFMAN):
            return

        self.special.set_bit(merc.SPC_WOLFMAN)
        self.send("You throw back your head and howl with rage!\n")
        handler_game.act("$n throws back $s head and howls with rage!.", self, None, None, merc.TO_ROOM)
        self.send("Coarse dark hair sprouts from your body.\n")
        handler_game.act("Coarse dark hair sprouts from $n's body.", self, None, None, merc.TO_ROOM)

        if not self.vampaff.is_set(merc.VAM_NIGHTSIGHT):
            self.send("Your eyes start glowing red.\n")
            handler_game.act("$n's eyes start glowing red.", self, None, None, merc.TO_ROOM)
            self.vampaff.set_bit(merc.VAM_NIGHTSIGHT)

        if not self.vampaff.is_set(merc.VAM_FANGS):
            self.send("A pair of long fangs extend from your mouth.\n")
            handler_game.act("A pair of long fangs extend from $n's mouth.", self, None, None, merc.TO_ROOM)
            self.vampaff.set_bit(merc.VAM_FANGS)

        if not self.vampaff.set_bit(merc.VAM_CLAWS):
            self.send("Razor sharp talons extend from your fingers.\n")
            handler_game.act("Razor sharp talons extend from $n's fingers.", self, None, None, merc.TO_ROOM)
            self.vampaff.set_bit(merc.VAM_CLAWS)

        # noinspection PyUnresolvedReferences
        item = self.get_eq("right_hand")
        if item and not item.flags.wolfweapon:
            handler_game.act("$p drops from your right hand.", self, item, None, merc.TO_CHAR)
            handler_game.act("$p drops from $n's right hand.", self, item, None, merc.TO_ROOM)
            # noinspection PyUnresolvedReferences
            self.get(item)
            # noinspection PyUnresolvedReferences
            self.put(item)

        # noinspection PyUnresolvedReferences
        item = self.get_eq("left_hand")
        if item and not item.flags.wolfweapon:
            handler_game.act("$p drops from your left hand.", self, item, None, merc.TO_CHAR)
            handler_game.act("$p drops from $n's left hand.", self, item, None, merc.TO_ROOM)
            # noinspection PyUnresolvedReferences
            self.get(item)
            # noinspection PyUnresolvedReferences
            self.put(item)

        # noinspection PyUnresolvedReferences
        self.affected_by.set_bit(merc.AFF_POLYMORPH)
        self.vampaff.set_bit(merc.VAM_DISGUISED)
        # noinspection PyUnresolvedReferences
        self.morph = "{} the werewolf".format(self.name)
        self.powers[merc.UNI_RAGE] += 25
        if self.powers[merc.WPOWER_WOLF] > 3:
            self.powers[merc.UNI_RAGE] += 100

        if self.powers[merc.UNI_RAGE] > 300:
            self.powers[merc.UNI_RAGE] = 300

        for vch in list(instance.characters.values()):
            if not vch.in_room:
                continue

            if self == vch:
                handler_game.act("You throw back your head and howl with rage!", self, None, None, merc.TO_CHAR)
                continue

            if not vch.is_npc() and vch.chobj:
                continue

            if not vch.is_npc():
                # noinspection PyUnresolvedReferences
                if vch.in_room == self.in_room:
                    handler_game.act("$n throws back $s head and howls with rage!", self, None, vch, merc.TO_VICT)
                # noinspection PyUnresolvedReferences
                elif vch.in_room.area == self.in_room.area:
                    vch.send("You hear a fearsome howl close by!\n")
                else:
                    vch.send("You hear a fearsome howl far off in the distance!\n")

                if not vch.can_pk():
                    continue

            # noinspection PyUnresolvedReferences
            if vch.in_room == self.in_room and self.can_see(vch):
                fight.multi_hit(self, vch, merc.TYPE_UNDEFINED)
                if not vch or vch.position <= merc.POS_STUNNED:
                    continue
                fight.multi_hit(self, vch, merc.TYPE_UNDEFINED)
                if not vch or vch.position <= merc.POS_STUNNED:
                    continue
                fight.multi_hit(self, vch, merc.TYPE_UNDEFINED)

    def show_page(self, book, pnum, pagefalse):
        buf = []
        found = False
        for page_id in book.inventory[:]:
            page = instance.items[page_id]

            if page.value[0] == pnum:
                found = True
                if len(page.victpoweruse) < 1:
                    buf += "Untitled page.\n"
                else:
                    buf += page.victpoweruse + ".\n"
                buf = buf[0].upper() + buf[1:]

                if not pagefalse:
                    if not page.chpoweruse:
                        if not page.are_runes():
                            buf += "This page is blank.\n"
                        # noinspection PyUnresolvedReferences
                        elif self.is_affected(merc.AFF_DETECT_MAGIC) and not page.quest.is_set(merc.QUEST_MASTER_RUNE) and \
                                not page.spectype.is_set(merc.ADV_STARTED):
                            buf += Living.show_runes(page, False)
                        else:
                            buf += "This page is blank.\n"
                        return "".join(buf)

                    buf += "--------------------------------------------------------------------------------\n"
                    buf += page.chpoweruse + "\n"
                    buf += "--------------------------------------------------------------------------------\n"

                    # noinspection PyUnresolvedReferences
                    if self.is_affected(merc.AFF_DETECT_MAGIC) and not page.quest.is_set(merc.QUEST_MASTER_RUNE) and \
                            not page.spectype.is_set(merc.ADV_STARTED):
                        buf += Living.show_runes(page, True)
        if not found:
            buf += "This page has been torn out.\n"
        return "".join(buf)

    @classmethod
    def show_runes(cls, page, endline):
        if sum([page.value[1], page.value[2], page.value[3]]) < 1:
            return ""

        buf = ["This page contains the following symbols:\n"]
        buf += "Runes:"

        if page.value[1] > 0:
            rune_list = [(merc.RUNE_FIRE, "Fire"), (merc.RUNE_AIR, "Air"), (merc.RUNE_EARTH, "Earth"), (merc.RUNE_WATER, "Water"),
                         (merc.RUNE_DARK, "Dark"), (merc.RUNE_LIGHT, "Light"), (merc.RUNE_LIFE, "Life"), (merc.RUNE_DEATH, "Death"),
                         (merc.RUNE_MIND, "Mind"), (merc.RUNE_SPIRIT, "Spirit")]
            for (aa, bb) in rune_list:
                if state_checks.is_set(page.value[1], aa):
                    buf += " " + bb
        else:
            buf += " None"
        buf += ".\n"

        buf += "Glyphs:"
        if page.value[2] > 0:
            rune_list = [(merc.GLYPH_CREATION, "Creation"), (merc.GLYPH_DESTRUCTION, "Destruction"), (merc.GLYPH_SUMMONING, "Summoning"),
                         (merc.GLYPH_TRANSFORMATION, "Transformation"), (merc.GLYPH_TRANSPORTATION, "Transportation"),
                         (merc.GLYPH_ENHANCEMENT, "Enhancement"), (merc.GLYPH_REDUCTION, "Reducation"), (merc.GLYPH_CONTROL, "Control"),
                         (merc.GLYPH_PROTECTION, "Protection"), (merc.GLYPH_INFORMATION, "Information")]
            for (aa, bb) in rune_list:
                if state_checks.is_set(page.value[2], aa):
                    buf += " " + bb
        else:
            buf += " None"
        buf += ".\n"

        buf += "Sigils:"
        if page.value[3] > 0:
            rune_list = [(merc.SIGIL_SELF, "Self"), (merc.SIGIL_TARGETING, "Targeting"), (merc.SIGIL_AREA, "Area"), (merc.SIGIL_OBJECT, "Object")]
            for (aa, bb) in rune_list:
                if state_checks.is_set(page.value[3], aa):
                    buf += " " + bb
        else:
            buf += " None"
        buf += ".\n"

        if endline:
            buf += "--------------------------------------------------------------------------------\n"
        return "".join(buf)

    def mortalvamp(self):
        # noinspection PyUnresolvedReferences
        if self.is_npc():
            return

        if self.is_vampire():
            # Have to make sure they have enough blood to change back
            blood = self.blood
            self.blood = 666

            # Remove physical vampire attributes when you take mortal form
            if self.vampaff.is_set(merc.VAM_DISGUISED):
                # noinspection PyUnresolvedReferences
                self.cmd_mask("self")

            # noinspection PyUnresolvedReferences
            if self.immune.is_set(merc.IMM_SHIELDED):
                # noinspection PyUnresolvedReferences
                self.cmd_shield("")

            # noinspection PyUnresolvedReferences
            if self.is_affected(merc.AFF_SHADOWPLANE):
                # noinspection PyUnresolvedReferences
                self.cmd_shadowplane("")

            if self.vampaff.is_set(merc.VAM_FANGS):
                # noinspection PyUnresolvedReferences
                self.cmd_fangs("")

            if self.vampaff.is_set(merc.VAM_CLAWS):
                # noinspection PyUnresolvedReferences
                self.cmd_claws("")

            if self.vampaff.is_set(merc.VAM_NIGHTSIGHT):
                # noinspection PyUnresolvedReferences
                self.cmd_nightsight("")

            # noinspection PyUnresolvedReferences
            if self.is_affected(merc.AFF_SHADOWSIGHT):
                # noinspection PyUnresolvedReferences
                self.cmd_shadowsight("")

            # noinspection PyUnresolvedReferences
            if self.act.is_set(merc.PLR_HOLYLIGHT):
                # noinspection PyUnresolvedReferences
                self.cmd_truesight("")

            if self.vampaff.is_set(merc.VAM_CHANGED):
                # noinspection PyUnresolvedReferences
                self.cmd_change("human")

            # noinspection PyUnresolvedReferences
            if self.polyaff.is_set(merc.POLY_SERPENT):
                # noinspection PyUnresolvedReferences
                self.cmd_serpent("")

            self.powers[merc.UNI_RAGE] = 0
            self.blood = blood
            self.send("You lose your vampire powers.\n")
            self.ch_class = state_checks.prefix_lookup(const.class_table, "human")
            self.vampaff.set_bit(merc.VAM_MORTAL)
            return

        self.send("You regain your vampire powers.\n")
        self.ch_class = state_checks.prefix_lookup(const.class_table, "vampire")
        self.vampaff.rem_bit(merc.VAM_MORTAL)


class Communication:
    def __init__(self):
        super().__init__()
        self.reply = None
        self.channels = bit.Bit(flagset_name="channel_flags")

    def send(self, pstr):
        pass

    # Generic channel function.
    def talk_channel(self, argument, channel, verb):
        if not argument:
            self.send("{} what?\n".format(verb.upper()))
            return

        # noinspection PyUnresolvedReferences
        if self.head.is_set(merc.LOST_TONGUE):
            self.send("You can't {} without a tongue!\n".format(verb))
            return

        # noinspection PyUnresolvedReferences
        if self.extra.is_set(merc.EXTRA_GAGGED):
            self.send("You can't {} with a gag on!\n".format(verb))
            return

        # noinspection PyUnresolvedReferences
        if not self.is_npc() and self.sentances.is_set(merc.SENT_SILENCE):
            self.send("You can't {}.\n".format(verb))
            return

        self.channels.rem_bit(channel)

        if channel == merc.CHANNEL_IMMTALK:
            buf1 = "$n: $t."
            buf2 = "$n: $t."
            handler_game.act(buf1, self, argument, None, merc.TO_CHAR, merc.POS_DEAD)
        elif channel == merc.CHANNEL_PRAY:
            buf1 = "You pray '$t'."
            buf2 = "$n prays '$t'."
            handler_game.act(buf1, self, argument, None, merc.TO_CHAR, merc.POS_DEAD)
        elif channel == merc.CHANNEL_MAGETALK:
            buf1 = "{$n} '$t'."
            buf2 = "{$n} '$t'."
            handler_game.act(buf1, self, argument, None, merc.TO_CHAR, merc.POS_DEAD)
        elif channel == merc.CHANNEL_HOWL:
            buf1 = "You howl '$t'."
            buf2 = "$n howls '$t'."
            handler_game.act(buf1, self, argument, None, merc.TO_CHAR, merc.POS_DEAD)
        elif channel == merc.CHANNEL_VAMPTALK:
            # noinspection PyUnresolvedReferences
            if not self.is_npc() and (self.powers[merc.UNI_GEN] == 1 or self.special.is_set(merc.SPC_ANARCH)):
                buf1 = "<[$n]> $t."
                buf2 = "<[$n]> $t."
            # noinspection PyUnresolvedReferences
            elif not self.is_npc() and self.powers[merc.UNI_GEN] == 2:
                buf1 = "<<$n>> $t."
                buf2 = "[[$n]] $t."
            else:
                buf1 = "<$n> $t."
                buf2 = "[$n] $t."
            handler_game.act(buf1, self, argument, None, merc.TO_CHAR, merc.POS_DEAD)
        else:
            self.send("You {} '{}'.\n".format(verb, argument))
            buf1 = "$n {}s '$t'.".format(verb)
            buf2 = "$n {}s '$t'.".format(verb)

        for vch in list(instance.players.values()):
            if vch == self or vch.channels.is_set(channel):
                continue

            if channel == merc.CHANNEL_IMMTALK:
                if not vch.is_immortal():
                    continue
            elif channel == merc.CHANNEL_VAMPTALK:
                if vch.is_npc() or (not vch.is_vampire() and not vch.is_immortal()):
                    continue
            elif channel == merc.CHANNEL_MAGETALK:
                if vch.is_npc() or (not vch.is_mage() and not vch.is_immortal()):
                    continue
            elif channel == merc.CHANNEL_PRAY:
                if vch.is_npc() or (not vch.is_demon() and not vch.is_immortal()):
                    continue
            elif channel == merc.CHANNEL_HOWL:
                if vch.is_npc() or (not vch.is_werewolf() and not vch.is_immortal()):
                    continue

                # noinspection PyUnresolvedReferences
                if vch.in_room and self.in_room:
                    # noinspection PyUnresolvedReferences
                    if vch.in_room == self.in_room:
                        handler_game.act("$n throws back $s head and howls loudly.", self, None, vch, merc.TO_VICT)
                        continue
                    # noinspection PyUnresolvedReferences
                    elif vch.in_room.area == self.in_room.area:
                        handler_game.act("You hear a loud howl nearby.", self, None, vch, merc.TO_VICT)
                        continue
                    else:
                        handler_game.act("You hear a loud howl in the distance.", self, None, vch, merc.TO_VICT)
                        continue
            elif channel == merc.CHANNEL_YELL:
                # noinspection PyUnresolvedReferences
                if vch.in_room.area != self.in_room.area:
                    continue

            if not vch.is_npc():
                # noinspection PyUnresolvedReferences
                if vch.is_vampire() and (game_utils.str_cmp(self.clan, vch.clan) or vch.is_immortal()):
                    handler_game.act(buf2, self, argument, vch, merc.TO_VICT, merc.POS_DEAD)
                    continue

                if vch.is_werewolf() or vch.is_immortal():
                    handler_game.act(buf2, self, argument, vch, merc.TO_VICT, merc.POS_DEAD)
                    continue

                if vch.is_demon() or vch.is_immortal():
                    handler_game.act(buf2, self, argument, vch, merc.TO_VICT, merc.POS_DEAD)
                    continue

                if vch.is_mage() or vch.is_immortal():
                    handler_game.act(buf2, self, argument, vch, merc.TO_VICT, merc.POS_DEAD)
                    continue

            handler_game.act(buf1, self, argument, vch, merc.TO_VICT, merc.POS_DEAD)


class Living(immortal.Immortal, Fight, Grouping, physical.Physical, environment.Environment, affects.Affects,
             Communication, inventory.Inventory, instance.Instancer, type_bypass.ObjectType, equipment.Equipment,
             ClassStuff, BodyParts):
    def __init__(self):
        super().__init__()
        self.is_living = True
        self.desc = None
        self.wizard = None
        self.familiar = None
        self.id = 0
        self.version = 1
        self.level = 0
        self.sex = 0
        self.played = 0
        self.played_fake = 0
        self.logon = merc.current_time

        # stats
        self.perm_stat = [13] * merc.MAX_STATS
        self.mod_stat = [0] * merc.MAX_STATS
        self.hit = 20
        self.max_hit = 20
        self.mana = 100
        self.max_mana = 100
        self.move = 100
        self.max_move = 100
        self.gold = 0
        self.exp = 0
        self.practice = 0
        self.quest = 0
        self.position = merc.POS_STANDING
        self.alignment = 0
        self.spectype = 0
        self.specaction = 0

        # Marriage
        self.propose = None
        self.marriage = ""

        # random stuff
        self.extra = bit.Bit(flagset_name="charextra_flags")
        self.sentances = bit.Bit(flagset_name="sentance_flags")
        self.chobj = None
        self.mount = None
        self.mounted = 0
        self.save_time = merc.current_time

        # equipment
        self.slots = equipment.Equipped()

    @property
    def equipped(self):
        return self.slots._equipped if self.is_living else None

    def get(self, instance_object):
        if instance_object.is_item and instance_object.instance_id in self.inventory:
            self.inventory.remove(instance_object.instance_id)
            self.carry_number -= instance_object.get_number()
            self.carry_weight -= instance_object.get_weight()
            instance_object.environment = None
            return instance_object
        elif instance_object.is_item and instance_object.instance_id in self.equipped.values():
            self.raw_unequip(instance_object)
            self.inventory.remove(instance_object.instance_id)
            self.carry_number -= instance_object.get_number()
            self.carry_weight -= instance_object.get_weight()
            instance_object.environment = None
            return instance_object
        else:
            if not instance_object.is_item:
                raise TypeError("Non-item object attempted "
                                "to be removed from character object - %s" % type(instance_object))

    def put(self, instance_object):
        # if instance_object.is_item:
        self.inventory.insert(0, instance_object.instance_id)
        instance_object.environment = self.instance_id

        if instance_object.instance_id not in self.equipped.values():
            self.carry_number += instance_object.get_number()
            self.carry_weight += instance_object.get_weight()
            return instance_object
        else:
            raise KeyError("Item is in equipped dict, run, screaming! %d" % instance_object.instance_id)

    def send(self, pstr):
        pass

    def is_npc(self):
        # noinspection PyUnresolvedReferences
        return self.act.is_set(merc.ACT_IS_NPC)

    def is_good(self):
        return self.alignment >= 350

    def is_evil(self):
        return self.alignment <= -350

    def is_neutral(self):
        return not self.is_good() and not self.is_evil()

    def is_awake(self):
        return self.position > merc.POS_SLEEPING

    def is_outside(self):
        if not self.in_room:
            return False

        return self.in_room.room_flags.is_set(merc.ROOM_INDOORS)

    def huh(self):
        self.send("Huh?\n")

    def not_imm(self):
        self.send("You cannot do that to an Immortal.\n")

    def not_npc(self):
        self.send("You cannot do that on NPCs.\n")

    def not_pc(self):
        self.send("You cannot do that on PCs.\n")

    def not_self(self):
        self.send("You cannot do that on yourself.\n")

    def no_obj(self):
        self.send("You are not carrying that object.\n")

    def miss_obj(self, vnum, function):
        self.send("Missing object, please inform an Immortal.\n")
        comm.notify("{}: missing vnum ##{}".format(function, vnum), merc.CONSOLE_WARNING)

    def miss_mob(self, vnum, function):
        self.send("Missing mobile, please inform an Immortal.\n")
        comm.notify("{}: missing vnum ##{}".format(function, vnum), merc.CONSOLE_WARNING)

    def not_here(self, argument):
        if not argument:
            self.send("They aren't here.\n")
        else:
            self.send("You couldn't find '{}'.\n".format(argument))

    def get_age(self):
        return 17 + (self.played + int(time.time() - self.logon)) // 72000

    def pers(self, looker):
        if looker.can_see(self):
            return self.short_descr if self.is_npc() else self.morph if self.is_affected(merc.AFF_POLYMORPH) else self.name
        else:
            return "someone"

    def check_blind(self):
        # noinspection PyUnresolvedReferences
        if not self.is_npc() and self.act.is_set(merc.PLR_HOLYLIGHT):
            return False

        if self.itemaff.is_set(merc.ITEMA_VISION):
            return False

        if self.head.is_set(merc.LOST_EYE_L) and self.head.is_set(merc.LOST_EYE_R):
            self.send("You have no eyes to see with!\n")
            return True

        if self.extra.is_set(merc.EXTRA_BLINDFOLDED):
            self.send("You can't see a thing through the blindfold!\n")
            return True

        if self.is_affected(merc.AFF_BLIND) and not self.is_affected(merc.AFF_SHADOWSIGHT):
            self.send("You can't see a thing!\n")
            return True
        return False

    def take_item(self, item):
        if not item:
            return

        self.unequip(item.equipped_to, silent=True, forced=True)
        self.get(item)
        self.in_room.put(item)
        handler_game.act("You wince in pain and $p falls to the ground.", self, item, None, merc.TO_CHAR)
        handler_game.act("$n winces in pain and $p falls to the ground.", self, item, None, merc.TO_ROOM)

    # command for retrieving stats
    def stat(self, stat):
        if self.is_npc():
            return 13

        return state_checks.urange(3, self.perm_stat[stat] + self.mod_stat[stat], 25)

    # True if char can see victim.
    def can_see(self, victim):
        if type(victim) is int:
            victim = instance.characters.get(victim, None)
        if not victim:
            return False

        if self == victim:
            return True

        if not victim.is_npc():
            if victim.is_immortal():
                if self.trust < victim.invis_level:
                    return False
            else:
                if victim.act.is_set(merc.PLR_WIZINVIS) and self.trust < victim.trust:
                    return False

        if self.trust < victim.incog_level and self.in_room != victim.in_room:
            return False

        if self.in_room.room_flags.is_set(merc.ROOM_TOTAL_DARKNESS):
            return not (not self.is_immortal() and not self.is_affected(merc.AFF_SHADOWSIGHT))

        # noinspection PyUnresolvedReferences
        if (not self.is_npc() and self.act.is_set(merc.PLR_HOLYLIGHT)) or self.itemaff.is_set(merc.ITEMA_VISION):
            return True

        if self.is_affected(merc.AFF_SHADOWPLANE) and not victim.is_affected(merc.AFF_SHADOWPLANE) and not self.is_affected(merc.AFF_SHADOWSIGHT):
            return False

        if not self.is_affected(merc.AFF_SHADOWPLANE) and victim.is_affected(merc.AFF_SHADOWPLANE) and not self.is_affected(merc.AFF_SHADOWSIGHT):
            return False

        if not self.is_npc() and self.vampaff.is_set(merc.VAM_SONIC):
            return True

        if self.head.is_set(merc.LOST_EYE_L) and self.head.is_set(merc.LOST_EYE_R):
            return False

        if self.extra.is_set(merc.EXTRA_BLINDFOLDED):
            return False

        if self.is_affected(merc.AFF_BLIND) and not self.is_affected(merc.AFF_SHADOWSIGHT):
            return False

        if self.in_room.is_dark() and not self.is_affected(merc.AFF_INFRARED) and (not self.is_npc() and not self.vampaff.is_set(merc.VAM_NIGHTSIGHT)):
            return False

        if victim.is_affected(merc.AFF_INVISIBLE) and not self.is_affected(merc.AFF_DETECT_INVIS):
            return False

        if victim.is_affected(merc.AFF_HIDE) and not self.is_affected(merc.AFF_DETECT_HIDDEN):
            return False

        if not self.is_npc():
            if self.head.is_set(merc.LOST_HEAD) or self.extra.is_set(merc.EXTRA_OSWITCH):
                return True

            if (self.extra.is_set(merc.EXTRA_OSWITCH) or self.head.is_set(merc.LOST_HEAD)) and self.in_room and \
                    self.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT:
                return True
        return True

    # True if char can see obj.
    def can_see_item(self, item):
        if type(item) == int:
            item = instance.items.get(item, None)
        if not item:
            return False

        # noinspection PyUnresolvedReferences
        if (not self.is_npc() and self.act.is_set(merc.PLR_HOLYLIGHT)) or self.itemaff.is_set(merc.ITEMA_VISION):
            return True

        if (item.flags.shadowplane and not item.in_living) and not self.is_affected(merc.AFF_SHADOWPLANE) and \
                not self.is_affected(merc.AFF_SHADOWSIGHT):
            return False

        if (not item.flags.shadowplane and not item.in_living) and self.is_affected(merc.AFF_SHADOWPLANE) and \
                not self.is_affected(merc.AFF_SHADOWSIGHT):
            return False

        if (not self.is_npc() and self.vampaff.is_set(merc.VAM_SONIC)) or item.item_type == merc.ITEM_POTION:
            return True

        if self.head.is_set(merc.LOST_EYE_L) and self.head.is_set(merc.LOST_EYE_R):
            return False

        if self.extra.is_set(merc.EXTRA_BLINDFOLDED):
            return False

        if self.is_affected(merc.AFF_BLIND) and not self.is_affected(merc.AFF_SHADOWSIGHT):
            return False

        if item.item_type == merc.ITEM_LIGHT and item.value[2] != 0:
            return True

        if self.in_room.is_dark() and not self.is_affected(merc.AFF_INFRARED) and (not self.is_npc() and
                                                                                   not self.vampaff.is_set(merc.VAM_NIGHTSIGHT)):
            return False

        if item.flags.invis and not self.is_affected(merc.AFF_DETECT_INVIS):
            return False

        if not self.is_npc() and (self.extra.is_set(merc.EXTRA_OSWITCH) or self.head.is_set(merc.LOST_HEAD)) and self.in_room and \
                self.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT:
            return True
        return True

    def clear_stats(self):
        for item_id in self.equipped.values():
            if not item_id:
                continue

            item = instance.items[item_id]
            self.unequip(item.equipped_to, silent=True, forced=True)

        for aff in self.affected[:]:
            self.affect_remove(aff)

        if self.is_affected(merc.AFF_POLYMORPH) and self.is_affected(merc.AFF_ETHEREAL):
            self.affected_by.bits = merc.AFF_POLYMORPH | merc.AFF_ETHEREAL
        elif self.is_affected(merc.AFF_POLYMORPH):
            self.affected_by.bits = merc.AFF_POLYMORPH
        elif self.is_affected(merc.AFF_ETHEREAL):
            self.affected_by.bits = merc.AFF_ETHEREAL
        else:
            self.affected_by.bits = 0

        self.armor = 100
        self.hit = max(1, self.hit)
        self.mana = max(1, self.mana)
        self.move = max(1, self.move)
        self.hitroll = 0
        self.damroll = 0
        self.saving_throw = 0
        self.mod_stat = [0 for _ in range(merc.MAX_STATS)]

    def paradox(self):
        self.send("The sins of your past strike back!\n"
                  "The paradox has come for your soul!\n")
        comm.info("{} is struck by a paradox.".format(self.name))
        self.hit = -10
        fight.update_pos(self)
        # noinspection PyUnresolvedReferences
        self.cmd_escape("")
        self.extra.set_bit(merc.EXTRA_TIED_UP)
        self.extra.set_bit(merc.EXTRA_GAGGED)
        self.extra.set_bit(merc.EXTRA_BLINDFOLDED)

    def oset_affect(self, item, value, affect, is_quest):
        if self.is_npc():
            return

        if value == 0:
            self.send("Please enter a positive or negative amount.\n")
            return

        if not self.is_judge() and not item.questowner:
            self.send("First you must set the owners name on the object.\n")
            return

        if not self.is_judge() and (not item.questmaker or not game_utils.str_cmp(self.name, item.questmaker)) and not is_quest:
            self.send("That item has already been oset by someone else.\n")
            return

        aff_list = [(merc.APPLY_STR, 3, 20, merc.QUEST_STR), (merc.APPLY_DEX, 3, 20, merc.QUEST_DEX), (merc.APPLY_INT, 3, 20, merc.QUEST_INT),
                    (merc.APPLY_WIS, 3, 20, merc.QUEST_WIS), (merc.APPLY_CON, 3, 20, merc.QUEST_CON), (merc.APPLY_HIT, 25, 5, merc.QUEST_HIT),
                    (merc.APPLY_MANA, 25, 5, merc.QUEST_MANA), (merc.APPLY_MOVE, 25, 5, merc.QUEST_MOVE), (merc.APPLY_HITROLL, 5, 30, merc.QUEST_HITROLL),
                    (merc.APPLY_DAMROLL, 5, 30, merc.QUEST_DAMROLL), (merc.APPLY_AC, 25, 10, merc.QUEST_AC)]
        for (aa, bb, cc, dd) in aff_list:
            if affect == aa:
                qrange = bb
                cost = cc
                quest = dd
                break
        else:
            return

        if item.flags.improved:
            qmax = 1250 + self.race * 20
        elif item.vnum == merc.OBJ_VNUM_PROTOPLASM:
            qrange *= 2
            qmax = 750 + self.race * 10
        else:
            qmax = 400 + self.race * 10

        if item.item_type == merc.ITEM_WEAPON:
            qmax *= 2
            qrange *= 2

        if not self.is_judge() and (value > 0 and value > qrange) or (value < 0 and value < (qrange - qrange - qrange)):
            self.send("That is not within the acceptable range...\n"
                      "Str, Dex, Int, Wis, Con... max =   3 each, at  20 quest points per +1 stat.\n"
                      "Hp, Mana, Move............ max =  25 each, at   5 quest point per point.\n"
                      "Hitroll, Damroll.......... max =   5 each, at  30 quest points per point.\n"
                      "Ac........................ max = -25,      at  10 points per point.\n\n"
                      "Note: Created items can have upto 2 times the above maximum.\n"
                      "Also: Weapons may have upto 2 (4 for created) times the above maximum.\n")
            return

        if quest >= merc.QUEST_HIT and value < 0:
            cost *= value - (value * 2)
        else:
            cost *= value
        if cost < 0:
            cost = 0

        if self.is_judge() and item.quest.is_set(quest):
            self.send("That affect has already been set on this object.\n")
            return

        if not self.is_judge() and item.points + cost > qmax:
            self.send("You are limited to {} quest points per item.\n".format(qmax))
            return

        if is_quest and self.quest < cost:
            self.send("That costs {} quest points, while you only have {}.\n".format(cost, self.quest))
            return

        item.quest.set_bit(quest)

        if is_quest:
            self.quest -= cost

        item.points += cost
        item.questmaker = self.name

        aff = handler_game.AffectData(type="reserved", duration=-1, location=affect, modifier=value)
        item.affect_add(aff)
        self.send("Ok.\n")

    def bind_char(self):
        if self.is_npc() or self.obj_vnum < 1:
            return

        if self.class_stuff[merc.CSTUFF_OBJ_VNUM] not in instance.item_templates:
            return

        if not self.in_room or self.in_room.vnum != merc.ROOM_VNUM_IN_OBJECT:
            location = instance.rooms[merc.ROOM_VNUM_ALTAR]
            self.in_room.get(self)
            location.put(self)
        else:
            location = self.in_room

        item = object_creator.create_item(instance.item_templates[self.class_stuff[merc.CSTUFF_OBJ_VNUM]], 50)
        item.chobj = self
        self.chobj = item
        location.put(item)
        self.affected_by.set_bit(merc.AFF_POLYMORPH)
        self.extra.set_bit(merc.EXTRA_OSWITCH)
        self.morph = item.short_descr
        self.send("You reform yourself.\n")
        handler_game.act("$p fades into existance on the floor.", self, item, None, merc.TO_ROOM)
        # noinspection PyUnresolvedReferences
        self.cmd_look("auto")

    def werewolf_regen(self):
        hmin = 5
        hmax = 10

        if self.is_npc():
            return

        if self.hit < 1:
            self.hit += game_utils.number_range(1, 3)
            fight.update_pos(self)
        else:
            hmin += 10 - self.powers[merc.UNI_GEN]
            hmin += 20 - self.powers[merc.UNI_GEN] * 2
            self.hit = min(self.hit + game_utils.number_range(hmin, hmax), self.max_hit)
            self.mana = min(self.mana + game_utils.number_range(hmin, hmax), self.max_mana)
            self.move = min(self.move + game_utils.number_range(hmin, hmax), self.max_move)

            if self.hit >= self.max_hit and self.mana >= self.max_mana and self.move >= self.max_move:
                self.send("Your body has completely regenerated itself.\n")

    # Extract a char from the world.
    def extract(self, fpull):
        if not self.in_room:
            comm.notify("extract: {} not in room".format(self.name), merc.CONSOLE_WARNING)
            return

        if fpull:
            handler_ch.die_followers(self)

        fight.stop_fighting(self, True)

        for item_id in self.equipped.values():
            if item_id:
                item = instance.global_instances[item_id]
                self.raw_unequip(item)

        for item_id in self.inventory[:]:
            item = instance.global_instances[item_id]
            item.extract()

        if self.in_room:
            self.in_room.get(self)

        if self.is_npc():
            # noinspection PyUnresolvedReferences
            npc_template = instance.npc_templates[self.vnum]
            npc_template.count -= 1
        elif self.chobj:
            self.chobj.chobj = None
            self.chobj = None

        if not fpull:
            room_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
            instance.rooms[room_id].put(self)
            return

        if self.desc and self.desc.original:
            self.cmd_return("")
            self.desc = None

        for wch in list(instance.players.values()):
            if wch.reply == self:
                wch.reply = None

        wizard = self.wizard
        if wizard:
            if not wizard.is_npc():
                wizard.familiar = None
            self.wizard = None

        if not self.is_npc():
            familiar = self.familiar
            if familiar:
                familiar.wizard = None
                self.familiar = None

                if familiar.is_npc():
                    handler_game.act("$n slowly fades away to nothing.", familiar, None, None, merc.TO_ROOM)
                    familiar.extract(True)

            familiar = self.propose
            if familiar:
                self.propose = None

            for familiar in list(instance.players.values()):
                if familiar.propose and familiar.propose == self:
                    familiar.propose = None
        else:
            if self.lord:
                for familiar in list(instance.players.values()):
                    if not game_utils.str_cmp(familiar.name, self.lord):
                        continue

                    if familiar.followrs > 0:
                        familiar.followrs -= 1

        if self.instance_id not in instance.characters:
            comm.notify("extract: char not found", merc.CONSOLE_ERROR)
            return

        # noinspection PyUnresolvedReferences
        self.instance_destructor()

        if self.desc:
            self.desc.character = None

    # Find a char in the room.
    def get_char_room(self, argument):
        number, arg = game_utils.number_argument(argument)
        count = 0

        if game_utils.str_cmp(arg, "self") and (self.is_npc() or not self.chobj):
            return self

        for rch_id in self.in_room.people[:]:
            rch = instance.characters[rch_id]

            if not rch.is_npc() and (rch.head.is_set(merc.LOST_HEAD) or rch.extra.is_set(merc.EXTRA_OSWITCH)):
                continue
            elif not self.can_see(rch) or (not game_utils.is_name(arg, rch.name) and (rch.is_npc() or not game_utils.is_name(arg, rch.morph))):
                continue

            count += 1
            if count == number:
                return rch
        return None

    # Find a char in the world.
    def get_char_world(self, argument):
        wch = self.get_char_room(argument)
        if wch:
            return wch

        number, arg = game_utils.number_argument(argument)
        count = 0

        for rch in list(instance.characters.values()):
            if not rch.is_npc() and (rch.head.is_set(merc.LOST_HEAD) or rch.extra.is_set(merc.EXTRA_OSWITCH)):
                continue
            elif not self.can_see(rch) or (not game_utils.is_name(arg, rch.name) and (rch.is_npc() or not game_utils.is_name(arg, rch.morph))):
                continue

            count += 1
            if count == number:
                return rch
        return None

    # Find an object within the object you are in.
    def get_item_in_item(self, argument):
        number, arg = game_utils.number_argument(argument)

        if self.is_npc() or not self.chobj or not self.chobj.in_item:
            return None

        item = self.chobj
        if item.in_item.item_type not in [merc.ITEM_CONTAINER, merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC]:
            return None

        item_list = [instance.items[item_id] for item_id in item.in_item.items if game_utils.is_name(arg, instance.items[item_id].name)]
        if item_list:
            try:
                if item != item_list[number - 1]:
                    return item_list[number - 1]
            except:
                return None
        return None

    # Find an obj in a list.
    def get_item_list(self, argument, contents):
        number, arg = game_utils.number_argument(argument)

        item_list = [instance.items[item_id] for item_id in contents if game_utils.is_name(arg, instance.items[item_id].name)]
        if item_list:
            try:
                if self.can_see_item(item_list[number - 1]):
                    return item_list[number - 1]
            except:
                return None
        return None

    # Find an obj in player's inventory.
    def get_item_carry(self, argument):
        number, arg = game_utils.number_argument(argument)
        count = 0
        for item_id in self.items:
            item = instance.items.get(item_id, None)
            if self.can_see_item(item) and game_utils.is_name(arg, item.name):
                count += 1
                if count == number:
                    return item
        return None

    # Find an obj in player's equipment.
    def get_item_wear(self, argument):
        number, arg = game_utils.number_argument(argument)
        count = 0
        for loc, item_id in self.equipped.items():
            if item_id:
                item = instance.items[item_id]
                if self.can_see_item(item) and game_utils.is_name(arg, item.name.lower()):
                    count += 1
                    if count == number:
                        return item
            else:
                continue
        return None

    # Find an obj in the room or in inventory.
    def get_item_here(self, argument):
        item = self.get_item_list(argument, self.in_room.items)
        if item:
            return item

        item = self.get_item_carry(argument)
        if item:
            return item

        item = self.get_item_wear(argument)
        if item:
            return item

        item = self.get_item_in_item(argument)
        if item:
            return item
        return None

    # Find an obj in the world.
    def get_item_world(self, argument):
        item = self.get_item_here(argument)
        if item:
            return item

        number, arg = game_utils.number_argument(argument)
        item_list = [instance.items[item_id] for item_id in sorted(instance.items.keys())
                     if game_utils.is_name(arg, instance.items[item_id].name)]
        if item_list:
            try:
                if self.can_see_item(item_list[number - 1]):
                    return item_list[number - 1]
            except:
                return None
        return None

    # True if char can drop obj.
    def can_drop_item(self, item):
        if not item.flags.no_drop or (not self.is_npc() and self.is_immortal()):
            return True
        return False

    # Find a piece of eq on a character.
    def get_eq(self, check_loc):
        """
        :param check_loc:
        :type check_loc:
        :return:
        :rtype:
        """
        if not self:
            return None

        found = self.equipped.get(check_loc, None)
        if found:
            item_id = self.equipped[check_loc]
            return instance.items[item_id]
        return None

    def apply_affect(self, aff_object):
        """
        This was taken from the equip code, to shorten its length, checks for Affects, and applies as needed

        :param aff_object:
        :type aff_object:
        :return: no return
        :rtype: nothing
        """
        for paf in aff_object.affected:
            self.affect_modify(paf, True)

    def raw_equip(self, item, to_location):
        if item.item_type == merc.ITEM_WEAPON and (item.vnum == 30000 or item.flags.loyal):
            if item.questowner and not game_utils.str_cmp(self.name, item.questowner):
                handler_game.act("$p leaps out of $n's hand.", self, item, None, merc.TO_ROOM)
                handler_game.act("$p leaps out of your hand.", self, item, None, merc.TO_CHAR)
                return

        self.equipped[to_location] = item.instance_id
        item.environment = self.instance_id

        if to_location in ["right_scabbard", "left_scabbard"]:
            return

        if self.is_npc() or not self.is_highlander():
            self.armor -= item.apply_ac()

        self.apply_affect(item)

        if item.flags.light and item.value[2] != 0 and self.in_room:
            self.in_room.available_light += 1

        if to_location in ["right_hand", "left_hand"] and not self.is_npc():
            # noinspection PyUnresolvedReferences
            self.cmd_skill("")

        if not self.is_npc():
            chch = self.get_char_world(self.name)
            if chch and chch.desc != self.desc:
                return

        if item.chpoweron and not item.spectype.is_set(merc.SITEM_TELEPORTER) and not item.spectype.is_set(merc.SITEM_TRANSPORTER):
            handler_game.kavitem(item.chpoweron, self, item, None, merc.TO_CHAR)

            if item.spectype.is_set(merc.SITEM_ACTION):
                handler_game.kavitem(item.chpoweron, self, item, None, merc.TO_ROOM)

        if item.victpoweron and not item.spectype.is_set(merc.SITEM_ACTION) and not item.spectype.is_set(merc.SITEM_TELEPORTER) and \
                not item.spectype.is_set(merc.SITEM_TRANSPORTER):
            handler_game.kavitem(item.victpoweron, self, item, None, merc.TO_ROOM)

        if not item.equipped_to:
            return

        if (item.item_type == merc.ITEM_ARMOR and item.value[3] >= 1) or (item.item_type == merc.ITEM_WEAPON and item.value[0] >= 1000) or \
                item.flags.silver or item.flags.demonic or item.flags.artifact:
            # It would be so much easier if weapons had 5 values *sigh*.
            # Oh well, I'll just have to use v0 for two.  KaVir.
            if item.item_type == merc.ITEM_ARMOR:
                sn = item.value[3]
            else:
                sn = item.value[0] // 1000

            aff_list = [([1, 45], merc.AFF_INFRARED), ([2, 27], merc.AFF_DETECT_INVIS), ([3, 39], merc.AFF_FLYING), ([4], merc.AFF_BLIND),
                        ([5, 46], merc.AFF_INVISIBLE), ([6, 52], merc.AFF_PASS_DOOR), ([7, 54], merc.AFF_PROTECT), ([8, 57], merc.AFF_SANCTUARY),
                        ([9], merc.AFF_SNEAK), ([60], merc.AFF_DETECT_HIDDEN)]
            for (aa, bb) in aff_list:
                if sn in aa and self.is_affected(bb):
                    return
            else:
                aff_list = [(10, merc.ITEMA_SHOCKSHIELD), (11, merc.ITEMA_FIRESHIELD), (12, merc.ITEMA_ICESHIELD), (13, merc.ITEMA_ACIDSHIELD),
                            (14, merc.ITEMA_DBPASS), (15, merc.ITEMA_CHAOSSHIELD), (16, merc.ITEMA_REGENERATE), (17, merc.ITEMA_SPEED),
                            (18, merc.ITEMA_VORPAL), (19, merc.ITEMA_PEACE), (20, merc.ITEMA_REFLECT), (21, merc.ITEMA_RESISTANCE),
                            (22, merc.ITEMA_VISION), (23, merc.ITEMA_STALKER), (24, merc.ITEMA_VANISH), (25, merc.ITEMA_RAGER)]
                for (aa, bb) in aff_list:
                    if sn == aa and self.itemaff.is_set(bb):
                        return

            if sn == 4:
                self.affected_by.set_bit(merc.AFF_BLIND)
                self.send("You cannot see a thing!\n")
                handler_game.act("$n seems to be blinded!", self, None, None, merc.TO_ROOM)
            elif sn in [2, 27]:
                self.affected_by.set_bit(merc.AFF_DETECT_INVIS)
                self.send("Your eyes tingle.\n")
                handler_game.act("$n's eyes flicker with light.", self, None, None, merc.TO_ROOM)
            elif sn in [3, 39]:
                self.affected_by.set_bit(merc.AFF_FLYING)
                self.send("Your feet rise off the ground.\n")
                handler_game.act("$n's feet rise off the ground.", self, None, None, merc.TO_ROOM)
            elif sn in [1, 45]:
                self.affected_by.set_bit(merc.AFF_INFRARED)
                self.send("Your eyes glow red.\n")
                handler_game.act("$n's eyes glow red.", self, None, None, merc.TO_ROOM)
            elif sn in [5, 46]:
                self.affected_by.set_bit(merc.AFF_INVISIBLE)
                self.send("You fade out of existance.\n")
                handler_game.act("$n fades out of existance.", self, None, None, merc.TO_ROOM)
            elif sn in [6, 52]:
                self.affected_by.set_bit(merc.AFF_PASS_DOOR)
                self.send("You turn translucent.\n")
                handler_game.act("$n turns translucent.", self, None, None, merc.TO_ROOM)
            elif sn == 60:
                self.affected_by.set_bit(merc.AFF_DETECT_HIDDEN)
                self.send("You awarenes improves.\n")
                handler_game.act("$n eyes tingle.", self, None, None, merc.TO_ROOM)
            elif sn in [7, 54]:
                self.affected_by.set_bit(merc.AFF_PROTECT)
                self.send("You are surrounded by a divine aura.\n")
                handler_game.act("$n is surrounded by a divine aura.", self, None, None, merc.TO_ROOM)
            elif sn in [8, 57]:
                self.affected_by.set_bit(merc.AFF_SANCTUARY)
                self.send("You are surrounded by a white aura.\n")
                handler_game.act("$n is surrounded by a white aura.", self, None, None, merc.TO_ROOM)
            elif sn == 9:
                self.affected_by.set_bit(merc.AFF_SNEAK)
                self.send("Your footsteps stop making any sound.\n")
                handler_game.act("$n's footsteps stop making any sound.", self, None, None, merc.TO_ROOM)
            elif sn == 10:
                self.itemaff.set_bit(merc.ITEMA_SHOCKSHIELD)
                self.send("You are surrounded by a crackling shield of lightning.\n")
                handler_game.act("$n is surrounded by a crackling shield of lightning.", self, None, None, merc.TO_ROOM)
            elif sn == 11:
                self.itemaff.set_bit(merc.ITEMA_FIRESHIELD)
                self.send("You are surrounded by a burning shield of flames.\n")
                handler_game.act("$n is surrounded by a burning shield of flames.", self, None, None, merc.TO_ROOM)
            elif sn == 12:
                self.itemaff.set_bit(merc.ITEMA_ICESHIELD)
                self.send("You are surrounded by a shimmering shield of ice.\n")
                handler_game.act("$n is surrounded by a shimmering shield of ice.", self, None, None, merc.TO_ROOM)
            elif sn == 13:
                self.itemaff.set_bit(merc.ITEMA_ACIDSHIELD)
                self.send("You are surrounded by a bubbling shield of acid.\n")
                handler_game.act("$n is surrounded by a bubbling shield of acid.", self, None, None, merc.TO_ROOM)
            elif sn == 14:
                self.itemaff.set_bit(merc.ITEMA_DBPASS)
                self.send("You are now safe from the DarkBlade clan guardians.\n")
            elif sn == 15:
                self.itemaff.set_bit(merc.ITEMA_CHAOSSHIELD)
                self.send("You are surrounded by a swirling shield of chaos.\n")
                handler_game.act("$n is surrounded by a swirling shield of chaos.", self, None, None, merc.TO_ROOM)
            elif sn == 16:
                self.itemaff.set_bit(merc.ITEMA_REGENERATE)
            elif sn == 17:
                self.itemaff.set_bit(merc.ITEMA_SPEED)
                self.send("You start moving faster than the eye can follow.\n")
                handler_game.act("$n starts moving faster than the eye can follow.", self, None, None, merc.TO_ROOM)
            elif sn == 18:
                self.itemaff.set_bit(merc.ITEMA_VORPAL)
            elif sn == 19:
                self.itemaff.set_bit(merc.ITEMA_PEACE)
            elif sn == 20:
                self.itemaff.set_bit(merc.ITEMA_REFLECT)
                self.send("You are surrounded by flickering shield of darkness.\n")
                handler_game.act("$n is surrounded by a flickering shield of darkness.", self, None, None, merc.TO_ROOM)
            elif sn == 21:
                self.itemaff.set_bit(merc.ITEMA_RESISTANCE)
            elif sn == 22:
                self.itemaff.set_bit(merc.ITEMA_VISION)
                self.send("Your eyes begin to glow bright white.\n")
                handler_game.act("$n's eyes begin to glow bright white.", self, None, None, merc.TO_ROOM)
            elif sn == 23:
                self.itemaff.set_bit(merc.ITEMA_STALKER)
            elif sn == 24:
                self.itemaff.set_bit(merc.ITEMA_VANISH)
                self.send("You blend into the shadows.\n")
                handler_game.act("$n gradually fades into the shadows.", self, None, None, merc.TO_ROOM)
            elif sn == 25 and not self.is_npc():
                self.itemaff.set_bit(merc.ITEMA_RAGER)
                if self.is_werewolf():
                    if self.powers[merc.UNI_RAGE] < 100:
                        self.powers[merc.UNI_RAGE] = 300
                        self.werewolf()
                    else:
                        self.powers[merc.UNI_RAGE] = 300
                elif self.is_vampire():
                    self.powers[merc.UNI_RAGE] = 2

            if not self.is_npc():
                if item.flags.demonic and self.powers[merc.DEMON_POWER] < 15:
                    self.powers[merc.DEMON_POWER] += 1

                if item.flags.highlander and item.item_type == merc.ITEM_WEAPON:
                    if item.value[3] == self.powers[merc.HPOWER_WPNSKILL]:
                        self.itemaff.set_bit(merc.ITEMA_HIGHLANDER)

            if item.flags.artifact:
                self.itemaff.set_bit(merc.ITEMA_ARTIFACT)

            if item.flags.silver and item.slots.right_hand:
                self.itemaff.set_bit(merc.ITEMA_RIGHT_SILVER)
            if item.flags.silver and item.slots.left_hand:
                self.itemaff.set_bit(merc.ITEMA_LEFT_SILVER)

    def can_equip(self, item, loc, should_replace=False, verbose=False):
        if item.environment:
            try:
                item.environment.get(item)
            except:
                return False

        if (item.flags.anti_evil and self.is_evil()) or (item.flags.anti_good and self.is_good()) or \
                (item.flags.anti_neutral and self.is_neutral()):
            handler_game.act("You are zapped by $p and drop it.", self, item, None, merc.TO_CHAR)
            handler_game.act("$n is zapped by $p and drops it.", self, item, None, merc.TO_ROOM)
            self.get(item)
            self.in_room.put(item)
            return False

        if (self.is_npc() or not self.is_demon()) and item.flags.demonic:
            handler_game.act("You are zapped by $p and drop it.", self, item, None, merc.TO_CHAR)
            handler_game.act("$n is zapped by $p and drops it.", self, item, None, merc.TO_ROOM)
            self.get(item)
            self.in_room.put(item)
            return False

        if (self.is_npc() or not self.is_immortal()) and item.flags.relic and not item.flags.demonic and not item.flags.highlander and \
                not item.chobj:
            handler_game.act("You are zapped by $p and drop it.", self, item, None, merc.TO_CHAR)
            handler_game.act("$n is zapped by $p and drops it.", self, item, None, merc.TO_ROOM)
            self.get(item)
            self.in_room.put(item)
            return False

        # Mercpoint - commented out to enable wearing more than one artifact.
        # Damcap is not modified by more than 500 on wearing more than one
        # artifact due to the fact that the damcap modifier is based on whether
        # a player is affected by ITEMA_ARTIFACT and as this can only be either
        # on or off it only affects damcap once :)
        # Therefore this enables a player to wear all the artifacts they have
        # aquired (call it a reward for having got them) as because we have
        # changed the code such that artifacts can no longer be put in bags,
        # it now follows that a player with more than one artifact who is decapped
        # will have his corpse looted for all of those artifacts.
        # Hence he might as well can the benefit for having them.
        #
        # It miht be an idea to add a check such that if the player is still
        # wearing an artifact when they remove one that the ITEMA_ARTIFACT bit
        # isn't removed. - Merc (4/10/96)
        # if item.flags.artifact and self.itemaff.is_set(merc.ITEMA_ARTIFACT):
        # handler_game.act("You are zapped by $p and drop it.", self, item, None, merc.TO_CHAR)
        # handler_game.act("$n is zapped by $p and drops it.", self, item, None, merc.TO_ROOM)
        # self.get(item)
        # self.in_room.put(item)
        # return

        if (self.is_npc() or not self.is_highlander()) and item.flags.highlander:
            handler_game.act("You are zapped by $p and drop it.", self, item, None, merc.TO_CHAR)
            handler_game.act("$n is zapped by $p and drops it.", self, item, None, merc.TO_ROOM)
            self.get(item)
            self.in_room.put(item)
            return False

        if should_replace:
            if not self.unequip(loc):
                return False

        if not self.is_npc():
            if loc in ["right_hand", "left_hand"]:
                if item.get_weight() > const.str_app[self.stat(merc.STAT_STR)].wield:
                    if verbose:
                        self.send("It is too heavy for you to wield.\n")
                    return False
                return True
            return True
        return True

    # Equip a char with an obj.
    def equip(self, item, replace: bool = False, verbose: bool = False, verbose_all: bool = False, to_loc: str = None):
        """

        :type item: int or Items
        :type replace: bool
        :type verbose: bool
        :param verbose_all:
        :type to_loc: builtins.NoneType
        :return: :rtype:
        """
        wolf_ok = (not self.is_npc() and self.is_werewolf() and item.flags.wolfweapon)

        if not item.equips_to:
            if verbose:
                self.send("You can't wear, wield, or hold that.\n")
            return

        if to_loc:
            success = self.can_equip(item, to_loc, False, False)
            success = self.is_ok_to_wear(to_loc, wolf_ok, success)
            if success:
                self.raw_equip(item, to_loc)
        else:
            possible_slots = item.equips_to & self.slots.available
            if len(possible_slots) > 0:
                success = self.can_equip(item, [k for k in possible_slots][0], False, verbose)
                success = self.is_ok_to_wear(possible_slots, wolf_ok, success)

                if success:
                    location = [k for k in possible_slots][0]
                    self.raw_equip(item, location)

                    if verbose_all:
                        self.verbose_wear_strings(item, location)
            else:
                if replace:
                    all_slots = {k for k in self.equipped.keys()}
                    overlap = item.equips_to & all_slots
                    if len(overlap) > 0:
                        success = self.can_equip(item, [k for k in overlap][0], True, verbose)
                        success = self.is_ok_to_wear(possible_slots, wolf_ok, success)
                        if success:
                            location = [k for k in overlap][0]
                            self.raw_equip(item, location)

                            if verbose_all:
                                self.verbose_wear_strings(item, location)
                    else:
                        if verbose:
                            self.send("You can't wear, wield, or hold that.\n")
                else:
                    if verbose:
                        self.send("You are already wearing something like that!\n")

    def remove_affect(self, aff_object):
        """
        Taken from unequip to shorten it, searches for Affects, and removes as needed

        :param aff_object:
        :type aff_object:
        :return: Nothing
        :rtype: none
        """
        for paf in aff_object.affected:
            self.affect_modify(paf, False)

    # Unequip a char with an obj.
    def unequip(self, unequip_from, forced: bool = True, silent: bool = False):
        """
        :param unequip_from:
        :type unequip_from:
        :param forced:
        :type forced:
        :param silent:
        :type silent:
        :return:
        :rtype:
        """
        if isinstance(unequip_from, int):
            try:
                item = instance.items[unequip_from]
            except:
                return False
        elif isinstance(unequip_from, str):
            try:
                item = instance.items[self.equipped[unequip_from]]
            except:
                return False
        elif hasattr(unequip_from, "is_item") and unequip_from.is_item:
            item = unequip_from
        else:
            return False

        if not item.is_item:
            raise TypeError("Expected item on unequip, got %r" % type(item))

        if not forced:
            return False

        if item.flags.no_remove:
            handler_game.act("You can't remove $p.", self, item, None, merc.TO_CHAR)
            return False

        self.raw_unequip(item)
        if not silent:
            handler_game.act("$n stops using $p.", self, item, None, merc.TO_ROOM)
            handler_game.act("You stop using $p.", self, item, None, merc.TO_CHAR)
        return True

    def raw_unequip(self, item):
        if not item:
            return None

        oldpos = item.equipped_to
        if (self.is_npc() or not self.is_highlander()) and oldpos not in ["left_scabbard", "right_scabbard"]:
            self.armor += item.apply_ac()

        self.equipped[item.equipped_to] = None
        self.inventory += [item.instance_id]

        if oldpos in ["left_scabbard", "right_scabbard"]:
            return

        self.remove_affect(item)

        if item.item_type == merc.ITEM_LIGHT and item.value[2] != 0 and self.in_room and self.in_room.available_light > 0:
            self.in_room.available_light -= 1

        if not self.is_npc():
            chch = self.get_char_world(self.name)
            if chch and chch.desc != self.desc:
                return

        if item.chpoweroff and not item.spectype.is_set(merc.SITEM_TELEPORTER) and not item.spectype.is_set(merc.SITEM_TRANSPORTER):
            handler_game.kavitem(item.chpoweroff, self, item, None, merc.TO_CHAR)

            if item.spectype.is_set(merc.SITEM_ACTION):
                handler_game.kavitem(item.chpoweroff, self, item, None, merc.TO_ROOM)

        if item.victpoweroff and not item.spectype.is_set(merc.SITEM_ACTION) and not item.spectype.is_set(merc.SITEM_TELEPORTER) and \
                not item.spectype.is_set(merc.SITEM_TRANSPORTER):
            handler_game.kavitem(item.victpoweroff, self, item, None, merc.TO_ROOM)

        if (item.item_type == merc.ITEM_ARMOR and item.value[3] >= 1) or (item.item_type == merc.ITEM_WEAPON and item.value[0] >= 1000) or \
                item.flags.silver or item.flags.demonic or item.flags.artifact:
            if item.item_type == merc.ITEM_ARMOR:
                sn = item.value[3]
            else:
                sn = item.value[0] // 1000

            if self.is_affected(merc.AFF_BLIND) and sn == 4 and not self.is_affected(4):
                self.affected_by.rem_bit(merc.AFF_BLIND)
                self.send("You can see again.\n")
                handler_game.act("$n seems to be able to see again.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_DETECT_INVIS) and sn in [2, 27] and not self.is_affected(27):
                self.affected_by.rem_bit(merc.AFF_DETECT_INVIS)
                self.send("Your eyes stop tingling.\n")
                handler_game.act("$n's eyes stop flickering with light.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_FLYING) and sn in [3, 39] and not self.is_affected(39):
                self.affected_by.rem_bit(merc.AFF_FLYING)
                self.send("You slowly float to the ground.\n")
                handler_game.act("$n slowly floats to the ground.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_INFRARED) and sn in [1, 45] and not self.is_affected(45):
                self.affected_by.rem_bit(merc.AFF_INFRARED)
                self.send("Your eyes stop glowing red.\n")
                handler_game.act("$n's eyes stop glowing red.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_INVISIBLE) and sn in [5, 46] and not self.is_affected(46):
                self.affected_by.rem_bit(merc.AFF_INVISIBLE)
                self.send("You fade into existance.\n")
                handler_game.act("$n fades into existance.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_PASS_DOOR) and sn in [6, 52] and not self.is_affected(52):
                self.affected_by.rem_bit(merc.AFF_PASS_DOOR)
                self.send("You feel solid again.\n")
                handler_game.act("$n is no longer translucent.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_PROTECT) and sn in [7, 54] and not self.is_affected(54):
                self.affected_by.rem_bit(merc.AFF_PROTECT)
                self.send("The divine aura around you fades.\n")
                handler_game.act("The divine aura around $n fades.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_SANCTUARY) and sn in [8, 57] and not self.is_affected(57):
                self.affected_by.rem_bit(merc.AFF_SANCTUARY)
                self.send("The white aura around your body fades.\n")
                handler_game.act("The white aura about $n's body fades.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_SNEAK) and sn == 9 and not self.is_affected(80):
                self.affected_by.rem_bit(merc.AFF_SNEAK)
                self.send("You are no longer moving so quietly.\n")
                handler_game.act("$n is no longer moving so quietly.", self, None, None, merc.TO_ROOM)
            elif self.is_affected(merc.AFF_DETECT_HIDDEN) and sn == 60:
                self.affected_by.rem_bit(merc.AFF_DETECT_HIDDEN)
                self.send("You feel less aware of your surrondings.\n")
                handler_game.act("$n eyes tingle.", self, None, None, merc.TO_ROOM)
            elif self.itemaff.is_set(merc.ITEMA_SHOCKSHIELD) and sn == 10:
                self.itemaff.rem_bit(merc.ITEMA_SHOCKSHIELD)
                self.send("The crackling shield of lightning around you fades.\n")
                handler_game.act("The crackling shield of lightning around $n fades.", self, None, None, merc.TO_ROOM)
            elif self.itemaff.is_set(merc.ITEMA_FIRESHIELD) and sn == 11:
                self.itemaff.rem_bit(merc.ITEMA_FIRESHIELD)
                self.send("The burning shield of fire around you fades.\n")
                handler_game.act("The burning shield of fire around $n fades.", self, None, None, merc.TO_ROOM)
            elif self.itemaff.is_set(merc.ITEMA_ICESHIELD) and sn == 12:
                self.itemaff.rem_bit(merc.ITEMA_ICESHIELD)
                self.send("The shimmering shield of ice around you fades.\n")
                handler_game.act("The shimmering shield of ice around $n fades.", self, None, None, merc.TO_ROOM)
            elif self.itemaff.is_set(merc.ITEMA_ACIDSHIELD) and sn == 13:
                self.affected_by.rem_bit(merc.ITEMA_ACIDSHIELD)
                self.send("The bubbling shield of acid around you fades.\n")
                handler_game.act("The bubbling shield of acid around $n fades.", self, None, None, merc.TO_ROOM)
            elif self.itemaff.is_set(merc.ITEMA_DBPASS) and sn == 14:
                self.affected_by.rem_bit(merc.ITEMA_DBPASS)
                self.send("You are no longer safe from the DarkBlade clan guardians.\n")
            elif self.itemaff.is_set(merc.ITEMA_CHAOSSHIELD) and sn == 15:
                self.itemaff.rem_bit(merc.ITEMA_CHAOSSHIELD)
                self.send("The swirling shield of chaos around you fades.\n")
                handler_game.act("The swirling shield of chaos around $n fades.", self, None, None, merc.TO_ROOM)
            elif sn == 16:
                self.itemaff.rem_bit(merc.ITEMA_REGENERATE)
            elif self.itemaff.is_set(merc.ITEMA_SPEED) and sn == 17:
                self.itemaff.rem_bit(merc.ITEMA_SPEED)
                self.send("Your actions slow down to normal speed.\n")
                handler_game.act("$n stops moving at supernatural speed.", self, None, None, merc.TO_ROOM)
            elif sn == 18:
                self.itemaff.rem_bit(merc.ITEMA_VORPAL)
            elif sn == 19:
                self.itemaff.rem_bit(merc.ITEMA_PEACE)
            elif self.itemaff.is_set(merc.ITEMA_REFLECT) and sn == 20:
                self.itemaff.rem_bit(merc.ITEMA_REFLECT)
                self.send("The flickering shield of darkness around you fades.\n")
                handler_game.act("The flickering shield of darkness around $n fades.", self, None, None, merc.TO_ROOM)
            elif sn == 21:
                self.itemaff.rem_bit(merc.ITEMA_RESISTANCE)
            elif self.itemaff.is_set(merc.ITEMA_VISION) and sn == 22:
                self.itemaff.rem_bit(merc.ITEMA_VISION)
                self.send("Your eyes stop glowing bright white.\n")
                handler_game.act("$n's eyes stop glowing bright white.", self, None, None, merc.TO_ROOM)
            elif sn == 23:
                self.itemaff.rem_bit(merc.ITEMA_STALKER)
            elif self.itemaff.is_set(merc.ITEMA_VANISH) and sn == 24:
                self.itemaff.rem_bit(merc.ITEMA_VANISH)
                self.send("You emerge from the shadows.\n")
                handler_game.act("$n gradually fades out of the shadows.", self, None, None, merc.TO_ROOM)
            elif not self.is_npc() and self.itemaff.is_set(merc.ITEMA_RAGER) and sn == 25:
                self.itemaff.rem_bit(merc.ITEMA_RAGER)

                if self.is_werewolf() and self.powers[merc.UNI_RAGE] >= 100:
                    self.powers[merc.UNI_RAGE] = 0
                    self.unwerewolf()
                self.powers[merc.UNI_RAGE] = 0

            if item.flags.demonic and not self.is_npc() and self.powers[merc.DEMON_POWER] > 0:
                self.powers[merc.DEMON_POWER] -= 1

            if item.flags.highlander and not self.is_npc() and item.item_type == merc.ITEM_WEAPON:
                if item.value[3] == self.powers[merc.HPOWER_WPNSKILL]:
                    self.itemaff.rem_bit(merc.ITEMA_HIGHLANDER)

            self.itemaff.rem_bit(merc.ITEMA_ARTIFACT)

            if item.flags.silver and oldpos == "right_hand":
                self.itemaff.rem_bit(merc.ITEMA_RIGHT_SILVER)
            if item.flags.silver and oldpos == "left_hand":
                self.itemaff.rem_bit(merc.ITEMA_LEFT_SILVER)

    def verbose_wear_strings(self, item, slot):
        """
        :param item:
        :type item:
        :param slot:
        :type slot:
        :return:
        :rtype:
        """
        if slot == "left_finger":
            handler_game.act("$n wears $p on $s left finger.", self, item, None, merc.TO_ROOM)
            handler_game.act("You wear $p on your left finger.", self, item, None, merc.TO_CHAR)
        elif slot == "right_finger":
            handler_game.act("$n wears $p on $s right finger.", self, item, None, merc.TO_ROOM)
            handler_game.act("You wear $p on your right finger.", self, item, None, merc.TO_CHAR)
        elif slot in ["neck_one", "neck_two"]:
            handler_game.act("$n slips $p around $s neck.", self, item, None, merc.TO_ROOM)
            handler_game.act("You slip $p around your neck.", self, item, None, merc.TO_CHAR)
        elif slot == "body":
            handler_game.act("$n fits $p on $s body.", self, item, None, merc.TO_ROOM)
            handler_game.act("You fit $p on your body.", self, item, None, merc.TO_CHAR)
        elif slot == "head":
            handler_game.act("$n places $p on $s head.", self, item, None, merc.TO_ROOM)
            handler_game.act("You place $p on your head.", self, item, None, merc.TO_CHAR)
        elif slot == "face":
            handler_game.act("$n places $p on $s face.", self, item, None, merc.TO_ROOM)
            handler_game.act("You place $p on your face.", self, item, None, merc.TO_CHAR)
        elif slot == "legs":
            handler_game.act("$n slips $s legs into $p.", self, item, None, merc.TO_ROOM)
            handler_game.act("You slip your legs into $p.", self, item, None, merc.TO_CHAR)
        elif slot == "feet":
            handler_game.act("$n slips $s feet into $p.", self, item, None, merc.TO_ROOM)
            handler_game.act("You slip your feet into $p.", self, item, None, merc.TO_CHAR)
        elif slot == "hands":
            handler_game.act("$n pulls $p onto $s hands.", self, item, None, merc.TO_ROOM)
            handler_game.act("You pull $p onto your hands.", self, item, None, merc.TO_CHAR)
        elif slot == "arms":
            handler_game.act("$n slides $s arms into $p.", self, item, None, merc.TO_ROOM)
            handler_game.act("You slide your arms into $p.", self, item, None, merc.TO_CHAR)
        elif slot == "about_body":
            handler_game.act("$n pulls $p about $s body.", self, item, None, merc.TO_ROOM)
            handler_game.act("You pull $p about your body.", self, item, None, merc.TO_CHAR)
        elif slot == "waist":
            handler_game.act("$n ties $p around $s waist.", self, item, None, merc.TO_ROOM)
            handler_game.act("You tie $p around your waist.", self, item, None, merc.TO_CHAR)
        elif slot == "left_wrist":
            handler_game.act("$n slides $s left wrist into $p.", self, item, None, merc.TO_ROOM)
            handler_game.act("You slide your left wrist into $p.", self, item, None, merc.TO_CHAR)
        elif slot == "right_wrist":
            handler_game.act("$n slides $s right wrist into $p.", self, item, None, merc.TO_ROOM)
            handler_game.act("You slide your right wrist into $p.", self, item, None, merc.TO_CHAR)
        elif slot == "right_hand":
            if item.item_type == merc.ITEM_LIGHT:
                handler_game.act("$n lights $p and clutches it in $s right hand.", self, item, None, merc.TO_ROOM)
                handler_game.act("You light $p and clutch it in your right hand.", self, item, None, merc.TO_CHAR)
            else:
                handler_game.act("$n clutches $p in $s right hand.", self, item, None, merc.TO_ROOM)
                handler_game.act("You clutch $p in your right hand.", self, item, None, merc.TO_CHAR)
        elif slot == "left_hand":
            if item.item_type == merc.ITEM_LIGHT:
                handler_game.act("$n lights $p and clutches it in $s left hand.", self, item, None, merc.TO_ROOM)
                handler_game.act("You light $p and clutch it in your left hand.", self, item, None, merc.TO_CHAR)
            else:
                handler_game.act("$n clutches $p in $s left hand.", self, item, None, merc.TO_ROOM)
                handler_game.act("You clutch $p in your left hand.", self, item, None, merc.TO_CHAR)
        else:
            raise LookupError("Unable to find verbose wear string for %s" % slot)
