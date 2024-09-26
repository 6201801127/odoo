"""Zoom.us REST API Python Client -- User component"""

# from __future__ import absolute_import

from . import util
from . import base


class UserComponentV2(base.BaseComponent):
    def list(self, **kwargs):
        return self.get_request("/users", params=kwargs)

    def create(self, **kwargs):
        return self.post_request("/users", data=kwargs)

    def update(self, **kwargs):
        util.require_keys(kwargs, "id")
        return self.patch_request("/users/{}".format(kwargs.get("id")), data=kwargs)

    def delete(self, **kwargs):
        util.require_keys(kwargs, "id")
        return self.delete_request("/users/{}".format(kwargs.get("id")), params=kwargs)

    def get(self, **kwargs):
        util.require_keys(kwargs, "id")
        return self.get_request("/users/{}".format(kwargs.get("id")), params=kwargs)
