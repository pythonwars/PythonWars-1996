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

import comm
import instance
import merc


class Environment:
    def __init__(self):
        super().__init__()
        self._environment = None
        self.was_in_room = None
        # When we load into a game without persistent room instances, this will get us to logged room
        self._room_vnum = None
        self.zone_template = ""
        self.zone = 0
        self.area = None
        self.available_light = 0
        self.blood = 0

    @property
    def environment(self):
        # TODO: Remove this once we track down the source. This should never happen.
        if self._environment == self:
            # noinspection PyUnresolvedReferences
            comm.notify("{} environment is set to itself".format(self.name), merc.CONSOLE_ERROR)
            self._environment = None

        return instance.global_instances.get(self._environment, None)

    @environment.setter
    def environment(self, input_value):
        if not input_value:
            self._environment = None
        elif isinstance(input_value, int):
            self._environment = input_value
        else:
            raise TypeError('Environment trying to be set with non integer value %r' % type(input_value))

    @property
    def in_area(self):
        current_step = self.environment
        while current_step:
            if current_step.is_area:
                return current_step
            current_step = current_step.environment
        return None

    @property
    def in_living(self):
        current_step = self.environment
        while current_step:
            if current_step.is_living:
                return current_step
            current_step = current_step.environment
        return None

    @property
    def in_room(self):
        current_step = self.environment
        while current_step:
            if current_step.is_room:
                return current_step
            current_step = current_step.environment
        return None

    @property
    def in_item(self):
        current_step = self.environment
        while current_step:
            if current_step.is_item:
                return current_step
            current_step = current_step.environment
        return None

    # Move an instance from a location
    def get(self, instance_object):
        pass

    # Give an obj to a char.
    def put(self, instance_object):
        pass

    def valid_key(self, key):
        # noinspection PyUnresolvedReferences
        instance_id = [item_id for item_id in self.items if instance.items[item_id].vnum == key.vnum]
        return bool(instance_id)

    # Return # of objects which an object counts as.
    # Thanks to Tony Chamberlain for the correct recursive code here.
    def get_number(self):
        try:  # if self is an item.
            noweight = [merc.ITEM_CONTAINER, merc.ITEM_MONEY]
            # noinspection PyUnresolvedReferences
            if self.item_type in noweight:
                number = 0
            else:
                number = 1
        except AttributeError:
            number = 1

        # noinspection PyUnresolvedReferences
        contents = self.inventory[:]
        # noinspection PyUnresolvedReferences
        counted = [self.instance_id]
        for content_id in contents:
            content = instance.items[content_id]
            number += 1
            if content.instance_id in counted:
                # noinspection PyUnresolvedReferences
                comm.notify("get_number: items contain each other. {} ({}) - {} ({})".format(self.short_descr, self.instance_id,
                                                                                             content.short_descr, content.instance_id), merc.CONSOLE_ERROR)
                break

            counted.append(content)
            contents.extend(content.inventory)
        return number

    # Return weight of an object, including weight of contents.
    def get_weight(self):
        # noinspection PyUnresolvedReferences
        weight = self.weight
        # noinspection PyUnresolvedReferences
        contents = self.inventory[:]
        # noinspection PyUnresolvedReferences
        counted = [self.instance_id]
        for content_id in contents:
            content = instance.items[content_id]

            if content.instance_id in counted:
                # noinspection PyUnresolvedReferences
                comm.notify("get_weight: items contain each other. {} ({}) - {} ({})".format(self.short_descr, self.instance_id,
                                                                                             content.short_descr, content.instance_id), merc.CONSOLE_ERROR)
                break

            counted.append(content)
            contents.extend(content.inventory)
            try:  # For items in containers
                weight += content.weight
            except AttributeError:
                pass
        return weight

    def true_weight(self):
        # noinspection PyUnresolvedReferences
        weight = self.weight
        # noinspection PyUnresolvedReferences
        for content_id in self.inventory[:]:
            content = instance.items[content_id]
            weight += content.get_weight()
        return weight
