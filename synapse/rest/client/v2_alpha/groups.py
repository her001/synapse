# -*- coding: utf-8 -*-
# Copyright 2017 Vector Creations Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from twisted.internet import defer

from synapse.http.servlet import RestServlet, parse_json_object_from_request
from synapse.types import GroupID

from ._base import client_v2_patterns

import logging

logger = logging.getLogger(__name__)


class GroupServlet(RestServlet):
    PATTERNS = client_v2_patterns("/groups/(?P<group_id>[^/]*)/profile$")

    def __init__(self, hs):
        super(GroupServlet, self).__init__()
        self.auth = hs.get_auth()
        self.clock = hs.get_clock()
        self.groups_handler = hs.get_groups_handler()

    @defer.inlineCallbacks
    def on_GET(self, request, group_id):
        requester = yield self.auth.get_user_by_req(request)
        user_id = requester.user.to_string()

        group_description = yield self.groups_handler.get_group_profile(group_id, user_id)

        defer.returnValue((200, group_description))


class GroupSummaryServlet(RestServlet):
    PATTERNS = client_v2_patterns("/groups/(?P<group_id>[^/]*)/summary$")

    def __init__(self, hs):
        super(GroupSummaryServlet, self).__init__()
        self.auth = hs.get_auth()
        self.clock = hs.get_clock()
        self.groups_handler = hs.get_groups_handler()

    @defer.inlineCallbacks
    def on_GET(self, request, group_id):
        requester = yield self.auth.get_user_by_req(request)
        user_id = requester.user.to_string()

        get_group_summary = yield self.groups_handler.get_group_summary(group_id, user_id)

        defer.returnValue((200, get_group_summary))


class GroupRoomServlet(RestServlet):
    PATTERNS = client_v2_patterns("/groups/(?P<group_id>[^/]*)/rooms$")

    def __init__(self, hs):
        super(GroupRoomServlet, self).__init__()
        self.auth = hs.get_auth()
        self.clock = hs.get_clock()
        self.groups_handler = hs.get_groups_handler()

    @defer.inlineCallbacks
    def on_GET(self, request, group_id):
        requester = yield self.auth.get_user_by_req(request)
        user_id = requester.user.to_string()

        result = yield self.groups_handler.get_rooms_in_group(group_id, user_id)

        defer.returnValue((200, result))


class GroupUsersServlet(RestServlet):
    PATTERNS = client_v2_patterns("/groups/(?P<group_id>[^/]*)/users$")

    def __init__(self, hs):
        super(GroupUsersServlet, self).__init__()
        self.auth = hs.get_auth()
        self.clock = hs.get_clock()
        self.groups_handler = hs.get_groups_handler()

    @defer.inlineCallbacks
    def on_GET(self, request, group_id):
        requester = yield self.auth.get_user_by_req(request)
        user_id = requester.user.to_string()

        result = yield self.groups_handler.get_users_in_group(group_id, user_id)

        defer.returnValue((200, result))


class GroupCreateServlet(RestServlet):
    PATTERNS = client_v2_patterns("/create_group$")

    def __init__(self, hs):
        super(GroupCreateServlet, self).__init__()
        self.auth = hs.get_auth()
        self.clock = hs.get_clock()
        self.groups_handler = hs.get_groups_handler()
        self.server_name = hs.hostname

    @defer.inlineCallbacks
    def on_POST(self, request):
        requester = yield self.auth.get_user_by_req(request)

        content = parse_json_object_from_request(request)
        localpart = content.pop("localpart")
        group_id = GroupID.create(localpart, self.server_name).to_string()

        result = yield self.groups_handler.create_group(group_id, requester, content)

        defer.returnValue((200, result))


class GroupAdminAddRoomsServlet(RestServlet):
    PATTERNS = client_v2_patterns("/groups/(?P<group_id>[^/]*)/admin/add_room$")

    def __init__(self, hs):
        super(GroupAdminAddRoomsServlet, self).__init__()
        self.auth = hs.get_auth()
        self.clock = hs.get_clock()
        self.groups_handler = hs.get_groups_handler()

    @defer.inlineCallbacks
    def on_POST(self, request, group_id):
        requester = yield self.auth.get_user_by_req(request)
        user_id = requester.user.to_string()

        content = parse_json_object_from_request(request)
        room_id = content.pop("room_id")
        result = yield self.groups_handler.add_room(group_id, user_id, room_id, content)

        defer.returnValue((200, result))


def register_servlets(hs, http_server):
    GroupServlet(hs).register(http_server)
    GroupSummaryServlet(hs).register(http_server)
    GroupUsersServlet(hs).register(http_server)
    GroupRoomServlet(hs).register(http_server)
    GroupCreateServlet(hs).register(http_server)
    GroupAdminAddRoomsServlet(hs).register(http_server)