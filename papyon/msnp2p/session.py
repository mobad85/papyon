# -*- coding: utf-8 -*-
#
# papyon - a python client library for Msn
#
# Copyright (C) 2007 Ali Sabil <ali.sabil@gmail.com>
# Copyright (C) 2008 Richard Spiers <richard.spiers@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from papyon.msnp2p.constants import *
from papyon.msnp2p.SLP import *
from papyon.msnp2p.transport import *
from papyon.msnp2p.exceptions import *
import papyon.util.element_tree as ElementTree
import struct

import papyon.util.guid as guid

import gobject
import base64
import random
__all__ = ['P2PSession']

MAX_INT32 = 0x7fffffff
MAX_INT16 = 0x7fff


class P2PSession(gobject.GObject):
    __gsignals__ = {
            "transfer-completed" : (gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE,
                (object,))
    }
    def __init__(self, session_manager, peer, euf_guid="", application_id=0):
        gobject.GObject.__init__(self)
        self._session_manager = session_manager
        self._peer = peer

        self._id =  self._generate_id()
        self._call_id = "{%s}" % guid.generate_guid()

        self._euf_guid = euf_guid
        self._application_id = application_id

        self._cseq = 0
        self._branch = "{%s}" % guid.generate_guid()
        self._session_manager._register_session(self)

    def _generate_id(self, max=MAX_INT32):
        """
        Returns a random ID.

        @return: a random integer between 1000 and sys.maxint
        @rtype: integer
        """
        return random.randint(1000, max)

    @property
    def id(self):
        return self._id

    @property
    def call_id(self):
        return self._call_id

    @property
    def peer(self):
        return self._peer

    def _respond(self, status_code):
        body = SLPSessionRequestBody(session_id=self._id,capabilities_flags=None,s_channel_state=None)
        self._cseq += 1
        response = SLPResponseMessage(status_code,
            to=self._peer.account,
            frm=self._session_manager._client.profile.account,
            cseq=self._cseq,
            branch=self._branch,
            call_id=self._call_id)
        response.body = body
        self._send_p2p_data(response)

    def _close(self):
        body = SLPSessionCloseBody()
        self._cseq = 0
        self._branch = "{%s}" % guid.generate_guid()
        message = SLPRequestMessage(SLPRequestMethod.BYE,
                "MSNMSGR:" + self._peer.account,
                to=self._peer.account,
                frm=self._session_manager._client.profile.account,
                branch=self._branch,
                cseq=self._cseq,
                call_id=self._call_id)
        message.body = body
        self._send_p2p_data(message)
        self._session_manager._unregister_session(self)

    def _send_p2p_data(self, data_or_file):
        if isinstance(data_or_file, SLPMessage):
            session_id = 0
            data = str(data_or_file)
            total_size = len(data)
        else:
            session_id = self._id
            data = data_or_file
            total_size = None

        blob = MessageBlob(self._application_id,
                data, total_size, session_id)
        self._session_manager._transport_manager.send(self.peer, blob)

    def _on_blob_sent(self, blob):
        if blob.session_id == 0:
            # FIXME: handle the signaling correctly
            return

        if blob.total_size == 4 and \
                blob.data.read() == ('\x00' * 4):
            self._on_data_preparation_blob_sent(blob)
        else:
            self._on_data_blob_sent(blob)

    def _on_blob_received(self, blob):
        if blob.session_id == 0:
            # FIXME: handle the signaling correctly
            return

        if blob.total_size == 4 and \
                blob.data.read() == ('\x00' * 4):
            self._on_data_preparation_blob_received(blob)
        else:
            self._on_data_blob_received(blob)
            self._close()

    def _on_data_preparation_blob_received(self, blob):
        pass

    def _on_data_preparation_blob_sent(self, blob):
        pass

    def _on_data_blob_sent(self, blob):
        blob.data.seek(0, 0)
        self.emit("transfer-completed", blob.data)

    def _on_data_blob_received(self, blob):
        blob.data.seek(0, 0)
        self.emit("transfer-completed", blob.data)

gobject.type_register(P2PSession)
