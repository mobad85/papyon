# -*- coding: utf-8 -*-
#
# Copyright (C) 2007  Ali Sabil <ali.sabil@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from base import BaseEventInterface

__all__ = ["ConversationEventInterface"]

class ConversationEventInterface(BaseEventInterface):
    def __init__(self, conversation):
        BaseEventInterface.__init__(self, conversation)

    def on_conversation_state_changed(self, state):
        pass

    def on_conversation_error(self, type, error):
        pass

    def on_conversation_user_joined(self, contact):
        pass

    def on_conversation_user_left(self, contact):
        pass

    def on_conversation_message_received(self, sender, message, formatting):
        pass
    
    def on_conversation_nudge_received(self, sender):
        pass
