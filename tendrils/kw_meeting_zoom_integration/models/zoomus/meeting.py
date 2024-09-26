"""Zoom.us REST API Python Client"""

# from __future__ import absolute_import

from . import util
from . import base


class MeetingComponentV2(base.BaseComponent):
    def list(self, **kwargs):
        util.require_keys(kwargs, "user_id")
        return self.get_request(
            "/users/{}/meetings".format(kwargs.get("user_id")), params=kwargs
        )

    def create(self, **kwargs):
        util.require_keys(kwargs, "user_id")
        if kwargs.get("start_time"):
            kwargs["start_time"] = util.date_to_str(kwargs["start_time"])
        return self.post_request(
            "/users/{}/meetings".format(kwargs.get("user_id")), data=kwargs
        )

    def get(self, **kwargs):
        util.require_keys(kwargs, "id")
        return self.get_request("/meetings/{}".format(kwargs.get("id")), params=kwargs)

    def update(self, **kwargs):
        util.require_keys(kwargs, "id")
        if kwargs.get("start_time"):
            kwargs["start_time"] = util.date_to_str(kwargs["start_time"])
        return self.patch_request("/meetings/{}".format(kwargs.get("id")), data=kwargs)

    def delete(self, **kwargs):
        util.require_keys(kwargs, "id")
        return self.delete_request(
            "/meetings/{}".format(kwargs.get("id")), params=kwargs
        )
